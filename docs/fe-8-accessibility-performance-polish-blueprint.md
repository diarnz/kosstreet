# FE-8 Accessibility, Performance, And Polish Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-8: Accessibility, Performance, And Polish**.

FE-0 through FE-7 built the frontend foundation, visual system, citizen reporting, municipal dashboard, map experience, AI Street Audit interface, workflow transparency contract, and pitch mode. FE-8 is the final frontend quality pass before handoff to backend/AI work and hackathon rehearsal.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Make the current frontend demo-ready, accessible enough for a hackathon prototype, responsive across expected devices, and stable under common failure states.

Primary outcome:

> After FE-8, KoStreet should be a polished frontend product surface that can be confidently shown in a 3-minute pitch, with no broken routes, no incoherent layout overflow, clear focus states, readable copy, reliable pitch mode, and a passing production build.

## Current-State Reality Check

Current frontend capabilities:

- Vue/Vite/TypeScript frontend builds with `npm run build`.
- Active routes exist for:
  - `/`
  - `/report`
  - `/report/status/:id`
  - `/dashboard`
  - `/audit`
  - `/audit/:runId`
  - `/audit/suggestions/:suggestionId`
- FE-7 pitch mode exists through nav toggle and query params.
- Demo reports and audit data are labeled and fallback-only.
- Leaflet map is integrated and dashboard remains usable when data is empty.
- Workflow status controls call future backend endpoints and fail honestly.

Current constraints:

- No frontend test runner is configured.
- No Playwright or axe accessibility tooling is installed.
- PowerShell may block `npm.ps1`, so Windows verification may require `cmd /c npm run build`.
- Backend detail/status endpoints are still future-contract endpoints.
- AI suggestion endpoints are still future-contract endpoints.

FE-8 should not introduce a large testing framework unless the team explicitly approves extra dependency work. The default FE-8 path should use build verification plus manual route/accessibility/responsive checks.

## Non-Goals

FE-8 will not implement:

- Backend endpoints.
- AI inference.
- Image upload/storage.
- Authentication.
- New feature phases.
- New visual redesign.
- New map provider.
- Automated end-to-end test framework, unless separately approved.
- Full WCAG audit certification.

FE-8 is a polish and readiness phase, not a product expansion phase.

## Quality Targets

FE-8 should verify and improve:

- Accessibility basics.
- Keyboard navigation.
- Visible focus states.
- Route resilience.
- Responsive layouts.
- Copy clarity.
- Empty/error states.
- Pitch mode clarity.
- Build stability.
- Basic runtime performance.
- Demo rehearsal readiness.

## Accessibility Scope

### Keyboard Navigation

Required checks:

- `Tab` reaches primary navigation links and Pitch Mode toggle.
- `Tab` reaches report form controls in logical order.
- Category selector is keyboard-operable.
- Dashboard filters are keyboard-operable.
- Report queue items are keyboard-operable buttons.
- Audit run queue items are keyboard-operable buttons.
- Status update controls are keyboard-operable.
- Focus does not get trapped inside map or scroll panels.

Implementation fixes if needed:

- Add missing `aria-label` to iconless/action buttons.
- Add `type="button"` to non-submit buttons where missing.
- Ensure custom radio/button groups have understandable labels.
- Ensure disabled controls still have nearby explanatory text.

### Focus States

Current global focus behavior:

```text
frontend/src/styles/main.css
```

FE-8 should verify:

- Focus ring is visible on buttons, links, inputs, textareas, report queue items, and audit queue items.
- Focus ring is not clipped by overflow containers.
- Focus ring has enough contrast against warm/paper backgrounds.

Allowed changes:

- Adjust `--shadow-focus` if contrast is weak.
- Add local `outline-offset` or `box-shadow` fixes for components with clipped focus.

### Semantic Structure

Required checks:

- Each route has a clear top-level heading through `AppSectionHeader`.
- No route skips from `h1`-style page heading directly into confusing nested structure.
- Dashboard metric sections have `aria-label`.
- Map has an accessible label and is not the only way to access report detail.
- Loading states use readable text.
- Error states use readable text and retry actions where possible.

### Forms

Required checks:

- Report description textarea has an accessible label.
- Manual latitude and longitude inputs have accessible labels.
- Audit form fields have accessible labels.
- Status note textarea has an accessible label.
- Validation messages are near the relevant control.
- Required/blocked actions are explained in text, not only disabled.

### Color And Meaning

Required checks:

