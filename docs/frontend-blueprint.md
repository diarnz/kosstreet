# KoStreet Frontend Blueprint

## Purpose

This document is the frontend-only implementation blueprint for KoStreet.

The main product blueprint defines the full hackathon system. This frontend blueprint turns that into a phase-by-phase plan for building the Vue/Vite user experience with clear scope, delivery order, and quality gates.

Primary frontend goal:

> Build a mobile-first civic issue reporting and municipal command interface that makes KoStreet feel credible, fast, and operational during the hackathon demo.

Frontend stack:

- Vite.js
- Vue.js
- TypeScript
- Vue Router
- Pinia
- Browser geolocation API
- Browser camera/photo upload APIs
- Map provider to be finalized: Google Maps, Mapbox, or Leaflet

Frontend audience priority:

- Primary: municipalities
- Secondary: citizens

## Product Surfaces

The frontend has three main product surfaces.

Citizen reporting:

- Mobile-first report creation
- Photo capture or upload
- Location capture
- AI result confirmation
- Report submission
- Tracking ID and status view

Municipality dashboard:

- Issue map
- Report queue
- Filters and triage
- Report detail
- Department routing
- Ticket workflow
- Analytics summary

AI Street Audit:

- Audit run overview
- AI-suggested issue review
- Street-level image preview where allowed
- Detection confidence and severity
- Conversion from AI suggestion to municipal ticket

## Current Frontend Baseline

Existing scaffold:

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

This is the architectural starting point. The current pages are placeholders for ownership boundaries, not the final experience.

## Frontend Architecture

Recommended source structure:

```text
frontend/src/
├── api/
│   ├── client.ts
│   ├── reports.ts
│   ├── auditRuns.ts
│   └── uploads.ts
├── assets/
├── components/
│   ├── common/
│   ├── forms/
│   ├── maps/
│   ├── reports/
│   ├── dashboard/
│   └── audit/
├── composables/
│   ├── useGeolocation.ts
│   ├── useCameraUpload.ts
│   ├── useAsyncState.ts
│   └── useMapProvider.ts
├── layouts/
│   ├── AppShell.vue
│   ├── CitizenLayout.vue
│   └── DashboardLayout.vue
├── pages/
│   ├── HomePage.vue
│   ├── citizen/
│   │   ├── CitizenReportPage.vue
│   │   ├── ReportConfirmPage.vue
│   │   └── ReportStatusPage.vue
│   ├── dashboard/
│   │   ├── DashboardPage.vue
│   │   ├── ReportDetailPage.vue
│   │   └── AnalyticsPage.vue
│   └── audit/
│       ├── AuditPage.vue
│       ├── AuditRunDetailPage.vue
│       └── AuditSuggestionDetailPage.vue
├── stores/
│   ├── reports.ts
│   ├── auditRuns.ts
│   └── ui.ts
├── styles/
│   ├── main.css
│   ├── tokens.css
│   └── utilities.css
└── types/
    ├── report.ts
    ├── audit.ts
    ├── detection.ts
    └── api.ts
```

Architecture rules:

- Pages own route-level composition only.
- Components own reusable UI units.
- Stores own shared frontend state.
- API modules own backend communication.
- Composables own browser/API behavior such as geolocation, uploads, async loading, and map lifecycle.
- TypeScript types should mirror backend API schemas closely.

## Phase FE-0: Frontend Foundation

Goal:

Stabilize the frontend base so multiple teammates can work without conflicts.

Build:

- Confirm route map
- Finalize layout structure
- Add design tokens
- Add shared button, card, badge, input, empty-state, and loading components
- Add typed API error handling
- Add basic responsive shell
- Add route-level navigation for citizen, dashboard, and audit flows

Deliverables:

- Clean app shell
- Shared UI primitives
- Stable route structure
- Frontend coding conventions

Quality gate:

- `npm run build` passes
- Pages work on mobile and desktop widths
- No duplicate one-off UI patterns for common elements

## Phase FE-1: Visual Direction And UX System

Goal:

Create a distinctive, professional interface that feels like a modern municipal command platform, not a generic dashboard.

Design direction:

- Municipality-first
- High-trust civic technology
- Clear status colors
- Map-centered operational feel
- Mobile-first for citizen reporting
- Dense but readable dashboard for municipal users
- Premium but practical, not flashy
- Pleasant visual warmth without looking decorative or unserious
- Enough depth, texture, and hierarchy to feel designed, without excessive gradients, animations, or effects

