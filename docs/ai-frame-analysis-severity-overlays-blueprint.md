# AI Frame Analysis Viewer with Severity Overlays Blueprint

## Goal

Let municipal reviewers **see the exact Street View frame the AI analyzed** and **understand where the model spotted issues**, with colored severity circles:

| Severity | Color |
|----------|-------|
| High (and critical) | Red |
| Medium | Yellow |
| Low | Green |

Today the product shows text metadata (category, severity, description) plus an interactive Google panorama. It does **not** show the analyzed JPEG or any visual indication of *where* on the image the AI found the problem.

**Status:** Phase 7 complete — legend, tooltips, accessibility, and tests shipped. Feature blueprint complete.

---

## Phase 1 — Locked Requirements (Approved)

These decisions were confirmed to unblock implementation. Defaults follow the recommendations in this blueprint unless noted.

| # | Decision | Approved choice | Rationale |
|---|----------|-----------------|-----------|
| 1 | Frame storage | **Option 2 — `audit_frames` table** | Reviewers can browse all analyzed frames (detected + clean), not only suggestions |
| 2 | Frame coverage | **All frames in a run** | Matches "see what the AI analyzed" goal (e.g. 64 frames on Bill Clinton Boulevard) |
| 3 | Circle accuracy | **Label overlays "AI-estimated location"** | Vision LLM coords are approximate; set reviewer expectations |
| 4 | Critical severity | **Dark red (`#b91c1c`) + radius 0.14** | Distinct from high; same red family, larger circle |
| 5 | Regions per frame | **One primary region initially** | Schema supports `regions[]` array; pipeline/UI start with one circle |
| 6 | Frame browser placement | **Audit run detail page first** | Main audit page stays focused; inline browser deferred unless needed |
| 7 | Existing runs | **Overlays for new runs only** | No backfill/re-analyze script in v1; old suggestions show frame without overlay |
| 8 | Region shape | **`DetectionRegion` circle** (`center_x`, `center_y`, `radius`, normalized 0–1) | Replaces unused `BoundingBox` shapes across stack |
| 9 | Image delivery | **Backend proxy endpoint** | Never expose Google API key in frontend URLs |
| 10 | Missing regions | **Show frame, no overlay, "Location not pinpointed" badge** | Missing coords must not fail the pipeline |

### Approved severity visual mapping

| Severity | Color | Circle radius (normalized) | UI label |
|----------|-------|------------------------------|----------|
| low | `#22c55e` (green) | 0.06 | Low |
| medium | `#eab308` (yellow) | 0.09 | Medium |
| high | `#ef4444` (red) | 0.12 | High |
| critical | `#b91c1c` (dark red) | 0.14 | Critical |

When the model returns a custom `radius` in `regions[]`, clamp to `[0.04, 0.18]`. If omitted, use the severity default above.

### Approved API surface (v1)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/audit-runs/{run_id}/frames` | List all frames for a run (summary) |
| `GET` | `/api/v1/audit-runs/{run_id}/frames/{frame_index}` | Single frame + full analysis |
| `GET` | `/api/v1/audit-suggestions/{suggestion_id}/frame-image` | Proxied static JPEG for a suggestion |
| `GET` | `/api/v1/audit-runs/{run_id}/frames/{frame_index}/image` | Proxied static JPEG for any frame |
| `GET` | `/api/v1/audit-suggestions/{suggestion_id}` | Include `detection_regions`, `frame_index` |

### Approved shared types

**Backend / frontend (`DetectionRegion`):**

```ts
interface DetectionRegion {
  center_x: number;  // 0–1
  center_y: number;  // 0–1
  radius: number;    // 0–1 relative to min(image width, height)
}
```

**Extended AI response (`ImageAnalysisResult`):**

```json
{
  "is_civic_issue": true,
  "category": "pothole",
  "confidence": 0.91,
  "severity": "high",
  "description": "...",
  "regions": [{ "center_x": 0.42, "center_y": 0.68, "radius": 0.12 }]
}
```

