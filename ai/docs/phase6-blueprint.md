# Phase 6 Blueprint: FastAPI AI Microservice Endpoints

## Goal

Expose everything built in Phases 1–4 over HTTP so the backend team can call the
AI layer. This is when the AI layer becomes a real deployable service.

After this phase:
- `POST /api/v1/classify` accepts a base64 JSON body and returns a classification
- `POST /api/v1/classify/upload` accepts a multipart file upload (what the frontend calls)
- `POST /api/v1/audit/plan` accepts a route and returns all scan frames
- `POST /api/v1/audit/analyze-frame` accepts one frame image and returns detections
- All endpoints are documented at `http://localhost:8001/docs`
- The backend team can wire up to this service immediately

---

## Current Project State

What already exists after Phases 0–5:

```
ai/src/kostreet_ai/
├── config.py              ← settings singleton, port 8001
├── main.py                ← FastAPI app, /health works, api_router mounted but empty
├── schemas.py             ← all request/response models ready
├── preprocessing/image.py ← validate, encode, decode all ready
├── inference/
│   ├── client.py          ← OpenRouter HTTP client
│   └── classifier.py      ← get_classifier(), classify() ready
├── street_audit/
│   └── planner.py         ← build_audit_scan_plan(), build_heading_plan() ready
├── geospatial/
│   └── deduplication.py   ← deduplicate_and_filter() ready
└── api/
    ├── __init__.py
    └── v1/
        ├── __init__.py
        └── router.py      ← empty router, sub-routers commented out
```

What Phase 6 adds:

```
ai/src/kostreet_ai/
└── api/v1/
    ├── router.py      ← MODIFY: uncomment and wire in sub-routers
    ├── classify.py    ← CREATE: POST /classify, POST /classify/upload
    └── audit.py       ← CREATE: POST /audit/plan, POST /audit/analyze-frame
```

---

## File 1: `api/v1/classify.py`

### Endpoint A: `POST /classify`

**Request:** JSON body matching `ClassificationRequest`
```json
{
  "image_base64": "<base64 string, with or without data URI prefix>",
  "latitude": 42.6629,
  "longitude": 21.1655
}
```

**Steps:**
1. Decode base64 to bytes using `decode_base64_to_bytes(request.image_base64)`
2. Validate with `validate_image(raw_bytes)` → raise `HTTP 422` with message
   `"Invalid or unreadable image."` if False
3. Re-encode with `encode_image_to_base64(raw_bytes, settings.max_image_size_px)`
   — this resizes and normalises to clean JPEG base64
4. Call `get_classifier().classify(b64)`
5. Return `ClassificationResponse`:
   ```json
   {
     "category": "pothole",
     "confidence": 0.91,
     "severity": "medium",
     "description": "...",
     "is_civic_issue": true,
     "model": "google/gemma-4-26b-a4b-it"
   }
   ```

**Response model:** `ClassificationResponse`

---

### Endpoint B: `POST /classify/upload`

**Request:** `multipart/form-data` with field `image` (file upload)

This is the endpoint the **frontend calls** when a citizen submits a photo.
The backend also calls this when forwarding a citizen upload to the AI layer.

**Steps:**
1. Read bytes from `UploadFile`: `image_bytes = await file.read()`
2. Check `len(image_bytes) > 0` → raise `HTTP 422` `"Empty file."` if zero
3. Validate with `validate_image(image_bytes)` → raise `HTTP 422` if invalid
4. Encode with `encode_image_to_base64(image_bytes, settings.max_image_size_px)`
5. Call `get_classifier().classify(b64)`
6. Return `ClassificationResponse` (same shape as above)

**Query parameters (optional):**
- `latitude: float | None = None`
- `longitude: float | None = None`

Both are accepted but not used in classification logic — they are passed through
in the response context only. The backend stores them.

---

## File 2: `api/v1/audit.py`

### Endpoint C: `POST /audit/plan`

**Request:** JSON body matching `AuditPlanRequest`
```json
{
  "waypoints": [
    {"lat": 42.6596, "lng": 21.1545},
    {"lat": 42.6617, "lng": 21.1578},
    {"lat": 42.6640, "lng": 21.1611}
  ],
  "step_meters": 30.0,
  "headings": [0, 60, 120, 180, 240, 300],
  "pitches": [-10, 0]
}
```

**Steps:**
1. Convert `request.waypoints` to `list[tuple[float, float]]`:
   `[(w.lat, w.lng) for w in request.waypoints]`
2. Call `build_audit_scan_plan(waypoints, step_meters, headings, pitches)`
3. Return `AuditPlanResponse`:
   ```json
   {
     "scan_points": [
       {"latitude": 42.6596, "longitude": 21.1545, "heading": 0, "pitch": -10},
       ...
     ],
     "total_frames": 288
   }
   ```

**Note:** This endpoint is fast — pure math, no model calls. Response is immediate.

---

### Endpoint D: `POST /audit/analyze-frame`

**Request:** JSON body matching `FrameAnalysisRequest`
```json
{
  "image_base64": "<base64>",
  "latitude": 42.6629,
  "longitude": 21.1655,
  "heading": 60,
  "pitch": -10
}
```

