# Proactive Street Audit Suggestions Blueprint

## Goal

Replace the current hardcoded/unavailable AI suggestion review UI with real backend and AI pipeline data.

After implementation, a municipal user should be able to:

- Create a proactive street-audit run from the frontend.
- Watch backend pipeline progress from real audit-run fields.
- Select a run and fetch its real AI suggestions from `GET /api/v1/audit-runs/{run_id}/suggestions`.
- Review each suggestion with real persisted status changes.
- Convert accepted suggestions into real dashboard reports.
- Open direct run and suggestion detail routes backed by API data, not frontend fixtures.

This blueprint is intentionally implementation-only-after-approval. No stubs, no fake live data, and no frontend-only replacement for model output.

## Current State

### What Already Exists

Backend:

- `GET /api/v1/audit-runs`
- `POST /api/v1/audit-runs`
- `GET /api/v1/audit-runs/{run_id}`
- `GET /api/v1/audit-runs/{run_id}/suggestions`
- `PATCH /api/v1/audit-suggestions/{suggestion_id}`
- `POST /api/v1/audit-suggestions/{suggestion_id}/convert-to-report`
- `AuditService._run_pipeline()` creates suggestions from Street View frames and OpenRouter image analysis.
- Seeded audit suggestion data exists and is returned by the backend.
- Newly created runs can also produce real suggestions when the external Street View and OpenRouter calls succeed.

Frontend:

- Audit run list and create flow are already wired to backend.
- `frontend/src/api/auditSuggestions.ts` declares suggestion endpoint paths.
- Demo suggestion fixtures exist for Pitch Mode only.

### What Is Still Hardcoded Or Unwired

Frontend:

- `AuditRunDetailPanel.vue` always renders `AuditSuggestionUnavailablePanel`.
- `AuditSuggestionUnavailablePanel.vue` contains the hardcoded copy the user sees.
- `auditSuggestions.ts` only exports endpoint constants and function types. It does not call `apiGet`, `apiPatch`, or `apiPost`.
- There is no Pinia store for audit suggestions.
- `AuditPage.vue` never fetches suggestions for the selected run.
- `AuditRunDetailPage.vue` resolves a run by searching `GET /api/v1/audit-runs`, even though `GET /api/v1/audit-runs/{run_id}` exists.
- `AuditSuggestionDetailPage.vue` is reserved/static and does not fetch a real suggestion.

Backend:

- There is no `GET /api/v1/audit-suggestions/{suggestion_id}` detail endpoint, but the frontend route expects a direct suggestion detail flow.
- `AuditSuggestionRead` omits useful fields that the UI likely needs: `department`, `heading`, `pitch`, `reviewer_note`, and `converted_report_id` are partly or fully missing from frontend/backend contracts.
- `AuditRunSummary` includes `frames_total` and `frames_done`, but frontend `AuditRunSummary` does not type them.
- There are no backend tests covering the audit suggestion endpoints.
- The pipeline has no deduplication yet, despite user-facing copy saying confidence scoring and deduplication are owned by backend/AI.
- The pipeline can produce no suggestions for a completed run if all frames fail, all model responses are below threshold, or external providers reject/timeout.

## Live API Findings

These were checked against the local backend on `127.0.0.1:8000`.

- `GET /api/v1/audit-runs` returns real records.
- `GET /api/v1/audit-runs/2320c6b1-77ef-5438-ad1b-0bcd9c3cdb5f/suggestions` returns seeded backend suggestions.
- `GET /api/v1/audit-runs/e16730c8-5495-43f1-92e4-c3a3012c4f1e/suggestions` now returns real model-produced suggestions for that selected run.
- The first request to the selected run timed out while the backend was busy processing the audit pipeline. A later request succeeded after suggestions had been persisted.

The core issue is therefore not that backend suggestions do not exist. The main product gap is frontend wiring plus API contract hardening.

## Target API Contract

### Audit Run Summary

Frontend type should match backend response:

```ts
interface AuditRunSummary {
  id: string;
  municipality: string;
  route_name: string;
  notes?: string | null;
  status: 'queued' | 'running' | 'completed' | 'failed';
  frames_total: number;
  frames_done: number;
  created_at: string;
}
```

### Audit Suggestion

Use one shared frontend type for list cards and detail view:

```ts
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
  department?: string | null;
  heading?: number | null;
  pitch?: number | null;
  reviewer_note?: string | null;
  converted_report_id?: string | null;
  created_at: string;
}
```