### Phase 1 completion checklist

- [x] Open decisions resolved
- [x] Frame storage model chosen (`audit_frames` + `detection_regions` on suggestions)
- [x] Severity color/radius mapping approved
- [x] API contract drafted for Phase 3
- [x] Shared `DetectionRegion` type defined
- [x] Phase 2 — AI prompt + schema (complete)
- [x] Phase 3 — Backend storage (complete)
- [x] Phase 4 — Frame viewer UI (complete)
- [x] Phase 5 — Run frame browser (complete)
- [x] Phase 6 — Demo seed update (complete)
- [x] Phase 7 — Polish (complete)

---

## Current State

### Pipeline

```
Audit run → waypoints × 4 headings → Google Static Street View (640×640)
         → OpenRouter vision model → persist AuditSuggestion if issue found
```

Key files:

- `backend/app/services/audit_service.py` — orchestrates the pipeline
- `backend/app/services/ai_service.py` — OpenRouter vision call + JSON parse
- `backend/app/integrations/street_imagery.py` — Google Static Street View fetch
- `backend/app/models/audit.py` — `AuditRun`, `AuditSuggestion` models
- `backend/app/schemas/audit.py` — API DTOs

### What the AI Returns Per Frame

From `backend/app/services/ai_service.py`, the model returns **one JSON object per frame**:

- `is_civic_issue`, `category`, `confidence`, `severity`, `description`
- **No pixel coordinates, bounding boxes, or center points**

Prompt schema today:

```json
{
  "is_civic_issue": true,
  "category": "pothole",
  "confidence": 0.91,
  "severity": "high",
  "description": "A large pothole is visible in the right lane."
}
```

### What Gets Stored

Each `AuditSuggestion` has geo + frame context:

- `latitude`, `longitude`, `heading`, `pitch`
- `image_url` (the exact static frame URL — stored but **not shown** in UI for API-key safety)
- `severity` as text: `low | medium | high | critical`
- **No** `bounding_box` or region column in the database (confirmed in Alembic `0001_initial.py`)

### What the UI Shows

| Location | Component | Behavior |
|----------|-----------|----------|
| Dashboard (`/`) | `StreetViewPanel` | Interactive panorama for selected citizen report |
| Audit suggestion detail (`/audit/suggestions/:id`) | `StreetViewPanel` (compact) | Panorama at suggestion lat/lng + heading/pitch |
| Audit list / run detail | `AuditSuggestionCard` | Text metadata only; link to detail page |

**Not shown:**

- The actual analyzed static image
- Any overlay or annotation on imagery
- Frame-by-frame progress during a run

### Parallel Schemas (Not Wired)

Three incompatible spatial shapes exist today:

| Location | Shape |
|----------|-------|
| Frontend `frontend/src/types/detection.ts` | `{ x, y, width, height }` — optional, never populated by backend |
| AI package `ai/src/kostreet_ai/detection/schemas.py` | `{ x_min, y_min, x_max, y_max }` normalized 0–1 — not used in live pipeline |
| Backend | No spatial fields |

Demo data in `ai/data/demo/audit_results.json` has 36 detections from 64 frames with **no bounding boxes**.

### Bottom Line

Today's Street View AI pipeline is **frame-level image classification**: each static JPEG is sent to a vision LLM, which returns category, confidence, severity, and description. Suggestions are geotagged to the **frame waypoint + camera orientation**, not to pixels on the image.

**Severity circles require new AI output, backend storage, a safe static-frame viewer, and overlay components — none of which exist yet.**

---

## Target UX

### 1. "What Is the AI Analyzing?" — Frame Evidence Viewer

A new **Analyzed Frame** panel that shows the **exact static JPEG** the model saw (not the live panorama), with metadata:

- Route / run name
- Frame index (e.g. "Frame 12 of 64")
- Heading, pitch, coordinates
- AI result: category, confidence, severity, description
- Timestamp / model name

**Where it lives:**

