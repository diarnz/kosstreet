# Frontend Wrap-Up And Backend/AI Handoff

## Purpose

This document summarizes the completed KoStreet frontend phases and defines the next backend/AI work needed to turn the current frontend contract into a fully connected product.

It also highlights the Google Street View / AI Street Audit story because that is the standout differentiator in the README blueprint.

## Alignment With README Blueprint

The frontend work is aligned with `README.md`.

README direction:

- Build KoStreet as citizen reporting first.
- Add a municipality dashboard for triage and workflow.
- Make location central through geospatial visualization.
- Add AI Street Audit as the standout proactive layer.
- Treat Google Street View carefully because storage, bulk download, indexing, and ML training/validation use can be restricted by platform terms.
- Keep human verification in the loop.
- Separate frontend, backend, and AI responsibilities.

Current frontend result:

- Citizen reporting flow exists at `/report`.
- Citizen tracking route exists at `/report/status/:id`.
- Municipal dashboard exists at `/dashboard`.
- Leaflet/OpenStreetMap map experience exists for report coordinates.
- AI Street Audit workspace exists at `/audit`.
- Frontend workflow controls target future backend endpoints without faking success.
- Pitch Mode exists for reliable judging demos and labels demo data clearly.
- Demo AI suggestions are labeled as demo scenarios and do not claim live AI inference.

Conclusion:

> The frontend matches the README product strategy: core challenge first, AI Street Audit second, and no misleading claims about backend persistence, Street View, or live model output.

## Completed Frontend Phases

### FE-0: Frontend Foundation

Delivered:

- Vue/Vite app shell.
- Route structure.
- Shared UI primitives.
- Typed API client.
- Base layouts.
- Design tokens and utility CSS.

### FE-1: Visual Direction And UX System

Delivered:

- Prishtina Civic Warmth visual direction.
- Shared badges, status pills, metric cards, feature panels.
- Style guide.
- Premium municipal dashboard look without generic admin styling.

### FE-2: Citizen Reporting Flow

Delivered:

- Mobile-first report form.
- Local image preview with honest no-upload copy.
- Browser geolocation and manual coordinate fallback.
- Category selection.
- Description field.
- Real structured submission to `POST /api/v1/reports`.
- Tracking route after submission.

### FE-3: Municipality Dashboard

Delivered:

- Real report fetching from `GET /api/v1/reports`.
- Dashboard metrics.
- Search and filters.
- Report queue.
- Report detail panel.
- Deterministic suggested department routing.

### FE-4: Map And Geospatial Experience

Delivered:

- Leaflet/OpenStreetMap dashboard map.
- Real markers from report coordinates.
- Map/list/detail synchronization.
- Invalid-coordinate handling.
- Map fallback behavior.

### FE-5: AI Street Audit Interface

Delivered:

- Real audit run list from `GET /api/v1/audit-runs`.
- Real audit run creation through `POST /api/v1/audit-runs`.
- Audit run filters, metrics, queue, and detail panel.
- Honest unavailable state for AI suggestions until backend endpoints exist.

### FE-6: Ticket Workflow And Transparency

Delivered:

- Frontend contract for report detail:
  - `GET /api/v1/reports/:id`
- Frontend contract for status mutation:
  - `PATCH /api/v1/reports/:id/status`
- Status action UI.
- Workflow history UI.
- Citizen tracking page that attempts backend detail and fails honestly if missing.
- No frontend-only fake status persistence.

### FE-7: Demo Data And Pitch Mode

Delivered:

- Pitch Mode toggle.
- `?demo=1` and `?demo=0`.
- `localStorage` persistence.
- Labeled demo reports.
- Labeled demo audit runs.
- Labeled demo AI suggestion scenarios.
- Dashboard/audit/tracking fallbacks when backend data is empty or unavailable.

### FE-8: Accessibility, Performance, And Polish

Delivered:

- Improved focus visibility.
- Reduced-motion handling.
- Keyboard support for custom category radio group.
- Accessible queue selection state.
- Direct demo route support.
- Updated demo script and style guide.
- Production build verification.

## Current Frontend API Contracts

