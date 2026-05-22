# FE-0 Frontend Foundation Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-0: Frontend Foundation**.

FE-0 is not about building the final product flows yet. It is about creating a stable, professional frontend foundation so the team can implement citizen reporting, municipal dashboard, maps, and AI Street Audit features without reworking the base structure.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Stabilize the Vue/Vite frontend base so multiple teammates can work independently with consistent routes, layouts, design tokens, shared UI primitives, typed API handling, and responsive structure.

Primary outcome:

> After FE-0, the frontend should feel like a real product shell with reusable building blocks, not placeholder pages. Future phases should build inside this foundation instead of replacing it.

## Non-Goals

FE-0 will not implement:

- Full citizen report submission flow
- Real image upload flow
- AI image analysis UI
- Map provider integration
- Ticket status mutation workflow
- Authentication
- Final municipal dashboard data model
- Street Audit scan execution

These belong to later phases.

FE-0 will implement the structure needed for those phases without pretending the functionality exists.

## Current State

Existing frontend files:

- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/AppShell.vue`
- `frontend/src/pages/HomePage.vue`
- `frontend/src/pages/citizen/CitizenReportPage.vue`
- `frontend/src/pages/dashboard/DashboardPage.vue`
- `frontend/src/pages/audit/AuditPage.vue`
- `frontend/src/api/client.ts`
- `frontend/src/api/reports.ts`
- `frontend/src/stores/reports.ts`
- `frontend/src/types/report.ts`
- `frontend/src/composables/useGeolocation.ts`
- `frontend/src/styles/main.css`
- `frontend/src/vite-env.d.ts`

Current limitation:

- Pages exist but are mostly route ownership placeholders.
- Styling exists but is not tokenized.
- Shared UI primitives do not exist yet.
- API client has only a basic `GET` helper.
- Error/loading states are not standardized.
- Layout does not yet separate citizen and dashboard needs.

## FE-0 Deliverables

FE-0 will deliver:

- Confirmed route structure
- Tokenized theme foundation
- Shared layout system
- Shared UI primitives
- Typed API client foundation
- Basic frontend state conventions
- Responsive navigation shell
- Base page upgrades using real reusable primitives
- Frontend coding conventions documented in the code structure

## Route Map

FE-0 will define the frontend routes that later phases will fill.

Routes to keep active:

```text
/              Home and product entry
/report        Citizen report entry
/dashboard     Municipality dashboard entry
/audit         AI Street Audit entry
```

Routes to reserve for later phases:

```text
/report/confirm
/report/status/:id
/dashboard/reports/:id
/dashboard/analytics
/audit/:runId
/audit/suggestions/:suggestionId
```

FE-0 implementation rule:

- Active routes should render usable product-shell pages.
- Reserved routes should not be linked as if complete.
- No route should imply working functionality that is not implemented yet.

## File Structure Changes

FE-0 should evolve the frontend structure to:

```text
frontend/src/
├── api/
│   ├── client.ts
│   └── reports.ts
├── components/
│   ├── common/
│   │   ├── AppBadge.vue
│   │   ├── AppButton.vue
│   │   ├── AppCard.vue
│   │   ├── AppEmptyState.vue
│   │   ├── AppField.vue
│   │   ├── AppInput.vue
│   │   ├── AppLoading.vue
│   │   └── AppSectionHeader.vue
│   └── navigation/
│       └── PrimaryNav.vue
├── composables/
│   ├── useAsyncState.ts
│   └── useGeolocation.ts
├── layouts/
│   ├── AppShell.vue
│   ├── CitizenLayout.vue
│   └── DashboardLayout.vue
├── pages/
│   ├── HomePage.vue
│   ├── citizen/
│   │   └── CitizenReportPage.vue
│   ├── dashboard/
│   │   └── DashboardPage.vue
│   └── audit/
│       └── AuditPage.vue
├── router/
│   └── index.ts
├── stores/
│   ├── reports.ts
│   └── ui.ts
├── styles/
│   ├── main.css
│   ├── tokens.css
│   └── utilities.css
└── types/
    ├── api.ts
    ├── report.ts
    └── ui.ts
