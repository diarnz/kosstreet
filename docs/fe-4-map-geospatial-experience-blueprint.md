# FE-4 Map And Geospatial Experience Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-4: Map And Geospatial Experience**.

FE-0 created the frontend foundation. FE-1 created the visual system. FE-2 created real citizen report submission. FE-3 created the municipality dashboard backed by real reports. FE-4 turns report coordinates into an operational map experience for Prishtina.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Make location central to the municipality dashboard without introducing fake geospatial behavior.

Primary outcome:

> After FE-4, Prishtina municipal users should be able to open `/dashboard`, see real reports rendered as map markers from `GET /api/v1/reports`, click markers to inspect reports, select reports from the queue to highlight them on the map, and keep using the dashboard if the map provider fails.

## Critical Backend Reality Check

Current backend endpoints:

```text
GET /api/v1/reports
POST /api/v1/reports
```

Current backend report fields available to the frontend:

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

Current backend does **not** yet provide:

- Geospatial bounding-box queries
- Server-side viewport filtering
- Server-side clustering
- Reverse geocoding
- Street names
- Administrative zones
- Severity scoring
- Map tiles
- Route geometry
- Street View image metadata

Therefore FE-4 should implement:

- Real marker rendering from fetched report coordinates
- Client-side map/list synchronization
- Client-side viewport fitting
- Client-side marker styling by real report category/status/source
- Client-side graceful fallback if the map provider fails
- Honest empty states when no valid coordinates exist

FE-4 should **not** implement fake neighborhoods, fake heatmaps, fake clusters, fake routes, fake street names, or fake issue density.

## Provider Decision

Recommended FE-4 provider:

```text
Leaflet + OpenStreetMap tiles
```

Reasoning:

- Fastest to integrate for the hackathon.
- No API key required for basic local/demo use.
- Lower risk than Google Maps billing/key setup during judging.
- Good enough for Prishtina report markers and dashboard synchronization.
- Keeps Google Street View work conceptually separate from dashboard map rendering.

Package:

```text
leaflet
@types/leaflet
```

Important limitation:

- OpenStreetMap public tile servers should not be abused for heavy production traffic.
- For the hackathon demo, light local usage is acceptable.
- If productionizing, switch tile hosting to a paid provider or self-hosted tiles.

Alternative providers intentionally deferred:

- Google Maps: useful later if Google Maps Platform keys and terms are finalized.
- Mapbox: useful later if custom styling and hosted tiles are preferred.

## Non-Goals

FE-4 will not implement:

- Google Street View 360 scanning
- AI detection overlays
- Heatmaps
- Marker clustering
- Backend geospatial APIs
- Route optimization
- Reverse geocoding
- Drawing tools
- Report creation from map clicks
- Status mutation
- Department assignment mutation
- Offline map tiles

These belong to later frontend, backend, or AI phases.

## User Flow

Municipality map flow:

```text
/dashboard
  ↓
Fetch real reports from GET /api/v1/reports
  ↓
Render metrics, filters, queue, and detail panel
  ↓
Render map centered on Prishtina
  ↓
Render one marker per report with valid coordinates
  ↓
Municipal user clicks marker
  ↓
Corresponding report becomes selected in queue/detail panel
  ↓
Municipal user selects report from queue
  ↓
Corresponding map marker becomes highlighted and map pans into view
```

Fallback flow:

```text
/dashboard
  ↓
Map provider fails or cannot initialize
  ↓
Dashboard remains fully usable
  ↓
Show list-first fallback panel with clear explanation
```

## Map Scope

FE-4 should render a real interactive map inside the existing dashboard map workspace.

Default map behavior:

- Center on Prishtina.
- Use a sensible city-level zoom.
- Fit bounds to real report markers when reports exist.
- Fall back to default Prishtina viewport when no valid report coordinates exist.
- Keep dashboard filters connected to both the queue and visible markers.

Recommended default viewport:

```text
Latitude: 42.6629
Longitude: 21.1655
Zoom: 13
```

Coordinate rules:

- A report is mappable only when latitude and longitude are finite numbers.
- Invalid coordinates should not crash the map.
- Invalid-coordinate reports remain visible in the queue and detail panel.
- The map should show a small count or note when reports are hidden from the map because coordinates are invalid.