| Surface | Purpose |
|---------|---------|
| **Audit run detail** | Browse all frames in a run (detected + clean), see pipeline progress |
| **Suggestion detail** | Focus on one detection with overlay on its source frame |
| Optional: **live run progress** | While pipeline runs, show "currently analyzing frame N" |

### 2. Severity Circles on the Analyzed Frame

Overlay on the static image (SVG or canvas):

- **Circle color** from severity (red / yellow / green)
- **Circle size** scales with severity (high = larger, low = smaller)
- **Optional label** on hover: category + confidence + description snippet
- **Multiple circles** if we later support multiple issues per frame (phase 2)

### 3. Keep Interactive Street View as Secondary Context

The existing `StreetViewPanel` stays useful for spatial context ("where on the street?"), but the **primary evidence** for "what did the AI see?" is the static analyzed frame + overlays.

Proposed layout on suggestion detail:

```
┌─────────────────────────────────────┐
│  Analyzed Frame + severity circles  │  ← primary evidence
├─────────────────────────────────────┤
│  Interactive Street View (compact)  │  ← geographic context
├─────────────────────────────────────┤
│  AuditSuggestionCard (review actions)│
└─────────────────────────────────────┘
```

---

## Technical Approach

### Phase A — Extend AI to Return Spatial Hints

Update the vision prompt in `backend/app/services/ai_service.py` to ask for **normalized image coordinates** (0–1, relative to image width/height):

```json
{
  "is_civic_issue": true,
  "category": "pothole",
  "confidence": 0.91,
  "severity": "high",
  "description": "A large pothole is visible in the right lane.",
  "regions": [
    {
      "center_x": 0.42,
      "center_y": 0.68,
      "radius": 0.12
    }
  ]
}
```

**Design choices:**

| Decision | Recommendation |
|----------|----------------|
| Shape | **Circle** (`center_x`, `center_y`, `radius`) — matches the UX ask and is easier for LLMs than precise boxes |
| Coordinate space | Normalized 0–1 (resolution-independent for 640×640 frames) |
| Multiple regions | Start with **one primary region** per frame; extend to array later |
| Validation | Clamp coords to [0,1]; reject/sanitize invalid values |
| Fallback | If model omits regions, show frame **without** overlay + "Location not pinpointed" badge |

**Severity → visual mapping (proposed):**

| Severity | Color | Circle radius (normalized) |
|----------|-------|------------------------------|
| low | `#22c55e` (green) | 0.06 |
| medium | `#eab308` (yellow) | 0.09 |
| high | `#ef4444` (red) | 0.12 |
| critical | `#b91c1c` (dark red) | 0.14 |

Radius can also incorporate bbox area if we switch to boxes later.

**Model note:** Vision LLMs give approximate locations, not pixel-perfect detections. Circles are **indicative**, not survey-grade. That is acceptable for reviewer context if we label them as "AI-estimated location."

---

### Phase B — Backend Persistence and API

#### Database

**Option 1 (minimal, suggestion-only):**

Add JSON column on `AuditSuggestion`:

```python
detection_regions: list[DetectionRegion] | null  # [{center_x, center_y, radius}]
```

**Option 2 (full transparency — recommended):**

New `audit_frames` table:

| Column | Purpose |
|--------|---------|
| `audit_run_id`, `frame_index` | Ordering |
| `latitude`, `longitude`, `heading`, `pitch` | Frame identity |
| `image_storage_key` or proxied path | Safe image access |
| `analysis_result` JSON | Full AI output including regions |
| `is_civic_issue`, `confidence`, etc. | Query/filter |
| `suggestion_id` FK (nullable) | Link detection → frame |

Option 2 lets reviewers browse **all 64 frames**, not only the detections.

#### API Changes

| Endpoint | Change |
|----------|--------|
| `GET /audit-runs/{id}/frames` | **New** — list all analyzed frames for a run |
| `GET /audit-runs/{id}/frames/{index}` | **New** — single frame + analysis |
| `GET /audit-suggestions/{id}` | Include `detection_regions` + frame reference |
| `GET /audit-suggestions/{id}/frame-image` | **New** — proxy static Street View image (hides API key) |

