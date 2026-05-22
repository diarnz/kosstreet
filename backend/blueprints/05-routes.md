# Phase 5 — Routes

> **Files to create / modify:**
> - `app/api/v1/routes/reports.py` — replaces existing stub
> - `app/api/v1/routes/audit.py` — replaces existing stub
> - `app/api/v1/router.py` — updated to add audit-suggestions sub-router

> **Depends on:** Phase 3 (ReportService), Phase 4 (AuditService)

---

## What this phase does

Wires services to HTTP endpoints. Routes are thin: they receive a request, call a service method, and return a typed response. No business logic lives here.

---

## Dependency pattern used in every route file

```python
def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)

def get_audit_service(
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = ...,
) -> AuditService:
    return AuditService(db)
```

Each request gets a fresh service instance bound to a fresh DB session. No shared state.

---

## File 1: `app/api/v1/routes/reports.py`

### 5 endpoints

---

#### `GET /api/v1/reports`

```
Query parameters (all optional):
  status   = one of: new | verified | assigned | in_progress | resolved | rejected
  category = one of: pothole | garbage | broken_streetlight | blocked_sidewalk | damaged_sign | other
  source   = one of: citizen | street_audit

Response: 200  list[ReportSummary]

Steps:
  1. call service.list_reports(status, category, source)
  2. return [ReportSummary.model_validate(r) for r in reports]
```

---

#### `POST /api/v1/reports/analyze-image`

> **Must be declared BEFORE `/{report_id}`** to avoid FastAPI routing it as a report ID lookup.

```
Content-Type: multipart/form-data
Form field:
  image   File   (required)

Response: 200  ImageAnalysisResult

Steps:
  1. if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
       raise 422 "Unsupported image type"
  2. result = await service.analyze_image(image)
  3. return result
```

---

#### `POST /api/v1/reports`

```
Content-Type: multipart/form-data
Form fields:
  data    str    (required) — JSON string of ReportCreate fields
  image   File   (optional)

Response: 201  ReportSummary

Steps:
  1. parsed = json.loads(data)  ← parse the JSON string
  2. report_data = ReportCreate(**parsed)  ← validate with Pydantic (raises 422 on bad data)
  3. report = await service.create_report(report_data, image or None)
  4. return ReportSummary.model_validate(report)

Why multipart?
  The frontend cannot send both a file and a JSON body in the same request.
  Wrapping the JSON fields in a form string field (named "data") is the standard pattern.
```

---

#### `GET /api/v1/reports/{report_id}`

```
Path parameter:
  report_id   UUID

Response: 200  ReportDetail
         404  {"detail": "Report not found"}

Steps:
  1. report = await service.get_report_detail(UUID(report_id))
  2. return ReportDetail.model_validate(report)
```

---

#### `PATCH /api/v1/reports/{report_id}/status`

```
Path parameter:
  report_id   UUID

Body (JSON):
  {
    "status": TicketStatus,
    "note":   string | null   (optional)
  }

Response: 200  ReportDetail
         404  {"detail": "Report not found"}
         422  {"detail": "Cannot move from '...' to '...'"}

Steps:
  1. report = await service.update_status(UUID(report_id), payload)
  2. return ReportDetail.model_validate(report)
```

---

## File 2: `app/api/v1/routes/audit.py`

This file handles both audit run routes and audit suggestion routes. They are split into two routers inside the same file and mounted separately in `router.py`.

### Audit run router — prefix: `/audit-runs`

---

#### `GET /api/v1/audit-runs`

```
Response: 200  list[AuditRunSummary]

Steps:
  1. runs = await service.list_runs()
  2. return [AuditRunSummary.model_validate(r) for r in runs]
```

---

#### `POST /api/v1/audit-runs`

```
Body (JSON):
  {
    "municipality": string  (default: "Prishtina"),
    "route_name":   string  (required),
    "notes":        string | null
  }

Response: 201  AuditRunSummary  (status = "queued")

Steps:
  1. run = await service.create_run(payload, background_tasks)
  2. return AuditRunSummary.model_validate(run)

Note:
  The pipeline starts in the background. The response is returned before any
  Street View frames are fetched. The frontend polls GET /{run_id} to track progress.
```

---

#### `GET /api/v1/audit-runs/{run_id}`

```
Path parameter:
  run_id   UUID

Response: 200  AuditRunSummary
         404

Steps:
  1. run = await service.get_run(UUID(run_id))
  2. return AuditRunSummary.model_validate(run)
```

---

#### `GET /api/v1/audit-runs/{run_id}/suggestions`

```
Path parameter:
  run_id   UUID

Response: 200  list[AuditSuggestionRead]
         404  (if run does not exist)

Steps:
  1. suggestions = await service.list_suggestions(UUID(run_id))
  2. return [AuditSuggestionRead.model_validate(s) for s in suggestions]
```

---

### Audit suggestion router — prefix: `/audit-suggestions`

---

#### `PATCH /api/v1/audit-suggestions/{suggestion_id}`

```
Path parameter:
  suggestion_id   UUID

Body (JSON):
  {
    "status":        "accepted" | "rejected" | "needs_manual_review",
    "reviewer_note": string | null
  }

Response: 200  AuditSuggestionRead
         404
         422  (if already converted_to_report)

Steps:
  1. suggestion = await service.review_suggestion(UUID(suggestion_id), payload)
  2. return AuditSuggestionRead.model_validate(suggestion)
```

---

#### `POST /api/v1/audit-suggestions/{suggestion_id}/convert-to-report`

```
Path parameter:
  suggestion_id   UUID

Body: none

Response: 201  SuggestionConversionResult  {"report_id": UUID}
         404
         409  (if already converted)

Steps:
  1. result = await service.convert_to_report(UUID(suggestion_id))
  2. return result
```

---

## File 3: `app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.api.v1.routes import health, reports
from app.api.v1.routes.audit import audit_runs_router, audit_suggestions_router

api_router = APIRouter()
api_router.include_router(health.router,               tags=["health"])
api_router.include_router(reports.router,              prefix="/reports",            tags=["reports"])
api_router.include_router(audit_runs_router,           prefix="/audit-runs",         tags=["street-audit"])
api_router.include_router(audit_suggestions_router,    prefix="/audit-suggestions",  tags=["street-audit"])
```

---

## Complete endpoint surface after this phase

```
GET    /health
GET    /api/v1/health

GET    /api/v1/reports
POST   /api/v1/reports/analyze-image
POST   /api/v1/reports
GET    /api/v1/reports/{report_id}
PATCH  /api/v1/reports/{report_id}/status

GET    /api/v1/audit-runs
POST   /api/v1/audit-runs
GET    /api/v1/audit-runs/{run_id}
GET    /api/v1/audit-runs/{run_id}/suggestions

PATCH  /api/v1/audit-suggestions/{suggestion_id}
POST   /api/v1/audit-suggestions/{suggestion_id}/convert-to-report
```
