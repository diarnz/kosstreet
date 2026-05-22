# FE-3 Municipality Dashboard Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-3: Municipality Dashboard**.

FE-0 created the frontend foundation. FE-1 created the visual system. FE-2 created real citizen report submission. FE-3 turns submitted reports into a municipality-first operational dashboard for Prishtina.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Build a functional municipal dashboard that helps a municipality understand, filter, inspect, and triage incoming civic issue reports.

Primary outcome:

> After FE-3, Prishtina municipal users should be able to open `/dashboard`, fetch real reports from `GET /api/v1/reports`, understand operational state in under 10 seconds, filter/search the queue, inspect report details, and clearly distinguish citizen reports from AI Street Audit suggestions when such data exists.

## Critical Backend Reality Check

Current backend endpoints:

```text
GET /api/v1/reports
POST /api/v1/reports
```

Current backend does **not** yet provide:

- `GET /api/v1/reports/:id`
- `PATCH /api/v1/reports/:id/status`
- Department assignment endpoint
- Resolution note endpoint
- Server-side filtering/search
- Persistent storage beyond current backend implementation
- Map/geospatial endpoint

Therefore FE-3 should implement:

- Real report list fetching from `GET /api/v1/reports`
- Real dashboard metrics computed from fetched reports
- Real client-side filtering and search over fetched reports
- Real selected report detail using the fetched report object
- Read-only workflow/status display
- Honest copy where status mutation is not available yet

FE-3 should **not** implement fake status changes, fake departments, fake report details, or fake map markers.

## Non-Goals

FE-3 will not implement:

- Map provider integration
- Real marker rendering
- Ticket status mutation
- Department assignment mutation
- Resolution notes
- Authentication
- AI Street Audit execution
- Server-side pagination
- Server-side filtering

These belong to later backend/frontend phases.

## User Flow

Municipality dashboard flow:

```text
/dashboard
  ↓
Fetch real reports from GET /api/v1/reports
  ↓
Compute metrics from fetched reports
  ↓
Render report queue
  ↓
Municipal user filters/searches reports
  ↓
Municipal user selects a report
  ↓
Dashboard shows report detail panel from loaded data
```

Optional detail route:

```text
/dashboard/reports/:id
```

Implementation decision:

- Prefer keeping details inside `/dashboard` as a selected side panel for FE-3.
- Add `/dashboard/reports/:id` only if it can be supported from loaded report state without pretending a backend detail endpoint exists.
- If direct URL detail is implemented and the report is not in the loaded list, show a recoverable “report not found in current queue” state.

## Dashboard Information Architecture

The dashboard should have four functional areas.

### 1. Header And Operating Summary

Purpose:

- Tell municipal users what they are looking at.
- Make the Prishtina focus clear.

Content:

- Page title
- Short description
- Data freshness/status indicator
- Refresh action

No-stub rule:

- Refresh must call `GET /api/v1/reports`.
- Do not show fake “last synced” timestamps unless derived from actual fetch time.

### 2. Metrics

Purpose:

- Let a municipality understand state quickly.

Metrics computed from real fetched reports:

- Total reports
- New reports
- In progress reports
- Resolved reports
- AI-suggested reports
- Citizen reports

Rules:

- Metrics must be computed only from fetched backend data.
- If there are no reports, show zeros and an empty state.
- Do not use seeded or fake counts in FE-3.

### 3. Report Queue

Purpose:

- List incoming and existing reports for review.

Fields:

- Category
- Status
- Source
- Confidence if present
- Coordinates
- Created time
- Description preview if present

Interactions:

- Select report
- Search
- Filter by status
- Filter by category
- Filter by source
- Clear filters
- Refresh data

Rules:

- Search/filter must operate on real fetched reports.
- Empty filtered state should explain that no reports match current filters.
- No fake rows.

### 4. Report Detail Panel

Purpose:

- Inspect a selected report.

Fields:

- Tracking ID
- Category
- Status
- Source
- Coordinates
- Confidence if present
- Created time
- Description
- Department routing suggestion derived locally from category
- Workflow timeline as read-only

Department routing suggestions:

- Pothole -> Roads/Public Works
- Garbage -> Sanitation
- Broken streetlight -> Electrical/Infrastructure
- Blocked sidewalk -> Urban Maintenance
- Damaged sign -> Public Works
- Other -> Municipal Intake Review

Rules:

- Department suggestion is allowed because it is deterministic business logic from category.
- It must be labeled as “Suggested department”.
- Do not imply the assignment was saved to backend.
- No status mutation controls until backend supports `PATCH`.

## Screens And Routes

### `/dashboard`

Primary FE-3 screen.

Build:

- Fetch reports on page load.
- Show loading state.
- Show recoverable error state.
- Show metrics.
- Show filter/search controls.
- Show queue.
- Show selected report detail panel.
- Show map placeholder clearly reserved for FE-4.

Acceptance:

- Dashboard works with zero reports.
- Dashboard works with one report.
- Dashboard works with multiple reports.
- Dashboard remains readable on mobile.

### `/dashboard/reports/:id`

Optional for FE-3.