## Dashboard Integration

FE-4 should replace the FE-3 placeholder with a real map panel.

The dashboard should have these synchronized surfaces:

- Metrics from all fetched reports.
- Filters applied to queue and map markers.
- Queue of filtered reports.
- Selected report detail panel.
- Map markers for filtered reports with valid coordinates.

Selection rules:

- Clicking a queue row selects the report and highlights its marker.
- Clicking a marker selects the report and updates the detail panel.
- If a selected report is filtered out, the first filtered report should become selected or selection should clear.
- If a selected report has invalid coordinates, the detail panel still works and the map shows no highlighted marker.

Refresh rules:

- Refresh still calls `GET /api/v1/reports`.
- After refresh, preserve the selected report if it still exists.
- If it no longer exists, select the first filtered report or clear selection.
- Recompute map markers only from refreshed real data.

## Marker Design

Markers should be clear and operational, not decorative.

Marker encoding:

- Category should drive the marker icon/glyph or border.
- Status should drive the marker fill or ring.
- Source should be visible in popup/detail copy, not necessarily in every marker shape.
- Selected marker should have a stronger ring, scale, or z-index.

Recommended marker labels:

- Pothole: road defect
- Garbage: sanitation issue
- Broken streetlight: lighting
- Blocked sidewalk: pedestrian obstruction
- Damaged sign: signage
- Other: intake review

Marker style rules:

- Use existing FE-1 palette semantics.
- Avoid saturated rainbow marker colors.
- Keep selected marker visibly distinct.
- Do not show fake severity if severity is not in the backend payload.
- Do not show fake AI confidence for citizen reports when confidence is missing.

Popup behavior:

- Popup opens on marker click.
- Popup should show category, status, source, short description if present, coordinates, and created time.
- Popup should include a clear “View details” or “Selected in queue” affordance.
- Popup content must come from the real report object.

## Components To Add

```text
frontend/src/components/maps/ReportMap.vue
frontend/src/components/maps/MapFallbackPanel.vue
frontend/src/components/maps/ReportMapPopup.vue
frontend/src/components/maps/MapLegend.vue
```

Optional if needed:

```text
frontend/src/components/maps/MapMarkerIcon.ts
frontend/src/composables/useLeafletMap.ts
frontend/src/composables/useMapBounds.ts
frontend/src/types/map.ts
```

## Components To Modify

```text
frontend/src/pages/dashboard/DashboardPage.vue
frontend/src/stores/reports.ts
frontend/src/styles/main.css
frontend/src/styles/tokens.css
frontend/src/styles/utilities.css
```

Potential modification:

```text
frontend/src/components/dashboard/ReportQueue.vue
```

Only modify `ReportQueue.vue` if keyboard/list selection needs an additional scroll or selected-state refinement for map synchronization.

## Types

Add map-specific types only if they clarify component contracts.

Recommended:

```ts
export interface MapPoint {
  id: string;
  latitude: number;
  longitude: number;
}

export interface MapViewport {
  center: {
    latitude: number;
    longitude: number;
  };
  zoom: number;
}

export interface HiddenMapReport {
  id: string;
  reason: 'invalid_coordinates';
}
```

Do not duplicate the full `ReportSummary` type as a separate map report model unless the transformation is necessary.

## Store Updates

The reports store already owns:

- Fetched reports
- Filter state
- Selected report ID
- Filtered reports
- Metrics
- Refresh state
- Error state

FE-4 should add only map-supporting derived behavior if needed:

- `mappableFilteredReports`
- `hiddenMapReports`
- `selectedMappableReport`

Rules:

- Keep backend fetching in `reports.ts`.
- Keep Leaflet map instance state inside map components/composables, not the Pinia report store.
- Do not store Leaflet objects in Pinia.
- Do not persist map viewport until there is a product reason.

## Composable Design

If map lifecycle code becomes more than a few lines, add:

```text
frontend/src/composables/useLeafletMap.ts
```

Responsibilities:

- Initialize Leaflet map after container mount.
- Add base tile layer.
- Clean up map on unmount.
- Expose map instance safely to the component.
- Handle initialization errors.

