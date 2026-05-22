# Phase 2 Blueprint: OpenRouter Client & Image Classifier

## Goal

Build the core AI inference path. Given a base64-encoded image, this phase produces
a fully typed `ClassificationResult` by calling Gemma 4 on OpenRouter and parsing
its structured JSON response.

After this phase the AI pipeline can take any photo and return:
- Which civic issue category it is
- How confident the model is (0.0 – 1.0)
- Severity level (low / medium / high)
- A plain-language description of the issue
- Whether it is a civic issue at all

---

## Current Project State

What already exists after Phases 0 and 1:

```
ai/src/kostreet_ai/
├── __init__.py
├── config.py          ← reads KOSTREET_AI_* from .env, settings singleton ready
├── main.py            ← FastAPI app running on port 8001, /health works
├── schemas.py         ← ClassificationResult, ClassificationRequest, all models defined
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── router.py  ← empty router, classify/audit sub-routers commented out
└── preprocessing/
    ├── __init__.py
    └── image.py       ← validate_image, encode_image_to_base64, decode_base64_to_bytes
```

What Phase 2 adds:

```
ai/src/kostreet_ai/
└── inference/
    ├── __init__.py    ← empty
    ├── client.py      ← OpenRouter HTTP wrapper
    └── classifier.py  ← prompt engineering, JSON parse, ClassificationResult factory
```

---

## Files to Create

### `inference/__init__.py`
Empty. Required for Python package resolution.

---

### `inference/client.py`

**Responsibility:** Make HTTP calls to OpenRouter. No prompt logic, no parsing, no
business rules. Only knows how to send a `messages` list and return the raw string
response from the model.

**Class: `OpenRouterClient`**

Constructor arguments:
- `api_key: str` — the OpenRouter key from settings
- `base_url: str` — `https://openrouter.ai/api/v1`
- `model: str` — `google/gemma-4-26b-a4b-it`

**Method: `chat(messages, response_format) -> str`**

Builds this exact request body:
```json
{
  "model": "google/gemma-4-26b-a4b-it",
  "response_format": { "type": "json_object" },
  "messages": [ ... ]
}
```

Required headers:
```
Authorization: Bearer <openrouter_api_key>
Content-Type: application/json
HTTP-Referer: https://kostreet.prizren.io
X-Title: KoStreet
```

Uses `httpx.Client(timeout=30.0)`.
Posts to `{base_url}/chat/completions`.
Calls `response.raise_for_status()` to surface HTTP errors.
Returns `response.json()["choices"][0]["message"]["content"]` as a plain string.

**No retry logic in this phase.** If the request fails it raises, and the classifier
catches it with a fallback.

---

### `inference/classifier.py`

**Responsibility:** Own the system prompt, build the message list, call the client,
parse the JSON response into a `ClassificationResult`, and handle every failure path
gracefully so the service never crashes.

#### System Prompt (exact text)

```
You are a civic infrastructure quality inspector working for Kosovo municipalities.
Your job is to analyze street-level photographs and identify visible civic issues
that require municipal attention.

You must respond with ONLY a valid JSON object. No explanation, no markdown, no
extra text before or after the JSON. The JSON must follow this exact structure:

{
  "category": "<value>",
  "confidence": <float>,
  "severity": "<value>",
  "description": "<text>",
  "is_civic_issue": <boolean>
}

Allowed values for category:
- pothole      : road surface crack, depression, hole, or damaged asphalt
- garbage      : bags, litter, scattered waste, illegal dumping, overflowing bins
- broken_streetlight : damaged light pole, missing fixture, visibly dark lamp
- blocked_sidewalk   : cracked pavement, obstacles, obstructions on walking paths
- damaged_sign       : bent, missing, graffitied, or fallen road or street signs
- other        : any civic issue not covered above

Allowed values for severity:
- high   : immediate safety risk, large damage, major obstruction
- medium : noticeable issue that needs attention within days
- low    : minor cosmetic issue, early-stage problem

confidence must be a float from 0.0 to 1.0 representing how certain you are.

If you do not see any civic issue, respond with:
{
  "category": "other",
  "confidence": 0.0,
  "severity": "low",
  "description": "No civic issue detected in this image.",
  "is_civic_issue": false
}
```

