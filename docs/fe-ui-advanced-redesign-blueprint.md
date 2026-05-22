# KoStreet Advanced UI Redesign Blueprint

> **Status:** Awaiting developer green light  
> **Scope:** Frontend only — no backend/API contract changes  
> **Constraint:** Street View panorama logic must remain fully functional (lookup, fallback, POV, selection binding)

---

## 1. Goal

Transform KoStreet from a documentation-heavy, basic card layout into a **responsive, animated, advanced civic platform** that is easier to scan and faster to use — especially for hackathon demos and municipal operators.

### Success criteria

- Less explanatory text; more visual hierarchy and action-first UI
- Consistent hero treatment on every page (logo mark + short title + one-line subtitle)
- Report flow feels like a modern step wizard, not four oversized boxes on one scroll page
- Location input uses **Google Places search restricted to Kosovo** (using existing `VITE_GOOGLE_MAPS_API_KEY`)
- Dashboard and Street Audit feel like a command center, not a spec document
- **Street View panel behavior unchanged** — only labels/copy around it may change
- Fully responsive down to 320px; respects `prefers-reduced-motion`

---

## 2. Non-goals (explicit)

| Will NOT change | Reason |
|-----------------|--------|
| `StreetViewPanel.vue` panorama lookup/render logic | User requirement |
| Backend API contracts | Out of scope |
| Pinia store data flow | Only presentation layer |
| Demo/Pitch Mode data fixtures | Behavior preserved |
| AI pipeline connection status | Still not connected; UI will hide stub notes instead of showing them |

---

## 3. Design system additions

### 3.1 New tokens (`styles/tokens.css`)

```css
--motion-fast: 160ms;
--motion-base: 240ms;
--motion-slow: 420ms;
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

--hero-max-width: 42rem;
--step-rail-width: 3.5rem;
```

### 3.2 New utilities (`styles/utilities.css`)

| Class | Purpose |
|-------|---------|
| `.animate-fade-up` | Page/section entrance (opacity + translateY) |
| `.animate-stagger > *` | Staggered children animation |
| `.hero-surface` | Shared hero box: gradient border, soft glow, centered content |
| `.step-rail` | Vertical/horizontal compact step indicator |
| `.icon-action` | Circular icon button (GPS, search, etc.) |
| `.surface-glass` | Stronger glassmorphism for command panels |

### 3.3 Animation rules

- Page sections: fade-up on mount (240ms)
- Step transitions: slide + fade between active step panels
- Card hover: subtle scale(1.01) + shadow lift (existing 160ms, kept)
- List selection: highlight border animate-in
- **Reduced motion:** all animations become instant opacity-only

### 3.4 Shared hero pattern

New component: `components/common/PageHero.vue`

```
┌─────────────────────────────────────────┐
│  [optional AppLogo sm]                  │
│  EYEBROW (small caps)                   │
│  Page Title (1 line, bold)              │
│  One-line subtitle only                 │
└─────────────────────────────────────────┘
```

Replaces verbose `AppSectionHeader` blocks on: Home, Report, Status, Dashboard, Audit.

---

## 4. New shared component: Kosovo location search

### 4.1 `components/maps/LocationSearchField.vue`

**Purpose:** Google Places Autocomplete input restricted to Kosovo.

**Implementation:**

1. Extend `utils/googleMaps.ts`:
   - Add `loadGooglePlaces()` importing `places` library (alongside existing `streetView`)
   - Export `getKosovoSearchOptions()` with:
     - `componentRestrictions: { country: 'XK' }`
     - `bounds` around Kosovo (`southwest: 41.85, 20.02` → `northeast: 43.27, 21.82`)
     - `strictBounds: true`

2. Component API:

```ts
interface LocationSearchFieldProps {
  modelValue: { latitude: number | null; longitude: number | null; label?: string };
  placeholder?: string;
  disabled?: boolean;
}
```

3. On place select → extract lat/lng via `place.geometry.location`, emit update + human-readable label.

4. Fallback: if API key missing, show inline warning + collapsed manual coordinate toggle (hidden by default).

### 4.2 `components/maps/GpsLocateButton.vue`

