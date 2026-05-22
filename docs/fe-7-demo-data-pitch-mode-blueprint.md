# FE-7 Demo Data And Pitch Mode Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-7: Demo Data And Pitch Mode**.

FE-0 created the frontend foundation. FE-1 established the visual system. FE-2 created real citizen report submission. FE-3 created the real municipal dashboard. FE-4 added real map/geospatial visualization. FE-5 added AI Street Audit run management. FE-6 prepared the frontend workflow and transparency surface against the future backend workflow contract. FE-7 makes the frontend reliable for a live hackathon demo without hiding backend, AI, map, or imagery limitations.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Build a controlled frontend pitch mode that makes the KoStreet demo reliable, repeatable, and judge-ready:

- The app can tell the complete KoStreet story even when backend data is empty.
- Demo data is explicit, labeled, and never confused with live backend records.
- The dashboard, map, citizen tracking, and AI Street Audit surfaces remain visually complete during judging.
- The pitch path can be completed in under 3 minutes.
- Backend-connected behavior remains available and preferred when real data exists.
- External service failures do not leave the app with empty or broken-looking screens.

Primary outcome:

> After FE-7, KoStreet should support a polished pitch-mode route through citizen reporting, municipal dashboard triage, map visualization, workflow transparency, and AI Street Audit positioning, while clearly distinguishing demo fixtures from live backend data.

## Current-State Reality Check

Current frontend capabilities:

- `/report` submits real structured reports to `POST /api/v1/reports`.
- `/report/status/:id` attempts `GET /api/v1/reports/:id` and explains when the backend detail endpoint is unavailable.
- `/dashboard` fetches real reports from `GET /api/v1/reports`.
- `/dashboard` computes metrics from reports currently in the report store.
- `/dashboard` renders real Leaflet markers from report coordinates.
- `/dashboard` attempts future workflow endpoints from FE-6 without faking success.
- `/audit` fetches and creates real audit runs through `GET/POST /api/v1/audit-runs`.
- `/audit` does not render fake AI detections because suggestion endpoints do not exist yet.
- `stores/ui.ts` already contains `demoMode`, but it is not wired into product behavior.

Current limitations:

- Backend report data is in-memory and may be empty after restart.
- Backend report detail and status mutation endpoints are not implemented yet.
- Backend audit suggestion endpoints are not implemented yet.
- No AI suggestion data is currently returned to the frontend.
- The demo route is still not finalized in docs.
- `scripts/seed_demo_data.py` intentionally does not seed concrete route data yet.

FE-7 should solve demo reliability from the frontend side only. It should not implement backend persistence, AI inference, image upload, or backend seeding.

## Non-Goals

FE-7 will not implement:

- Backend persistence.
- Backend seed endpoints.
- Backend workflow endpoints.
- Backend audit suggestion endpoints.
- AI inference or fake model calls.
- Street View imagery retrieval.
- Image upload/storage.
- Authentication.
- Real notifications.
- Production analytics.
- New map provider.

These belong to backend, AI, or later production phases.

## Demo Mode Principle

FE-7 is allowed to introduce demo data because FE-7 explicitly exists for demo reliability. The key rule is that demo data must be clearly represented as demo fixtures.

Allowed:

- Static frontend fixture reports labeled as `Demo`.
- Static frontend fixture audit runs labeled as `Demo`.
- Static frontend fixture AI suggestions labeled as `Demo scenario`.
- Pitch-mode banners that explain the app is showing prepared demo records.
- Demo route labels for Prishtina.
- Fallback state when backend returns an empty list or is unavailable.
- Local-only demo workflow history, but only inside demo mode and labeled as demo history.

Not allowed:

- Showing demo data without a demo label.
- Mixing demo records into live backend state without distinction.
- Sending demo fixture records to backend automatically.
- Pretending demo AI suggestions came from a real model endpoint.
- Pretending demo status changes were persisted to backend.
- Showing real Street View or third-party imagery unless legally approved.
- Fake progress bars that imply active scanning.

## Product Positioning For FE-7

Pitch mode should communicate:

