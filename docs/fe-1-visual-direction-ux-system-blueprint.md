# FE-1 Visual Direction And UX System Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-1: Visual Direction And UX System**.

FE-0 created the frontend foundation: routes, layouts, shared primitives, API helpers, basic tokens, and honest empty states. FE-1 turns that foundation into a polished, coherent visual system that feels premium, functional, municipal, and pleasant without looking over-designed.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Create a distinctive frontend design language for KoStreet that supports:

- Citizen reporting
- Municipality dashboard work
- AI Street Audit review
- Future maps, tickets, and analytics

Primary outcome:

> After FE-1, KoStreet should look and feel like a serious municipal technology product with clear hierarchy, restrained premium styling, strong status semantics, and reusable visual patterns ready for the next product phases.

## FE-1 Design North Star

KoStreet should feel:

- Premium but practical
- Calm, civic, and competent
- Warm but operational
- Designed, but not theatrical
- Data-ready, but not dense too early
- Friendly for citizens and trustworthy for municipalities

KoStreet should not feel:

- Like a generic admin dashboard
- Like a plain white SaaS template
- Like a flashy AI landing page
- Like a government form from the past
- Like minimalism hiding unfinished work
- Like visual effects are more important than triage and action

## Non-Goals

FE-1 will not implement:

- Real report submission
- Real image upload
- Real AI analysis
- Real map provider integration
- Real dashboard metrics from backend data
- Ticket status mutation
- Audit run execution
- Authentication

FE-1 is a visual and UX system phase. It should improve the interface quality without pretending unavailable product functionality exists.

## Current State After FE-0

Existing FE-0 assets:

- Tokenized CSS base
- Global utilities
- `AppShell`
- `CitizenLayout`
- `DashboardLayout`
- `PrimaryNav`
- Shared components:
  - `AppBadge`
  - `AppButton`
  - `AppCard`
  - `AppEmptyState`
  - `AppField`
  - `AppInput`
  - `AppLoading`
  - `AppSectionHeader`
- Active pages:
  - `/`
  - `/report`
  - `/dashboard`
  - `/audit`
- Typed API helper foundation
- UI store
- Async state composable

Current FE-1 opportunities:

- Token system needs richer semantic tokens.
- Badge tones need status, severity, source, and category semantics.
- Button and card variants need refinement for future dashboard density.
- Empty/loading/error states need consistent tone and hierarchy.
- Homepage should feel more intentionally premium.
- Dashboard and audit pages should feel more like operational workspaces.
- Citizen page should feel guided and trustworthy.
- Navigation should feel more polished and stable across screen sizes.

## FE-1 Deliverables

FE-1 will deliver:

- Expanded design tokens
- Status, severity, source, and category visual systems
- Refined component variants
- Better page composition and visual hierarchy
- Reusable visual patterns for future phases
- A lightweight frontend style guide page or section
- Premium-but-functional UI polish across active routes
- Build and local route verification

## Visual System Strategy

### Core Theme

Theme name:

```text
Prishtina Civic Warmth
```

Theme principle:

> Use warm civic surfaces, deep municipal greens, infrastructure graphite, and restrained signal colors to make KoStreet feel trustworthy, modern, and operational.

### Palette Expansion

FE-0 introduced base colors. FE-1 should expand them into semantic tokens.

Required base tokens:

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

Required semantic tokens:

```css
--surface-app;
--surface-panel;
--surface-panel-strong;
--surface-muted;
--surface-inset;
--surface-map-placeholder;

--text-primary;
--text-secondary;
--text-muted;
--text-inverse;

--action-primary;
--action-primary-hover;
--action-secondary;
--action-danger;

--status-new;
--status-verified;
--status-assigned;
--status-in-progress;
--status-resolved;
--status-rejected;

--severity-low;
--severity-medium;
--severity-high;
--severity-critical;

--source-citizen;
--source-ai-audit;
```

Palette rules:

- Use warm stone and sage as app-level surfaces.
- Use paper for panels and cards.
- Use municipal green for trust and primary actions.
- Use amber only for attention and medium severity.
- Use red only for errors, high severity, rejected, and urgent states.
- Use resolved blue for verified/resolved municipal clarity.
- Avoid large saturated blocks.
- Avoid pure white as a full-page background.

## Status, Severity, Source, And Category Systems

FE-1 should introduce reusable visual semantics now, before the dashboard and report flows become complex.

### Status System

Statuses:

- New
- Verified
- Assigned
- In Progress
- Resolved
- Rejected

