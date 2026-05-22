# Phase 4 — Audit Service

> **Files to create / modify:**
> - `app/services/audit_service.py` — replaces existing stub

> **Depends on:** Phase 0 (repositories, schemas), Phase 1 (GSV client), Phase 2 (AI service), Phase 3 (report service for `create_from_suggestion`)

---

## What this phase does

Builds the service that manages the full street-audit lifecycle:

1. **List and fetch** audit runs
2. **Create a run** — registers it in the DB, immediately queues the AI pipeline as a background task, and returns the run in `queued` status so the frontend can start polling
3. **Run the pipeline** — fetches Street View frames, calls AI on each, stores detections as suggestions
4. **Review suggestions** — accept / reject / flag for manual review
5. **Convert a suggestion to a report** — creates an official report ticket from an AI finding

---

## Known route waypoints

The service contains a hardcoded registry of named routes mapped to GPS waypoint lists. These coordinates were extracted directly from `ai/data/demo/audit_results.json`.

For unknown route names the service falls back to a single-point plan using the Google Geocoding API (best effort — if geocoding fails the run is marked `failed`).

```
KNOWN_ROUTES = {
    "Bill Clinton Boulevard": [
        (42.6596,   21.1545),
        (42.65989,  21.15496),
        (42.66019,  21.15542),
        (42.66048,  21.15589),
        (42.66078,  21.15635),
        (42.66107,  21.15681),
        (42.66137,  21.15727),
        (42.66166,  21.15774),
        (42.66205,  21.15830),
        (42.66236,  21.15875),
        (42.66267,  21.15919),
        (42.66298,  21.15964),
        (42.66329,  21.16008),
        (42.66360,  21.16052),
        (42.66391,  21.16097),
        (42.664,    21.1611),
    ],
}
```

---

## Heading plan per waypoint

For each waypoint the pipeline uses these camera angles:

```
headings: 0°, 90°, 180°, 270°   (N, E, S, W)
pitch:    0°  (horizon level)
```

This gives **4 frames per waypoint**. With 16 waypoints on Bill Clinton Boulevard that is **64 total frames** — matching the `total_frames_analyzed: 64` in `audit_results.json`.

---

## Class: `AuditService`

```
AuditService(db: AsyncSession)
    → creates AuditRunRepository(db)
    → creates AuditSuggestionRepository(db)
    → creates GoogleStreetViewClient(settings.google_maps_api_key)
    → creates AIService(settings)
```

### Methods

```
async def list_runs() -> list[AuditRun]
    → run_repo.list()


async def get_run(run_id: UUID) -> AuditRun
    → run_repo.get(run_id) or raise 404


async def create_run(
    data:             AuditRunCreate,
    background_tasks: BackgroundTasks,
) -> AuditRun
    Steps:
    1. run = await run_repo.create(data)       ← status = "queued"
    2. background_tasks.add_task(
           self._run_pipeline, run.id
       )
    3. return run                               ← caller gets the queued run immediately


async def list_suggestions(run_id: UUID) -> list[AuditSuggestion]
    Steps:
    1. run = await run_repo.get(run_id)
    2. if run is None: raise 404
    3. return await sugg_repo.list_for_run(run_id)


async def review_suggestion(
    suggestion_id: UUID,
    payload:       AuditSuggestionReview,
) -> AuditSuggestion
    Steps:
    1. suggestion = await sugg_repo.get(suggestion_id)
    2. if None: raise 404
    3. if suggestion.status == "converted_to_report": raise 422 "Already converted"
    4. return await sugg_repo.review(suggestion, payload.status, payload.reviewer_note)


async def convert_to_report(suggestion_id: UUID) -> SuggestionConversionResult
    Steps:
    1. suggestion = await sugg_repo.get(suggestion_id)
    2. if None: raise 404
    3. if suggestion.status == "converted_to_report": raise 409 "Already converted"
    4. report = await report_repo.create_from_suggestion(
           category=suggestion.category,
           latitude=suggestion.latitude,
           longitude=suggestion.longitude,
           description=suggestion.description,
           confidence=suggestion.confidence,
       )
    5. await sugg_repo.convert_to_report(suggestion, report.id)
    6. return SuggestionConversionResult(report_id=report.id)
```

---

## Background pipeline: `_run_pipeline`

This method runs **outside the request lifecycle** — it gets its own database session.

```
async def _run_pipeline(run_id: UUID) -> None
    Opens a new AsyncSessionLocal() session for this entire pipeline run.

    Step 1 — Mark as running
        run_repo.set_status(run_id, "running")
        commit

    Step 2 — Resolve waypoints
        run = run_repo.get(run_id)
        waypoints = KNOWN_ROUTES.get(run.route_name)
        if waypoints is None:
            try geocode with Google Geocoding API
            if fails: mark "failed" and return

    Step 3 — Build frame list
        frames = []
        for (lat, lng) in waypoints:
            for heading in [0, 90, 180, 270]:
                frames.append(AuditFrame(lat, lng, heading, pitch=0))
        run_repo.set_frames_total(run_id, len(frames))
        commit

    Step 4 — Process each frame
        for frame in frames:
            try:
                gsv_frame  = gsv_client.fetch_frame(StreetImageryFrameRequest(...))
                ai_result  = await ai_service.analyze_image_bytes(gsv_frame.data)

                if ai_result.is_civic_issue and ai_result.confidence >= threshold:
                    image_url = build GSV static URL for this frame (used in UI)
                    sugg_repo.create_bulk([{
                        "audit_run_id": run_id,
                        "category":     ai_result.category,
                        "latitude":     frame.latitude,
                        "longitude":    frame.longitude,
                        "confidence":   ai_result.confidence,
                        "severity":     ai_result.severity,
                        "description":  ai_result.description,
                        "model_name":   settings.ai_model_name,
                        "department":   DEPARTMENT_MAP[ai_result.category],
                        "image_url":    image_url,
                        "image_attribution": "© Google Street View",
                        "heading":      frame.heading,
                        "pitch":        frame.pitch,
                    }])
                    commit
            except Exception as e:
                log warning, continue to next frame
            finally:
                run_repo.increment_frames_done(run_id)
                commit

    Step 5 — Mark complete
        run_repo.set_status(run_id, "completed")
        commit

    On unrecoverable exception in outer try:
        run_repo.set_status(run_id, "failed")
        commit
        log error
```

### Why it has its own DB session

FastAPI's `get_db()` dependency is scoped to the HTTP request. Once the route handler returns, that session is closed. The background task continues after the response is sent, so it must open a fresh `AsyncSessionLocal()` session itself.

---

## What is NOT in this phase
- No HTTP routing
- The `DEPARTMENT_MAP` constant is shared with the report service — it will live in a shared `app/utils/departments.py` module so both services import from the same place