- KoStreet works as a citizen reporting product.
- KoStreet gives municipalities a command center.
- Location and map context are central.
- Ticket workflow transparency is part of the civic loop.
- AI Street Audit is the standout proactive layer, currently represented by clearly labeled demo scenarios until backend/AI suggestion endpoints are connected.

Pitch mode should not overclaim:

- It should not say AI detected issues live unless a backend endpoint returns real detections.
- It should not say imagery was scanned unless actual imagery was processed.
- It should not claim backend persistence if using frontend fixtures.

## Demo Data Model

Add dedicated frontend fixture files:

```text
frontend/src/demo/demoReports.ts
frontend/src/demo/demoAuditRuns.ts
frontend/src/demo/demoAuditSuggestions.ts
frontend/src/demo/demoScenario.ts
```

### Demo Reports

`demoReports.ts` should export a typed list of `ReportDetail` records.

Demo reports must include:

- One pothole report.
- One garbage or illegal dumping report.
- One broken streetlight report.
- One blocked sidewalk report.
- One damaged sign report.
- One `street_audit` source report or AI-suggested converted-ticket scenario if the current types can represent it honestly.

Recommended Prishtina coordinate area:

```text
Default center: 42.6629, 21.1655
```

Rules:

- Use realistic but generic Prishtina-facing descriptions.
- Avoid naming specific private people or sensitive addresses.
- Use public-street style labels only when they are generic or already part of the demo script.
- Use fixed timestamps for deterministic display.
- Include `workflow_events` only in `ReportDetail` demo records.
- Use `confidence` only for `street_audit` or AI-assisted demo records, not ordinary citizen records unless the scenario clearly labels it as demo AI assistance.

### Demo Audit Runs

`demoAuditRuns.ts` should export typed `AuditRunSummary` records.

Demo audit run coverage:

- One completed demo audit run for a recognizable Prishtina corridor.
- One queued or running demo audit run to show operational state.
- One failed or unavailable run only if it helps explain resilience; otherwise avoid adding noise.

Rules:

- Label route names as demo routes.
- Do not imply live scanning.
- Keep statuses consistent with the available `AuditRunStatus` type.

### Demo Audit Suggestions

`demoAuditSuggestions.ts` should use the future-contract `AuditSuggestion` type from `frontend/src/types/detection.ts`.

Demo suggestions should include:

- At least one pothole suggestion.
- At least one garbage suggestion.
- At least one damaged-sign or blocked-sidewalk suggestion.

Rules:

- Every suggestion must be visually labeled as `Demo scenario`.
- Do not include real image URLs unless legally approved.
- If no legally approved image exists, use a no-image evidence panel rather than a fake image.
- Use confidence values only as scenario values and label them as demo values.

### Demo Scenario

`demoScenario.ts` should export centralized pitch metadata:

```ts
export const demoScenario = {
  enabledLabel: 'Pitch Mode',
  municipality: 'Prishtina',
  routeName: 'Prishtina civic corridor demo',
  durationTarget: '3 minutes',
  disclaimer: 'Demo records are frontend fixtures for judging reliability.',
};
```

## Demo Mode Activation

Use the existing `ui` store.

Modify:

```text
frontend/src/stores/ui.ts
```

Required behavior:

- Keep `demoMode`.
- Add persistence in `localStorage` so refreshes preserve pitch mode during rehearsal.
- Add `toggleDemoMode`.
- Add `hydrateDemoMode`.
- Default should be off unless a query parameter enables it.

Activation options:

```text
?demo=1
```

Route behavior:

- If URL contains `?demo=1`, enable demo mode and store it.
- If URL contains `?demo=0`, disable demo mode and store it.
- If no query param exists, use stored preference.

No-stub rule:

- Demo mode must be a real state toggle used by dashboard/audit/tracking surfaces.
- It must not be a visual-only switch that changes nothing.

## Demo Data Integration Strategy

The frontend should prefer real backend data when available, then use demo fixtures only when appropriate.

### Reports Store

Modify:

```text
frontend/src/stores/reports.ts
```

Add derived behavior:

- `hasLiveReports`
- `visibleReports`
- `visibleReportDetailsById`
- `visibleSelectedReport`
- `visibleSelectedReportDetail`
- `usingDemoReports`

Rules:

