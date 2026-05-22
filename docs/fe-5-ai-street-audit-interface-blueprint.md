# FE-5 AI Street Audit Interface Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-5: AI Street Audit Interface**.

FE-0 created the frontend foundation. FE-1 created the visual system. FE-2 created real citizen report submission. FE-3 created the real municipality dashboard. FE-4 added real map/geospatial visualization. FE-5 creates the frontend review surface for proactive AI Street Audit results.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Build the frontend interface that lets municipalities start and review AI Street Audit runs without pretending the frontend performs AI inference.

Primary outcome:

> After FE-5, Prishtina municipal users should be able to open `/audit`, create a real audit run through the backend, view real audit runs from `GET /api/v1/audit-runs`, understand AI pipeline status, and review AI suggestions only when the backend exposes real suggestion data produced by the AI pipeline.

## Ownership Boundary

The AI side owns:

- Google Street View or approved imagery retrieval strategy.
- PaliGemma/Gemma or other model inference.
- Detection localization.
- Confidence scoring.
- Deduplication across frames/headings.
- Frame-level explanations.
- Any bounding boxes or image overlays.

The backend owns:

- API endpoints.
- Audit run persistence.
- Audit orchestration.
- Calls into the AI service/API.
- Conversion from accepted AI suggestion into municipal report/ticket.

The frontend owns:

- Audit run creation form.
- Audit run list and status display.
- Reviewable AI suggestion UI when real data exists.
- Human-in-the-loop accept/reject/manual-review flows when real backend endpoints exist.
- Clear UX around confidence, source, model output, and legal imagery constraints.
- Polished presentation for hackathon judging.

Frontend rule:

- The frontend must never fabricate AI detections, progress, image previews, bounding boxes, confidence, severity, or converted tickets.

## Critical Backend Reality Check

Current backend endpoints:

```text
GET /api/v1/audit-runs
POST /api/v1/audit-runs
```

Current audit run create payload:

```ts
interface AuditRunCreatePayload {
  municipality?: string;
  route_name: string;
  notes?: string | null;
}
```

Current audit run response:

```ts
type AuditRunStatus = 'queued' | 'running' | 'completed' | 'failed';

interface AuditRunSummary {
  id: string;
  municipality: string;
  route_name: string;
  notes?: string | null;
  status: AuditRunStatus;
  created_at: string;
}
```

Current backend does **not** yet provide:

- `GET /api/v1/audit-runs/:id`
- `GET /api/v1/audit-runs/:id/suggestions`
- `PATCH /api/v1/audit-suggestions/:id`
- `POST /api/v1/audit-suggestions/:id/convert-to-report`
- Audit run progress percentage.
- Audit run frame counts.
- Detection explanations.
- Bounding boxes.
- Street-level image preview URLs.
- Legal imagery attribution payload.
- Suggestion severity.
- Suggestion review status.

Therefore FE-5 implementation should be split into two honest frontend capabilities.

Current-contract capability:

- Real audit run creation via `POST /api/v1/audit-runs`.
- Real audit run list via `GET /api/v1/audit-runs`.
- Real status display using `queued`, `running`, `completed`, and `failed`.
- Selected audit run detail from the loaded list object.
- Empty and error states.
- Explanation of what will appear once the backend/AI suggestion endpoints are connected.

Future-contract-ready capability:

- Typed API modules, types, and UI boundaries for suggestions.
- Components designed to render real suggestion data once endpoints exist.
- No fake suggestion cards should appear until real API data is available.

## FE-5 Non-Goals

FE-5 will not implement:

- AI model inference in the frontend.
- Google Street View fetching in the frontend.
- Fake audit progress.
- Fake detection cards.
- Fake image preview.
- Fake bounding boxes.
- Fake severity.
- Fake confidence.
- Fake conversion into reports.
- Local-only accept/reject state pretending to be backend persistence.
- Route drawing or scan geometry unless the backend provides real route data.

