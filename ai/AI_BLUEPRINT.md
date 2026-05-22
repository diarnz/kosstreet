# KoStreet AI Layer Blueprint

## Purpose

This document is the authoritative implementation guide for the `ai/` layer of KoStreet.
It mirrors the structure of the root `README.md` but goes deep on every AI engineering
decision, file, prompt, data contract, and verification step.

The goal of this layer is to power two things:

1. **Citizen photo classification** — a citizen uploads a photo and the AI identifies the
   civic issue type, confidence, severity, and a plain-language description.

2. **Street Audit Agent** — an automated pipeline that takes a street route, generates
   scan frames, fetches imagery (via Google Street View or demo images), runs the AI on
   every frame, deduplicates detections, and produces a ranked list of AI-suggested
   municipal tickets.

The AI layer runs as a standalone **FastAPI microservice on port 8001**. The backend
calls it over HTTP. It has no direct database access and no frontend dependency.

---

## Stack

| Concern | Choice | Reason |
|---|---|---|
| Vision model | `google/gemma-4-26b-a4b-it` via OpenRouter | Latest Gemma, multimodal, native JSON output, vision + text |
| Fallback model | `google/gemma-3-4b-it` via OpenRouter | Cheaper, faster, still vision-capable |
| HTTP client | `httpx` | Async-ready, modern, already in ecosystem |
| Image handling | `Pillow` | Already a declared dependency |
| Service framework | `FastAPI` | Matches backend, OpenAPI docs free |
| Config | `pydantic-settings` | Reads `.env`, type-safe |
| Testing | `pytest` | Already declared |

OpenRouter API endpoint: `https://openrouter.ai/api/v1/chat/completions`
Required headers: `Authorization: Bearer <key>`, `HTTP-Referer: https://kostreet.prizren.io`, `X-Title: KoStreet`

---

## Environment Variables

Add these to the root `.env` file (already gitignored):

```
# AI Service
KOSTREET_AI_OPENROUTER_API_KEY=sk-or-v1-your-key-here
KOSTREET_AI_MODEL_NAME=google/gemma-4-26b-a4b-it
KOSTREET_AI_CONFIDENCE_THRESHOLD=0.55
KOSTREET_AI_DUPLICATE_RADIUS_METERS=20.0
KOSTREET_AI_MAX_IMAGE_SIZE_PX=1024
KOSTREET_AI_SERVICE_PORT=8001
```

---

## Final File Tree (target state after all phases)

```
ai/
├── AI_BLUEPRINT.md                         ← this file
├── pyproject.toml                          ← Phase 0: updated deps
├── src/
│   └── kostreet_ai/
│       ├── __init__.py
│       ├── config.py                       ← Phase 0: rewritten with pydantic-settings
│       ├── main.py                         ← Phase 6: FastAPI app factory
│       ├── schemas.py                      ← Phase 1: all Pydantic models
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py               ← Phase 6: mounts sub-routers
│       │       ├── classify.py             ← Phase 6: POST /classify
│       │       └── audit.py                ← Phase 6: POST /audit/plan + /audit/analyze-frame
│       ├── inference/
│       │   ├── __init__.py
│       │   ├── client.py                   ← Phase 2: OpenRouter HTTP client
│       │   └── classifier.py              ← Phase 2: prompt engineering + JSON parse
│       ├── preprocessing/
│       │   ├── __init__.py
│       │   └── image.py                    ← Phase 1: resize, encode, validate
│       ├── street_audit/
│       │   ├── __init__.py
│       │   └── planner.py                  ← Phase 3: build_heading_plan, interpolate_route
│       └── geospatial/
│           ├── __init__.py
│           └── deduplication.py            ← Phase 4: haversine, deduplicate
├── data/
│   ├── demo/                               ← Phase 5: seeded demo images
│   ├── raw/
│   └── processed/
└── tests/
    ├── test_street_audit_planner.py        ← existing, passes after Phase 3
    ├── test_classifier.py                  ← Phase 7
    └── test_deduplication.py               ← Phase 7
```