- If `demoMode` is off, show only live backend reports.
- If `demoMode` is on and backend returns reports, default to live reports plus a clear option to switch to demo fixtures only if needed.
- If `demoMode` is on and backend returns empty or fails, show demo reports with a visible pitch-mode banner.
- Demo reports must not be written into `reports` as if they came from the backend unless the store has an explicit source marker.

Recommended simpler implementation:

- Keep `reports` for backend data only.
- Add getters that return demo fixtures when `demoMode` is enabled and `reports.length === 0`.
- Keep a source flag such as `reportDataMode: 'live' | 'demo'`.
- Update dashboard components to consume visible getter data.

### Audit Runs Store

Modify:

```text
frontend/src/stores/auditRuns.ts
```

Add derived behavior:

- `visibleRuns`
- `visibleSelectedRun`
- `usingDemoRuns`
- `runDataMode: 'live' | 'demo'`

Rules:

- If demo mode is off, use backend audit runs only.
- If demo mode is on and backend returns empty or fails, show demo audit runs.
- Creating a real audit run still calls the backend. Do not create fake runs from the form when backend fails.

### Audit Suggestions

Current backend does not expose suggestions. FE-7 may add a frontend-only demo suggestion panel, but only inside demo mode and only with explicit labeling.

Allowed implementation:

- Add a demo suggestion review panel to `/audit` when `demoMode` is on.
- Use `demoAuditSuggestions`.
- Label the section `Demo AI suggestion scenarios`.
- Include copy that real suggestions will come from `GET /api/v1/audit-runs/:id/suggestions`.

Not allowed:

- Showing demo suggestions when demo mode is off.
- Adding active accept/reject/convert controls that pretend to persist.
- Rendering fake image evidence as if it came from Street View.

## Pitch Mode UI

### Global Pitch Banner

Add:

```text
frontend/src/components/common/PitchModeBanner.vue
```

Purpose:

- Make demo mode explicit across product surfaces.

Props:

```ts
dataMode?: 'live' | 'demo' | 'mixed';
message?: string;
```

Behavior:

- Shows when `uiStore.demoMode` is enabled.
- Indicates whether current page is using live backend data or demo fixtures.
- Provides a disable action.
- Stays compact and does not dominate the interface.

### Demo Mode Toggle

Modify:

```text
frontend/src/components/navigation/PrimaryNav.vue
```

Add:

- A compact `Pitch Mode` toggle.
- Visible only in development or always visible with restrained styling, depending on team preference.
- If always visible, label it clearly and keep it out of primary user actions.

Recommended FE-7 decision:

- Always visible during hackathon development because the judges/demo team need quick recovery.
- Use `AppBadge` plus a small button-style toggle.

### Home Page

Modify:

```text
frontend/src/pages/HomePage.vue
```

Add:

- A pitch-mode entry action when demo mode is enabled.
- A concise demo path panel: Report -> Dashboard -> Audit -> Tracking.
- Do not turn homepage into a marketing page.

### Dashboard Page

Modify:

```text
frontend/src/pages/dashboard/DashboardPage.vue
```

Required behavior:

- Use visible report data from store, not raw backend-only reports.
- Show `PitchModeBanner` when demo fixtures are being used.
- Metrics, filters, queue, detail, and map must all operate on the same visible dataset.
- Map markers must be generated from visible report data and labeled as demo when appropriate.
- Status update controls should remain disabled or backend-contract-only for demo fixtures. Do not let demo records pretend to PATCH.

### Citizen Tracking Page

Modify:

```text
frontend/src/pages/citizen/ReportStatusPage.vue
```

Required behavior:

- If backend detail exists, show live backend detail.
- If backend detail fails and demo mode is enabled, show a matching demo report only if the tracking ID matches a demo record or a known demo tracking ID.
- Clearly label demo tracking details as demo.
- If no matching demo report exists, keep the current endpoint-pending state.

### Audit Page

Modify:

```text
frontend/src/pages/audit/AuditPage.vue
```

Required behavior:

- Use visible audit run data from store.
- Show demo audit runs only in demo mode fallback.
- Add a demo suggestion scenario panel only in demo mode.
- Keep real audit run creation form connected to backend only.
- Do not fake scan progress.

## Components To Add