These belong to backend, AI, or later frontend phases once API contracts are available.

## Routes

FE-5 should define these route-level surfaces:

```text
/audit
/audit/:runId
/audit/suggestions/:suggestionId
```

Implementation recommendation for FE-5:

- `/audit` should be fully implemented against the current backend contract.
- `/audit/:runId` should be implemented only from the loaded run list unless backend detail endpoint is added.
- `/audit/suggestions/:suggestionId` should show a real-data-required state until suggestion endpoints exist.

Route behavior:

- If `/audit/:runId` cannot find the run after fetching the run list, show a recoverable “run not found in current backend response” state.
- If `/audit/suggestions/:suggestionId` is opened before backend suggestion APIs exist, show a clear “suggestion API not connected yet” state, not placeholder content.

## User Flow

Current-contract audit run flow:

```text
/audit
  ↓
Fetch real audit runs from GET /api/v1/audit-runs
  ↓
Show audit run list, statuses, and selected run detail
  ↓
Municipal user creates a new run with route name and notes
  ↓
POST /api/v1/audit-runs
  ↓
New queued run appears in the workspace
```

Future AI suggestion review flow:

```text
/audit/:runId
  ↓
Fetch real suggestions for that run
  ↓
Municipal reviewer opens suggestion
  ↓
Reviews category, confidence, image context, location, and model explanation
  ↓
Accept, reject, or flag for manual review through backend endpoint
  ↓
If accepted, convert suggestion into a real municipal report/ticket
```

FE-5 should prepare the UX for this flow but only activate the interaction when real backend endpoints exist.

## Information Architecture

The `/audit` screen should have six functional areas.

### 1. Audit Header

Purpose:

- Make the proactive AI value clear.
- Position AI as assistant, not automatic truth.

Content:

- Title: AI Street Audit
- Description focused on proactive street defect discovery.
- Badges: `PaliGemma/Gemma pipeline`, `Human reviewed`, `Prishtina`.
- Refresh action.

Rules:

- Do not claim the browser is scanning imagery.
- Do not claim live detection results exist unless returned by backend.

### 2. Audit Run Creation

Purpose:

- Let municipal users start a backend audit run.

Fields:

- Municipality, default `Prishtina`.
- Route name.
- Notes.

Validation:

- Route name required.
- Municipality required.
- Notes optional.

Submission:

- Calls `POST /api/v1/audit-runs`.
- Shows loading state.
- Shows recoverable error state.
- Adds returned run to the run list or refreshes list after creation.

No-stub rule:

- Submit must call the backend.
- Do not create local-only audit runs if backend request fails.

### 3. Audit Run Metrics

Purpose:

- Summarize current real backend audit runs.

Metrics from real run list:

- Total runs.
- Queued runs.
- Running runs.
- Completed runs.
- Failed runs.

Rules:

- Metrics must be computed only from `GET /api/v1/audit-runs`.
- Do not show fake suggestion counts until suggestion endpoint exists.

### 4. Audit Run Queue

Purpose:

- Show the municipality what runs exist and what status they are in.

Fields:

- Route name.
- Municipality.
- Status.
- Created time.
- Notes preview if present.

Interactions:

- Select run.
- Filter by status.
- Search route name, municipality, notes, or ID.
- Refresh.

Rules:

- Filtering is client-side over real fetched runs.
- No fake runs.

### 5. Selected Run Detail

Purpose:

- Explain what the selected run represents and what data is currently available.

Fields:

- Run ID.
- Municipality.
- Route name.
- Status.
- Created time.
- Notes.
- Pipeline handoff explanation.

Current-contract behavior:

- Show that suggestion review will appear after backend returns AI suggestions for the run.
- If status is queued/running, describe that the backend/AI side owns execution.
- If status is completed but no suggestion endpoint exists, explain that completion is known but detections are not exposed to frontend yet.

No-stub rule:

- Do not render fake suggestions inside run detail.