Visual rules:

- New: neutral outline, calm and pending
- Verified: blue/green, trusted
- Assigned: municipal green, active ownership
- In Progress: amber, work underway
- Resolved: deep green or resolved blue, completed
- Rejected: muted red, not alarming unless paired with an error

Implementation target:

- Extend `AppBadge` to support semantic status tones or add helper mapping utilities.
- Do not hardcode report status styles inside page files.

### Severity System

Severities:

- Low
- Medium
- High
- Critical

Visual rules:

- Low: sage/green
- Medium: amber
- High: repair red
- Critical: deeper red, rare, high contrast

Implementation target:

- Add badge support for severity tones.
- Add CSS tokens for severity surfaces, borders, and text.

### Source System

Sources:

- Citizen
- AI Street Audit

Visual rules:

- Citizen: green/trust tone
- AI Street Audit: distinct AI audit tone, not neon, not magical

Implementation target:

- Add source badge helpers or examples.
- AI labels must communicate reviewability, not certainty.

### Category System

Issue categories:

- Pothole
- Garbage or illegal dumping
- Broken streetlight
- Blocked sidewalk
- Damaged sign
- Other

Visual rules:

- Pothole: graphite/road tone
- Garbage: green/cleanup tone
- Broken streetlight: amber/electrical tone
- Blocked sidewalk: blue/urban mobility tone
- Damaged sign: red/orange infrastructure tone
- Other: neutral tone

Implementation target:

- Add category tone support to `AppBadge` or central mapping utilities.
- Category colors should be scannable but not visually chaotic.

## Component Updates

### `AppBadge.vue`

FE-1 changes:

- Add more semantic tone support.
- Preserve existing simple usage.
- Ensure badges work in dense dashboard rows.

Recommended tones:

```ts
'neutral'
'success'
'warning'
'danger'
'info'
'ai'
'status-new'
'status-verified'
'status-assigned'
'status-in-progress'
'status-resolved'
'status-rejected'
'severity-low'
'severity-medium'
'severity-high'
'severity-critical'
'category-pothole'
'category-garbage'
'category-broken-streetlight'
'category-blocked-sidewalk'
'category-damaged-sign'
'category-other'
```

Acceptance:

- Badges remain readable at small size.
- Status colors are distinguishable.
- Category colors are useful but restrained.

### `AppButton.vue`

FE-1 changes:

- Refine hover, active, and disabled states.
- Add optional full-width support if needed.
- Ensure primary/secondary/ghost/danger have clear hierarchy.

Acceptance:

- Primary buttons are visually clear without being loud.
- Secondary buttons work well inside cards and page actions.
- Danger buttons do not appear unless a real destructive action exists.

### `AppCard.vue`

FE-1 changes:

- Add header/body/footer slots if needed.
- Add variants suitable for:
  - default panels
  - elevated hero cards
  - muted readiness panels
  - inset operational panels

Recommended variants:

```ts
'default'
'elevated'
'muted'
'inset'
'command'
```

Acceptance:

- Cards support homepage, citizen flow, dashboard, and audit pages.
- Cards do not rely on one-off page CSS for base surface quality.

### `AppEmptyState.vue`

FE-1 changes:

- Add tone support:
  - neutral
  - report
  - dashboard
  - audit
- Improve visual marker to feel intentional.

Acceptance:

- Empty states look designed, not like missing content.
- Copy remains honest about unavailable functionality.

### `AppLoading.vue`

FE-1 changes:

- Refine spinner and skeleton styling.
- Add calm loading tone.

Acceptance:

- Loading is visible but not playful.

### `AppSectionHeader.vue`

FE-1 changes:

- Add optional `align` or `size` prop if needed.
- Improve spacing and responsive typography.

Acceptance:

- Works across hero, dashboard, audit, and citizen pages.

### New Component: `StatusPill.vue`

Purpose:

- Standardize future report status display.

Props:

- `status`: `new | verified | assigned | in_progress | resolved | rejected`

Behavior:

- Maps status to label and badge tone.

Acceptance:

- No page-specific status label mapping.

### New Component: `IssueCategoryBadge.vue`

Purpose:

- Standardize issue category display.

Props:

- `category`: report issue category

Behavior:

- Maps category to label and badge tone.

Acceptance:

- Category labels are consistent across dashboard, report detail, and audit review.

### New Component: `MetricCard.vue`

Purpose:

- Provide dashboard-ready metric card styling without fake metrics.

Props:

- `label`
- `value`
- `description`
- `tone`