Visual personality:

- Calm, competent, and civic-minded
- Modern European municipal technology rather than startup landing-page hype
- Trustworthy enough for government users
- Friendly enough for citizens
- Operational enough for field teams and public works departments

Design balance:

- Avoid extreme minimalism that makes the product feel empty or unfinished
- Avoid over-designed UI that distracts from reporting, triage, and decision-making
- Use restrained visual richness: soft surfaces, subtle borders, gentle shadows, strong spacing, and clear typography
- Make important data feel scannable before making it decorative

Recommended color palette:

```text
Primary ink:        #17211A  Deep civic green-black for headings and key text
Municipal green:    #2F5D50  Primary action and trust color
Sage surface:       #DDE8D5  Soft environmental/civic background tint
Warm stone:         #F4EFE4  Main page background
Paper:              #FFFDF7  Cards, panels, forms
Road graphite:      #3A3F3B  Secondary text and infrastructure tone
Amber signal:       #D9902F  Warnings, medium severity, attention states
Repair red:         #C84C3A  High severity, rejected, urgent defects
Resolved blue:      #3F6E8C  Resolved or verified municipal state
Muted line:         #D7D0C2  Borders and separators
```

Palette rules:

- Use `Warm stone` as the primary app background.
- Use `Paper` for cards and form panels.
- Use `Primary ink` for headings and strong text.
- Use `Municipal green` for primary actions, selected filters, active navigation, and trusted states.
- Use `Amber signal` sparingly for attention, not as a general brand color.
- Use `Repair red` only for high-severity defects, errors, or urgent issues.
- Use map/category colors only where they improve operational scanning.
- Avoid large blocks of saturated color.
- Avoid pure white backgrounds across the whole app because they can feel generic and harsh.
- Avoid purple/blue SaaS defaults unless used intentionally for status semantics.

Status color direction:

- New: neutral graphite or municipal green outline
- Verified: resolved blue
- Assigned: municipal green
- In Progress: amber signal
- Resolved: deep green or resolved blue
- Rejected: muted red or graphite-red

Severity color direction:

- Low: sage green
- Medium: amber signal
- High: repair red
- Critical: deep red with strong contrast, used rarely

Theme and surface rules:

- Use soft card backgrounds with subtle borders.
- Use shadows lightly to separate operational panels, not to create floating gimmicks.
- Use rounded corners consistently, but keep them moderate.
- Use map and dashboard panels as the visual anchor.
- Use subtle background gradients only on major surfaces such as the landing hero or dashboard shell.
- Use small civic/map-inspired details such as route lines, coordinate labels, or grid textures only if they remain subtle.

Typography direction:

- Use a confident sans-serif with strong readability.
- Prefer a slightly expressive heading face only if it does not reduce professionalism.
- Body text should prioritize clarity over personality.
- Numeric dashboard values should be easy to scan.
- Avoid tiny labels in operational areas.

Layout direction:

- Citizen flow should feel guided, vertical, and calm.
- Dashboard should feel like a command center: map, queue, filters, and details should be visible without clutter.
- Audit interface should feel like a review workstation, not a chatbot.
- Use spacing to create hierarchy instead of relying only on color.
- Keep key actions close to the object they affect.

Motion direction:

- Use motion sparingly.
- Page transitions should be subtle and fast.
- Loading states should communicate progress without feeling playful.
- Avoid excessive animation during the pitch; it can make the product feel less serious.

Design anti-patterns:

- Do not make the product look like a generic admin template.
- Do not use a plain white/gray minimalist SaaS look.
- Do not overuse glassmorphism, neon colors, heavy gradients, or dramatic shadows.
- Do not hide operational information behind overly large hero sections.
- Do not make AI confidence look absolute or magical.
- Do not let aesthetic choices reduce dashboard density or readability.

Build:

- CSS variables for color, spacing, radius, shadow, typography, and status colors
- Theme tokens for the approved palette
- Typography scale
- Status badge system
- Severity badge system
- Source badge system: `Citizen`, `AI Street Audit`
- Category badge system for potholes, garbage, broken lights, blocked sidewalks, damaged signs, and other issues
- Card, panel, and map surface styles
- Button hierarchy: primary, secondary, ghost, danger
- Form field styling for mobile capture and dashboard filters
- Empty states
- Error states
- Loading skeletons
- Responsive layout rules

