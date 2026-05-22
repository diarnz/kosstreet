# Google Street View Map Replacement Blueprint

## Goal

Replace the current Leaflet/OpenStreetMap dashboard map with a Google Street View-first experience.

After implementation, KoStreet should no longer render a Leaflet map in the municipal dashboard. Instead, the geospatial surface should show an interactive Google Street View panorama centered on the selected report or AI audit suggestion when Street View imagery is available, with a clear fallback when imagery is unavailable.

This blueprint is review-only. No implementation should begin until approved.

## Product Direction

The current map answers:

- Where are civic reports located?
- Which marker corresponds to the selected report?

The new Street View surface should answer:

- What does the street-level evidence context look like near this report or AI suggestion?
- Can a municipal reviewer visually inspect the relevant location before deciding?
- Does the selected issue have a nearby Google Street View panorama?

This is not just a tile-provider swap. Leaflet is map-marker oriented; Google Street View is evidence/context oriented. The UI should be redesigned around selected records, panorama availability, and reviewer context.

## Current State

### Frontend Leaflet Usage

Leaflet is currently used in:

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/main.ts`
- `frontend/src/components/maps/ReportMap.vue`
- `frontend/src/components/maps/MapLegend.vue`
- `frontend/src/components/maps/ReportMapPopup.vue`
- `frontend/src/components/maps/MapFallbackPanel.vue`
- `frontend/src/utils/map.ts`
- `frontend/src/types/map.ts`

Current behavior:

- `ReportMap.vue` initializes `L.map`.
- It loads OpenStreetMap tiles from `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`.
- It creates category/status markers with `L.divIcon`.
- It pans/fits to filtered reports and selected report.
- It emits report selection from marker clicks.
- `DashboardPage.vue` renders `ReportMap` above the queue/detail workspace.

### Backend Google Street View Usage

Backend already has Google Street View integration:

- `backend/app/core/config.py` reads `GOOGLE_MAPS_API_KEY`.
- `backend/app/integrations/street_imagery.py` builds Google Street View Static API URLs and fetches frames.
- `backend/app/services/audit_service.py` uses Street View frames for proactive audit inference.
- `backend/app/models/audit.py` stores suggestion `latitude`, `longitude`, `heading`, `pitch`, `image_url`, and `image_attribution`.

This backend integration is for server-side Street View Static API frame retrieval. The dashboard replacement needs browser-side Google Maps JavaScript API Street View rendering.

### Environment State

The repo `.env` currently has:

- `GOOGLE_MAPS_API_KEY` for backend usage.
- No dedicated browser-safe `VITE_GOOGLE_MAPS_API_KEY`.

Vite only exposes variables prefixed with `VITE_` to the browser. A frontend Street View viewer cannot directly read `GOOGLE_MAPS_API_KEY` unless we deliberately expose it through a `VITE_` variable or through a backend config endpoint.

## Key Decision: How To Provide The Google Key

Google Maps JavaScript API runs in the browser, so the browser needs a key that is allowed to load the Maps JS API and Street View services.

Recommended approach:

- Add `VITE_GOOGLE_MAPS_API_KEY` for frontend-only Google Maps JavaScript usage.
- Keep `GOOGLE_MAPS_API_KEY` for backend Street View Static API usage.
- Restrict the frontend key in Google Cloud Console by HTTP referrer, for example local dev and deployment domains.
- Restrict the backend key separately by API and server-side usage where possible.

Alternative approach:

- Add `GET /api/v1/config/public` returning public runtime config.
- Return only values that are intentionally browser-public.
- This still exposes the key to the browser, but avoids hardcoding `VITE_` use in frontend build env.

Do not reuse a privileged unrestricted backend key in browser code.

## Target User Experience

### Dashboard Street View Panel

Replace `ReportMap` with a new component, tentatively:

- `frontend/src/components/streetview/StreetViewPanel.vue`

Behavior:

- Receives the filtered reports and selected report ID from `DashboardPage.vue`.
- Uses the selected report as the primary Street View target.
- If no report is selected, selects the first mappable filtered report or shows a neutral Prishtina starting state.
- Uses Google Maps JS API `StreetViewService.getPanorama()` to find a panorama near the selected coordinates.
- Renders `google.maps.StreetViewPanorama` when found.
- Displays selected report metadata beside or below the panorama.
- Shows a clear fallback if no panorama is available within the configured radius.

### Selection Model

Because Street View itself is not a marker map, the queue remains the primary way to select a report.

Selection flow:

1. User selects a report in the queue.
2. `DashboardPage.vue` updates `reportsStore.selectedReportId`.
3. `StreetViewPanel.vue` receives the selected report.
4. Street View searches for the closest panorama near that report coordinate.
5. If found, it sets panorama position and POV.
6. If not found, it shows fallback copy and keeps queue/detail usable.

### Optional Mini Location Context

If reviewers still need map orientation, add a small non-Leaflet Google Maps mini-map or static coordinate card later. The first implementation should prioritize Street View itself, not recreate the old marker map.

## Google Maps JavaScript API Plan

### Loader

Use one frontend loader utility to avoid loading Google Maps multiple times.

Suggested file:

- `frontend/src/utils/googleMaps.ts`

Responsibilities:

- Read `import.meta.env.VITE_GOOGLE_MAPS_API_KEY`.
- Inject `https://maps.googleapis.com/maps/api/js?key=...&v=weekly`.
- Resolve once and reuse the same loading promise.
- Reject with a clear error if the key is missing or script loading fails.
- Type the global `google` object.