FE-1 usage rule:

- Use only with honest values such as "Ready" or "Awaiting data" unless real/demo data exists.

Acceptance:

- Later FE-3 can use the same component for real metrics.

### New Component: `FeaturePanel.vue`

Purpose:

- Standardize homepage and product-surface cards.

Props:

- `eyebrow`
- `title`
- `description`
- `tone`

Acceptance:

- Homepage no longer needs custom card markup for each product surface.

## Layout And Surface Updates

### `AppShell.vue`

FE-1 changes:

- Refine app background for premium warmth.
- Add less generic surface treatment.
- Preserve readability and performance.
- Avoid heavy effects.

Acceptance:

- Looks complete on `/`, `/report`, `/dashboard`, and `/audit`.
- No horizontal overflow on mobile.

### `PrimaryNav.vue`

FE-1 changes:

- Refine active state.
- Improve mobile wrapping.
- Add subtle trust-oriented styling.
- Keep links limited to active routes.

Acceptance:

- Active route is obvious but not loud.
- Navigation feels stable on small screens.

### `CitizenLayout.vue`

FE-1 changes:

- Improve guided flow feel.
- Add optional side note or progress visual area if needed.

Acceptance:

- `/report` feels intentionally mobile-first.

### `DashboardLayout.vue`

FE-1 changes:

- Improve command center feel.
- Add layout classes for future metric grid, map/table split, and side panels.

Acceptance:

- `/dashboard` and `/audit` feel like operational workspaces, not content pages.

## Page Updates

### Home Page

Goal:

- Make the product story feel premium and complete.

FE-1 updates:

- Upgrade hero composition.
- Replace repeated card markup with `FeaturePanel`.
- Add a restrained "municipal operating loop" section:
  - Detect
  - Verify
  - Route
  - Resolve
  - Measure
- Use badges and panels to show product surfaces.

No-stub rule:

- Do not claim live AI scanning is working.
- Do not show fake counts.

Acceptance:

- Homepage clearly communicates KoStreet in under 10 seconds.
- Visual system feels distinctive without being flashy.

### Citizen Report Page

Goal:

- Make the future citizen flow feel guided and trustworthy.

FE-1 updates:

- Add a staged flow panel:
  - Photo
  - Location
  - AI suggestion
  - Submit
- Add privacy/trust note.
- Keep upload/action controls disabled or absent until FE-2.

No-stub rule:

- No fake upload buttons.
- No fake submit button.

Acceptance:

- Page explains what will happen next without pretending functionality exists.

### Dashboard Page

Goal:

- Make the municipality dashboard feel like an operational command center.

FE-1 updates:

- Add metric-ready cards with honest "Awaiting live data" values.
- Add report queue empty state with improved visual treatment.
- Add future filter bar visual shell only if disabled and labeled as coming in FE-3.
- Add map panel placeholder that is clearly labeled for FE-4.

No-stub rule:

- No fake report counts.
- No fake map markers.
- No fake filters that look interactive.

Acceptance:

- Dashboard looks prepared for real data but does not fake data.

### Audit Page

Goal:

- Make AI Street Audit feel like a serious review workspace.

FE-1 updates:

- Add AI review principle panel:
  - Suggested, not automatic
  - Confidence shown
  - Human verified
  - Converted to municipal ticket
- Add audit run empty state.
- Add future suggestion card shell only if clearly labeled as "review model".

No-stub rule:

- No fake detections.
- No fake Street View imagery.
- No fake scan progress.

Acceptance:

- Judges would understand the AI interface philosophy even before FE-5.

## Style Guide Section

FE-1 should create a lightweight internal style guide for frontend contributors.

Recommended file:

```text
docs/frontend-style-guide.md
```

Contents:

- Palette
- Typography
- Status semantics
- Severity semantics
- Source semantics
- Category semantics
- Component usage rules
- Anti-patterns

Acceptance:

- Teammates can follow the visual rules without guessing.

## No-Stub Rule For FE-1

FE-1 may include:

- Honest empty states
- Disabled future controls if clearly labeled
- Style examples
- "Awaiting data" labels
- Visual shells for future map/report areas

FE-1 may not include:

- Fake reports
- Fake metrics
- Fake AI detections
- Fake map markers
- Fake upload/submit behavior
- Fake audit progress
- Lorem ipsum
- Buttons that appear active but do nothing

If a UI element represents future functionality:

- Label it clearly as upcoming, or
- Keep it disabled, or
- Do not render it.