```

## Design Foundation

FE-0 should implement the first version of the visual system from the frontend blueprint.

Design target:

- Premium but practical
- Calm municipal trust
- Warm but operational
- Not over-designed
- Not minimalist or empty

Token files:

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/styles/main.css`

Required token groups:

- Color
- Typography
- Spacing
- Radius
- Shadow
- Border
- Status colors
- Severity colors
- Z-index basics

Approved initial palette:

```css
--color-ink: #17211a;
--color-municipal-green: #2f5d50;
--color-sage-surface: #dde8d5;
--color-warm-stone: #f4efe4;
--color-paper: #fffdf7;
--color-road-graphite: #3a3f3b;
--color-amber-signal: #d9902f;
--color-repair-red: #c84c3a;
--color-resolved-blue: #3f6e8c;
--color-muted-line: #d7d0c2;
```

Surface rules:

- App background uses warm stone and subtle civic gradient.
- Cards use paper surfaces with soft borders.
- Shadows are subtle and functional.
- Primary actions use municipal green or ink depending on context.
- Severity colors are reserved for issue urgency.

Typography rules:

- Use a clean sans-serif stack for now.
- Keep headings strong and compact.
- Keep dashboard labels readable.
- Avoid tiny metadata text that becomes illegible on laptops during demo.

## Shared Components

### `AppButton.vue`

Purpose:

- Standardize buttons and links.

Props:

- `variant`: `primary | secondary | ghost | danger`
- `size`: `sm | md | lg`
- `type`: native button type
- `disabled`: boolean

Behavior:

- Renders a native button.
- Supports slot content.
- Does not perform routing by itself.

Acceptance:

- Keyboard focus is visible.
- Disabled state is clear.
- Variants are visually distinct but restrained.

### `AppCard.vue`

Purpose:

- Standardize panel/card surfaces.

Props:

- `variant`: `default | elevated | muted`
- `interactive`: boolean

Behavior:

- Provides consistent border, radius, background, and spacing.
- Interactive state only changes visual treatment; it does not attach click behavior.

Acceptance:

- Cards work in homepage, report, dashboard, and audit pages.

### `AppBadge.vue`

Purpose:

- Standardize status, severity, category, and source labels.

Props:

- `tone`: `neutral | success | warning | danger | info | ai`
- `size`: `sm | md`

Behavior:

- Slot-based label.
- Visual styles support future report and audit states.

Acceptance:

- Badges remain readable on paper and muted surfaces.

### `AppInput.vue`

Purpose:

- Standardize text input styling.

Props:

- `modelValue`
- `placeholder`
- `type`
- `disabled`
- `ariaLabel`

Events:

- `update:modelValue`

Acceptance:

- Works with `v-model`.
- Has visible focus state.

### `AppField.vue`

Purpose:

- Standardize label, helper text, and error text around inputs.

Props:

- `label`
- `helper`
- `error`
- `for`

Acceptance:

- Keeps form layout consistent for later citizen report forms.

### `AppEmptyState.vue`

Purpose:

- Standardize empty or not-yet-available states without looking broken.

Props:

- `title`
- `description`
- `actionLabel`

Events:

- `action`

Acceptance:

- Clearly says what is missing or what happens next.
- Does not fake data.

### `AppLoading.vue`

Purpose:

- Standardize loading indicators.

Props:

- `label`
- `variant`: `spinner | skeleton`

Acceptance:

- Loading state is calm and not playful.

### `AppSectionHeader.vue`

Purpose:

- Standardize page and section headers.

Props:

- `eyebrow`
- `title`
- `description`

Acceptance:

- Used across Home, Citizen Report, Dashboard, and Audit pages.

### `PrimaryNav.vue`

Purpose:

- Own top-level navigation.

Links:

- Home
- Report
- Dashboard
- Street Audit

Acceptance:

- Active route is visually indicated.
- Mobile wrapping works cleanly.
- Navigation does not link to unfinished reserved routes.