Non-responsibilities:

- Fetch reports.
- Own selected report state.
- Own dashboard filters.
- Create fake markers.

## ReportMap Component Contract

`ReportMap.vue` should be a controlled component.

Props:

```ts
reports: ReportSummary[];
selectedReportId: string | null;
isLoading?: boolean;
```

Emits:

```ts
select: [reportId: string]
```

Behavior:

- Initialize a Leaflet map.
- Render markers for reports with valid coordinates.
- Fit bounds when mappable reports change.
- Highlight selected marker.
- Emit `select` when marker is clicked.
- Render fallback if Leaflet initialization fails.
- Render empty map state if there are no mappable reports.

No-stub rule:

- Every marker must correspond to a real `ReportSummary` from the backend response.

## MapFallbackPanel Component

Purpose:

- Keep the dashboard useful if the map cannot load.

Triggers:

- Leaflet import/init failure.
- Map container init failure.
- Tile loading issues if detectable.

Content:

- Clear explanation that the report list and detail panel remain available.
- Count of reports still available in the queue.
- Optional retry action if practical.

Rules:

- Do not hide reports because the map failed.
- Do not block dashboard usage.
- Do not present fallback as a fake map.

## MapLegend Component

Purpose:

- Explain marker category/status semantics without overloading marker labels.

Content:

- Category indicators.
- Status indicators.
- Selected marker indicator.

Rules:

- Use existing category/status labels from `reportFormatting.ts`.
- Do not introduce category labels in multiple places.
- Keep the legend compact so it does not dominate the dashboard.

## CSS And Visual Requirements

Map panel should feel integrated with the FE-1 visual direction.

Requirements:

- Use the existing card/panel surface language.
- Keep map height usable on laptop demo screens.
- Use rounded corners and subtle borders around the map container.
- Ensure Leaflet controls are readable against the premium civic theme.
- Avoid heavy overlays that make the map hard to use.

Recommended sizes:

- Desktop dashboard map height: 28rem to 34rem.
- Tablet map height: 24rem to 28rem.
- Mobile map height: 20rem to 24rem.

Responsive behavior:

- On desktop, map should sit above or alongside queue/detail in a way that supports quick triage.
- On tablet/mobile, map can stack above the queue.
- The report queue and detail panel must remain usable even if the map is vertically compact.

## Accessibility Requirements

Leaflet maps are not fully accessible by default, so FE-4 must add supporting accessible controls and text.

Requirements:

- Map panel has a clear heading.
- Map container has an accessible label.
- Marker popups use readable text.
- Queue remains the accessible primary way to navigate reports.
- Marker click behavior is mirrored by keyboard-accessible queue selection.
- Color is not the only way category/status is communicated.
- Fallback and empty states are readable by screen readers.

Practical rule:

- Do not rely on map markers as the only way to access report details.

## Data Integrity Rules

Allowed:

- Real markers from real backend reports.
- Client-side marker filtering based on existing dashboard filters.
- Client-side marker selection and map pan.
- Client-side map bounds computed from real marker coordinates.
- Honest invalid-coordinate counts.

Not allowed:

- Fake markers.
- Fake heatmaps.
- Fake clustering.
- Fake route lines.
- Fake municipal zones.
- Fake street names.
- Fake severity.
- Fake density statistics.
- Fake “nearby reports” if not computed from real data.
- Console-only map interactions.
- Buttons that appear active but do nothing.

## Error Handling

FE-4 should handle:

- Backend unavailable.
- No reports.
- Reports with invalid coordinates.
- Leaflet module failure.
- Map initialization failure.
- Tile load issues where detectable.

Expected UX:

- Backend error: existing dashboard error state remains.
- No reports: map shows Prishtina viewport and an empty state.
- Invalid coordinates only: map shows Prishtina viewport and explains no reports can be mapped.
- Map init failure: fallback panel appears, queue/detail remain usable.
- Tile issue: fallback copy or visible map shell should explain the map layer could not load if this can be detected reliably.

## Implementation Sequence