Backend `AuditSuggestionRead` should include the same persisted fields. `bounding_box` should stay out unless the backend actually stores it.

### Endpoints To Use

- `GET /api/v1/audit-runs`
- `POST /api/v1/audit-runs`
- `GET /api/v1/audit-runs/{run_id}`
- `GET /api/v1/audit-runs/{run_id}/suggestions`
- `GET /api/v1/audit-suggestions/{suggestion_id}` to add
- `PATCH /api/v1/audit-suggestions/{suggestion_id}`
- `POST /api/v1/audit-suggestions/{suggestion_id}/convert-to-report`

## Backend Plan

### 1. Harden Suggestion Schemas

Update `backend/app/schemas/audit.py`:

- Add `department`, `heading`, `pitch`, `reviewer_note`, and `converted_report_id` to `AuditSuggestionRead`.
- Keep `from_attributes=True`.
- Do not add fields that are not stored yet, such as `bounding_box`.

### 2. Add Suggestion Detail Endpoint

Update `backend/app/api/v1/routes/audit.py`:

- Add `GET /api/v1/audit-suggestions/{suggestion_id}`.
- Reuse `AuditService._get_suggestion_or_404()` through a public `get_suggestion()` method.
- Return `AuditSuggestionRead`.

### 3. Make Review And Convert Responses Complete

Keep existing endpoints, but ensure returned data includes the expanded fields:

- `PATCH /api/v1/audit-suggestions/{suggestion_id}`
- `POST /api/v1/audit-suggestions/{suggestion_id}/convert-to-report`

For conversion, the response can stay `{ report_id }`, but the frontend should refetch or locally mark the suggestion as `converted_to_report`.

### 4. Improve Pipeline Run Semantics

Keep completed status meaning “all frames processed,” not “suggestions exist.”

Frontend copy should distinguish:

- Completed with suggestions.
- Completed with no suggestions above threshold.
- Failed because external imagery/geocoding/AI failed.
- Running and suggestions may still be arriving.

Backend should eventually store a failure reason, but that can be a later migration unless you want it included in this implementation.

### 5. Add Focused Backend Tests

Add tests for:

- Listing suggestions for an existing run.
- Listing suggestions for a missing run returns 404.
- Getting a suggestion by ID.
- Reviewing a suggestion updates status and note.
- Converting a suggestion creates a `street_audit` report and marks the suggestion converted.

If the current test setup depends on the real configured database, keep these integration-style and avoid mocking the AI pipeline.

## Frontend Plan

### 1. Implement Real API Functions

Update `frontend/src/api/auditSuggestions.ts`:

- `listAuditSuggestions(runId)`
- `getAuditSuggestion(suggestionId)`
- `reviewAuditSuggestion(suggestionId, payload)`
- `convertAuditSuggestionToReport(suggestionId)`

Use the existing `apiGet`, `apiPatch`, and `apiPost` helpers.

### 2. Fix Frontend Types

Update:

- `frontend/src/types/audit.ts` to include `frames_total` and `frames_done`.
- `frontend/src/types/detection.ts` to include backend-returned suggestion fields and remove or stop relying on unstored `bounding_box` for live records.

### 3. Add Audit Suggestions Store

Create `frontend/src/stores/auditSuggestions.ts` with:

- `suggestionsByRunId`
- `suggestionDetailsById`
- `loadingByRunId`
- `errorByRunId`
- `reviewErrorById`
- `convertErrorById`
- `fetchForRun(runId)`
- `fetchSuggestion(suggestionId)`
- `reviewSuggestion(suggestionId, payload)`
- `convertSuggestionToReport(suggestionId)`

This should mirror the existing reports store pattern.

### 4. Replace The Unavailable Panel In Run Detail

Update `AuditRunDetailPanel.vue` to accept suggestion state:

- `suggestions`
- `suggestionsLoading`
- `suggestionsError`
- `isDemoData`
- review/convert callbacks

Render:

- Loading state while fetching.
- Error state with retry.
- Empty state if completed but no suggestions exist.
- Real suggestion cards/table if suggestions are returned.
- The unavailable panel only when backend fails with a real capability error, not as the default for live runs.

### 5. Wire Selection To Fetch Suggestions

Update `AuditPage.vue`:

- Watch `auditRunsStore.selectedRunId`.
- Fetch suggestions for that run when selected.
- Refetch suggestions periodically or after manual refresh while the run is `running`.
- Pass real suggestions into `AuditRunDetailPanel`.
- Keep `DemoAuditSuggestionPanel` isolated to Pitch Mode and clearly separate from live run detail.