---

## Issue Taxonomy

All classification results must map to exactly one of these categories.
The AI is instructed to use these exact string values.

| Category key | Human label | Routing target |
|---|---|---|
| `pothole` | Pothole / road damage | Roads / Public Works |
| `garbage` | Garbage / illegal dumping | Sanitation |
| `broken_streetlight` | Broken streetlight | Electrical / Infrastructure |
| `blocked_sidewalk` | Blocked or damaged sidewalk | Urban Maintenance |
| `damaged_sign` | Damaged sign or infrastructure | Public Works |
| `other` | Other / unrecognized | General queue |

Severity levels: `low`, `medium`, `high`

Confidence range: `0.0` to `1.0` (float)

---

## Data Flow

```
Citizen photo (bytes)
        │
        ▼
preprocessing/image.py
  resize → max 1024px
  encode → JPEG base64
        │
        ▼
inference/classifier.py
  build system prompt
  build user message with image
  call OpenRouter /chat/completions
  parse JSON response
        │
        ▼
schemas.ClassificationResult
  category, confidence, severity,
  description, is_civic_issue
        │
        ▼
api/v1/classify.py
  return ClassificationResponse to backend
```

```
Route waypoints
        │
        ▼
street_audit/planner.py
  interpolate scan points every N meters
  generate (lat, lng, heading, pitch) frames
        │
        ▼
Backend fetches Street View image per frame
  passes image_base64 + location back to AI
        │
        ▼
api/v1/audit.py → inference/classifier.py
  same inference pipeline as citizen classify
        │
        ▼
geospatial/deduplication.py
  group by category
  merge detections within radius_meters
  keep highest confidence per cluster
        │
        ▼
Ranked list of DetectionWithLocation
  → AI-suggested municipal tickets
```

---

## Phase 0: Foundation Setup

**Goal:** The AI package installs cleanly, the service starts, and `/health` responds.
Nothing functional yet — just the skeleton that all later phases depend on.

### Files to create or modify

#### `pyproject.toml` — add to `[project] dependencies`

```toml
"fastapi>=0.115.6",
"uvicorn[standard]>=0.34.0",
"pydantic-settings>=2.7.1",
"httpx>=0.28.1",
"python-multipart>=0.0.20",
```

The existing `models` optional group (torch, transformers, ultralytics) stays as-is.
We are not using it in this pipeline — OpenRouter handles model inference remotely.

#### `config.py` — full rewrite

Replace the current dataclass with a `pydantic-settings` `BaseSettings` class.

Fields:
- `openrouter_api_key: str = ""`
- `openrouter_base_url: str = "https://openrouter.ai/api/v1"`
- `model_name: str = "google/gemma-4-26b-a4b-it"`
- `confidence_threshold: float = 0.55`
- `duplicate_radius_meters: float = 20.0`
- `max_image_size_px: int = 1024`
- `service_port: int = 8001`

Env prefix: `KOSTREET_AI_`
Env file: `../.env` (points to root `.env`)

#### `main.py` — new file

FastAPI app factory. Mounts `api_router` at `/api/v1`. Adds CORS middleware
allowing all origins (the backend on port 8000 will call this). Defines `GET /health`.

#### `api/__init__.py`, `api/v1/__init__.py` — empty files

#### `api/v1/router.py` — new file

Imports and includes the `classify_router` and `audit_router`. No logic here.

### Verification gate

```bash
cd ai
pip install -e .
uvicorn kostreet_ai.main:app --port 8001
# curl http://localhost:8001/health
# → {"status": "ok", "service": "kostreet-ai", "model": "google/gemma-4-26b-a4b-it"}
```

The service must start with zero import errors before Phase 1 begins.

---

## Phase 1: Schemas and Image Preprocessing