Circular icon button with crosshair/GPS SVG — replaces text button "Use current location".

- States: idle, loading (spinner), success (brief checkmark), error
- Tooltip: "Use my location"
- Uses existing `useGeolocation` composable

### 4.3 Where used

| Location | Replaces |
|----------|----------|
| `LocationCaptureField.vue` | Lat/lng inputs as primary UI |
| `AuditRunForm.vue` | Route name text field + lat/lng grid |

---

## 5. Page-by-page changes

### 5.1 Global — all pages

| Change | Detail |
|--------|--------|
| `AppShell.vue` | Softer outer padding on mobile; main panel full-bleed below 620px |
| `PrimaryNav.vue` | Subtle slide-down on load; active link underline animation |
| Every page | Replace long `AppSectionHeader` with `PageHero` (title ≤ 8 words, subtitle ≤ 1 sentence) |

---

### 5.2 Home (`HomePage.vue`)

**Before:** Large logo + long hero + 3 feature panels + operating loop + pitch card  
**After:**

```
PageHero: "Civic intelligence for Prishtina"
3 compact feature tiles (icon + title + 6-word tagline)
Operating loop → horizontal animated pills (no paragraph)
Pitch path → unchanged but collapsible
```

- Feature panels: smaller, icon-led, hover lift animation
- Remove duplicate long descriptions

---

### 5.3 Report flow (`CitizenReportPage.vue` + child components)

#### A. Step indicator redesign — `ReportProgress.vue`

**Before:** 4 large numbered boxes (01 Photo, 02 Location, …)  
**After:** Compact horizontal step rail

```
 ● ─── ○ ─── ○ ─── ○
Photo  Loc  Cat  Review
```

- Current step: filled dot + accent line
- Complete: checkmark icon, green
- Size: ~48px tall total (not 8rem cards)
- Clickable to jump back to completed steps (optional, desktop only)

#### B. Step panel layout

Convert single scroll page to **one active step panel at a time** with Next/Back navigation:

| Step | Panel content |
|------|---------------|
| 1 Photo | `PhotoCaptureField` — trimmed copy |
| 2 Location | Search bar + GPS icon button |
| 3 Category | Icon tile grid |
| 4 Review | `ReportReviewCard` + submit |

Mobile: full-width step; desktop: centered max-width 640px hero box per step.

#### C. `PhotoCaptureField.vue`

- Remove "Local preview only" badge and backend disclaimer
- Larger dashed dropzone with camera icon
- Drag-over highlight animation
- Copy: **"Add a photo of the issue"** (one line)

#### D. `LocationCaptureField.vue`

**New layout:**

```
┌──────────────────────────────────────────────┐
│ Location                              [req]  │
│ Search an address or landmark in Kosovo      │
│                                              │
│ [ 🔍 Search Kosovo...                    ]   │
│                                              │
│        ( GPS icon button )                   │
│                                              │
│ ✓ Rruga Bill Clinton, Prishtina  (if set)   │
└──────────────────────────────────────────────┘
```

- Primary: `LocationSearchField`
- Secondary: `GpsLocateButton` centered below search
- Remove visible lat/lng fields (values still stored internally; optional "Advanced" collapsible for manual entry)
- Accuracy shown as small chip after GPS

#### E. `IssueCategorySelector.vue`

**New layout:** 3×2 icon tile grid

```
┌─────────┐ ┌─────────┐ ┌─────────┐
│  🕳️     │ │  🗑️     │ │  💡     │
│ Pothole │ │ Garbage │ │ Light   │
└─────────┘ └─────────┘ └─────────┘
...
```

- Remove per-category paragraph descriptions from tiles
- Selected: accent ring + scale animation
- **Remove** "AI analysis not connected" card entirely
- Category names only (short labels)

#### F. `ReportReviewCard.vue`

- Cleaner summary grid with icons
- Remove AI-not-connected copy
- Prominent submit button with loading state animation

#### G. Remove from page

- "Citizen trust note" card (backend upload disclaimer)

---

### 5.4 Report status (`ReportStatusPage.vue`)