### 6. Suggestion Review Preview Boundary

Purpose:

- Show the exact future review structure without fake data.

Allowed current behavior:

- A locked or unavailable panel titled “AI suggestion review”.
- Copy: “Suggestion review activates after `GET /api/v1/audit-runs/:id/suggestions` is connected.”
- List the real fields the frontend expects.

Not allowed:

- Fake pothole cards.
- Fake confidence percentages.
- Fake preview images.
- Fake bounding boxes.
- Fake “Accept” button that does nothing.

## Future Suggestion API Contract

The frontend should be designed around this contract, but must not assume it exists until backend confirms it.

Recommended endpoint:

```text
GET /api/v1/audit-runs/:runId/suggestions
```

Recommended response:

```ts
type AuditSuggestionStatus =
  | 'pending_review'
  | 'accepted'
  | 'rejected'
  | 'needs_manual_review'
  | 'converted_to_report';

type AuditSuggestionSeverity = 'low' | 'medium' | 'high' | 'critical';

interface AuditSuggestion {
  id: string;
  audit_run_id: string;
  category: IssueCategory;
  status: AuditSuggestionStatus;
  latitude: number;
  longitude: number;
  confidence: number;
  severity?: AuditSuggestionSeverity | null;
  description?: string | null;
  model_name?: string | null;
  explanation?: string | null;
  image_url?: string | null;
  image_attribution?: string | null;
  bounding_box?: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
  created_at: string;
}
```

Recommended review endpoints:

```text
PATCH /api/v1/audit-suggestions/:id
POST /api/v1/audit-suggestions/:id/convert-to-report
```

Recommended patch payload:

```ts
interface AuditSuggestionReviewPayload {
  status: 'accepted' | 'rejected' | 'needs_manual_review';
  reviewer_note?: string | null;
}
```

Recommended conversion response:

```ts
interface AuditSuggestionConversionResult {
  report_id: string;
}
```

## Frontend Types To Add

```text
frontend/src/types/audit.ts
frontend/src/types/detection.ts
```

`audit.ts` should include:

- `AuditRunStatus`
- `AuditRunCreatePayload`
- `AuditRunSummary`
- `AuditRunFiltersState`
- `AuditRunMetrics`

`detection.ts` should include future-contract types:

- `AuditSuggestionStatus`
- `AuditSuggestionSeverity`
- `AuditSuggestion`
- `AuditSuggestionReviewPayload`
- `AuditSuggestionConversionResult`
- `BoundingBox`

Rule:

- Future suggestion types can exist before endpoints, but UI must not render fake instances.

## API Modules To Add

```text
frontend/src/api/auditRuns.ts
frontend/src/api/auditSuggestions.ts
```

`auditRuns.ts` should implement now:

```ts
listAuditRuns(): Promise<AuditRunSummary[]>
createAuditRun(payload: AuditRunCreatePayload): Promise<AuditRunSummary>
```

`auditSuggestions.ts` should be added only if implementation uses it safely.

If added before backend endpoints exist:

- It may export typed functions for future use.
- It must not be called from production UI until backend support exists.
- Any unavailable state should be explicit in the page, not caused by failing API calls to missing endpoints.

## Store To Add

```text
frontend/src/stores/auditRuns.ts
```

State:

- `runs`
- `selectedRunId`
- `isLoading`
- `isCreating`
- `error`
- `createError`
- `lastFetchedAt`
- `filters`

Getters:

- `filteredRuns`
- `selectedRun`
- `metrics`

Actions:

- `fetchRuns`
- `createRun`
- `selectRun`
- `setSearch`
- `setStatus`
- `clearFilters`

Rules:

- Store only serializable audit run state.
- Do not store model outputs unless returned by backend.
- Do not store fake progress.

## Components To Add