**Steps:**
1. Decode and validate image (same as classify endpoint)
2. Encode to clean base64 (resize applied)
3. Call `get_classifier().classify(b64)`
4. Check `result.is_civic_issue` AND `result.confidence >= settings.confidence_threshold`
   - If **both true**: wrap into `DetectionWithLocation`:
     ```python
     DetectionWithLocation(
         category=result.category,
         confidence=result.confidence,
         severity=result.severity,
         description=result.description,
         is_civic_issue=True,
         latitude=request.latitude,
         longitude=request.longitude,
         heading=request.heading,
         pitch=request.pitch,
     )
     ```
   - If **either false**: detections list is empty
5. Return `FrameAnalysisResponse`:
   ```json
   {
     "detections": [ ... ],
     "frame_latitude": 42.6629,
     "frame_longitude": 21.1655,
     "heading": 60,
     "pitch": -10
   }
   ```

**Why deduplication is not called here:**
Each `analyze-frame` call is for one frame. The backend collects many frame
responses and then calls deduplication when it wants a cleaned list. The
deduplication logic is available but is the backend's orchestration responsibility.

---

## File 3: `api/v1/router.py` (modify existing)

Uncomment and wire in both sub-routers:

```python
from fastapi import APIRouter
from kostreet_ai.api.v1.classify import router as classify_router
from kostreet_ai.api.v1.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(classify_router, tags=["classify"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
```

---

## Complete API Surface After Phase 6

| Method | Path | Input | Speed | Description |
|---|---|---|---|---|
| GET | `/health` | — | instant | Service health |
| POST | `/api/v1/classify` | JSON `{image_base64, lat?, lng?}` | ~4s | Classify citizen photo |
| POST | `/api/v1/classify/upload` | multipart `image` file | ~4s | Classify file upload |
| POST | `/api/v1/audit/plan` | JSON waypoints | instant | Generate scan frame list |
| POST | `/api/v1/audit/analyze-frame` | JSON `{image_base64, lat, lng, heading, pitch}` | ~4s | Analyze one audit frame |

OpenAPI docs: `http://localhost:8001/docs`

---

## Error Handling Contract

Every endpoint must return consistent errors the backend can rely on:

| Situation | HTTP code | Detail message |
|---|---|---|
| Image is empty | 422 | `"Empty file."` |
| Image cannot be parsed by Pillow | 422 | `"Invalid or unreadable image."` |
| Classifier returns fallback (model error) | 200 | Normal response with `confidence: 0.0, is_civic_issue: false` |
| OpenRouter is down | 200 | Same fallback — never 500 to backend |
| waypoints list has < 2 points | 422 | Pydantic validation on `AuditPlanRequest` |

**The AI service never returns 500 to the backend.** All model failures are caught
and returned as safe fallback `ClassificationResponse` objects. The backend decides
what to do with low-confidence results.

---

## Verification Plan

After implementation, test each endpoint with curl. Run these from any terminal
(not inside the venv — just any terminal with curl available):

### Step 1 — Health check (already works)
```powershell
Invoke-RestMethod http://localhost:8001/health
```

### Step 2 — Classify with base64 JSON
```powershell
# From ai/ directory
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("data\demo\pothole_01.jpg"))
$body = "{`"image_base64`": `"$b64`", `"latitude`": 42.6629, `"longitude`": 21.1655}"
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/classify -Body $body -ContentType "application/json"
```
Expected: `category=pothole, confidence>=0.8, is_civic_issue=true`

### Step 3 — Classify with file upload
```powershell
# PowerShell multipart upload
$form = @{ image = Get-Item "data\demo\garbage_01.jpg" }
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/classify/upload -Form $form
```
Expected: `category=garbage, confidence>=0.8, is_civic_issue=true`

### Step 4 — Audit plan
```powershell
$body = '{"waypoints":[{"lat":42.6596,"lng":21.1545},{"lat":42.6640,"lng":21.1611}],"step_meters":30}'
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/audit/plan -Body $body -ContentType "application/json"
```
Expected: `total_frames` between 100 and 300, `scan_points` is a non-empty list

### Step 5 — Analyze frame
```powershell
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("data\demo\pothole_01.jpg"))
$body = "{`"image_base64`": `"$b64`", `"latitude`": 42.6629, `"longitude`": 21.1655, `"heading`": 60, `"pitch`": -10}"
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/audit/analyze-frame -Body $body -ContentType "application/json"
```
Expected: `detections` list has 1 entry with `category=pothole`

### Step 6 — OpenAPI docs
Open `http://localhost:8001/docs` in browser.
All 5 endpoints must appear with correct request/response schemas.

---

## Files Changed Summary

| File | Action |
|---|---|
| `api/v1/classify.py` | Create |
| `api/v1/audit.py` | Create |
| `api/v1/router.py` | Modify (uncomment sub-router imports) |

No other files are modified.

---

## Gate to Pass Before Phase 7

All 5 curl verification steps above must return correct JSON.
`http://localhost:8001/docs` must show all 5 endpoints.