- Status meaning is text + color, never color only.
- Severity and demo labels include text.
- Pitch Mode banner uses text that explains data source.
- AI demo suggestions are labeled as demo scenarios.
- Error states use text labels, not just red styling.

## Responsive Scope

FE-8 must check these viewport widths:

```text
360px mobile
768px tablet
1280px desktop/laptop
```

Routes to check:

```text
/
/report
/report/status/demo-report-pothole-001?demo=1
/dashboard?demo=1
/audit?demo=1
/audit/demo-audit-run-001?demo=1
/audit/suggestions/demo-suggestion-pothole-001?demo=1
```

Required behavior:

- No horizontal page overflow.
- Navigation wraps without covering content.
- Pitch Mode banner does not dominate mobile screens.
- Report form remains single-column and readable.
- Dashboard metrics wrap cleanly.
- Dashboard filters wrap cleanly.
- Map remains usable and does not collapse.
- Queue and detail panels stack cleanly on mobile/tablet.
- Audit form and audit detail stack cleanly.
- Demo suggestion cards stack cleanly.
- Long report IDs and notes wrap instead of overflowing.

Implementation fixes if needed:

- Add `min-width: 0` to grid children that overflow.
- Add `overflow-wrap: anywhere` to ID/note containers.
- Reduce excessive padding on mobile.
- Adjust grid breakpoints where panels become cramped.

## Performance Scope

FE-8 should keep performance practical for a hackathon demo.

Required checks:

- `npm run build` passes.
- Production bundle does not grow unexpectedly from FE-8 changes.
- No repeated API fetch loops after route changes.
- No repeated Leaflet map reinitialization loops.
- Demo fixture data remains small and static.
- Pitch mode does not trigger unnecessary backend calls beyond existing page fetch behavior.

Current build output should be used as a baseline from the latest successful build.

Allowed optimizations:

- Remove duplicated computed work if obvious.
- Avoid adding new dependencies.
- Avoid expensive watchers.
- Keep demo fixtures static.

Not required:

- Code splitting.
- Lazy route loading.
- Bundle analyzer setup.
- Advanced performance profiling.

## Route Resilience

FE-8 should validate behavior when:

- Backend is running and returns empty lists.
- Backend is unavailable.
- Pitch Mode is enabled.
- Pitch Mode is disabled.
- Report detail endpoint is unavailable.
- Status mutation endpoint is unavailable.
- Audit suggestion endpoint is unavailable.
- Map tiles partially fail.

Expected behavior:

- Pages do not crash.
- Empty states are intentional.
- Errors are recoverable.
- Pitch mode fallback is clearly labeled.
- No frontend-only backend mutation is shown as success.

## Copy Polish

FE-8 should tighten visible copy for:

- Empty states.
- Backend unavailable states.
- Pitch Mode labels.
- Demo AI suggestion labels.
- Citizen tracking unavailable state.
- Status update errors.
- Map fallback copy.
- Audit suggestion unavailable copy.

Copy rules:

- Use short direct sentences.
- Avoid apologetic or uncertain language where the app is behaving correctly.
- Avoid overclaiming AI.
- Avoid saying "live" for demo fixtures.
- Avoid "coming soon" where a specific backend contract exists.

Preferred examples:

```text
Backend workflow endpoint is not connected yet. The report status was not changed.
```

```text
Pitch Mode is showing prepared demo records because live backend data is empty.
```

```text
Real AI suggestions will appear after the backend suggestion endpoint is connected.
```

## Pitch Mode QA

FE-8 must verify FE-7 behavior:

- Nav toggle enables/disables Pitch Mode.
- `?demo=1` enables Pitch Mode.
- `?demo=0` disables Pitch Mode.
- Pitch Mode persists across refresh.
- Dashboard demo fallback appears only when expected.
- Audit demo fallback appears only when expected.
- Citizen tracking demo detail appears only for matching demo IDs.
- Demo labels are visible on dashboard reports, audit runs, AI suggestions, and pitch banner.
- Demo records do not pretend to persist workflow changes.

## Final Demo Path

FE-8 should document and verify the exact 3-minute route:

1. Open `/`.
2. Enable Pitch Mode.
3. Open `/report` and show citizen submission shape.
4. Open `/dashboard`.
5. Select the pothole demo report.
6. Show metrics, queue, detail, workflow, and map marker.
7. Show that status update is backend-contract-aware and does not fake persistence.
8. Open `/audit`.
9. Show demo AI suggestion scenarios and human-review framing.
10. Open `/report/status/demo-report-pothole-001`.
11. Close on detect, verify, route, resolve, and measure.