#### User Message Structure

The user turn sent to the model is a list with two content items:
1. A text item: `"Analyze this street-level photograph for civic infrastructure issues."`
2. An image_url item: `{"url": "data:image/jpeg;base64,<b64>"}`

Full message list passed to `client.chat()`:
```python
[
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this street-level photograph for civic infrastructure issues."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
        ],
    },
]
```

#### Class: `ImageClassifier`

Constructor arguments:
- `client: OpenRouterClient`
- `model_name: str`
- `confidence_threshold: float`

**Method: `classify(image_base64: str) -> ClassificationResult`**

Steps in order:
1. Call `self.client.chat(messages, response_format={"type": "json_object"})`
2. Parse the returned string with `json.loads(raw)`
3. Extract fields: `category`, `confidence`, `severity`, `description`, `is_civic_issue`
4. Coerce `category` into `IssueCategory` — if unknown value, use `IssueCategory.other`
5. Coerce `severity` into `IssueSeverity` — if unknown value, use `IssueSeverity.low`
6. Clamp `confidence` to `[0.0, 1.0]`
7. Build and return `ClassificationResult(...)`

**Severity override table** applied after parsing (post-processing):

| Category | Minimum severity | Condition |
|---|---|---|
| `broken_streetlight` | `high` | always — safety risk at night |
| `pothole` | `medium` | always — road hazard |
| `garbage` | `medium` | always — health hazard |

This override runs after the model response to ensure consistent severity for the demo
regardless of what the model returns. It does NOT change `confidence`.

**Fallback on any exception:**

If `json.loads` fails, a key is missing, an enum coercion fails, or the HTTP call
raises — catch all exceptions and return this exact fallback:
```python
ClassificationResult(
    category=IssueCategory.other,
    confidence=0.0,
    severity=IssueSeverity.low,
    description="Classification failed. Please review this image manually.",
    is_civic_issue=False,
)
```

This guarantees the service never returns a 500 to the backend for a bad model response.

#### Module-level singleton factory

```python
def get_classifier() -> ImageClassifier:
    client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.model_name,
    )
    return ImageClassifier(
        client=client,
        model_name=settings.model_name,
        confidence_threshold=settings.confidence_threshold,
    )
```

Called once per request. Stateless — safe to call on every request with no caching needed.

---

## Data Flow After Phase 2

```
image_base64 (str)
      │
      ▼
ImageClassifier.classify()
      │
      ├─► builds messages list (system prompt + image)
      │
      ├─► OpenRouterClient.chat()
      │         │
      │         └─► POST https://openrouter.ai/api/v1/chat/completions
      │                   model: google/gemma-4-26b-a4b-it
      │                   response_format: {type: json_object}
      │
      ├─► json.loads(raw_response)
      │
      ├─► severity override table
      │
      └─► ClassificationResult(category, confidence, severity, description, is_civic_issue)
```

---

## Verification Plan

After implementation, run this manually in the terminal to confirm the full path works
with a real OpenRouter call:

```powershell
cd c:\Users\diar\Desktop\itpprizren\kostreet\ai
.venv\Scripts\activate
python -c "
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import encode_image_to_base64

# use any test photo — even a placeholder JPEG
with open('data/demo/pothole_01.jpg', 'rb') as f:
    b64 = encode_image_to_base64(f.read())

result = get_classifier().classify(b64)
print(result)
"
```

Expected: a `ClassificationResult` with a non-empty `description` and `confidence > 0`.

---

## What Phase 2 Does NOT Include

- No FastAPI endpoint yet — that is Phase 6
- No deduplication — that is Phase 4
- No street audit frame analysis — that builds on this in Phase 3 and 6
- No tests — those are Phase 7 (but the verification step above confirms live behavior)

---

## Files Changed Summary

| File | Action |
|---|---|
| `inference/__init__.py` | Create (empty) |
| `inference/client.py` | Create |
| `inference/classifier.py` | Create |

No existing files are modified.

---

## Gate to Pass Before Phase 3

Running the verification command above must produce a valid `ClassificationResult`
with `category` matching what is visually in the test image, `confidence > 0.3`,
and no exceptions raised.
