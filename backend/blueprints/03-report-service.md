# Phase 3 — Report Service

> **Files to create / modify:**
> - `app/services/report_service.py` — replaces existing stub

> **Depends on:** Phase 0 (repositories, schemas, storage), Phase 2 (AI service)

---

## What this phase does

Builds the service class that owns all business logic for citizen reports:
- Creating reports (with or without an image)
- Fetching report detail (with workflow history)
- Updating report status (with transition validation)
- Delegating AI image analysis to `AIService`

Routes call this service. The service calls repositories and storage. Nothing in this service touches HTTP directly.

---

## Business rules defined here

### Department routing map

Maps an `IssueCategory` to the municipal department responsible for it.
Used by the dashboard's department suggestion panel.

```
pothole             → Roads / Public Works
garbage             → Sanitation
broken_streetlight  → Electrical / Infrastructure
blocked_sidewalk    → Roads / Public Works
damaged_sign        → Roads / Public Works
other               → General Services
```

This map is a module-level constant. It is not stored in the database — it is computed on read from the category field.

### Valid status transitions

```
new         → can move to:  verified,    rejected
verified    → can move to:  assigned,    rejected
assigned    → can move to:  in_progress, rejected
in_progress → can move to:  resolved,    rejected
resolved    → terminal (no further transitions allowed)
rejected    → terminal (no further transitions allowed)
```

Attempting an invalid transition raises an HTTP 422 with a message naming the current and requested status.

---

## Class: `ReportService`

```
ReportService(db: AsyncSession)
    → creates ReportRepository(db)
    → creates LocalFileStorage(settings.upload_dir)
    → creates AIService(settings)
```

### Methods

```
async def list_reports(
    status:   str | None,
    category: str | None,
    source:   str | None,
) -> list[Report]
    → delegates directly to repo.list(status, category, source)


async def create_report(
    data:  ReportCreate,
    image: UploadFile | None,
) -> Report
    Steps:
    1. if image is provided:
         image_path = await storage.save(image)
       else:
         image_path = None
    2. return await repo.create(data, image_path=image_path)


async def get_report_detail(report_id: UUID) -> Report
    Steps:
    1. report = await repo.get_with_events(report_id)
    2. if report is None: raise HTTPException(404, "Report not found")
    3. return report


async def update_status(
    report_id: UUID,
    payload:   ReportStatusUpdate,
) -> Report
    Steps:
    1. report = await repo.get_with_events(report_id)
    2. if report is None: raise HTTPException(404, "Report not found")
    3. allowed = VALID_TRANSITIONS[report.status]
    4. if payload.status not in allowed:
         raise HTTPException(422,
             f"Cannot move from '{report.status}' to '{payload.status}'. "
             f"Allowed next statuses: {sorted(allowed) or 'none (terminal status)'}"
         )
    5. return await repo.update_status(
           report, payload.status, note=payload.note
       )


async def analyze_image(file: UploadFile) -> ImageAnalysisResult
    → delegates to ai_service.analyze_upload(file)
```

---

## How the route receives the report creation payload

Because the `POST /api/v1/reports` endpoint accepts `multipart/form-data` (to support image upload), the JSON fields cannot be sent as a normal JSON body. The frontend will send:

- `data` — a form field containing the JSON string of `ReportCreate` fields
- `image` — an optional file field

The **route** (Phase 5) is responsible for parsing the `data` string into a `ReportCreate` object before calling `service.create_report(data, image)`. The service itself only receives typed objects.

---

## What is NOT in this phase
- No HTTP routing
- No dependency injection wiring (that is Phase 5)
- No audit-related logic