| Change | Detail |
|--------|--------|
| Hero | Tracking ID as large monospace in hero box |
| Timeline | Compact horizontal stepper (not 6 paragraphs) |
| Trim | Remove API endpoint fallback messages from user-facing copy |
| Add | Mini static map pin or coordinate chip (no new map embed — just formatted location) |

---

### 5.5 Dashboard (`DashboardPage.vue` + dashboard components)

#### Layout restructure

```
PageHero: "Issue command center" + Refresh
DashboardMetrics (compact hero strip — 6 cards, smaller)
DashboardFilters (toolbar)
┌──────────────────────┬─────────────────────┐
│ ReportQueue          │ ReportDetailPanel   │
│                      │                     │
│                      │ StreetViewPanel     │  ← moved inside detail column
└──────────────────────┴─────────────────────┘
```

#### Street View — copy-only changes

| Prop / element | Before | After |
|----------------|--------|-------|
| `eyebrow` | "Street-level evidence" | "Street context" |
| `title` | "Google Street View context" | "Location preview" |
| Badge | "Google Street View" | Remove badge |
| Subtitle | Long explanation | "Nearest panorama for selected report" |

**No changes** to: `panoramaElement`, lookup token, radius fallback, `StreetViewRecordSummary` data binding.

#### Other dashboard trims

- Header description: one line
- `ReportDetailPanel`: remove department routing paragraphs → icon + badge
- `ReportQueue`: denser list rows, selection animation
- Metrics: smaller cards with count animation on load

---

### 5.6 Street Audit (`AuditPage.vue` + audit components)

#### Layout restructure

```
PageHero: "Street audit workspace" + badges + refresh
AuditRunMetrics (top strip)
┌──────────────────────┬─────────────────────┐
│ AuditRunForm         │ AuditRunQueue       │
│ (with location search)│                     │
└──────────────────────┴─────────────────────┘
AuditRunDetailPanel (full width below)
DemoAuditSuggestionPanel (demo only)
```

- **Remove** "Review philosophy" card (3 principles grid)
- Remove pipeline ownership paragraphs from form

#### `AuditRunForm.vue`

**New fields:**

```
Municipality: [Prishtina]
Location:     [🔍 Search route or address in Kosovo]
Notes:        [optional]
[Create audit run]
```

- `LocationSearchField` populates `route_name` (from `place.name` or formatted address) AND lat/lng
- Remove separate lat/lng inputs
- Remove hint paragraph about Street View headings

#### `AuditRunDetailPanel.vue`

- Trim pipeline handoff paragraph to one line
- Suggestion list unchanged functionally

---

## 6. File change manifest

### New files

| File | Purpose |
|------|---------|
| `components/common/PageHero.vue` | Shared page hero |
| `components/maps/LocationSearchField.vue` | Kosovo Places Autocomplete |
| `components/maps/GpsLocateButton.vue` | Icon GPS button |
| `composables/usePlacesAutocomplete.ts` | Places init + cleanup |
| `utils/places.ts` | Kosovo bounds, place → coordinates helper |
| `styles/animations.css` | Keyframes + motion utilities |

### Modified files

| File | Changes |
|------|---------|
| `utils/googleMaps.ts` | Add places library loader |
| `utils/map.ts` | Export `KOSOVO_BOUNDS` |
| `styles/tokens.css` | Motion tokens |
| `styles/main.css` | Import animations.css |
| `styles/utilities.css` | Hero + step utilities |
| `layouts/AppShell.vue` | Responsive polish |
| `pages/HomePage.vue` | Compact hero + tiles |
| `pages/citizen/CitizenReportPage.vue` | Step wizard layout |
| `pages/citizen/ReportStatusPage.vue` | Compact status UI |
| `pages/dashboard/DashboardPage.vue` | Layout restructure, SV props |
| `pages/audit/AuditPage.vue` | Layout restructure, remove philosophy card |
| `components/reports/ReportProgress.vue` | Compact step rail |
| `components/reports/PhotoCaptureField.vue` | Visual refresh |
| `components/reports/LocationCaptureField.vue` | Search + GPS icon |
| `components/reports/IssueCategorySelector.vue` | Icon tiles |
| `components/reports/ReportReviewCard.vue` | Cleaner summary |
| `components/audit/AuditRunForm.vue` | Location search |
| `components/streetview/StreetViewPanel.vue` | **Default prop text only** |
| `components/streetview/StreetViewRecordSummary.vue` | Shorter labels |
| `components/streetview/StreetViewFallbackPanel.vue` | Shorter user copy |