Because this project currently does not use `@googlemaps/js-api-loader`, two options exist:

1. Add `@googlemaps/js-api-loader` dependency for a safer official loader.
2. Implement a small local script loader.

Recommended: add `@googlemaps/js-api-loader` because it handles duplicate loads and errors cleanly.

### TypeScript Types

Add:

- `@types/google.maps` as a dev dependency.

This gives strong typing for:

- `google.maps.StreetViewPanorama`
- `google.maps.StreetViewService`
- `google.maps.LatLngLiteral`
- `google.maps.StreetViewStatus`

### Component Structure

Suggested new files:

- `frontend/src/components/streetview/StreetViewPanel.vue`
- `frontend/src/components/streetview/StreetViewFallbackPanel.vue`
- `frontend/src/components/streetview/StreetViewRecordSummary.vue`
- `frontend/src/utils/googleMaps.ts`
- `frontend/src/utils/streetView.ts`
- `frontend/src/types/streetView.ts`

Potentially remove after migration:

- `frontend/src/components/maps/ReportMap.vue`
- `frontend/src/components/maps/MapLegend.vue`
- `frontend/src/components/maps/ReportMapPopup.vue`

Keep and rename if useful:

- `MapFallbackPanel.vue` can become `StreetViewFallbackPanel.vue`.
- `utils/map.ts` can retain coordinate validation helpers but should be renamed or generalized if no map remains.

## Street View Lookup Behavior

### Report Coordinates

Use report fields:

- `latitude`
- `longitude`

Validate them with existing coordinate checks before querying Street View.

### Search Radius

Start with:

- `radius: 50` meters for exact nearby imagery.

If no result:

- Optionally retry with `radius: 100`.

Avoid broad radius by default because a far panorama can misrepresent report evidence.

### POV And Heading

Citizen reports do not currently store a heading. For report records:

- Use default POV from Street View.
- Let reviewer rotate manually.

AI audit suggestions do store heading and pitch. For suggestion-specific Street View:

- Use `heading` and `pitch` when available.
- Fall back to default POV otherwise.

### Fallback States

Street View panel should handle:

- Missing frontend Google key.
- Google script load failure.
- Invalid coordinates.
- No panorama found nearby.
- API quota or authorization failure.
- Selected record changes before prior request completes.

Fallback copy should say the queue/detail data remains available.

## Dashboard Integration Plan

### Replace `ReportMap`

Update `frontend/src/pages/dashboard/DashboardPage.vue`:

- Remove `ReportMap` import.
- Add `StreetViewPanel` import.
- Pass:
  - `reportsStore.filteredReports`
  - `reportsStore.selectedReportId`
  - `reportsStore.isLoading`
- Preserve `@select` only if the Street View panel includes a nearby-record list. Otherwise selection stays in `ReportQueue`.

### Preserve Existing Queue/Detail Workflow

Do not make Street View the only way to inspect records. The report queue and detail panel must remain accessible and usable if Street View fails.

### Update Copy

Replace dashboard map language:

- From “Prishtina report map”
- To “Street-level evidence view” or “Google Street View context”

Replace badges:

- From “Leaflet / OSM”
- To “Google Street View”

## AI Audit Suggestion Integration

The new Street View system should also support AI suggestions because proactive street audit is now wired end to end.

### Short-Term

In `AuditSuggestionCard.vue`, keep not rendering raw `image_url` if it contains a key. Instead, add a “Open Street View context” action once the Street View component can accept a suggestion target.

### Suggested Shared Type

Create a generic Street View target type:

```ts
interface StreetViewTarget {
  id: string;
  label: string;
  latitude: number;
  longitude: number;
  heading?: number | null;
  pitch?: number | null;
  description?: string | null;
  source: 'report' | 'audit_suggestion';
}
```

Then both dashboard reports and audit suggestions can feed the same Street View viewer.

### Future Audit Detail Usage

The audit suggestion detail page can embed `StreetViewPanel` or a smaller `StreetViewEvidencePanel` using:

- suggestion latitude/longitude
- suggestion heading
- suggestion pitch
- suggestion model explanation
- suggestion attribution

This avoids exposing raw Google Static API URLs containing keys.

## Backend Considerations

### Do We Need Backend Changes?

For a browser-rendered Google Maps JavaScript Street View panel:

- No backend proxy is required for the panorama itself.
- The frontend calls Google Maps JS directly.

Backend changes are only needed if we choose to expose public config via API.