```text
frontend/src/components/audit/AuditRunForm.vue
frontend/src/components/audit/AuditRunMetrics.vue
frontend/src/components/audit/AuditRunFilters.vue
frontend/src/components/audit/AuditRunQueue.vue
frontend/src/components/audit/AuditRunDetailPanel.vue
frontend/src/components/audit/AuditRunStatusPill.vue
frontend/src/components/audit/AuditSuggestionUnavailablePanel.vue
```

Future components after suggestion endpoints exist:

```text
frontend/src/components/audit/AuditSuggestionCard.vue
frontend/src/components/audit/AuditSuggestionDetailPanel.vue
frontend/src/components/audit/DetectionImagePreview.vue
frontend/src/components/audit/BoundingBoxOverlay.vue
frontend/src/components/audit/SuggestionReviewActions.vue
```

Current FE-5 should add future components only if they render no fake data and are not wired into active flows prematurely.

## Pages To Modify Or Add

Modify:

```text
frontend/src/pages/audit/AuditPage.vue
frontend/src/router/index.ts
```

Optional additions:

```text
frontend/src/pages/audit/AuditRunDetailPage.vue
frontend/src/pages/audit/AuditSuggestionDetailPage.vue
```

Recommended FE-5 decision:

- Implement `/audit` fully now.
- Add routes for `/audit/:runId` and `/audit/suggestions/:suggestionId` only if the route pages can show honest real-data-required states.
- Avoid complex route pages until backend detail/suggestion endpoints exist.

## Visual Direction

FE-5 should feel premium, operational, and AI-literate without looking like a generic neon AI demo.

Direction:

- Keep the warm civic command-center style from FE-1 through FE-4.
- Use AI-audit tone as a restrained warm technical accent.
- Emphasize human verification and reviewability.
- Make the audit workspace feel like an operations console, not a chatbot.

UI patterns:

- Strong route/run cards.
- Clear status chips.
- Compact metrics.
- Review panels with evidence hierarchy.
- Calm “not connected yet” states for suggestion endpoints.
- Transparent model/source labels.

Avoid:

- Magic sparkle AI styling.
- Fake “thinking” animations.
- Fake live scan progress.
- Dramatic model certainty language.
- Over-promising automatic decisions.

## Current Backend UX Copy

Use language like:

```text
Audit run created. Backend orchestration now owns AI pipeline execution.
```

```text
Suggestion review activates after the backend exposes real AI suggestion results for this run.
```

```text
KoStreet treats AI detections as municipal suggestions that require human review before becoming tickets.
```

Avoid language like:

```text
AI found 12 potholes.
```

unless the backend has returned those exact detections.

## No-Stub Rule For FE-5

Allowed:

- Real audit run fetch.
- Real audit run creation.
- Real audit run metrics.
- Real audit run filters/search.
- Honest suggestion unavailable panel.
- Future endpoint contract documentation in UI copy if helpful.
- Human-in-the-loop explanation.

Not allowed:

- Fake audit runs.
- Fake AI detections.
- Fake confidence.
- Fake severity.
- Fake Street View image previews.
- Fake bounding boxes.
- Fake scan progress.
- Fake accept/reject actions.
- Fake conversion into reports.
- Fake map markers for suggestions.
- Console-only actions.
- Buttons that appear active but do nothing.

## Accessibility Requirements

FE-5 must include:

- Semantic headings.
- Form labels.
- Status text, not color-only status.
- Keyboard-accessible run selection.
- Clear loading and error states.
- Recoverable empty states.
- Screen-reader-readable unavailable suggestion panel.
- Disabled/unavailable actions should explain why they are unavailable.

## Responsive Requirements

Test at:

- 360px mobile width.
- 768px tablet width.
- 1280px desktop width.

Expected behavior:

- Audit creation form stacks on mobile.
- Metrics wrap cleanly.
- Run queue remains readable.
- Detail panel stacks below queue on mobile.
- Suggestion unavailable panel remains clear and compact.

## Implementation Sequence