## Layouts

### `AppShell.vue`

Purpose:

- Global app background and navigation shell.

Responsibilities:

- Render `PrimaryNav`
- Render main content region
- Apply global shell spacing

### `CitizenLayout.vue`

Purpose:

- Layout for mobile-first citizen flows.

Responsibilities:

- Narrower content width
- Guided single-column structure
- Clear next-action area

### `DashboardLayout.vue`

Purpose:

- Layout for municipality and audit surfaces.

Responsibilities:

- Wider content area
- Header + panel grid support
- Space for future map/table split views

## API Foundation

Current `api/client.ts` should be upgraded from a `GET` helper into a typed request utility.

Required API types:

```ts
export interface ApiErrorBody {
  detail?: string;
  message?: string;
}

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody | unknown;
}

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
}
```

Required functions:

- `apiRequest<T>(path, options)`
- `apiGet<T>(path)`
- `apiPost<TResponse, TPayload>(path, payload)`
- `apiPatch<TResponse, TPayload>(path, payload)`

Rules:

- JSON requests set `Content-Type: application/json`.
- Failed responses throw `ApiError`.
- Empty responses are handled safely.
- API base URL stays controlled by `VITE_API_BASE_URL`.

Acceptance:

- Existing `listReports()` still works.
- Future phases can add API modules without rewriting the client.

## State Foundation

### `stores/ui.ts`

Purpose:

- Shared non-business UI state.

State:

- `sidebarOpen`
- `demoMode`

Actions:

- `toggleSidebar`
- `setDemoMode`

### `stores/reports.ts`

FE-0 should keep this lightweight.

Responsibilities:

- Own report list state shape.
- Do not create fake reports in the store.
- Later phases will add fetching and mutation actions.

## Composables

### `useAsyncState.ts`

Purpose:

- Standardize loading/error/data patterns.

Return:

- `isLoading`
- `error`
- `run`
- `reset`

Acceptance:

- Works with any async callback.
- Does not swallow errors silently.

### `useGeolocation.ts`

Existing composable should remain.

FE-0 changes:

- Keep the current location helper.
- Do not build full report location flow yet.
- Future FE-2 will integrate this into report submission.

## Page Updates

FE-0 should upgrade current pages to use the new layout and components.

### Home Page

Purpose:

- Introduce product clearly.
- Route users to citizen report, dashboard, and audit surfaces.

Content:

- KoStreet positioning
- Prishtina municipal focus
- Three product surface cards:
  - Citizen reporting
  - Municipality dashboard
  - AI Street Audit
- Clear primary action to dashboard or report

No fake claims:

- Do not claim AI is already detecting real issues.
- Use phrasing such as "AI Street Audit workspace" instead of "live AI scan" until implemented.

### Citizen Report Page

Purpose:

- Establish the future report flow area.

Content:

- Page header
- Foundation card explaining upcoming capture flow
- Static checklist of future report steps
- No fake upload behavior

### Dashboard Page

Purpose:

- Establish municipal command center area.

Content:

- Page header
- Empty state for report queue if no data exists
- Summary card placeholders only if clearly labeled as "ready for live data"
- No fake metrics unless demo mode is explicitly introduced in FE-7

### Audit Page

Purpose:

- Establish AI Street Audit review area.

Content:

- Page header
- Explanation of human verification
- Empty state for audit runs
- No fake scan results

## No-Stub Rule For FE-0

FE-0 may include:

- Empty states
- "Ready for data" panels
- Documentation of future flows
- Reserved route definitions if not linked as complete

FE-0 may not include:

- Fake working upload buttons
- Fake AI detections
- Fake municipal metrics
- Buttons that appear to submit or mutate data but do nothing
- Placeholder text like "Lorem ipsum"
- Console-only interactions presented as product behavior

If a control is not functional yet, either:

- Do not render it, or
- Render it as disabled with explicit copy explaining what phase will activate it.

## Accessibility Requirements

FE-0 must include:

- Semantic landmarks
- Visible focus states
- Buttons for actions, links for navigation
- Sufficient contrast for text and badges
- Inputs with labels where inputs are introduced
- `aria-live` or clear text for loading/error states where applicable

## Responsive Requirements

Minimum viewport targets:

- Mobile: 360px width
- Tablet: 768px width
- Desktop: 1280px width

FE-0 behavior:

- Navigation wraps cleanly on mobile.
- Cards stack on mobile.
- Dashboard shell has enough width for future table/map layout.
- No horizontal page overflow.

## Implementation Sequence

1. Create token and utility CSS files.
2. Refactor `main.css` to import tokens and utilities.
3. Add common components.
4. Add `PrimaryNav`.
5. Refactor `AppShell`.
6. Add `CitizenLayout` and `DashboardLayout`.
7. Upgrade API client and API types.
8. Add `useAsyncState`.
9. Add `ui` store.
10. Refactor pages to use the foundation.
11. Run build verification.
12. Review visual output manually in browser.

## Files To Add

```text
frontend/src/components/common/AppBadge.vue
frontend/src/components/common/AppButton.vue
frontend/src/components/common/AppCard.vue
frontend/src/components/common/AppEmptyState.vue
frontend/src/components/common/AppField.vue
frontend/src/components/common/AppInput.vue
frontend/src/components/common/AppLoading.vue
frontend/src/components/common/AppSectionHeader.vue
frontend/src/components/navigation/PrimaryNav.vue
frontend/src/composables/useAsyncState.ts
frontend/src/layouts/CitizenLayout.vue
frontend/src/layouts/DashboardLayout.vue
frontend/src/stores/ui.ts
frontend/src/styles/tokens.css
frontend/src/styles/utilities.css
frontend/src/types/api.ts
frontend/src/types/ui.ts
```

## Files To Modify

```text
frontend/src/api/client.ts
frontend/src/api/reports.ts
frontend/src/layouts/AppShell.vue
frontend/src/pages/HomePage.vue
frontend/src/pages/citizen/CitizenReportPage.vue
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/pages/audit/AuditPage.vue
frontend/src/router/index.ts
frontend/src/stores/reports.ts
frontend/src/styles/main.css
```

## Verification Plan

Required commands:

```bash
cd frontend
npm run build
```

Manual browser checks:

```bash
cd frontend
npm run dev
```

Check:

- `/`
- `/report`
- `/dashboard`
- `/audit`

Manual acceptance checklist:

- Navigation works.
- Active navigation state is visible.
- Layout works on mobile width.
- Layout works on desktop width.
- Empty states look intentional.
- Buttons, badges, cards, and section headers are visually consistent.
- No fake working controls are present.
- No console errors appear during normal navigation.

## Risks And Mitigations

Risk: Overbuilding FE-0 and delaying product features.

Mitigation:

- Keep FE-0 focused on reusable foundation only.
- Do not build final dashboard, map, upload, or AI flows.

Risk: Design system becomes too generic.

Mitigation:

- Use KoStreet-specific palette and civic surface treatment from the frontend blueprint.
- Use Prishtina and municipal command center language in page content.

Risk: Team creates duplicate UI patterns later.

Mitigation:

- Add shared primitives now.
- Use shared primitives in all FE-0 pages.

Risk: Pages look like placeholders.

Mitigation:

- Use meaningful empty states and "ready for data" language.
- Avoid fake data and lorem ipsum.

## FE-0 Acceptance Criteria

FE-0 is complete when:

- `npm run build` passes.
- All active routes render without errors.
- The frontend has a clean shell, navigation, and responsive structure.
- Shared UI primitives exist and are used by current pages.
- API client has typed error handling and request helpers.
- Design tokens exist and match the approved visual direction.
- Empty states communicate future functionality honestly.
- No fake product behavior is introduced.

## Approval Gate

If this blueprint is approved, the implementation should proceed exactly in the implementation sequence above.

Any change to route structure, visual direction, or FE-0 scope should be agreed before coding.