Target:

```text
Under 3 minutes without broken screens or empty critical surfaces.
```

## Documentation Updates

Add:

```text
docs/fe-8-accessibility-performance-polish-blueprint.md
```

Modify:

```text
docs/frontend-style-guide.md
docs/demo-script.md
```

Recommended updates:

- Add Pitch Mode rules to style guide.
- Add final demo path to demo script.
- Add a short manual QA checklist to demo script or a new section in this blueprint.

Do not modify README unless the team wants the pitch-mode instructions visible at top level.

## Implementation Scope

FE-8 should be implemented as focused fixes discovered by inspection and manual verification.

Likely files to modify:

```text
frontend/src/styles/main.css
frontend/src/styles/utilities.css
frontend/src/components/navigation/PrimaryNav.vue
frontend/src/components/common/PitchModeBanner.vue
frontend/src/components/reports/IssueCategorySelector.vue
frontend/src/components/reports/ReportStatusActions.vue
frontend/src/components/dashboard/ReportQueue.vue
frontend/src/components/dashboard/ReportDetailPanel.vue
frontend/src/components/audit/AuditRunQueue.vue
frontend/src/components/audit/DemoAuditSuggestionCard.vue
frontend/src/components/maps/ReportMap.vue
frontend/src/pages/HomePage.vue
frontend/src/pages/citizen/CitizenReportPage.vue
frontend/src/pages/citizen/ReportStatusPage.vue
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/pages/audit/AuditPage.vue
docs/frontend-style-guide.md
docs/demo-script.md
```

Only modify files where a concrete issue is found. FE-8 should not churn every page.

## Verification Plan

Required command:

```bash
cd frontend
npm run build
```

Windows fallback:

```bash
cd frontend
cmd /c npm run build
```

Manual route checks:

```text
/
/report
/report/status/demo-report-pothole-001?demo=1
/dashboard?demo=1
/audit?demo=1
/audit/demo-audit-run-001?demo=1
/audit/suggestions/demo-suggestion-pothole-001?demo=1
```

Manual viewport checks:

```text
360px
768px
1280px
```

Manual keyboard checks:

```text
Tab
Shift+Tab
Enter
Space
Arrow keys where radio-style selection is used
```

Manual backend-state checks:

- Backend unavailable.
- Backend available with empty reports.
- Backend available with at least one submitted report.
- Pitch Mode off.
- Pitch Mode on.

## Acceptance Criteria

FE-8 is complete when:

- `npm run build` passes.
- All active routes render without runtime errors.
- No route has obvious horizontal overflow at 360px, 768px, or 1280px.
- Primary navigation and Pitch Mode toggle are keyboard accessible.
- Citizen report flow is keyboard usable.
- Dashboard filters, report queue, and detail actions are keyboard usable.
- Audit form, audit queue, and demo suggestion surfaces are keyboard usable.
- Focus states are visible and not clipped.
- Status, category, source, severity, demo, and error meaning is conveyed with text.
- Pitch Mode labels are clear and visible.
- Backend unavailable states are readable and recoverable.
- Demo fixtures are never presented as live backend data.
- Status update failures do not appear successful.
- AI demo suggestions do not imply live inference.
- Final demo path can be completed under 3 minutes.
- `docs/demo-script.md` reflects the final demo path.
- `docs/frontend-style-guide.md` reflects Pitch Mode/demo labeling rules.

## Risks And Mitigations

Risk: FE-8 turns into a visual redesign.

Mitigation:

- Only fix concrete accessibility, responsiveness, copy, and demo-readiness issues. Preserve the established visual system.

Risk: Manual QA misses regressions.

Mitigation:

- Use a written route/viewport/keyboard checklist and run it after changes.

Risk: New dependencies slow the team down.

Mitigation:

- Do not add test or accessibility tooling by default. Use manual checks unless the team explicitly approves dependency additions.

Risk: Pitch Mode labels become visually noisy.

Mitigation:

- Keep labels compact but present. Every demo surface needs clear data-source labeling, but labels should not dominate the workflow.

Risk: The frontend looks complete but backend endpoints are still pending.

Mitigation:

- Keep backend-contract errors honest and visible. Do not hide missing backend endpoints behind fake success states.

## Approval Gate

If this blueprint is approved, implementation should proceed as a focused final frontend polish pass.

Any change to adding automated test dependencies, changing the visual system, hiding Pitch Mode labels, or expanding scope beyond frontend polish should be agreed before coding.