**Image proxy (required):**

Today `image_url` contains the Google API key, so the frontend hides it. A backend proxy endpoint serves the JPEG to authenticated frontend clients without exposing credentials.

#### Pipeline Update

In `audit_service._process_frame`:

1. Fetch frame (already done)
2. Run AI (extend schema)
3. Persist frame record (+ suggestion if issue found)
4. Store `detection_regions` from AI response

---

### Phase C — Frontend Components

#### New: `AnalyzedFrameViewer.vue`

- Renders proxied static image (`<img>` or background)
- SVG overlay layer with severity circles
- Props: `imageUrl`, `regions[]`, `severity`, `category`, `description`
- Responsive: circles use `%` positioning from normalized coords

#### New: `AuditFrameBrowser.vue` (run detail)

- Grid or filmstrip of all frames in a run
- Filter: all / detections only / by severity / by category
- Click frame → expand with overlay + metadata

#### Update: `AuditSuggestionDetailPage.vue`

Replace or supplement `StreetViewPanel` layout with analyzed frame as primary evidence (see layout above).

#### Types

Align on one region shape across the stack:

```ts
interface DetectionRegion {
  center_x: number;  // 0–1
  center_y: number;
  radius: number;    // 0–1 relative to min(width, height)
}
```

Deprecate or map the old `BoundingBox { x, y, width, height }` in `frontend/src/types/detection.ts` if unused.

#### Styling

Reuse existing severity tokens from `AppBadge` where possible (`severity-low`, `severity-high`, etc.) for consistency.

---

## Implementation Phases

| Phase | Scope | Outcome |
|-------|--------|---------|
| **1. Blueprint approval** ✅ | Review this doc, pick open decisions | Locked requirements |
| **2. AI + schema** ✅ | Prompt, `ImageAnalysisResult`, validation | Model returns regions |
| **3. Backend storage** ✅ | Migration, pipeline, proxy endpoint | API serves frames + regions |
| **4. Frame viewer UI** ✅ | `AnalyzedFrameViewer` + suggestion detail | One detection visible with circles |
| **5. Run frame browser** ✅ | All frames in audit run detail | Full "what AI analyzed" transparency |
| **6. Demo seed update** ✅ | Hand-annotated regions + frame seeding | Demo mode shows overlays |
| **7. Polish** ✅ | Legend, hover tooltips, accessibility, tests | Production-ready |

### Phase 1 — Blueprint Approval ✅

- [x] Confirm open decisions — see **Phase 1 — Locked Requirements** above
- [x] Choose Option 2 (`audit_frames` table) for frame storage
- [x] Approve severity color/radius mapping

### Phase 2 — AI + Schema

Files:

- `backend/app/services/ai_service.py` — extend `CIVIC_ISSUE_PROMPT`
- `backend/app/schemas/report.py` — add `DetectionRegion`, extend `ImageAnalysisResult`

Tasks:

- Add `regions` array to prompt and response schema
- Validate and clamp normalized coordinates
- Handle missing regions gracefully (no overlay, not a pipeline failure)

### Phase 3 — Backend Storage

Files:

- `backend/app/models/audit.py` — new `AuditFrame` model or `detection_regions` column
- `backend/alembic/versions/` — new migration
- `backend/app/services/audit_service.py` — persist frames and regions in `_process_frame`
- `backend/app/schemas/audit.py` — expose regions in API responses
- `backend/app/api/v1/routes/audit.py` — new frame list/detail/image-proxy routes
- `backend/app/integrations/street_imagery.py` — image proxy helper

Tasks:

- Alembic migration for frame/region storage
- `GET /audit-runs/{id}/frames` and frame detail endpoints
- `GET /audit-suggestions/{id}/frame-image` proxy (no API key in frontend)
- Update seeder if demo data needs sample regions