```text
frontend/src/components/common/PitchModeBanner.vue
frontend/src/components/audit/DemoAuditSuggestionPanel.vue
frontend/src/components/audit/DemoAuditSuggestionCard.vue
```

Optional:

```text
frontend/src/components/common/DataModeBadge.vue
frontend/src/components/common/PitchPathPanel.vue
```

Only add optional components if they reduce duplication.

## Types To Add Or Extend

Add:

```text
frontend/src/types/demo.ts
```

Recommended types:

```ts
export type DataMode = 'live' | 'demo' | 'mixed';

export interface DemoDatasetMeta {
  id: string;
  label: string;
  description: string;
  municipality: string;
  routeName: string;
}
```

Extend existing stores with data-mode getters rather than changing backend API types.

## Demo Fixture Files

Add:

```text
frontend/src/demo/demoScenario.ts
frontend/src/demo/demoReports.ts
frontend/src/demo/demoAuditRuns.ts
frontend/src/demo/demoAuditSuggestions.ts
```

Rules:

- Fixture IDs should be stable and recognizable, such as `demo-report-pothole-001`.
- Coordinates should be valid and clustered around Prishtina.
- Use deterministic timestamps.
- Descriptions should be short and judge-readable.
- Demo data must not contain private personal data.
- Demo data must not include restricted imagery URLs.

## Visual And Copy Rules

Use copy like:

```text
Pitch Mode is showing prepared demo records because live backend data is empty.
```

```text
Demo AI suggestion scenario. Real suggestions will appear after the backend suggestion endpoint is connected.
```

```text
This marker comes from a frontend demo fixture for judging reliability.
```

Avoid copy like:

```text
AI detected this live.
```

```text
Street View scan completed.
```

```text
Municipality resolved this.
```

unless the backend or real workflow data supports the statement.

## File Changes

Files to add:

```text
docs/fe-7-demo-data-pitch-mode-blueprint.md
frontend/src/components/common/PitchModeBanner.vue
frontend/src/components/audit/DemoAuditSuggestionPanel.vue
frontend/src/components/audit/DemoAuditSuggestionCard.vue
frontend/src/demo/demoScenario.ts
frontend/src/demo/demoReports.ts
frontend/src/demo/demoAuditRuns.ts
frontend/src/demo/demoAuditSuggestions.ts
frontend/src/types/demo.ts
```

Files to modify:

```text
frontend/src/main.ts
frontend/src/router/index.ts
frontend/src/stores/ui.ts
frontend/src/stores/reports.ts
frontend/src/stores/auditRuns.ts
frontend/src/components/navigation/PrimaryNav.vue
frontend/src/pages/HomePage.vue
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/pages/citizen/ReportStatusPage.vue
frontend/src/pages/audit/AuditPage.vue
frontend/src/components/dashboard/ReportDetailPanel.vue
frontend/src/components/maps/ReportMap.vue
frontend/src/components/maps/ReportMapPopup.vue
frontend/src/components/dashboard/ReportQueue.vue
```

Modify map/queue/detail components only where needed to display demo labels and consume visible data.

## Route And Query Behavior

Routes stay unchanged:

```text
/
/report
/report/status/:id
/dashboard
/audit
/audit/:runId
/audit/suggestions/:suggestionId
```

Query params:

```text
?demo=1
?demo=0
```

Rules:

- `?demo=1` enables demo mode.
- `?demo=0` disables demo mode.
- Query param should be processed once per navigation.
- Stored preference should persist across refreshes.
- Demo mode should not alter API base URL.

## Implementation Sequence

1. Add demo types.
2. Add demo scenario metadata.
3. Add demo report fixtures.
4. Add demo audit run fixtures.
5. Add demo audit suggestion fixtures.
6. Update `ui` store with localStorage-backed demo mode and toggle behavior.
7. Add route query handling for `?demo=1` and `?demo=0`.
8. Add `PitchModeBanner`.
9. Add visible-data getters to reports store.
10. Add visible-data getters to audit runs store.
11. Update dashboard page to consume visible reports.
12. Update dashboard components to label demo records where needed.
13. Update map popup and marker context to label demo records where needed.
14. Update citizen tracking page to optionally show matching demo detail in demo mode.
15. Add demo audit suggestion components.
16. Update audit page to show demo audit suggestions in demo mode only.
17. Update navigation with pitch mode toggle.
18. Update homepage with pitch path panel or demo entry.
19. Run frontend build.
20. Rehearse the 3-minute demo path.