**Goal:** Define every data shape used across the entire AI layer. Build the image
utility that all inference phases will call. No model calls yet.

### `schemas.py`

All Pydantic models live here. No logic — only shapes.

```
IssueCategory(StrEnum)
  pothole | garbage | broken_streetlight | blocked_sidewalk | damaged_sign | other

IssueSeverity(StrEnum)
  low | medium | high

ClassificationResult(BaseModel)
  category: IssueCategory
  confidence: float  (ge=0, le=1)
  severity: IssueSeverity
  description: str
  is_civic_issue: bool

ClassificationRequest(BaseModel)
  image_base64: str
  latitude: float | None
  longitude: float | None

ClassificationResponse(BaseModel)
  category: IssueCategory
  confidence: float
  severity: IssueSeverity
  description: str
  is_civic_issue: bool
  model: str

FramePlan(BaseModel, frozen=True)
  latitude: float
  longitude: float
  heading: int
  pitch: int

Waypoint(BaseModel)
  lat: float
  lng: float

AuditPlanRequest(BaseModel)
  waypoints: list[Waypoint]  (min_length=2)
  step_meters: float = 30.0
  headings: list[int] = [0, 60, 120, 180, 240, 300]
  pitches: list[int] = [-10, 0]

AuditPlanResponse(BaseModel)
  scan_points: list[FramePlan]
  total_frames: int

FrameAnalysisRequest(BaseModel)
  image_base64: str
  latitude: float
  longitude: float
  heading: int
  pitch: int

DetectionWithLocation(BaseModel)
  category: IssueCategory
  confidence: float
  severity: IssueSeverity
  description: str
  is_civic_issue: bool
  latitude: float
  longitude: float
  heading: int
  pitch: int

FrameAnalysisResponse(BaseModel)
  detections: list[DetectionWithLocation]
  frame_latitude: float
  frame_longitude: float
  heading: int
  pitch: int
```

### `preprocessing/image.py`

Two pure functions. No side effects.

**`encode_image_to_base64(image_bytes: bytes, max_size_px: int = 1024) -> str`**

1. Open with `Image.open(io.BytesIO(image_bytes))`
2. Convert to RGB (handles RGBA, palette modes, etc.)
3. Call `img.thumbnail((max_size_px, max_size_px), Image.LANCZOS)` — preserves aspect ratio
4. Save to new `io.BytesIO` buffer as JPEG, quality=85
5. Return `base64.b64encode(buffer.getvalue()).decode("utf-8")`

**`validate_image(image_bytes: bytes) -> bool`**

1. Try `Image.open(io.BytesIO(image_bytes)).verify()`
2. Return `True` on success, `False` on any exception
3. Must also check `len(image_bytes) > 0`

**`decode_base64_to_bytes(b64: str) -> bytes`**

Convenience inverse. Strips data URI prefix if present (`data:image/...;base64,`).

### Verification gate

```python
from kostreet_ai.preprocessing.image import encode_image_to_base64, validate_image
# open any .jpg from data/demo/ and encode it
# assert len(result) > 0
# assert validate_image(open(..., 'rb').read()) is True
```

---

## Phase 2: OpenRouter Client and Image Classifier

**Goal:** The core AI inference path. Given a base64 image, call Gemma 4 on OpenRouter,
parse the structured JSON response, and return a typed `ClassificationResult`.

### `inference/client.py`

**`OpenRouterClient` class**

Constructor: `__init__(self, api_key: str, base_url: str, model: str)`

One public method:

**`chat(self, messages: list[dict], response_format: dict | None = None) -> str`**

Builds the request:
```python
{
  "model": self.model,
  "response_format": response_format or {"type": "json_object"},
  "messages": messages,
}
```

Headers:
```python
{
  "Authorization": f"Bearer {self.api_key}",
  "Content-Type": "application/json",
  "HTTP-Referer": "https://kostreet.prizren.io",
  "X-Title": "KoStreet",
}
```