### 6. Make Detail Routes Real

Update `AuditRunDetailPage.vue`:

- Use `GET /api/v1/audit-runs/{run_id}` instead of scanning the list only.
- Fetch suggestions for that run.

Update `AuditSuggestionDetailPage.vue`:

- Use `GET /api/v1/audit-suggestions/{suggestion_id}`.
- Render category, confidence, severity, department, coordinates, heading/pitch, evidence URL, attribution, model name, explanation, review status, reviewer note, and conversion state.
- Show review and convert actions for live suggestions.

### 7. UI Components To Add Or Replace

Add real live components rather than modifying demo-only components:

- `AuditSuggestionList.vue`
- `AuditSuggestionCard.vue`
- `AuditSuggestionReviewForm.vue`
- `AuditSuggestionEvidencePanel.vue`

Keep `DemoAuditSuggestionPanel.vue` and `DemoAuditSuggestionCard.vue` for Pitch Mode only.

## AI Pipeline Plan

### Current Pipeline

The current backend pipeline:

- Resolves route waypoints.
- Builds frames from headings.
- Fetches Google Street View frames.
- Sends image bytes to OpenRouter.
- Parses a single JSON result.
- Stores suggestions above confidence threshold.

This is enough for real retrieval, but not enough for polished production semantics.

### Required For This Implementation

No separate AI service API is required for the frontend. The backend should remain the owner of AI orchestration, and the frontend should only consume stored audit suggestions.

The implementation should:

- Keep external provider errors from crashing API requests.
- Continue marking frames done even when one frame fails.
- Persist only model-produced suggestions.
- Expose enough evidence fields for human review.

### Later Hardening

These are valuable but can be separate unless explicitly approved for this pass:

- Deduplicate suggestions within `KOSTREET_AI_DUPLICATE_RADIUS_METERS`.
- Store per-run failure counts and failure reason.
- Store raw model/provider metadata for traceability.
- Store a legal image snapshot or provider-safe reference instead of exposing API-key-bearing Google URLs.
- Use async Street View fetching instead of thread-wrapped sync calls.

## Data And Security Concerns

Current `image_url` values include the Google Maps API key. The UI should not render or expose those URLs as final user-facing evidence without a decision.

Options:

1. Keep image URL hidden and show attribution plus coordinates for now.
2. Add backend proxy endpoint that strips keys from frontend-visible URLs.
3. Store sanitized provider metadata and only use signed/temporary image access if legally allowed.

Recommended for this implementation: do not display raw `image_url` if it includes a key. Show “Google Street View frame available through backend evidence record” and display attribution, heading, pitch, coordinates, model explanation, and confidence. Add a proxy/sanitization pass later if images must be visible.

## Acceptance Criteria

- The selected run panel no longer shows “Backend endpoint required” for live runs when suggestions are available.
- Selecting run `e16730c8-5495-43f1-92e4-c3a3012c4f1e` renders the real suggestions returned by the backend.
- Completed runs with zero suggestions show an honest empty state, not a fake/demo suggestion panel.
- Running runs show progress and can display suggestions already persisted.
- Review actions persist through `PATCH /api/v1/audit-suggestions/{id}`.
- Convert action creates a dashboard report with `source = street_audit`.
- Direct suggestion detail route is backed by `GET /api/v1/audit-suggestions/{id}`.
- Frontend build/typecheck passes.
- Backend tests pass.
- No frontend live path uses demo fixtures or hardcoded suggestion field descriptions as replacement data.

## Suggested Implementation Order

1. Backend schema expansion and suggestion detail endpoint.
2. Backend tests for suggestion list/detail/review/convert.
3. Frontend API functions and type fixes.
4. Audit suggestions Pinia store.
5. Real suggestion list/card/review components.
6. Wire `AuditPage.vue` and `AuditRunDetailPanel.vue`.
7. Wire direct run and suggestion detail pages.
8. Run backend tests, frontend typecheck/build, and manual end-to-end API verification.

## Open Decisions Before Implementation

- Should live UI display raw `image_url` if it contains a Google API key? Recommended answer: no.
- Should this pass include backend deduplication, or should we only expose currently persisted suggestions? Recommended answer: expose currently persisted suggestions now, deduplicate later.
- Should completed runs with no suggestions be marked `completed` or a new status like `completed_no_findings`? Recommended answer: keep status unchanged and express no findings in frontend copy.
- Should review require a note for rejection/manual review? Recommended answer: optional for now, can enforce later.