### Optional Public Config Endpoint

If we do not want `VITE_GOOGLE_MAPS_API_KEY`, add:

- `GET /api/v1/config/public`

Response:

```json
{
  "googleMapsBrowserApiKey": "browser-public-key",
  "streetViewSearchRadiusMeters": 50
}
```

This should only return browser-public keys and non-secret config. It must not return database URLs, OpenRouter keys, or backend-only Google keys.

### Existing Static Image URLs

Current audit suggestions may store `image_url` containing Google Static API request URLs. The frontend should not display those URLs directly. Street View JS rendering is the safer evidence path for reviewers.

## Dependency Changes

Remove:

- `leaflet`
- `@types/leaflet`
- `import 'leaflet/dist/leaflet.css'` from `frontend/src/main.ts`

Add:

- `@googlemaps/js-api-loader`
- `@types/google.maps`

Update:

- `frontend/package.json`
- `frontend/package-lock.json`

## Files To Modify

### Frontend

Likely update:

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/main.ts`
- `frontend/src/pages/dashboard/DashboardPage.vue`
- `frontend/src/components/audit/AuditSuggestionCard.vue`
- `frontend/src/utils/map.ts` or replace with generalized coordinate utilities
- `frontend/src/types/map.ts` or replace with Street View types

Likely add:

- `frontend/src/components/streetview/StreetViewPanel.vue`
- `frontend/src/components/streetview/StreetViewFallbackPanel.vue`
- `frontend/src/components/streetview/StreetViewRecordSummary.vue`
- `frontend/src/utils/googleMaps.ts`
- `frontend/src/utils/streetView.ts`
- `frontend/src/types/streetView.ts`

Likely remove or retire:

- `frontend/src/components/maps/ReportMap.vue`
- `frontend/src/components/maps/MapLegend.vue`
- `frontend/src/components/maps/ReportMapPopup.vue`

### Backend

Only if using public config endpoint:

- `backend/app/schemas/config.py`
- `backend/app/api/v1/routes/config.py`
- `backend/app/api/v1/router.py`
- `backend/app/core/config.py`

Otherwise backend can remain unchanged.

### Environment

Add to `.env.example`:

```env
VITE_GOOGLE_MAPS_API_KEY=
```

Add to local `.env` manually with a browser-restricted key. Do not document or commit real key values.

## Implementation Sequence

1. Add Google Maps JS dependencies and remove Leaflet dependencies.
2. Add frontend `VITE_GOOGLE_MAPS_API_KEY` documentation in `.env.example`.
3. Create Google Maps loader utility.
4. Create Street View target types and coordinate helpers.
5. Build `StreetViewFallbackPanel`.
6. Build `StreetViewRecordSummary`.
7. Build `StreetViewPanel` with `StreetViewService` and `StreetViewPanorama`.
8. Replace `ReportMap` usage in `DashboardPage.vue`.
9. Remove Leaflet CSS import from `main.ts`.
10. Retire old map components.
11. Add optional Street View context action/panel for audit suggestion details.
12. Run frontend typecheck/build.
13. Smoke test with selected report and selected AI suggestion coordinates.

## Acceptance Criteria

- No runtime code imports `leaflet`.
- `frontend/package.json` no longer depends on `leaflet` or `@types/leaflet`.
- Dashboard renders a Google Street View panorama for selected reports with valid nearby imagery.
- Dashboard shows a clear fallback for missing key, invalid coordinates, no panorama, or Google API errors.
- Report queue and detail panel remain usable without Street View.
- The selected report changes the Street View target.
- The UI no longer labels the map as Leaflet/OSM.
- Raw Google Static API URLs from audit suggestions are not rendered to users.
- `npm run typecheck` passes.
- `npm run build` passes.

## Risks And Decisions

### Browser Key Exposure

Maps JavaScript API keys are inherently browser-visible. The key must be restricted in Google Cloud Console. Do not expose backend-only keys or AI keys.

### Terms And Imagery Handling

Street View should be rendered through Google’s official JS API. Do not bulk download, cache, store, or use Street View imagery as training/validation data unless terms explicitly allow it.

### Loss Of Marker Overview

Removing Leaflet removes the old all-report marker overview. If an overview remains important, use Google Maps JavaScript map or a list-based nearby-record rail, not Leaflet.

Recommended first pass: Street View primary, queue/detail for selection, no marker overview.

### API Availability

Google Street View coverage may be missing or offset from issue coordinates. The UI must clearly say when no nearby panorama exists.

## Open Questions Before Implementation

- Should we add `VITE_GOOGLE_MAPS_API_KEY`, or should backend expose public config through `GET /api/v1/config/public`?
- Should the dashboard be Street View only, or should it include a small Google Map overview beside the panorama?
- Should audit suggestion detail embed Street View in this same pass, or only dashboard reports first?
- Should the selected AI suggestion heading/pitch be used immediately in Street View POV?
- Should we keep old map components temporarily until the Street View panel is verified, or remove them in the same implementation pass?