1. Install `leaflet` and `@types/leaflet`.
2. Add Leaflet CSS import in the frontend entry or map component.
3. Add map-specific types if needed.
4. Add coordinate validation utility.
5. Add `MapFallbackPanel`.
6. Add `MapLegend`.
7. Add `ReportMapPopup`.
8. Add `ReportMap`.
9. Add Leaflet marker icon generation using existing category/status semantics.
10. Add map bounds fitting for real mappable reports.
11. Add selected marker highlighting.
12. Connect marker click to `reportsStore.selectReport`.
13. Replace FE-3 dashboard placeholder with `ReportMap`.
14. Add hidden invalid-coordinate messaging.
15. Confirm dashboard filters affect both queue and map markers.
16. Confirm queue selection highlights/pans to the marker.
17. Confirm marker selection updates queue/detail.
18. Run frontend build.
19. Run backend and frontend together.
20. Verify with real backend reports.

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
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Required backend checks:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/v1/reports
```

Manual dashboard flow:

1. Open `/dashboard`.
2. Confirm real reports are fetched.
3. Confirm map renders centered on Prishtina.
4. Confirm one marker appears for each filtered report with valid coordinates.
5. Confirm no marker appears for invalid-coordinate reports.
6. Click a queue report with valid coordinates.
7. Confirm the map marker highlights and pans into view.
8. Click a marker.
9. Confirm the report detail panel updates to that report.
10. Apply status, category, source, and search filters.
11. Confirm queue and map marker set update together.
12. Clear filters.
13. Confirm marker set returns to all mappable reports.
14. Stop the map provider from loading if practical.
15. Confirm fallback panel appears and queue/detail remain usable.
16. Resize to mobile width and confirm map, queue, and detail stack cleanly.

Expected behavior with the current FE-2 test reports:

- Reports load from `GET /api/v1/reports`.
- Pothole reports with Prishtina coordinates appear as real markers.
- Selecting the pothole in the queue highlights the corresponding marker.
- Clicking the pothole marker selects the corresponding report in the detail panel.
- Metrics remain unchanged because FE-4 only changes geospatial presentation.

## Testing Notes

Automated testing is optional for FE-4 unless the team adds a test runner.

If tests are added later, prioritize:

- Coordinate validation utility.
- Report-to-marker transformation.
- Hidden invalid-coordinate count.
- Store derived mappable reports.

Do not over-invest in testing Leaflet internals during the hackathon.

## Risks And Mitigations

Risk: Map provider setup slows the team down.

Mitigation:

- Use Leaflet/OpenStreetMap for FE-4 and defer Google Maps/Mapbox decisions.

Risk: Public tile server fails during demo.

Mitigation:

- Keep queue/detail fully functional and show a polished fallback panel.

Risk: Judges expect Street View in this phase.

Mitigation:

- Explain clearly that FE-4 is the municipality geospatial dashboard, while Street View AI audit belongs to FE-5 and AI/backend phases.

Risk: Map markers look like fake demo data.

Mitigation:

- Every marker is generated from real backend report IDs and coordinates.

Risk: Accessibility suffers because map interactions are mouse-first.

Mitigation:

- Keep the queue as the primary accessible report navigation surface.

Risk: Too many markers clutter the map.

Mitigation:

- FE-4 can defer clustering because the MVP report count is low. If report count becomes high, add clustering in a later phase using real report data only.

## FE-4 Acceptance Criteria

FE-4 is complete when:

- `npm run build` passes.
- `/dashboard` still fetches real reports from `GET /api/v1/reports`.
- The FE-3 map placeholder is replaced by a real interactive map.
- Map defaults to the Prishtina viewport.
- Markers are rendered only from real reports with valid coordinates.
- Marker styling reflects real category/status/source data without inventing severity.
- Clicking a marker selects the real report in the dashboard.
- Selecting a report from the queue highlights or pans to its marker when coordinates are valid.
- Dashboard filters update both the queue and map markers.
- Invalid-coordinate reports do not crash the map and remain visible in the queue.
- Map failure does not break the dashboard.
- No fake markers, heatmaps, clusters, routes, zones, street names, or density statistics are introduced.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to map provider choice, Street View scope, backend geospatial assumptions, or clustering scope should be agreed before coding.