## Verification Plan

Required command:

```bash
cd frontend
npm run build
```

Use `cmd /c npm run build` on Windows if PowerShell blocks `npm.ps1`.

Manual checks with backend running:

1. Open `/`.
2. Enable pitch mode through the nav toggle.
3. Confirm pitch banner appears.
4. Open `/dashboard`.
5. If backend report list is empty, confirm demo reports appear and are labeled.
6. Confirm dashboard metrics derive from visible demo reports.
7. Confirm filters/search work on demo reports.
8. Confirm map markers render for demo reports.
9. Confirm selecting a demo marker selects the matching demo report.
10. Confirm status update controls do not pretend to persist for demo records.
11. Open `/audit`.
12. Confirm demo audit runs appear only when pitch mode is enabled and live runs are empty.
13. Confirm demo AI suggestion scenarios appear only in pitch mode and are clearly labeled.
14. Open `/report/status/demo-report-pothole-001`.
15. Confirm demo tracking data appears only in pitch mode.
16. Disable pitch mode.
17. Confirm demo fixtures disappear and live backend/empty states return.

Manual checks with backend unavailable:

1. Open `/dashboard?demo=1`.
2. Confirm demo reports appear with a backend-unavailable explanation.
3. Confirm dashboard, map, queue, and detail remain usable.
4. Open `/audit?demo=1`.
5. Confirm demo audit data and suggestion scenarios appear.
6. Confirm no page crashes because backend is unavailable.

Demo timing check:

1. Start on `/`.
2. Show citizen report flow briefly.
3. Open `/dashboard?demo=1`.
4. Select pothole and garbage demo reports.
5. Show map marker synchronization.
6. Open `/audit`.
7. Show demo AI suggestion scenario.
8. Open tracking page for a demo report.
9. Finish under 3 minutes.

## Acceptance Criteria

FE-7 is complete when:

- `npm run build` passes.
- Demo mode can be enabled and disabled from the UI.
- `?demo=1` and `?demo=0` work.
- Demo mode state persists across refreshes.
- Dashboard can show demo reports when live backend data is empty or unavailable.
- Dashboard clearly labels demo data as demo data.
- Dashboard metrics, filters, queue, detail, and map operate on the same visible demo dataset.
- Audit page can show demo audit runs when live backend data is empty or unavailable.
- Audit page can show demo AI suggestion scenarios only in pitch mode.
- Citizen tracking page can show a matching demo report only in pitch mode.
- No demo data is shown as live backend truth.
- No fake backend mutation, AI inference, scan progress, image evidence, or persisted workflow state is introduced.
- The app remains presentable if backend, AI, or map tiles fail.
- The pitch path can be rehearsed in under 3 minutes.

## Risks And Mitigations

Risk: Demo data undermines the no-fake-data rule.

Mitigation:

- Demo mode is explicit, opt-in, and visually labeled across affected surfaces. Live mode remains the default.

Risk: Team forgets whether they are looking at live or demo data.

Mitigation:

- Add persistent `PitchModeBanner` and data-mode labels on dashboard/audit surfaces.

Risk: Demo fixtures drift from backend types.

Mitigation:

- Type fixtures with existing `ReportDetail`, `AuditRunSummary`, and future `AuditSuggestion` types.

Risk: Demo mode hides real backend failures.

Mitigation:

- Show backend-unavailable copy when fallback data is used. Do not silently replace live data.

Risk: Judges ask whether AI suggestions are real.

Mitigation:

- Label them as demo scenarios and explain that real suggestions connect through the planned backend suggestion endpoint.

Risk: Demo mode adds complexity before FE-8 polish.

Mitigation:

- Keep pitch mode scoped to fixture fallback, banner, and demo panels. Avoid broad routing or visual redesign.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to whether demo data is allowed, whether demo fixtures can appear alongside live data, whether demo AI suggestions should be shown, or whether demo mode should be visible to judges should be agreed before coding.