Uses `httpx.Client(timeout=30.0)`. Posts to `{base_url}/chat/completions`.
Calls `response.raise_for_status()`.
Returns `response.json()["choices"][0]["message"]["content"]`.

### `inference/classifier.py`

**System prompt (exact text — do not paraphrase)**

```
You are a civic infrastructure quality inspector working for Kosovo municipalities.
Your job is to analyze street-level photographs and identify visible civic issues
that require municipal attention.

You must respond with ONLY a valid JSON object. No explanation, no markdown, no
extra text. The JSON must follow this exact structure:

{
  "category": "<one of: pothole, garbage, broken_streetlight, blocked_sidewalk, damaged_sign, other>",
  "confidence": <float between 0.0 and 1.0>,
  "severity": "<one of: low, medium, high>",
  "description": "<one concise sentence describing the visible issue and its location in the image>",
  "is_civic_issue": <true or false>
}

Category definitions:
- pothole: any road surface crack, depression, hole, or damage to asphalt
- garbage: bags, litter, scattered waste, illegal dumping, overflowing bins
- broken_streetlight: damaged light pole, missing fixture, visibly dark lamp
- blocked_sidewalk: cracked pavement, obstacles, obstructions on walking paths
- damaged_sign: bent, missing, graffitied, or fallen road or street signs
- other: any civic issue not matching the above categories

Severity guide:
- high: immediate safety risk, large damage, major obstruction
- medium: noticeable issue that needs attention within days
- low: minor cosmetic issue, early-stage problem

If you do not see any civic issue in the image, set is_civic_issue to false,
category to "other", confidence to 0.0, severity to "low", and description to
"No civic issue detected in this image."
```

**`ImageClassifier` class**

Constructor: `__init__(self, client: OpenRouterClient, model_name: str, confidence_threshold: float)`

**`classify(self, image_base64: str) -> ClassificationResult`**

1. Build messages:
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
2. Call `self.client.chat(messages, response_format={"type": "json_object"})`
3. Parse JSON with `json.loads(raw_response)`
4. Validate and coerce into `ClassificationResult`
5. **On any exception** (JSON parse error, key error, network error): return safe fallback
   `ClassificationResult(category="other", confidence=0.0, severity="low", description="Classification failed. Please review manually.", is_civic_issue=False)`

**Module-level singleton factory**

```python
def get_classifier() -> ImageClassifier:
    client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.model_name,
    )
    return ImageClassifier(client, settings.model_name, settings.confidence_threshold)
```

### Verification gate

With a real OpenRouter key in `.env`, run manually:
```python
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import encode_image_to_base64

# use any pothole photo
with open("data/demo/pothole_test.jpg", "rb") as f:
    b64 = encode_image_to_base64(f.read())

result = get_classifier().classify(b64)
print(result)
# → ClassificationResult(category=<IssueCategory.pothole: 'pothole'>, confidence=0.84, ...)
```

The model must return a valid parsed result without raising. Confidence must be > 0
for a photo that clearly shows a civic issue.

---

## Phase 3: Street Audit Planner

**Goal:** Implement the spatial logic that converts a street route into a full set of
scan frames. This phase also fixes the one existing test that is currently failing.

### `street_audit/planner.py`

**`FramePlan` dataclass** (use the one from `schemas.py` — do not redeclare)

Import from schemas and re-export for backwards compatibility.

**`build_heading_plan`**

```python
def build_heading_plan(
    latitude: float,
    longitude: float,
    headings: tuple[int, ...] = (0, 60, 120, 180, 240, 300),
    pitches: tuple[int, ...] = (-10, 0),
) -> list[FramePlan]:
```

Returns the **cartesian product** of headings × pitches as a flat list of `FramePlan`.
Outer loop is headings, inner loop is pitches.