1. Add `frontend/src/types/audit.ts`.
2. Add `frontend/src/types/detection.ts` with future suggestion contracts.
3. Add `frontend/src/api/auditRuns.ts`.
4. Add `frontend/src/stores/auditRuns.ts`.
5. Add `AuditRunStatusPill`.
6. Add `AuditRunMetrics`.
7. Add `AuditRunForm`.
8. Add `AuditRunFilters`.
9. Add `AuditRunQueue`.
10. Add `AuditSuggestionUnavailablePanel`.
11. Add `AuditRunDetailPanel`.
12. Refactor `AuditPage.vue` to fetch real audit runs and compose the workspace.
13. Add optional honest routes for `/audit/:runId` and `/audit/suggestions/:suggestionId` if needed.
14. Run frontend build.
15. Run backend and frontend together.
16. Create a real audit run through the UI or API.
17. Confirm the new run appears in `/audit`.
18. Confirm no fake AI suggestions appear.

## Verification Plan

Required frontend command:

```bash
cd frontend
npm run build
```

Local integrated verification:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Backend checks:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/v1/audit-runs
```

Create-run API check:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/audit-runs \
  -H 'Content-Type: application/json' \
  -d '{"municipality":"Prishtina","route_name":"Bill Clinton Boulevard demo segment","notes":"FE-5 verification run."}'
```

Manual `/audit` flow:

1. Open `/audit`.
2. Confirm audit runs are fetched from backend.
3. Confirm empty state if no runs exist.
4. Create a real audit run.
5. Confirm submit calls backend and returned run appears.
6. Confirm metrics update from real backend data.
7. Search by route, municipality, notes, or ID.
8. Filter by status.
9. Clear filters.
10. Select an audit run.
11. Confirm detail panel shows real run data.
12. Confirm suggestion review panel does not show fake detections.
13. Confirm unavailable copy references missing backend suggestion endpoint honestly.

Expected behavior with one created run:

- Total runs: 1.
- Queued runs: 1.
- Selected run detail shows the returned ID, route name, municipality, status, created time, and notes.
- Suggestion panel says real AI suggestions are not connected to frontend yet unless backend endpoint exists.

## Risks And Mitigations

Risk: Judges expect visible AI suggestions.

Mitigation:

- If backend/AI suggestion endpoints are ready before implementation, wire them in with real data.
- If not, use the audit run creation and review-boundary UI to explain the architecture truthfully.

Risk: Current backend only stores queued runs.

Mitigation:

- Frontend should display the real queued status and explain that backend/AI orchestration owns status progression.

Risk: Frontend appears incomplete without suggestion cards.

Mitigation:

- Make the audit run workspace polished, operational, and explicit about the pipeline handoff.
- Use strong visual hierarchy around what is connected now and what activates after backend suggestion data exists.

Risk: Fake demo pressure causes bad data integrity.

Mitigation:

- Keep no-stub rule strict. If demo needs suggestions, backend should expose real sample outputs from the AI pipeline rather than frontend fabricating them.

Risk: Street View legal constraints are misunderstood.

Mitigation:

- UI copy should say “approved street-level imagery” and show imagery previews only when backend returns legally usable image URLs and attribution.

## FE-5 Acceptance Criteria

FE-5 is complete when:

- `npm run build` passes.
- `/audit` fetches real audit runs from `GET /api/v1/audit-runs`.
- `/audit` can create a real audit run through `POST /api/v1/audit-runs`.
- Audit run metrics are computed from real backend data.
- Audit run filters/search operate on real backend data.
- Selecting an audit run shows real run details.
- Suggestion review area is honest if suggestion endpoints are unavailable.
- No fake AI detections, confidence, severity, image previews, bounding boxes, progress, or conversion actions are introduced.
- UI clearly communicates human-in-the-loop review.
- UI clearly separates frontend review responsibility from backend/AI pipeline responsibility.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to backend suggestion endpoints, conversion behavior, image preview legality, or whether real AI suggestions are available before implementation should be agreed before coding.