Already backed by current backend:

```text
GET /api/v1/reports
POST /api/v1/reports
GET /api/v1/audit-runs
POST /api/v1/audit-runs
```

Frontend-targeted contracts for next backend work:

```text
GET /api/v1/reports/:id
PATCH /api/v1/reports/:id/status
GET /api/v1/audit-runs/:id
GET /api/v1/audit-runs/:id/suggestions
PATCH /api/v1/audit-suggestions/:id
POST /api/v1/audit-suggestions/:id/convert-to-report
POST /api/v1/uploads
POST /api/v1/analyze-image
```

These names are already reflected in frontend expectations and docs.

## Google Street View And AI Street Audit Story

The README positions AI Street Audit as the standout feature:

> KoStreet does not only wait for citizen reports. It can proactively scan approved street-level imagery, surface likely civic defects, and send them to the dashboard for human municipal verification.

Frontend state today:

- `/audit` shows the municipal AI Street Audit workspace.
- Audit runs can be created and listed through real backend endpoints.
- Demo AI suggestion scenarios show how model outputs will be reviewed.
- The UI uses language such as "approved street-level imagery" and "human reviewed".
- The UI does not show fake Street View frames.
- The UI does not claim live AI scanning.

Important Street View constraint:

- KoStreet should not store, bulk download, index, or use Street View imagery for training/testing/validation unless terms explicitly allow it.
- The backend should handle imagery retrieval.
- The AI model should analyze images after retrieval; it should not fetch Google imagery itself.
- Store derived civic issue metadata only where allowed.

Recommended pitch wording:

```text
For the proactive layer, KoStreet can request approved street-level imagery for a selected route, sample headings around each location, pass the frames through the AI pipeline for transient analysis, and turn high-confidence findings into reviewable municipal suggestions.
```

Avoid wording:

```text
We trained on Google Street View.
```

```text
The browser scans Street View.
```

```text
AI automatically creates tickets.
```

Correct framing:

```text
AI suggests. Municipality verifies. Backend converts accepted suggestions into tickets.
```

## Recommended Backend Work Next

### Backend Phase B-1: Persistence And Report Detail

Goal:

Make reports durable and support citizen tracking.

Build:

- SQLite or PostgreSQL persistence.
- Report table/model.
- Workflow event table/model.
- `GET /api/v1/reports/:id`.
- `PATCH /api/v1/reports/:id/status`.
- Transition validation.
- Resolution/rejection notes.
- Backend tests.

Frontend impact:

- `/report/status/:id` becomes live.
- Dashboard status updates become real.
- Workflow history becomes real.

### Backend Phase B-2: Upload And Image Handling

Goal:

Support citizen photo upload without pretending local previews are persisted.

Build:

- `POST /api/v1/uploads`.
- File validation.
- Local filesystem storage for hackathon MVP.
- Image metadata model.
- Link uploaded image to report.
- Safe upload size/type restrictions.

Frontend impact:

- `/report` can replace "local preview only" with real upload success.
- Dashboard can show citizen-submitted evidence.

### Backend Phase B-3: Image Analysis Endpoint

Goal:

Connect citizen-uploaded images to AI-assisted category suggestions.

Build:

- `POST /api/v1/analyze-image`.
- Request references uploaded image ID or multipart image.
- Backend calls AI package/service.
- Response returns category, confidence, explanation, and optional bounding box.
- Human override remains possible.

Frontend impact:

- `/report` can show real AI category suggestion.
- Confidence appears only from real backend response.

### Backend Phase B-4: Audit Runs And Suggestions

Goal:

Expose AI Street Audit outputs to the frontend.

Build:

- `GET /api/v1/audit-runs/:id`.
- `GET /api/v1/audit-runs/:id/suggestions`.
- `PATCH /api/v1/audit-suggestions/:id`.
- `POST /api/v1/audit-suggestions/:id/convert-to-report`.
- Audit suggestion persistence.
- Review status.
- Conversion from accepted suggestion to report/ticket.

Frontend impact:

- Demo AI suggestion cards can be replaced by real backend suggestions.
- Municipal users can review, accept, reject, or flag suggestions.
- Accepted suggestions can become dashboard reports.