### Phase 4 — Frame Viewer UI

Files:

- `frontend/src/components/audit/AnalyzedFrameViewer.vue` — **new**
- `frontend/src/pages/audit/AuditSuggestionDetailPage.vue` — integrate viewer
- `frontend/src/types/detection.ts` — add `DetectionRegion`
- `frontend/src/api/auditSuggestions.ts` or new `auditFrames.ts` — fetch frame + image

Tasks:

- SVG severity circle overlay on static image
- Severity color mapping (red / yellow / green)
- "AI-estimated location" label when regions present
- Fallback state when regions missing

### Phase 5 — Run Frame Browser

Files:

- `frontend/src/components/audit/AuditFrameBrowser.vue` — **new**
- `frontend/src/pages/audit/AuditRunDetailPage.vue` or `AuditRunDetailPanel.vue` — embed browser

Tasks:

- Filmstrip or grid of all frames in a run
- Filters: all / detections only / by severity / by category
- Click-to-expand with overlay and metadata
- Lazy-load thumbnails for performance

### Phase 6 — Demo Seed Update

Files:

- `ai/data/demo/audit_results.json` — optional hand-annotated regions
- `backend/app/seeds/demo.py` — seed frame records and regions

Tasks:

- Either re-run pipeline on demo route to get real AI regions
- Or hand-annotate a subset of demo detections for Pitch Mode

### Phase 7 — Polish

Tasks:

- Severity legend (red / yellow / green)
- Hover tooltips: category, confidence, description
- Keyboard/accessibility for frame browser
- Backend tests for new endpoints and region validation
- Frontend tests for overlay positioning

---

## Open Decisions (Resolved in Phase 1)

| # | Question | Resolution |
|---|----------|------------|
| 1 | All frames vs detections only | **All frames** via `audit_frames` table |
| 2 | Circle accuracy expectations | **"AI-estimated location"** label in UI |
| 3 | Critical severity | **Dark red, radius 0.14** (distinct from high) |
| 4 | Multiple issues per frame | **One primary region** in v1; array reserved for later |
| 5 | Frame browser placement | **Audit run detail page** first |
| 6 | Existing suggestions | **New runs only** — no backfill in v1 |

---

## Files That Will Change

| Area | Files |
|------|-------|
| AI prompt & schema | `backend/app/services/ai_service.py`, `backend/app/schemas/report.py` |
| Pipeline & storage | `backend/app/services/audit_service.py`, `backend/app/models/audit.py`, Alembic migration |
| API | `backend/app/api/v1/routes/audit.py`, `backend/app/schemas/audit.py` |
| Image proxy | `backend/app/integrations/street_imagery.py` or new route |
| Frontend viewer | `frontend/src/components/audit/AnalyzedFrameViewer.vue`, `AuditFrameBrowser.vue` |
| Pages | `frontend/src/pages/audit/AuditSuggestionDetailPage.vue`, `AuditRunDetailPage.vue`, `AuditRunDetailPanel.vue` |
| Types & API | `frontend/src/types/detection.ts`, new `frontend/src/api/auditFrames.ts` |
| Demo data | `ai/data/demo/audit_results.json`, `backend/app/seeds/demo.py` |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLM gives bad/wrong coordinates | Validate + clamp; show frame anyway; optional "no overlay" state |
| Static frame ≠ live panorama | Always show static analyzed frame as source of truth |
| API key in URLs | Backend image proxy only |
| Performance (64 frames × images) | Lazy-load thumbnails; paginate frame list |
| Cost (re-prompting with richer JSON) | Minimal token increase; same image call |
| Three incompatible bbox shapes | Standardize on `DetectionRegion` circle model across stack |

---

## Summary

To deliver "see what the AI analyzed + severity circles," three layers are required:

1. **AI** — return normalized region coordinates per detection
2. **Backend** — store frames/regions and serve images safely
3. **Frontend** — static frame viewer with SVG severity circles, plus optional frame browser on audit runs

All seven phases are complete.
