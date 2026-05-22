# FE-6 Ticket Workflow And Transparency Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-6: Ticket Workflow And Transparency**.

FE-0 created the frontend foundation. FE-1 established the visual system. FE-2 created real citizen report submission. FE-3 created the real municipal dashboard. FE-4 added real map/geospatial visualization. FE-5 added real AI Street Audit run management. FE-6 prepares the frontend ticket workflow and transparency experience against an explicit backend contract, while keeping behavior honest until the backend branch implements the endpoints.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Build a frontend-complete ticket workflow layer against the agreed backend API contract:

- Municipal users see the exact status controls that will call the backend status endpoint.
- Municipal users can submit status changes only through the configured backend route.
- Citizens can open a tracking URL that attempts to load live backend report detail.
- Workflow history renders only from real backend events when the backend endpoint exists.
- The frontend gracefully explains when workflow endpoints are not connected yet.
- The UI clearly separates suggested department routing from saved workflow status.

Primary outcome:

> After FE-6, KoStreet should have the complete frontend workflow and transparency surface wired to the intended backend routes, with no fake status mutation or fake workflow history while those routes are still pending.

## Critical Current-State Reality Check

Current backend endpoints:

```text
GET /api/v1/reports
POST /api/v1/reports
GET /api/v1/audit-runs
POST /api/v1/audit-runs
```

Current report fields:

```text
id
category
status
latitude
longitude
source
description
confidence
created_at
```

Current frontend report workflow behavior:

- `/report` creates real reports through `POST /api/v1/reports`.
- `/dashboard` fetches real reports through `GET /api/v1/reports`.
- `ReportDetailPanel.vue` shows status and workflow timeline as read-only.
- `/report/status/:id` shows a real tracking ID but does not fetch live report detail.
- `ReportWorkflowTimeline.vue` can display a current status but has no event history.

Current backend limitations:

- No `GET /api/v1/reports/:id`.
- No `PATCH /api/v1/reports/:id/status`.
- No persisted workflow events.
- No status transition validation.
- No resolution note or rejection reason.
- In-memory repositories mean data disappears when the backend restarts.

FE-6 must define and call the missing workflow API surface from the frontend, but must not implement backend code in this frontend branch.

## Non-Goals

FE-6 will not implement:

- Authentication or role-based permissions.
- Full database persistence or migrations.
- Image upload or image storage.
- AI image analysis.
- AI audit suggestion conversion.
- Department assignment persistence beyond deterministic suggested routing.
- Notifications, email, SMS, or push updates.
- Public search by phone number or personal identity.
- Complex SLA management.
- Server-side filtering or pagination.

These can be handled in later backend, platform, or production phases.

## End-To-End User Flow

Citizen-to-municipality workflow:

```text
/report
  ↓
Citizen submits category, location, source, and description
  ↓
POST /api/v1/reports creates report with status new
  ↓
/report/status/:id
  ↓
Citizen sees live backend status and workflow timeline
  ↓
Municipality opens /dashboard
  ↓
GET /api/v1/reports loads report queue
  ↓
Municipality selects report
  ↓
Municipality updates status through PATCH /api/v1/reports/:id/status
  ↓
Backend validates transition and stores workflow event
  ↓
Dashboard updates selected report and metrics from backend response
  ↓
Citizen refreshes /report/status/:id
  ↓
Citizen sees the updated real status and workflow event history
```

## Backend Contract Targeted By FE-6

FE-6 targets these backend endpoints. Until they exist, the frontend must handle `404`, `405`, and network errors without pretending the operation succeeded.

### Get Report Detail

```text
GET /api/v1/reports/:id
```

Purpose:

- Return one report by ID for citizen tracking and direct dashboard lookup.

Response:

```ts
interface ReportDetail {
  id: string;
  category: IssueCategory;
  status: TicketStatus;
  latitude: number;
  longitude: number;
  source: ReportSource;
  description?: string | null;
  confidence?: number | null;
  created_at: string;
  updated_at: string;
  resolution_note?: string | null;
  rejection_reason?: string | null;
  workflow_events: ReportWorkflowEvent[];
}
```

Error behavior:

- `404` if report does not exist.
- `422` if ID format is invalid.

### Update Report Status

```text
PATCH /api/v1/reports/:id/status
```

Purpose:

- Change a report's workflow status through backend validation.
- Create a real workflow event.
- Return the updated report detail.

Request:

```ts
interface ReportStatusUpdatePayload {
  status: TicketStatus;
  note?: string | null;
}
```

Response:

```ts
ReportDetail
```

Validation:

- `status` is required.
- `note` is optional for most transitions.
- `note` is required when status is `resolved` or `rejected`.
- Backend must reject invalid status transitions.
- Backend must reject updates for missing reports.

Error behavior:

- `404` if report does not exist.
- `409` if transition is invalid from current status.
- `422` if payload is invalid.

### Workflow Event Shape

```ts
interface ReportWorkflowEvent {
  id: string;
  report_id: string;
  from_status?: TicketStatus | null;
  to_status: TicketStatus;
  note?: string | null;
  created_at: string;
  actor_type: 'municipality' | 'system';
  actor_label: string;
}
```

FE-6 actor decision:

- Use `actor_type: 'system'` and `actor_label: 'KoStreet'` for the initial report-created event.
- Use `actor_type: 'municipality'` and `actor_label: 'Prishtina municipal staff'` for dashboard status updates.
- Do not introduce user accounts or authentication in FE-6.

## Backend Implementation Notes For Later

This frontend phase must not modify backend files. The backend implementation phase should later add:

- Report detail schemas.
- Report workflow event schemas.
- Status update request schema.
- `GET /api/v1/reports/:id`.
- `PATCH /api/v1/reports/:id/status`.
- Backend transition validation.
- Real workflow event creation.
- Tests for report detail, status transitions, and invalid transition handling.

## Status Transition Rules

FE-6 should support a practical municipal workflow without overengineering.

Allowed transitions:

```text
new -> verified
new -> rejected
verified -> assigned
verified -> rejected
assigned -> in_progress
assigned -> rejected
in_progress -> resolved
in_progress -> rejected
resolved -> verified
rejected -> new
```

Reasoning:

- `new -> verified` supports intake review.
- `new -> rejected` supports invalid reports.
- `verified -> assigned` models department ownership.
- `assigned -> in_progress` models field work starting.
- `in_progress -> resolved` models completion.
- Rejection is allowed before completion.
- `resolved -> verified` allows reopening after citizen or staff feedback.
- `rejected -> new` allows restoring a report rejected by mistake.

Not allowed:

```text
new -> assigned
new -> in_progress
new -> resolved
verified -> in_progress
verified -> resolved
assigned -> resolved
resolved -> rejected
rejected -> resolved
```

Frontend must only show allowed next statuses for the selected report.

## Frontend Contract Updates

### Types

Modify:

```text
frontend/src/types/report.ts
```

Add:

```ts
export interface ReportWorkflowEvent {
  id: string;
  report_id: string;
  from_status?: TicketStatus | null;
  to_status: TicketStatus;
  note?: string | null;
  created_at: string;
  actor_type: 'municipality' | 'system';
  actor_label: string;
}

export interface ReportDetail extends ReportSummary {
  updated_at: string;
  resolution_note?: string | null;
  rejection_reason?: string | null;
  workflow_events: ReportWorkflowEvent[];
}

export interface ReportStatusUpdatePayload {
  status: TicketStatus;
  note?: string | null;
}
```

Important:

- Keep `ReportSummary` stable for list rendering.
- Use `ReportDetail` only where detail fields or workflow events are needed.

### API

Modify:

```text
frontend/src/api/reports.ts
```

Add:

```ts
getReport(reportId: string): Promise<ReportDetail>
updateReportStatus(reportId: string, payload: ReportStatusUpdatePayload): Promise<ReportDetail>
```

Rules:

- Do not mutate local report status before backend confirmation.
- Surface `ApiError` messages in dashboard and tracking pages.

### Store

Modify:

```text
frontend/src/stores/reports.ts
```

Add state:

```ts
reportDetailsById: Record<string, ReportDetail>;
detailLoadingById: Record<string, boolean>;
detailErrorById: Record<string, string | null>;
isUpdatingStatus: boolean;
statusUpdateError: string | null;
```

Add actions:

- `fetchReportDetail(reportId)`
- `updateReportStatus(reportId, payload)`
- `mergeReportDetail(detail)`

Add getters:

- `selectedReportDetail`
- `selectedReportWorkflowEvents`
- `allowedNextStatuses`

Rules:

- After a status update succeeds, update both `reports` list state and `reportDetailsById`.
- Metrics must update from the real changed status.
- If detail fetch fails, keep list data available.
- Do not store fake workflow events.

## Frontend UX Scope

### Dashboard Detail Panel

Modify:

```text
frontend/src/components/dashboard/ReportDetailPanel.vue
```

New behavior:

- If selected report detail is not loaded, fetch it through `GET /api/v1/reports/:id`.
- Show detail loading state inside the panel.
- Show workflow history from real `workflow_events`.
- Show status update controls only after detail is loaded.
- Show only valid next statuses.
- Require a note when moving to `resolved` or `rejected`.
- Disable submit while PATCH is in flight.
- Display backend validation errors.

No-stub rule:

- Do not show status controls if the status update endpoint is unavailable.
- Do not optimistically show status changes before backend confirmation.
- Do not create local-only workflow events.

### New Component: `ReportStatusActions.vue`

Add:

```text
frontend/src/components/reports/ReportStatusActions.vue
```

Purpose:

- Render allowed next status choices and note input.

Props:

```ts
currentStatus: TicketStatus;
allowedStatuses: TicketStatus[];
isUpdating: boolean;
error?: string | null;
```

Events:

```ts
update: [payload: ReportStatusUpdatePayload]
```

Behavior:

- If no allowed statuses exist, show a clear terminal-state message.
- Require note for `resolved` and `rejected`.
- Use `StatusPill` labels for status choices.
- Use `AppTextarea` for note.
- Render a real submit button only when the update can be sent.

### New Component: `ReportWorkflowHistory.vue`

Add:

```text
frontend/src/components/reports/ReportWorkflowHistory.vue
```

Purpose:

- Show real backend workflow events.

Props:

```ts
events: ReportWorkflowEvent[];
```

Behavior:

- Sort events by `created_at` ascending.
- Show `from_status -> to_status` where `from_status` exists.
- Show initial creation event when `from_status` is null.
- Show note if present.
- Show actor label and timestamp.
- Show empty state only if backend returns no events.

### Existing Timeline Component

Modify:

```text
frontend/src/components/reports/ReportWorkflowTimeline.vue
```

Updates:

- Keep current status timeline behavior.
- Add optional compact mode if needed for dashboard density.
- Do not make timeline event history. Use `ReportWorkflowHistory` for that.

## Citizen Tracking Page

Modify:

```text
frontend/src/pages/citizen/ReportStatusPage.vue
```

New behavior:

- Fetch `GET /api/v1/reports/:id` on mount.
- Show loading state while fetching.
- Show `404` not-found state if report is missing.
- Show real category, status, source, submitted time, updated time, and coordinates.
- Show resolution note or rejection reason when present.
- Show `ReportWorkflowTimeline` using real current status.
- Show `ReportWorkflowHistory` using real backend events.
- Provide a refresh button that refetches the same report ID.

No-stub rule:

- Do not show "live status" unless the detail endpoint succeeds.
- Do not show fake events if backend returns none.
- Do not invent estimated completion dates.
- Do not imply the citizen can edit or escalate the report in FE-6.

## Dashboard Page Integration

Modify:

```text
frontend/src/pages/dashboard/DashboardPage.vue
```

Required behavior:

- Keep current fetch/list/filter/map behavior.
- When selected report changes, ensure detail panel can fetch the selected report detail.
- After a status update succeeds, list metrics, queue status pill, map marker ring, and detail panel must all reflect the updated backend status.
- Refresh should call `GET /api/v1/reports` and preserve selected report if it still exists.

## Report Queue Updates

Modify only if needed:

```text
frontend/src/components/dashboard/ReportQueue.vue
```

Possible FE-6 updates:

- Add small updated-status feedback if list rows receive changed status.
- Keep row selection keyboard-accessible.
- Do not add inline status mutation inside the queue; status changes belong in detail panel to keep confirmation and notes clear.

## Workflow Copy

Use language like:

```text
Status updated after backend confirmation.
```

```text
Add a short municipal note before closing this report.
```

```text
This tracking page shows the current backend status for your report.
```

Avoid language like:

```text
Assigned to field team
```

unless assignment is actually persisted.

Avoid:

```text
Estimated completion
```

unless an ETA field exists.

## Files To Add

```text
frontend/src/components/reports/ReportStatusActions.vue
frontend/src/components/reports/ReportWorkflowHistory.vue
```

Optional if transition logic becomes large:

```text
frontend/src/utils/reportWorkflow.ts
backend/app/services/report_workflow.py
```

## Files To Modify

Frontend only:

```text
frontend/src/api/reports.ts
frontend/src/stores/reports.ts
frontend/src/types/report.ts
frontend/src/components/dashboard/ReportDetailPanel.vue
frontend/src/components/reports/ReportWorkflowTimeline.vue
frontend/src/pages/citizen/ReportStatusPage.vue
frontend/src/pages/dashboard/DashboardPage.vue
```

Optional frontend test files only if a frontend test runner is introduced. The current repo does not have one.

## Verification Plan

Frontend command:

```bash
cd frontend
npm run build
```

Integrated local run:

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Manual end-to-end flow:

1. Open `/report`.
2. Submit a report with valid category and coordinates.
3. Confirm navigation to `/report/status/:id`.
4. Confirm tracking page fetches real report detail.
5. Open `/dashboard`.
6. Select the submitted report.
7. Confirm detail panel fetches real report detail.
8. Attempt to move status from `new` to `verified`.
9. If backend endpoints are not implemented yet, confirm the UI shows a recoverable backend-contract error and does not change local status.
10. If backend endpoints are implemented later, confirm dashboard queue, metrics, map marker status ring, and detail panel update after backend confirmation.
11. Try a close-status action without a note and confirm frontend validation blocks it before calling the backend.
12. Refresh `/report/status/:id`.
13. If backend detail exists, confirm citizen tracking page shows real status and workflow history.
14. If backend detail is pending, confirm citizen tracking page explains the tracking endpoint is not connected yet.

API verification examples:

```bash
curl -s http://127.0.0.1:8000/api/v1/reports
```

```bash
curl -s http://127.0.0.1:8000/api/v1/reports/<report-id>
```

```bash
curl -s -X PATCH http://127.0.0.1:8000/api/v1/reports/<report-id>/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"verified","note":"Municipal intake reviewed the report."}'
```

Expected behavior with one report moved to resolved:

- `GET /api/v1/reports` returns the report with `status: "resolved"`.
- `GET /api/v1/reports/:id` returns `workflow_events` with creation and status update events.
- Dashboard metrics count the report under resolved.
- Citizen tracking page shows the real resolved status.
- Resolution note is visible.

## Data Integrity Rules

Allowed:

- Real status changes after backend confirmation.
- Real workflow events created by backend.
- Real citizen tracking fetched from report detail endpoint.
- Deterministic allowed-next-status UI from current backend status.
- In-memory workflow storage for FE-6, if documented as local MVP behavior.

Not allowed:

- Frontend-only status changes.
- Fake workflow events.
- Fake actor names that imply authenticated staff.
- Fake department assignments.
- Fake resolution notes.
- Fake citizen notifications.
- Fake live tracking if the detail endpoint fails.
- Fake ETA or SLA status.

## Accessibility Requirements

FE-6 must include:

- Labels for status controls.
- Labels for note textarea.
- Status conveyed by text, not color only.
- Workflow history readable in chronological order.
- Loading and error states that are visible and understandable.
- Keyboard-operable status selection and submit.
- Clear disabled states for invalid transitions.
- Citizen tracking page that does not require map interaction.

## Responsive Requirements

Test at:

- 360px mobile width.
- 768px tablet width.
- 1280px desktop width.

Expected behavior:

- Status action controls stack cleanly on mobile.
- Workflow history remains readable on mobile.
- Dashboard detail panel does not overflow with long tracking IDs or notes.
- Citizen tracking page remains usable as a single-column mobile view.
- Buttons and status controls have comfortable touch targets.

## Implementation Sequence

1. Add frontend report detail and workflow event types.
2. Add `getReport` and `updateReportStatus` API functions targeting the future backend routes.
3. Add frontend status transition utility for UX-level allowed actions.
4. Expand reports store with detail fetch and status update actions.
5. Add `ReportStatusActions`.
6. Add `ReportWorkflowHistory`.
7. Update `ReportDetailPanel` to fetch detail when possible and update status only through backend calls.
8. Update `ReportStatusPage` to fetch real report detail when possible and show a clear unavailable state otherwise.
9. Keep dashboard map/list synchronized after successful status updates.
10. Run frontend build.
11. Run integrated manual workflow against the current backend and confirm missing endpoints fail honestly.

## Risks And Mitigations

Risk: In-memory backend data disappears during demo.

Mitigation:

- FE-6 should not solve persistence. Demo rehearsal must avoid backend restarts after submitting reports until the backend phase adds persistence.

Risk: Status mutation controls create unrealistic municipal authority without authentication.

Mitigation:

- Label actor as `Prishtina municipal staff` and keep auth out of scope for hackathon MVP. Do not show individual staff names.

Risk: Workflow becomes too complex for hackathon timing.

Mitigation:

- Use a fixed transition map and one optional/required note field. Avoid assignments, SLA, internal comments, and notifications in FE-6.

Risk: Citizen tracking implies real-time updates.

Mitigation:

- Use explicit refresh behavior. Do not claim live push updates.

Risk: Frontend and backend status rules drift.

Mitigation:

- Keep the canonical transition map in backend. Frontend can mirror it for UX, but backend remains authoritative and returns `409` for invalid transitions.

## FE-6 Acceptance Criteria

FE-6 frontend work is complete when:

- `npm run build` passes for frontend.
- Frontend defines typed contracts for `GET /api/v1/reports/:id` and `PATCH /api/v1/reports/:id/status`.
- Dashboard detail panel attempts status updates only through the backend API.
- Dashboard status actions show allowed transitions and require notes for `resolved` and `rejected`.
- Missing backend endpoints show recoverable, honest errors.
- Frontend does not mutate local status when the backend update fails.
- Dashboard queue, metrics, map marker styling, and detail panel reflect updated status after backend confirmation once the backend endpoint exists.
- `/report/status/:id` attempts to fetch backend report detail.
- Citizen tracking page shows real workflow timeline and event history only when returned by backend.
- No fake status mutation, fake workflow events, fake actor identities, fake ETA, or fake citizen notifications are introduced.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to persistence scope, transition rules, citizen tracking behavior, resolution-note requirements, or authentication assumptions should be agreed before coding.
