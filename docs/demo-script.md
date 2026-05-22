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
8. Open the AI Street Audit section.
9. Show the demo AI suggestion scenarios and explain that real suggestions will come from the backend/AI endpoint.
10. Open `/report/status/demo-report-pothole-001` in Pitch Mode and show citizen-facing tracking.
11. Close on the civic loop: detect, verify, route, resolve, and measure.

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