## Accessibility Requirements

FE-1 must preserve and improve:

- Visible focus states
- Sufficient color contrast
- Semantic heading order
- Buttons vs links correctness
- Keyboard reachable navigation
- Text labels for status and severity, not color-only meaning
- No motion that causes distraction

## Responsive Requirements

FE-1 must test:

- 360px mobile width
- 768px tablet width
- 1280px desktop width

Expected behavior:

- Navigation wraps cleanly.
- Homepage cards stack on mobile.
- Citizen flow panels remain readable on mobile.
- Dashboard cards stack before becoming cramped.
- Audit panels stack cleanly below tablet width.

## Implementation Sequence

1. Expand `tokens.css` with semantic tokens.
2. Expand `utilities.css` with reusable layout helpers.
3. Refine global typography and surface behavior in `main.css`.
4. Update `AppBadge` with semantic status, severity, source, and category tones.
5. Refine `AppButton`, `AppCard`, `AppEmptyState`, `AppLoading`, and `AppSectionHeader`.
6. Add `StatusPill`.
7. Add `IssueCategoryBadge`.
8. Add `MetricCard`.
9. Add `FeaturePanel`.
10. Refine `PrimaryNav`.
11. Refine `AppShell`, `CitizenLayout`, and `DashboardLayout`.
12. Update Home page.
13. Update Citizen Report page.
14. Update Dashboard page.
15. Update Audit page.
16. Add `docs/frontend-style-guide.md`.
17. Run build verification.
18. Run local route verification.

## Files To Add

```text
frontend/src/components/common/FeaturePanel.vue
frontend/src/components/common/MetricCard.vue
frontend/src/components/reports/IssueCategoryBadge.vue
frontend/src/components/reports/StatusPill.vue
docs/frontend-style-guide.md
```

## Files To Modify

```text
frontend/src/components/common/AppBadge.vue
frontend/src/components/common/AppButton.vue
frontend/src/components/common/AppCard.vue
frontend/src/components/common/AppEmptyState.vue
frontend/src/components/common/AppLoading.vue
frontend/src/components/common/AppSectionHeader.vue
frontend/src/components/navigation/PrimaryNav.vue
frontend/src/layouts/AppShell.vue
frontend/src/layouts/CitizenLayout.vue
frontend/src/layouts/DashboardLayout.vue
frontend/src/pages/HomePage.vue
frontend/src/pages/citizen/CitizenReportPage.vue
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/pages/audit/AuditPage.vue
frontend/src/styles/main.css
frontend/src/styles/tokens.css
frontend/src/styles/utilities.css
frontend/src/types/ui.ts
```

## Verification Plan

Required command:

```bash
cd frontend
npm run build
```

Local route verification:

```bash
cd frontend
npm run dev
```

Check routes:

- `/`
- `/report`
- `/dashboard`
- `/audit`

Manual visual checklist:

- Homepage feels premium but not flashy.
- Navigation active states are clear.
- Citizen page feels guided and mobile-first.
- Dashboard feels operational and municipality-first.
- Audit page communicates human-reviewed AI.
- Empty states feel intentional.
- No fake functionality appears.
- Status/severity/category badges are readable.
- Layout works at mobile, tablet, and desktop widths.

## Risks And Mitigations

Risk: Visual polish consumes time without helping the product.

Mitigation:

- Focus polish on reusable tokens/components and active routes only.
- Do not add decorative work that cannot be reused in FE-2 through FE-5.

Risk: UI becomes over-designed.

Mitigation:

- Use restrained shadows, soft surfaces, limited motion, and semantic colors.
- Avoid dramatic gradients, neon AI styling, and heavy glass effects.

Risk: Dashboard looks fake without data.

Mitigation:

- Use honest "Awaiting live data" and "Ready for backend data" states.
- Do not invent counts or reports.

Risk: Too many badge tones create inconsistency.

Mitigation:

- Centralize badge tone names and document their intended usage.

## FE-1 Acceptance Criteria

FE-1 is complete when:

- `npm run build` passes.
- Active routes render with the improved visual system.
- Semantic tokens exist for surfaces, text, actions, statuses, severities, sources, and categories.
- Shared components support the visual direction without page-specific duplication.
- Homepage, report, dashboard, and audit pages all look intentionally designed.
- No fake data or fake functionality is introduced.
- The frontend style guide exists.
- The interface feels premium, functional, and pleasant without looking like it is trying too hard.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to visual direction, new components, or FE-1 scope should be agreed before coding.

