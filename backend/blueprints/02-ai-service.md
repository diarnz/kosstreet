# Phase 2 — AI Service

> **Files to create:**
> - `app/services/ai_service.py` — new file

> **Depends on:** Phase 1 (`OpenRouterClient`), Phase 0 (`Settings`, `ImageAnalysisResult` schema)

---

## What this phase does

Builds the single class that bridges the backend to the Gemma vision model on OpenRouter.

It has two jobs:
1. Resize and encode an image to what the model expects
2. Send it to OpenRouter with a structured prompt and parse the response back into a typed `ImageAnalysisResult`

This service has **no database access**. It is used by both the report service (citizen photo analysis) and the audit service (Street View frame analysis).

---

## File: `app/services/ai_service.py`

### The prompt

```
CIVIC_ISSUE_PROMPT = """
You are analyzing a street-level image for a municipal issue detection system
in Prishtina, Kosovo.

Identify whether the image contains a civic street issue that needs municipal attention.
Respond ONLY with a single valid JSON object — no explanation, no markdown:

{
  "is_civic_issue": true or false,
  "category": one of "pothole" | "garbage" | "broken_streetlight" | "blocked_sidewalk" | "damaged_sign" | "other" | null,
  "confidence": a float between 0.0 and 1.0,
  "severity": one of "low" | "medium" | "high" | "critical" | null,
  "description": a single sentence describing exactly what you see | null
}

Rules:
- Set is_civic_issue to false for clean streets, normal traffic, buildings, or people with no issue.
- confidence reflects how certain you are that the detected issue is genuinely present.
- severity reflects urgency and impact on citizens using the street.
- description must be specific: name what you see, not just the category label.
- If category is null, set is_civic_issue to false.
"""
```

### Class: `AIService`

```
AIService(settings: Settings)
    → creates OpenRouterClient(api_key=settings.ai_openrouter_api_key)
    → stores settings.ai_model_name, settings.ai_max_image_size_px, settings.ai_confidence_threshold

async def analyze_image_bytes(image_bytes: bytes) -> ImageAnalysisResult
    Steps:
    1. base64-encode image_bytes → b64_string
    2. build message:
       {"role": "user", "content": [
           {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,{b64_string}"}},
           {"type": "text",      "text": CIVIC_ISSUE_PROMPT}
       ]}
    3. call openrouter_client.chat_completion(model, [message])
    4. parse the returned string as JSON
    5. if JSON parse fails or required keys missing → return ImageAnalysisResult(is_civic_issue=False)
    6. return ImageAnalysisResult(**parsed_json)  (validated by Pydantic)

async def analyze_upload(file: UploadFile) -> ImageAnalysisResult
    Steps:
    1. content = await file.read()
    2. open with Pillow: Image.open(BytesIO(content))
    3. apply EXIF orientation: ImageOps.exif_transpose(img)
    4. convert to RGB
    5. resize: thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)  ← keeps aspect ratio, never upscales
    6. re-encode to JPEG bytes in a BytesIO buffer (quality=85)
    7. call analyze_image_bytes(buffer.getvalue())
    8. return result
```

### Error handling table

| Situation | What happens |
|---|---|
| OpenRouter returns non-JSON text | Return `ImageAnalysisResult(is_civic_issue=False)` |
| OpenRouter HTTP 429 / 503 | `OpenRouterClient` retries once, then raises — caller logs and moves on |
| Image cannot be opened by Pillow | Raise `ValueError("Unsupported image format")` — route returns 422 |
| Model returns `is_civic_issue=false` | Return as-is — caller decides whether to use it |

### `ImageAnalysisResult` shape (defined in Phase 0 schemas)

```python
class ImageAnalysisResult(BaseModel):
    category:       IssueCategory | None = None
    confidence:     float | None = None
    description:    str | None = None
    is_civic_issue: bool = False
```

---

## What is NOT in this phase
- No database access
- No route definitions
- The route that exposes `analyze-image` to the frontend is in Phase 5