For `headings=(0, 90), pitches=(-10, 0)` the result is:
```
FramePlan(lat, lng, heading=0,  pitch=-10)
FramePlan(lat, lng, heading=0,  pitch=0)
FramePlan(lat, lng, heading=90, pitch=-10)
FramePlan(lat, lng, heading=90, pitch=0)
```
→ `len == 4`, `frames[0].heading == 0`, `frames[-1].pitch == 0` ✓ (existing test passes)

**`interpolate_route_points`**

```python
def interpolate_route_points(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
) -> list[tuple[float, float]]:
```

Walks the polyline defined by `waypoints` (list of `(lat, lng)` tuples).
Places a new point every `step_meters` along each segment using linear interpolation
in geographic coordinates (accurate enough for city-scale distances under 1 km).

Algorithm:
1. Always include the first waypoint.
2. For each segment (A → B): compute segment length in meters using haversine.
3. Walk along the segment placing points every `step_meters`.
4. Use linear interpolation: `lat = lat_A + t * (lat_B - lat_A)`, same for lng.
5. Include the last waypoint.
6. Return the deduplicated list of points.

**`build_audit_scan_plan`**

```python
def build_audit_scan_plan(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
    headings: list[int] = (0, 60, 120, 180, 240, 300),
    pitches: list[int] = (-10, 0),
) -> list[FramePlan]:
```

Combines `interpolate_route_points` and `build_heading_plan`.
Returns the complete list of all frames for the entire route.

### Verification gate

```bash
cd ai
pytest tests/test_street_audit_planner.py -v
# → PASSED test_build_heading_plan_combines_headings_and_pitches
```

---

## Phase 4: Geospatial Deduplication

**Goal:** When the Street Audit Agent scans a segment from multiple headings and
neighboring points, the same pothole will be detected 3–6 times. This phase
collapses those duplicates into one high-confidence detection.

### `geospatial/deduplication.py`

**`haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float`**

Standard haversine formula. Earth radius = 6,371,000 meters. Returns distance in meters.

```
R = 6_371_000
φ1, φ2 = radians(lat1), radians(lat2)
Δφ = radians(lat2 - lat1)
Δλ = radians(lon2 - lon1)
a = sin(Δφ/2)² + cos(φ1)·cos(φ2)·sin(Δλ/2)²
c = 2·atan2(√a, √(1−a))
return R · c
```

**`deduplicate_detections`**

```python
def deduplicate_detections(
    detections: list[DetectionWithLocation],
    radius_meters: float = 20.0,
) -> list[DetectionWithLocation]:
```

Algorithm — greedy spatial merge:
1. Sort all detections by `confidence` descending.
2. Initialize empty list `kept = []`.
3. For each detection `d`:
   - Check if any detection already in `kept` has the **same `category`** AND
     is within `radius_meters` of `d`.
   - If yes: skip `d` (it is a duplicate of a higher-confidence detection).
   - If no: add `d` to `kept`.
4. Return `kept`.

This ensures that for each spatial cluster of same-category detections, only the
highest-confidence one survives.

**`compute_centroid`**

```python
def compute_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
```

Arithmetic mean of lat and lng. Used optionally to place the merged detection at the
center of its cluster.

### Verification gate

Manual test:
```python
from kostreet_ai.geospatial.deduplication import deduplicate_detections, haversine_meters

# two potholes 10m apart, one pothole 50m away
assert haversine_meters(42.66, 21.16, 42.66009, 21.16) < 20
# after dedup: should return 2 (the cluster of 2 → 1 best, plus the far one)
```

---

## Phase 5: Demo Data Setup

**Goal:** Populate `ai/data/demo/` with test images that prove the pipeline works
during the live demo. These images must be legally usable (citizen-uploaded, team-captured,
or open-licensed — not raw Google Street View imagery).

### What to collect

Collect at least **2 clear images per issue category** = 12 images minimum:

| Filename pattern | Category |
|---|---|
| `pothole_01.jpg`, `pothole_02.jpg` | pothole |
| `garbage_01.jpg`, `garbage_02.jpg` | garbage |
| `streetlight_01.jpg`, `streetlight_02.jpg` | broken_streetlight |
| `sidewalk_01.jpg`, `sidewalk_02.jpg` | blocked_sidewalk |
| `sign_01.jpg`, `sign_02.jpg` | damaged_sign |
| `clean_street_01.jpg` | negative sample (no issue) |

### Demo fixture file: `data/demo/fixtures.json`

```json
[
  {
    "filename": "pothole_01.jpg",
    "expected_category": "pothole",
    "latitude": 42.6629,
    "longitude": 21.1655,
    "label": "Pothole on Bill Clinton Blvd"
  }
]
```

This file is used by the seed script and the demo runner. The backend team uses it to
populate the demo database. The AI team uses it to validate classification accuracy.

### Verification gate

```bash
# run classifier against all demo images
python -c "
import json, pathlib
from kostreet_ai.preprocessing.image import encode_image_to_base64
from kostreet_ai.inference.classifier import get_classifier

clf = get_classifier()
fixtures = json.loads(pathlib.Path('data/demo/fixtures.json').read_text())
for f in fixtures:
    b = pathlib.Path(f'data/demo/{f[\"filename\"]}').read_bytes()
    result = clf.classify(encode_image_to_base64(b))
    match = result.category.value == f['expected_category']
    print(f'{f[\"filename\"]}: {result.category.value} ({result.confidence:.2f}) [{\"OK\" if match else \"MISS\"}]')
"
```

Target: at least 8 out of 12 correct classifications. Document any misses and adjust
the system prompt if needed before Phase 6.

---

## Phase 6: FastAPI AI Microservice

**Goal:** Expose everything built in Phases 1–4 over HTTP. The backend team can now
call this service. This is when the AI layer becomes a real deployable unit.

### `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kostreet_ai.api.v1.router import api_router
from kostreet_ai.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="KoStreet AI Service",
        version="0.1.0",
        description="Vision classification and street audit pipeline for KoStreet.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {
            "status": "ok",
            "service": "kostreet-ai",
            "model": settings.model_name,
        }

    return app

