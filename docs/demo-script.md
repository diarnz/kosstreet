# KoStreet Demo Script

## Pitch Emphasis

Primary audience: municipalities.

Core message:

> KoStreet gives Prishtina a municipal command center for detecting, routing, and resolving street-level civic issues.

## Demo Flow

1. Open the KoStreet landing page.
2. Enable Pitch Mode if live backend data is empty.
3. Show the citizen report flow and explain the structured report payload.
4. Open the municipality dashboard.
5. Select the demo pothole report and show category, source, status, department suggestion, and workflow timeline.
6. Show the Prishtina map marker synchronization with the report queue.
7. Explain that workflow status updates call the backend contract and do not fake persistence.
8. Open the AI Street Audit section (`/audit?demo=1`).
9. Select **Prizren old town corridor demo** in the run queue.
10. In the **Scanner** tab, walk through the scan timeline (16 points) and select a flagged point.
11. Show **evidence mode**: severity-colored circles on the static frame, legend, and **AI-estimated location** disclaimer.
12. Select a suggestion in the sidebar (pothole / garbage / sidewalk) and show accept/reject review actions.
13. Optionally select **Legacy four-heading corridor (demo)** to show the legacy banner and **All frames** filmstrip fallback (64 frames).
14. Mention the separate **Demo AI suggestion scenarios** panel as review-only fixtures when the backend is offline.
15. Open `/report/status/demo-report-pothole-001` in Pitch Mode and show citizen-facing tracking.
16. Close on the civic loop: detect, verify, route, resolve, and measure.

## Final Pitch Route

```text
/
/report
/dashboard?demo=1
/audit?demo=1
/report/status/demo-report-pothole-001?demo=1
```

Target duration: under 3 minutes.

Pitch Mode rule:

> Demo fixtures are frontend records for judging reliability. They must be described as demo data, not live backend data or live AI output.

## Prishtina Demo Target

Final route is still to be selected. The route should be recognizable, likely to have street-level imagery coverage, and understandable to judges.

## Street Audit Scanner (Pitch Mode)

- Demo scan path: 16 waypoints along a Prizren corridor fixture.
- Three detections include severity overlays (high / medium / low) on local JPEG evidence.
- **Analyze this view** is hidden in demo mode; on-demand analyze requires a live backend.
- Timeline markers update when suggestions are accepted, rejected, or converted to reports.
- Legacy demo run (`demo-audit-run-legacy`) opens on **All frames** with a banner explaining the old four-heading format.
