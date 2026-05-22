# KoStreet Frontend Style Guide

## Visual Direction

Theme: **Prishtina Civic Warmth**

KoStreet should feel premium, functional, municipal, and calm. The interface should look intentionally designed without becoming decorative or distracting.

Use the product surfaces to communicate trust:

- Citizen reporting should feel guided and approachable.
- Municipality dashboard should feel operational and clear.
- AI Street Audit should feel reviewable, transparent, and human-supervised.

## Palette

Base colors:

```text
Primary ink:        #17211A
Municipal green:    #2F5D50
Sage surface:       #DDE8D5
Warm stone:         #F4EFE4
Paper:              #FFFDF7
Road graphite:      #3A3F3B
Amber signal:       #D9902F
Repair red:         #C84C3A
Resolved blue:      #3F6E8C
Muted line:         #D7D0C2
```

Rules:

- Use warm stone and sage as broad surfaces.
- Use paper for cards, panels, and forms.
- Use municipal green for primary actions and trust states.
- Use amber only for attention, work in progress, or medium severity.
- Use repair red only for errors, rejected states, and high severity.
- Avoid pure white full-page backgrounds.
- Avoid neon AI styling.

## Typography

Use the shared CSS tokens from `frontend/src/styles/tokens.css`.

Rules:

- Keep headings compact and confident.
- Keep body copy direct and readable.
- Avoid tiny operational labels.
- Dashboard numbers and statuses must scan quickly.

## Status Semantics

Statuses:

- `new`: neutral pending state
- `verified`: municipal confirmation
- `assigned`: active department ownership
- `in_progress`: work underway
- `resolved`: completed issue
- `rejected`: not accepted or invalid

Use `StatusPill.vue` instead of hardcoding status labels inside pages.

## Severity Semantics

Severities:

- Low: sage/green
- Medium: amber
- High: repair red
- Critical: deeper red, used rarely

Severity colors should never be the only signal. Always include readable text.

## Source Semantics

Sources:

- Citizen: green trust tone
- AI Street Audit: warm AI-audit tone

AI labels should communicate that suggestions are reviewable, not automatic truth.

## Category Semantics

Issue categories:

- Pothole: graphite/road tone
- Garbage: cleanup green
- Broken streetlight: amber/electrical tone
- Blocked sidewalk: blue/urban mobility tone
- Damaged sign: red/orange infrastructure tone
- Other: neutral tone

Use `IssueCategoryBadge.vue` instead of hardcoding category labels inside pages.

## Component Rules

Use shared components first:

- `AppBadge`
- `AppButton`
- `AppCard`
- `AppEmptyState`
- `AppField`
- `AppInput`
- `AppLoading`
- `AppSectionHeader`
- `FeaturePanel`
- `MetricCard`
- `StatusPill`
- `IssueCategoryBadge`

Do not duplicate common button, badge, card, or empty-state styling inside page files unless the page has a legitimate layout-specific reason.

## Empty States

Empty states should feel intentional and honest.

Allowed:

- “Awaiting live data”
- “Ready for backend data”
- “Reserved for FE-4 map integration”

Not allowed:

- Fake reports
- Fake metrics
- Fake detections
- Fake upload behavior
- Fake scan progress

## Pitch Mode

Pitch Mode is allowed only for hackathon demo reliability.

Rules:

- Demo records must be visibly labeled as demo records.
- Demo AI suggestions must be labeled as demo scenarios, not live model output.
- Pitch Mode banners should explain when prepared fixtures are shown because backend data is empty or unavailable.
- Demo data must never be presented as live backend truth.
- Status updates on demo records must not appear persisted.
- Do not show restricted imagery in demo suggestion cards unless the team has approved the source and usage rights.

## Motion

Use motion sparingly.

Allowed:

- Subtle hover lift
- Calm loading spinner
- Skeleton shimmer

Avoid:

- Dramatic page transitions
- Repeated attention-grabbing animation
- Playful AI effects

## Anti-Patterns

Avoid:

- Generic admin dashboard styling
- Plain white/gray minimalist SaaS look
- Heavy glassmorphism
- Neon AI colors
- Large decorative gradients that reduce readability
- Buttons that look functional but do nothing
- Color-only status communication