Deliverables:

- Reusable design system primitives
- Updated homepage
- Updated navigation and layout
- Frontend style guide section in docs if time allows

Quality gate:

- The UI has a clear visual identity
- Dashboard remains readable with many reports
- Citizen flow is usable on a phone screen
- The interface feels premium and calm without looking over-styled
- Color choices reinforce status, severity, and municipal trust
- The product looks complete even before advanced AI and map integrations are fully implemented

## Phase FE-2: Citizen Reporting Flow

Goal:

Allow a citizen to create a structured civic issue report quickly.

Screens:

- `/report`
- `/report/confirm`
- `/report/status/:id`

Build:

- Issue photo capture or upload
- Image preview
- Location capture through browser geolocation
- Manual location fallback if geolocation is denied
- Issue category selection
- AI suggestion display once backend supports analysis
- User confirmation or category override
- Description field
- Submit report
- Success state with tracking ID

Key UX requirements:

- Camera/upload interaction must be simple
- Location permission must be explained clearly
- User must be able to submit even if AI confidence is low
- AI should assist, not block submission

API dependencies:

- `POST /api/v1/reports`
- Future upload endpoint
- Future AI analysis endpoint

Deliverables:

- End-to-end citizen report UI
- Typed report payload
- Validation and error states
- Tracking success screen

Quality gate:

- A citizen can create a report from a mobile browser
- The submitted payload matches backend schema
- Network failures show recoverable errors

## Phase FE-3: Municipality Dashboard

Goal:

Build the primary judge-facing product surface: a municipal command center for Prishtina.

Screens:

- `/dashboard`
- `/dashboard/reports/:id`
- `/dashboard/analytics`

Build:

- Summary metric cards
- Report queue table/list
- Status filters
- Category filters
- Source filters
- Severity filters
- Search by location, category, or department
- Report detail panel
- Ticket status transitions
- Department routing display
- Map placeholder first, real map integration later

Core dashboard metrics:

- Total reports
- New reports
- Verified reports
- In-progress reports
- Resolved reports
- AI-suggested issues
- Reports by category

Report list fields:

- Category
- Status
- Source
- Confidence
- Location
- Department
- Created time

API dependencies:

- `GET /api/v1/reports`
- Future `GET /api/v1/reports/:id`
- Future `PATCH /api/v1/reports/:id/status`

Deliverables:

- Functional municipal dashboard
- Report queue
- Report detail view
- Filter and status UI

Quality gate:

- Municipality can understand operational state in under 10 seconds
- Dashboard clearly separates citizen reports from AI Street Audit suggestions
- The UI makes the pitch emphasis on municipalities obvious

## Phase FE-4: Map And Geospatial Experience

Goal:

Make location central to the product.

Build:

- Map provider integration
- Prishtina default viewport
- Report markers
- Marker clustering if needed
- Category-based marker styling
- Status-based marker styling
- Selected report map highlight
- Map/list synchronization
- Fallback list-only mode if map provider fails

Provider decision:

- Google Maps if API access and terms are suitable
- Mapbox if styling and developer speed are stronger
- Leaflet/OpenStreetMap if simplicity and cost control are prioritized

Deliverables:

- Interactive report map
- Marker click to report detail
- Map filters connected to dashboard filters

Quality gate:

- Map loads reliably in demo conditions
- App remains usable if map API fails
- Prishtina route/area is visually clear

## Phase FE-5: AI Street Audit Interface

Goal:

Show the standout proactive capability: AI-suggested issues from street-level scanning.

Screens:

- `/audit`
- `/audit/:runId`
- `/audit/suggestions/:suggestionId`

Build:

- Audit run list
- Audit run status display
- Scan progress UI
- Suggested issue cards
- Confidence and severity display
- Image preview where legally allowed
- Detection explanation summary
- Accept suggestion as municipal ticket
- Reject suggestion
- Flag for manual review

AI-specific UX:

- Clearly label suggestions as `AI-suggested`
- Show confidence without pretending certainty
- Show source and imagery constraints transparently
- Make human verification part of the product, not an apology

API dependencies:

- `GET /api/v1/audit-runs`
- `POST /api/v1/audit-runs`
- Future audit suggestion endpoints
- Future convert-suggestion-to-report endpoint

Deliverables:

- AI Street Audit dashboard
- Suggestion review flow
- Conversion UI into municipal ticket

Quality gate:

- Judges understand that KoStreet can detect issues proactively
- AI outputs are reviewable and actionable
- The interface avoids overstating model certainty

## Phase FE-6: Ticket Workflow And Transparency

Goal:

Make issue resolution trackable from report to municipal action.

Build:

- Status transition controls
- Status timeline component
- Department assignment display
- Resolution note UI
- Citizen-facing tracking page
- Municipal internal notes placeholder if needed

Statuses:

- New
- Verified
- Assigned
- In Progress
- Resolved
- Rejected

Deliverables:

- Ticket timeline component
- Citizen tracking page
- Municipality status update UI

Quality gate:

- The app demonstrates transparency clearly
- Workflow states match backend schema
- Invalid transitions are either prevented or clearly handled

## Phase FE-7: Demo Data And Pitch Mode

Goal:

Make the live demo reliable even if backend, AI, map, or external APIs are unstable during judging.

Build:

- Seeded frontend demo state if backend data is empty
- Demo route label for Prishtina
- Polished sample reports
- Sample AI Street Audit suggestions
- Pitch-mode path through the app
- Loading fallback states

Demo content should include:

- Pothole report
- Garbage report
- Broken streetlight report
- Blocked sidewalk report
- Damaged sign report
- At least one AI-suggested issue

Deliverables:

- Demo-safe UI path
- Seeded data contract with backend
- Pitch rehearsal checklist

Quality gate:

- Demo can be completed in under 3 minutes
- No empty screens during pitch
- App still tells the story if one external service fails

## Phase FE-8: Accessibility, Performance, And Polish

Goal:

Bring the frontend to pitch-ready quality.

Build:

- Keyboard navigation checks
- Visible focus states
- Accessible labels on form inputs
- Color contrast checks
- Mobile viewport testing
- Loading performance cleanup
- Error copy cleanup
- Empty-state copy cleanup
- Final responsive polish

Deliverables:

- Polished mobile citizen flow
- Polished municipal dashboard
- Polished audit review flow
- Final frontend demo route

Quality gate:

- `npm run build` passes
- UI works on mobile and desktop
- No broken navigation routes
- Demo path is rehearsed and stable

## Suggested Implementation Order

1. FE-0: Frontend Foundation
2. FE-1: Visual Direction And UX System
3. FE-2: Citizen Reporting Flow
4. FE-3: Municipality Dashboard
5. FE-4: Map And Geospatial Experience
6. FE-5: AI Street Audit Interface
7. FE-6: Ticket Workflow And Transparency
8. FE-7: Demo Data And Pitch Mode
9. FE-8: Accessibility, Performance, And Polish

Reasoning:

Foundation and design system come first to prevent rework. Citizen reporting and municipal dashboard come before the advanced audit interface because they satisfy the core challenge. The AI Street Audit interface then becomes the standout feature. Demo mode and polish come last but must not be skipped.

## Frontend API Contract Needs

Current backend endpoints:

- `GET /api/v1/reports`
- `POST /api/v1/reports`
- `GET /api/v1/audit-runs`
- `POST /api/v1/audit-runs`

Frontend will likely need these additional endpoints:

- `POST /api/v1/uploads`
- `POST /api/v1/analyze-image`
- `GET /api/v1/reports/:id`
- `PATCH /api/v1/reports/:id/status`
- `GET /api/v1/audit-runs/:id`
- `GET /api/v1/audit-runs/:id/suggestions`
- `PATCH /api/v1/audit-suggestions/:id`
- `POST /api/v1/audit-suggestions/:id/convert-to-report`

These should be finalized with the backend team before the relevant frontend phase begins.

## Frontend Success Criteria

The frontend is successful if:

- A citizen can submit a geolocated issue report from mobile.
- A municipality can triage and understand reports from a dashboard.
- AI Street Audit suggestions are visually distinct and reviewable.
- The Prishtina municipal focus is clear.
- The product tells a complete story in a short live demo.
- The app remains usable even when AI or map integrations are delayed.

## Next Frontend Gate

Before implementing FE-0, confirm:

- Map provider preference
- Whether Tailwind CSS should be added or custom CSS should continue
- Whether frontend should include demo-mode mock data before backend persistence is ready
- Whether authentication is needed for the hackathon demo or skipped for speed