app = create_app()
```

### `api/v1/router.py`

```python
from fastapi import APIRouter
from kostreet_ai.api.v1.classify import router as classify_router
from kostreet_ai.api.v1.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(classify_router, tags=["classify"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
```

### `api/v1/classify.py`

Endpoint: `POST /api/v1/classify`

Request body: `ClassificationRequest` (JSON with `image_base64`, optional `latitude`, `longitude`)

Steps:
1. Decode base64 input using `decode_base64_to_bytes`
2. Validate image with `validate_image` — raise `HTTP 422` if invalid
3. Encode back to clean base64 (resize applied) with `encode_image_to_base64`
4. Call `get_classifier().classify(b64)`
5. Return `ClassificationResponse` including `model: settings.model_name`

Also expose `POST /api/v1/classify/upload` that accepts `multipart/form-data` with an
`image` file field. This is the endpoint the frontend actually calls when a citizen
uploads a photo. Internally it converts bytes to base64 and calls the same logic.

### `api/v1/audit.py`

**`POST /api/v1/audit/plan`**

Request body: `AuditPlanRequest`

Steps:
1. Convert `waypoints` list to `list[tuple[float, float]]`
2. Call `build_audit_scan_plan(waypoints, step_meters, headings, pitches)`
3. Return `AuditPlanResponse(scan_points=frames, total_frames=len(frames))`

**`POST /api/v1/audit/analyze-frame`**

Request body: `FrameAnalysisRequest`

Steps:
1. Validate and resize image
2. Call `get_classifier().classify(b64)`
3. If `result.is_civic_issue` and `result.confidence >= settings.confidence_threshold`:
   - Wrap into `DetectionWithLocation` including `latitude`, `longitude`, `heading`, `pitch`
   - Return `FrameAnalysisResponse(detections=[detection], ...)`
4. Else: return `FrameAnalysisResponse(detections=[], ...)`

### Run command

```bash
cd ai
uvicorn kostreet_ai.main:app --reload --port 8001
```

OpenAPI docs available at `http://localhost:8001/docs`

### Verification gate

```bash
# classify endpoint
curl -X POST http://localhost:8001/api/v1/classify \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$(base64 -w0 data/demo/pothole_01.jpg)\"}"

# audit plan endpoint
curl -X POST http://localhost:8001/api/v1/audit/plan \
  -H "Content-Type: application/json" \
  -d '{"waypoints":[{"lat":42.6629,"lng":21.1655},{"lat":42.6640,"lng":21.1670}],"step_meters":30}'
```

Both must return valid JSON matching the schemas before moving to Phase 7.

---

## Phase 7: Tests

**Goal:** Every core function has a test. Tests must pass with `pytest` from the `ai/`
directory without a live OpenRouter key (use mocks for the API client).

### `tests/test_street_audit_planner.py` (existing — must pass after Phase 3)

```python
def test_build_heading_plan_combines_headings_and_pitches() -> None:
    frames = build_heading_plan(42.6629, 21.1655, headings=(0, 90), pitches=(-10, 0))
    assert len(frames) == 4
    assert frames[0].heading == 0
    assert frames[-1].pitch == 0
```

### `tests/test_deduplication.py`

```python
def test_haversine_returns_meters():
    # Prishtina city center to a point ~100m north
    d = haversine_meters(42.6629, 21.1655, 42.6638, 21.1655)
    assert 95 < d < 105

def test_deduplication_merges_nearby_same_category():
    # Two potholes 10m apart → should collapse to 1
    ...

def test_deduplication_keeps_different_categories():
    # A pothole and garbage at same location → should keep both
    ...

def test_deduplication_keeps_far_same_category():
    # Two potholes 50m apart → should keep both
    ...
```

### `tests/test_classifier.py`

```python
def test_classifier_returns_fallback_on_bad_json(monkeypatch):
    # Mock client.chat() to return invalid JSON
    # Assert ClassificationResult has category="other", confidence=0.0

def test_classifier_parses_valid_response(monkeypatch):
    # Mock client.chat() to return well-formed JSON
    # Assert result.category == IssueCategory.pothole
    # Assert result.confidence == 0.87

def test_classifier_handles_unknown_category(monkeypatch):
    # Mock returns category="road_crack" (not in enum)
    # Assert fallback or "other" returned cleanly
```

### Run all tests

```bash
cd ai
pytest tests/ -v
# All tests must pass
```

---

## Phase 8: Integration and Demo Readiness

**Goal:** End-to-end pipeline works with real images and the live OpenRouter key.
The demo flow is rehearsed and all edge cases are handled.

### Integration checklist

- [ ] Backend can call `POST /api/v1/classify/upload` with a real photo
- [ ] Backend can call `POST /api/v1/audit/plan` and receive scan points
- [ ] Backend can call `POST /api/v1/audit/analyze-frame` per frame and get detections
- [ ] Deduplication reduces multi-frame detections correctly
- [ ] All 12 demo images classify correctly (or prompt adjustments are made)
- [ ] Response time per classification < 5 seconds on OpenRouter
- [ ] Service recovers from timeout without crashing (fallback result returned)
- [ ] `/health` endpoint responds instantly

### Prompt calibration

If demo image classification accuracy is below 75% in Phase 5, adjust the system
prompt before Phase 6. Specific adjustments:

- For potholes being misclassified as `other`: add "pavement crack or surface depression"
  to the pothole definition.
- For garbage misclassified as `blocked_sidewalk`: clarify the garbage definition with
  "any visible waste material on the ground, regardless of location".
- For low confidence on legitimate issues: add "When in doubt, lean toward detecting
  the issue rather than reporting none. Municipal workers will verify."

### Severity calibration table

Use this as a hard override if the model produces inconsistent severity for the demo:

| Category | Default severity | High override condition |
|---|---|---|
| pothole | medium | confidence > 0.85 |
| garbage | medium | confidence > 0.80 |
| broken_streetlight | high | always |
| blocked_sidewalk | medium | — |
| damaged_sign | medium | — |

Implement in `classifier.py` as a post-processing step after JSON parse.

### Street Audit demo route (Prishtina)

Suggested demo route for the pitch:

```json
{
  "route_name": "Bill Clinton Boulevard Audit",
  "waypoints": [
    {"lat": 42.6596, "lng": 21.1545},
    {"lat": 42.6617, "lng": 21.1578},
    {"lat": 42.6640, "lng": 21.1611}
  ],
  "step_meters": 30,
  "headings": [0, 60, 120, 180, 240, 300],
  "pitches": [-10, 0]
}
```

This generates approximately 12–15 scan points × 12 frame plans = ~144–180 frames.
For the live demo, use a reduced set (3–4 scan points × 6 headings × 1 pitch = ~18–24 frames)
to keep demo runtime under 30 seconds.

### Demo fallback plan

If OpenRouter is slow or unavailable during the live pitch:

1. Pre-run the street audit on the demo route and store results in `data/demo/audit_results.json`
2. The backend reads this file instead of calling the AI service live
3. The demo still shows correct map markers, detections, and ticket creation
4. Announce: "We are showing pre-computed results to respect demo time constraints"

---

## Key Risks and Mitigations

| Risk | Mitigation |
|---|---|
| OpenRouter rate limit during demo | Pre-compute and cache all demo results in Phase 8 |
| Gemma 4 returns non-JSON despite `json_object` mode | Fallback parser in `classifier.py`, never crash |
| Street View images unavailable or low quality | Use team-captured demo images from `data/demo/` |
| Low classification accuracy on Kosovo imagery | Prompt calibration in Phase 8, see table above |
| Slow response time (> 5s per image) | Switch to `google/gemma-3-4b-it` (faster, cheaper) |
| Duplicate detections flood the dashboard | Phase 4 deduplication must run before any results are sent |

---

## API Contract Summary (for backend team coordination)

| Method | Path | Input | Output |
|---|---|---|---|
| GET | `/health` | — | `{status, service, model}` |
| POST | `/api/v1/classify` | `{image_base64, latitude?, longitude?}` | `{category, confidence, severity, description, is_civic_issue, model}` |
| POST | `/api/v1/classify/upload` | multipart file `image` | same as above |
| POST | `/api/v1/audit/plan` | `{waypoints, step_meters, headings, pitches}` | `{scan_points: [{lat, lng, heading, pitch}], total_frames}` |
| POST | `/api/v1/audit/analyze-frame` | `{image_base64, latitude, longitude, heading, pitch}` | `{detections: [{category, confidence, severity, description, is_civic_issue, latitude, longitude, heading, pitch}], ...}` |

Service runs on: `http://localhost:8001`
Backend env var: `KOSTREET_AI_SERVICE_URL=http://localhost:8001`

---

## Phase Gate Summary

| Phase | Deliverable | Gate check |
|---|---|---|
| 0 | Package installs, service starts | `GET /health` → 200 |
| 1 | Schemas defined, image preprocessing works | Unit test encode/validate |
| 2 | OpenRouter client + classifier works | Manual classify of a demo image |
| 3 | Street audit planner works | Existing pytest test passes |
| 4 | Deduplication works | Manual test of nearby/far detections |
| 5 | Demo images collected, accuracy ≥ 75% | Demo fixture accuracy script |
| 6 | All endpoints live | `curl` all 5 endpoints, all return correct JSON |
| 7 | All tests pass | `pytest tests/ -v` → all green |
| 8 | Full demo flow rehearsed, fallback ready | End-to-end demo run under 3 minutes |