### NOT modified (Street View core)

- Panorama mount logic in `StreetViewPanel.vue` (script section)
- `utils/streetView.ts`
- `stores/reports.ts` Street View target computation

---

## 7. Google Maps API requirements

Uses existing `VITE_GOOGLE_MAPS_API_KEY`.

**APIs needed enabled in Google Cloud Console:**

- Maps JavaScript API
- Places API
- Street View Static API (already used)

**Autocomplete restriction:**

```js
autocomplete.setOptions({
  componentRestrictions: { country: 'XK' },
  bounds: kosovoBounds,
  strictBounds: true,
  fields: ['geometry', 'formatted_address', 'name'],
});
```

**Error handling:**

- Missing key → graceful fallback to GPS + manual coords (collapsed)
- Places load failure → same fallback with inline message

---

## 8. Responsive breakpoints

| Breakpoint | Behavior |
|------------|----------|
| ≤ 620px | Single column; step rail horizontal scroll; full-bleed shell |
| 621–980px | Dashboard/audit workspace stacks |
| ≥ 981px | Two-column command layouts |

---

## 9. Implementation phases

| Phase | Scope | Est. files |
|-------|-------|------------|
| **P1 — Foundation** | Tokens, animations, PageHero, googleMaps/places utils | 6 new, 4 modified |
| **P2 — Location search** | LocationSearchField, GpsLocateButton, composable | 4 new, 2 modified |
| **P3 — Report flow** | Step wizard, progress rail, photo/location/category/review | 0 new, 6 modified |
| **P4 — Dashboard** | Layout restructure, SV copy, trim text | 0 new, 5 modified |
| **P5 — Street Audit** | Form search, layout, trim text | 0 new, 4 modified |
| **P6 — Polish** | Home, status page, nav animations, final responsive pass | 0 new, 4 modified |

Each phase is fully functional before moving to the next — **no stubs**.

---

## 10. Text reduction policy

Remove or shorten any copy that:

- Mentions backend endpoints (`GET /api/v1/...`)
- Explains what is "not connected yet"
- Describes internal pipeline ownership (backend/AI team)
- Repeats information already visible in UI labels

Keep copy that:

- Tells the user what to do next
- Explains required fields
- Shows errors with actionable fixes

---

## 11. Testing checklist

- [ ] Report flow: all 4 steps work on mobile (375px) and desktop
- [ ] Location search returns Kosovo places only
- [ ] GPS button sets coordinates
- [ ] Category selection + submit still creates report
- [ ] Dashboard: selecting report loads Street View panorama (same as before)
- [ ] Dashboard: Street View fallback still works for unmapped coords
- [ ] Audit: create run with search-selected location
- [ ] Audit: create run with GPS
- [ ] Pitch Mode still works on all pages
- [ ] `prefers-reduced-motion`: no jarring animations
- [ ] Missing API key: fallbacks work, no console crashes

---

## 12. Open questions for developer

1. **Report wizard vs scroll:** Blueprint proposes true step-by-step (one panel visible). Confirm this over keeping single scroll with compact step rail only.

2. **Manual coordinates:** Hidden behind "Advanced" toggle, or removed entirely from citizen flow?

3. **Category icons:** Use emoji (fast, no assets) or custom SVG icons per category?

4. **Audit form:** When user searches a place, should we send `route_name` = formatted address, or `place.name` only?

5. **Home page:** Keep operating loop section or replace with simpler 3-tile navigation only?

---

## 13. Approval

Reply with **green** (and any answers to §12) to begin implementation in order P1 → P6.

Suggested reply format:

```
Green — proceed with blueprint
Q1: step wizard
Q2: advanced toggle ok
Q3: SVG icons
Q4: formatted address
Q5: keep loop, make compact
```