### Backend Phase B-5: Street Imagery Integration Boundary

Goal:

Safely retrieve approved route imagery for AI Street Audit.

Build:

- Street imagery integration service.
- Route/point input contract.
- Heading and pitch sampling request model.
- Google Street View or alternative imagery API adapter.
- Legal/terms-aware no-storage mode.
- Image attribution handling where required.
- Fallback when panorama coverage is missing.

Frontend impact:

- Audit runs can show real run status and legally allowed attribution.
- Suggestion evidence can include legally permitted preview URLs only when allowed.

## Recommended AI Work Next

### AI Phase A-1: Inference Contract

Goal:

Standardize AI output shape before model integration.

Build:

- Detection result schema aligned with frontend `AuditSuggestion`.
- Category mapping:
  - `pothole`
  - `garbage`
  - `broken_streetlight`
  - `blocked_sidewalk`
  - `damaged_sign`
  - `other`
- Confidence scoring.
- Severity scoring.
- Explanation field.
- Optional bounding box.

### AI Phase A-2: Citizen Image Classifier

Goal:

Classify uploaded citizen images.

Build:

- Preprocessing pipeline.
- Model adapter.
- Prompting or zero-shot strategy if using a vision-language model.
- Fallback to manual category when confidence is low.

### AI Phase A-3: Street Audit Planner

Goal:

Generate route scan frames.

Build:

- Route points.
- Heading plan, such as `0, 60, 120, 180, 240, 300`.
- Pitch plan, such as `-10, 0`.
- Deduplication by distance and category.
- Confidence aggregation.

### AI Phase A-4: Street-Level Defect Detection

Goal:

Analyze approved street-level frames.

Candidate approach:

- PaliGemma/Gemma-style vision-language reasoning for civic defect inspection.
- Optional detector pipeline for bounding boxes.
- Human-review threshold for low-confidence detections.

Output:

- Candidate audit suggestions stored by backend.
- No training or validation on Google Street View unless terms allow.

## Data And Legal Guardrails

Safe sources:

- Citizen-uploaded images with permission.
- Team-captured images or footage.
- Open imagery with compatible license.
- Approved street-level imagery through terms-compliant API flow.

Risky or restricted:

- Bulk-downloaded Google Street View.
- Stored Street View frames without allowed use.
- Training, testing, validating, or fine-tuning on Google Street View without explicit permission.

Frontend implication:

- Keep demo suggestions image-free unless there is approved imagery.
- Show attribution when backend provides it.
- Keep human verification visible.

## Final Demo Route

Recommended route:

```text
/
/report
/dashboard?demo=1
/audit?demo=1
/report/status/demo-report-pothole-001?demo=1
```

Talk track:

1. Citizen reports a pothole with photo, location, category, and description.
2. Municipality sees structured, geolocated reports in the dashboard.
3. Map shows where problems cluster.
4. Workflow and tracking show transparency.
5. AI Street Audit shows how KoStreet can proactively surface issues from approved street-level imagery.
6. Human review prevents automatic or unsafe decisions.

## Frontend Readiness Checklist

Current frontend is ready for:

- Product demo.
- Backend contract integration.
- AI contract integration.
- Pitch-mode fallback.
- Municipal dashboard walkthrough.
- Citizen reporting walkthrough.

Current frontend is not claiming:

- Persistent backend workflow status.
- Real image upload.
- Real AI classification.
- Real Street View scan output.
- Real audit suggestion conversion.

Those are the correct next backend/AI milestones.

## Immediate Next Step

Recommended next engineering step:

> Start backend persistence and report detail/status endpoints first.

Reason:

- This unlocks real citizen tracking.
- This makes dashboard workflow controls real.
- This makes the core challenge stronger before advanced AI work.
- It gives AI Street Audit a proper ticket/report destination when suggestion conversion is implemented.

After that:

1. Add upload endpoint.
2. Add image analysis endpoint.
3. Add audit suggestion endpoints.
4. Add Street View or approved imagery integration.
5. Connect AI inference outputs to audit suggestions.