If implemented:

- Load report list.
- Find report by ID from loaded list.
- Show detail if found.
- Show “not found in current queue” if not found.

If not implemented:

- Keep detail inside `/dashboard` only and defer route to backend detail endpoint phase.

Recommended FE-3 decision:

- Do not implement a separate detail route yet. Use an in-page detail panel to avoid pretending there is a dedicated backend detail endpoint.

## Components To Add

```text
frontend/src/components/dashboard/DashboardFilters.vue
frontend/src/components/dashboard/DashboardMetrics.vue
frontend/src/components/dashboard/ReportQueue.vue
frontend/src/components/dashboard/ReportDetailPanel.vue
frontend/src/components/dashboard/ReportSourceBadge.vue
frontend/src/components/dashboard/DepartmentSuggestion.vue
```

### `DashboardFilters.vue`

Purpose:

- Own search and filter controls.

Props:

- `search`
- `status`
- `category`
- `source`

Events:

- `update:search`
- `update:status`
- `update:category`
- `update:source`
- `clear`

Controls:

- Search input
- Status select
- Category select
- Source select
- Clear filters button

Acceptance:

- Filters are real and affect the queue.
- Clear button resets filters.
- No disabled fake controls.

### `DashboardMetrics.vue`

Purpose:

- Render computed operational metrics.

Props:

- `reports`

Metrics:

- Total
- New
- In Progress
- Resolved
- Citizen
- AI-suggested

Acceptance:

- All values derive from real `reports`.
- Zero state is displayed honestly.

### `ReportQueue.vue`

Purpose:

- Render selectable list/table of fetched reports.

Props:

- `reports`
- `selectedReportId`
- `isLoading`

Events:

- `select`

Acceptance:

- Shows loading state while fetching.
- Shows empty state when no reports exist.
- Shows filtered empty state when filters produce no results.
- Selection is keyboard-accessible.

### `ReportDetailPanel.vue`

Purpose:

- Render selected report details.

Props:

- `report`

Acceptance:

- Shows prompt when no report is selected.
- Shows read-only report details when selected.
- Does not show fake mutation controls.

### `ReportSourceBadge.vue`

Purpose:

- Standardize source display.

Props:

- `source`: `citizen | street_audit`

Acceptance:

- Citizen and AI Street Audit sources are visually distinct.

### `DepartmentSuggestion.vue`

Purpose:

- Show deterministic department routing suggestion from category.

Props:

- `category`

Acceptance:

- Suggestion is clearly labeled.
- Does not imply backend assignment.

## Files To Add

```text
frontend/src/components/dashboard/DashboardFilters.vue
frontend/src/components/dashboard/DashboardMetrics.vue
frontend/src/components/dashboard/ReportQueue.vue
frontend/src/components/dashboard/ReportDetailPanel.vue
frontend/src/components/dashboard/ReportSourceBadge.vue
frontend/src/components/dashboard/DepartmentSuggestion.vue
frontend/src/types/dashboard.ts
frontend/src/utils/reportRouting.ts
frontend/src/utils/reportFormatting.ts
```

## Files To Modify

```text
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/stores/reports.ts
frontend/src/api/reports.ts
frontend/src/types/report.ts
```

Optional:

```text
frontend/src/router/index.ts
```

Only modify router if adding `/dashboard/reports/:id`.

## Data Model

Current report shape:

```ts
export interface ReportSummary {
  id: string;
  category: IssueCategory;
  status: TicketStatus;
  latitude: number;
  longitude: number;
  source: 'citizen' | 'street_audit';
  confidence?: number;
  created_at: string;
}
```

Recommended FE-3 additions:

```ts
export type ReportSource = 'citizen' | 'street_audit';

export interface DashboardFiltersState {
  search: string;
  status: TicketStatus | 'all';
  category: IssueCategory | 'all';
  source: ReportSource | 'all';
}

export interface DashboardMetrics {
  total: number;
  new: number;
  inProgress: number;
  resolved: number;
  citizen: number;
  streetAudit: number;
}
```

## Report Store Updates

Current reports store is lightweight.

FE-3 should add:

- `reports`
- `selectedReportId`
- `isLoading`
- `error`
- `lastFetchedAt`
- `filters`

Actions:

- `fetchReports`
- `selectReport`
- `setFilters`
- `clearFilters`

Getters:

- `filteredReports`
- `selectedReport`
- `metrics`

Rules:

- Store must not seed fake reports.
- Store fetch action must call real `listReports`.
- Store errors must be visible in UI.

## Filtering And Search Logic

Search should match:

- Report ID
- Category label
- Status label
- Source label
- Description if present
- Coordinates as text

Filters:

- Status: all, new, verified, assigned, in progress, resolved, rejected
- Category: all MVP categories
- Source: all, citizen, street audit

Rules:

- Filtering is client-side in FE-3.
- Filtering operates only on fetched reports.
- Clear filters must restore the full fetched list.

## Metrics Logic

Metrics computed from fetched reports:

```ts
total = reports.length
new = reports.filter(status === 'new').length
inProgress = reports.filter(status === 'in_progress').length
resolved = reports.filter(status === 'resolved').length
citizen = reports.filter(source === 'citizen').length
streetAudit = reports.filter(source === 'street_audit').length
```

No fake counts.

## Map Placeholder

FE-3 should retain a map workspace placeholder but make it honest.

Allowed:

- Static panel labeled “Map integration in FE-4”
- Explanation that report coordinates are ready for map markers
- No marker visuals that imply real geospatial rendering

Not allowed:

- Fake map markers
- Fake heatmaps
- Fake clustering
- Fake selected marker behavior

## Status Workflow In FE-3

FE-3 should show workflow state read-only.

Allowed:

- Status badge
- Workflow timeline
- Copy explaining status mutation requires backend `PATCH`

Not allowed:

- Active buttons to change status
- Fake status mutation in frontend only
- Pretending assignment is saved

Status mutation belongs to a later phase after backend support exists.

## Error Handling

Dashboard should handle:

- Backend unavailable
- Empty report list
- Network error
- Malformed/unexpected response
- Filtered empty state

UX requirements:

- Show clear recoverable error.
- Provide retry action that calls real fetch.
- Do not clear existing reports until a successful refresh unless this is a deliberate loading state.

## No-Stub Rule For FE-3

Allowed:

- Real report fetch from backend
- Real client-side filters/search
- Real metrics from fetched reports
- Real selected report detail from fetched report data
- Honest map placeholder
- Read-only workflow/status display
- Deterministic department suggestion from category

Not allowed:

- Fake reports
- Fake metrics
- Fake map markers
- Fake status mutation
- Fake department assignment save
- Fake report detail fetch
- Fake AI suggestions
- Buttons that appear active but do nothing
- Console-only interactions
- Lorem ipsum

## Accessibility Requirements

FE-3 must include:

- Semantic headings
- Search input label
- Filter labels
- Keyboard-accessible report selection
- Button roles only for actions
- Links only for navigation
- Status conveyed with text, not color only
- Empty/error states announced with readable text

## Responsive Requirements

Test at:

- 360px mobile width
- 768px tablet width
- 1280px desktop width

Expected behavior:

- Metrics stack on mobile.
- Filters wrap cleanly.
- Report queue remains readable.
- Detail panel stacks below queue on mobile.
- Dashboard still communicates state quickly on laptop demo screens.

## Implementation Sequence

1. Add dashboard types.
2. Add report formatting utilities.
3. Add deterministic department routing utility.
4. Expand reports store with fetch, filters, metrics, and selection.
5. Add `ReportSourceBadge`.
6. Add `DepartmentSuggestion`.
7. Add `DashboardMetrics`.
8. Add `DashboardFilters`.
9. Add `ReportQueue`.
10. Add `ReportDetailPanel`.
11. Refactor `DashboardPage` to fetch real reports and compose dashboard.
12. Preserve honest FE-4 map placeholder.
13. Run frontend build.
14. Run backend and frontend together.
15. Submit at least one real report from FE-2 or API.
16. Confirm dashboard fetches, filters, metrics, and details from real data.

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
uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Manual dashboard flow:

1. Open `/dashboard`.
2. Confirm loading state appears if fetch is pending.
3. Confirm empty state if no reports exist.
4. Submit a real report from `/report` or API.
5. Refresh dashboard.
6. Confirm metrics update from real data.
7. Search by category/status/source/ID text.
8. Apply status/category/source filters.
9. Clear filters.
10. Select a report.
11. Confirm detail panel shows real report data.
12. Confirm map placeholder does not show fake markers.
13. Confirm there are no fake status mutation controls.

Expected dashboard behavior with one FE-2 pothole report:

- Total reports: 1
- New reports: 1
- Citizen reports: 1
- AI-suggested reports: 0
- Detail panel shows pothole category, new status, citizen source, coordinates, and suggested department Roads/Public Works.

## Risks And Mitigations

Risk: Dashboard looks empty if no backend reports exist.

Mitigation:

- Use a strong empty state and suggest creating a real report through `/report`.

Risk: Users expect status changes.

Mitigation:

- Show status read-only and explain backend mutation is not connected yet.

Risk: Client-side filters are mistaken for server filters.

Mitigation:

- No issue for MVP. Document that FE-3 filters fetched queue locally.

Risk: Map placeholder feels like unfinished work.

Mitigation:

- Present it as “Coordinates ready for FE-4 map integration” and keep it visually polished but honest.

## FE-3 Acceptance Criteria

FE-3 is complete when:

- `npm run build` passes.
- `/dashboard` fetches real reports from `GET /api/v1/reports`.
- Metrics are computed from real fetched reports.
- Search and filters operate on real fetched reports.
- Queue displays real reports only.
- Selecting a report shows a real detail panel.
- Dashboard clearly separates citizen and AI Street Audit sources when present.
- Map area remains an honest FE-4 placeholder with no fake markers.
- No fake status mutation, fake assignment, fake metrics, or fake report data is introduced.
- Errors and empty states are recoverable and clear.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to backend endpoint assumptions, separate detail route behavior, or status mutation scope should be agreed before coding.

