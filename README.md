# KoStreet Hackathon Blueprint

## Challenge Context

Challenge: **AI-Enhanced Civic Issue Reporting (Smart Municipality)**

The challenge asks for a simple, mobile-first civic issue reporting solution that allows citizens to report local problems by taking a photo, while using AI and location-based tools to classify, structure, and route reports to the responsible municipal department.

Expected outcome:

- Issue capture
- AI-supported categorization
- Basic location tagging
- Simple workflow or dashboard for municipal follow-up
- Transparency for citizens tracking what happens after reporting

## Product Concept

**KoStreet** is a civic issue intelligence platform for Kosovo municipalities.

It combines:

- A mobile-first citizen reporting app
- AI-based issue classification
- Geolocation and structured ticket creation
- Municipal dashboard and workflow management
- A proactive AI street-audit agent that scans 360-degree street imagery to detect likely civic defects such as potholes, garbage, broken lights, damaged sidewalks, and other street-level problems

Positioning:

> KoStreet helps municipalities move from reactive complaint handling to proactive street maintenance by combining citizen reports, AI visual detection, geolocation, and transparent ticket tracking.

The base product satisfies the official challenge. The standout layer is the **AI Street Audit Agent**, which can proactively surface issues before citizens report them.

## Important Constraints

Google Street View can be useful for the hackathon demo, but it must be used carefully.

Current Google Maps Platform terms restrict storing, bulk downloading, indexing, or using Street View content to train, test, validate, or fine-tune ML models. For the hackathon, the safer approach is:

- Use Street View only in a compliant demo flow
- Store derived issue metadata only where allowed
- Do not train or fine-tune models on Google Street View imagery unless terms explicitly allow it
- Prefer citizen-uploaded images, team-captured images, or other legally usable imagery for model evaluation and demos
- Keep a fallback plan if Kosovo Street View coverage is incomplete or outdated
- Street View image retrieval must be handled through approved Google Maps Platform APIs or another legally usable imagery source; the AI model analyzes images after retrieval and does not fetch imagery by itself

## Approved Technology Stack

This project will use a three-part architecture: frontend, backend, and AI engineering. The goal is to keep responsibilities clean, make parallel team development easier, and avoid mixing UI, API, and model logic in the same layer.

Frontend:

- Vite.js
- Vue.js
- TypeScript
- Vue Router
- Pinia for frontend state management if needed
- Tailwind CSS or a lightweight custom CSS system for fast mobile-first UI
- Map rendering through Google Maps, Mapbox, or Leaflet depending on API and licensing decisions
- Browser geolocation and camera/photo upload APIs

Backend:

- Python
- FastAPI
- Pydantic for request and response validation
- SQLAlchemy or SQLModel for database access
- Alembic for migrations if PostgreSQL is used
- PostgreSQL with PostGIS for production-style geospatial data, or SQLite for fast local MVP development
- Local filesystem or object storage abstraction for uploaded images
- REST API between frontend, backend, and AI services

AI Engineering:

- Python
- OpenCV for image preprocessing and annotation
- Pillow for image handling
- PyTorch or Ultralytics YOLO for object detection if a detector is used
- Google's Gemma family, especially PaliGemma for vision-language analysis, as a candidate model for inspecting street-level images and identifying civic issues
- Zero-shot or multimodal vision model integration if training time is limited
- Geospatial post-processing for deduplication and confidence aggregation
- Human-in-the-loop verification for low-confidence detections

Development and operations:

- Monorepo with separated `frontend`, `backend`, and `ai` folders
- Environment-based configuration through `.env` files
- Shared API contracts documented in backend OpenAPI docs
- Seed data for demos
- Clear separation between demo data, citizen-uploaded data, and restricted third-party imagery

## Local Development

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

AI package:

```bash
cd ai
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Local helper:

```bash
./scripts/run_local.sh
```

## Phase 0: Alignment And Feasibility

Goal: lock the exact product scope before implementation.

Confirmed Phase 0 decisions:

- Target municipality: Prishtina
- MVP issue classes: all listed classes
- Pitch emphasis: municipalities
- Fallback data source strategy: use all available approved sources to maximize accuracy and demo resilience

MVP issue classes:

- Pothole
- Garbage or illegal dumping
- Broken streetlight
- Blocked sidewalk
- Damaged sign
- Other

Fallback data sources:

- Citizen photo uploads
- Uploaded test photos
- Open imagery
- Team-captured phone footage
- Team-captured 360-degree footage
- Google Street View or other street-level imagery where usage terms allow

Remaining feasibility tasks:

- Check Street View coverage for selected streets
- Check Google API usage limits, cost, and legal constraints
- Choose the exact Prishtina demo route or street segment
- Confirm which fallback sources can be legally stored, analyzed, and shown in the live demo

Deliverables:

- Final scope document
- Demo route
- Issue taxonomy
- Team green light before development

## Phase 1: Product Strategy

KoStreet should have two core user experiences and one standout AI layer.

Citizen experience:

- Citizen takes or uploads a photo
- Location is attached
- AI classifies the issue
- Citizen confirms or edits category
- Ticket is submitted
- Citizen can track status

Municipality experience:

- Officials view incoming reports
- Reports are categorized, geolocated, and prioritized
- Issues are routed to the right department
- Staff update workflow status
- Dashboard shows hotspots and unresolved issues

AI Street Audit Agent:

- Scans selected street imagery
- Looks around 360 degrees
- Detects possible defects
- Creates AI-suggested issues
- Sends issues to municipal dashboard for human verification

Why this can stand out:

- It satisfies the challenge requirements directly
- It adds proactive issue discovery
- It creates practical municipal value
- It gives judges a clear and memorable live demo

## Phase 2: Technical Architecture

The project should be structured as a professional monorepo with three primary application areas.

High-level architecture:

```text
kostreet/
├── README.md
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   │   ├── citizen/
│   │   │   ├── dashboard/
│   │   │   └── audit/
│   │   ├── composables/
│   │   ├── types/
│   │   └── styles/
│   └── public/
├── backend/
│   ├── pyproject.toml
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── db/
│   │   ├── storage/
│   │   └── integrations/
│   └── tests/
├── ai/
│   ├── pyproject.toml
│   ├── src/
│   │   ├── kostreet_ai/
│   │   │   ├── inference/
│   │   │   ├── detection/
│   │   │   ├── preprocessing/
│   │   │   ├── street_audit/
│   │   │   ├── geospatial/
│   │   │   ├── evaluation/
│   │   │   └── config.py
│   ├── models/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── demo/
│   ├── notebooks/
│   └── tests/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── demo-script.md
└── scripts/
    ├── seed_demo_data.py
    └── run_local.sh
```

Frontend responsibilities:

- Citizen mobile-first reporting flow
- Photo capture or upload
- Browser geolocation
- AI result confirmation UI
- Citizen ticket tracking UI
- Municipality dashboard
- Map visualization, filters, and report details
- AI Street Audit review interface

Backend responsibilities:

- Authentication or lightweight demo access control if needed
- Report creation and retrieval
- Image upload handling
- Ticket workflow and status transitions
- Department routing
- Persistence for reports, detections, departments, and audit runs
- API endpoints consumed by the Vue frontend
- Orchestration calls into the AI layer
- Google Street View or alternative street-imagery API integration, subject to usage terms and demo constraints

AI responsibilities:

- Image preprocessing
- Issue classification or object detection
- PaliGemma or Gemma-based image understanding for street-level defect recognition
- Bounding box generation if supported by the selected model
- Confidence scoring
- Severity estimation
- Street audit scan planning
- 360-degree heading and pitch sampling logic
- Detection deduplication across nearby views
- Municipal-ready issue summaries

Core data flow:

```text
Citizen photo / street audit image
        ↓
Backend upload or audit orchestration
        ↓
AI inference and validation
        ↓
Structured detection result
        ↓
Backend report or AI-suggested issue
        ↓
Municipal dashboard and ticket workflow
```

Core backend modules:

- Report capture
- AI inference orchestration
- Routing engine
- Ticket workflow
- Geo dashboard API
- Street audit job management

Core AI modules:

- Detector
- Classifier fallback
- Street audit scout
- Detection verifier
- Deduplication engine
- Severity scorer
- Ticket summarizer

## Phase 3: Data And AI Plan

Initial issue taxonomy:

- Pothole: road-surface damage, crater, asphalt break
- Garbage: bags, scattered waste, dumping, illegal disposal
- Broken light: damaged lamp pole, visibly off light at night, missing fixture
- Damaged sidewalk: cracked pavement, obstruction
- Damaged sign or infrastructure: bent sign, missing cover, damaged pole

Model strategy:

- Start with a real pretrained vision model or object detector
- Use Google's Gemma family as the preferred open-weight model direction for AI reasoning
- Use PaliGemma as the preferred candidate for vision-language inspection of street-level images, including potholes, garbage, damaged signs, broken lights, and other visible civic defects
- Use zero-shot or prompt-based vision for fast category support if training time is short
- Combine PaliGemma-style visual reasoning with a detector pipeline if bounding boxes or localization are required
- Fine-tune only if legally usable data and time are available
- Keep human verification in the loop for low-confidence detections
- Store class, confidence, severity, bounding box, timestamp, source, and location

Data source rule:

- Citizen-uploaded and team-captured images can be used normally if permissions are clear
- Google Street View imagery should not be stored or used for model training unless terms allow it
- Google Street View images, when used, are fetched by the backend integration and then passed into the AI pipeline for transient analysis

## Phase 4: Citizen Reporting MVP

User flow:

1. Citizen opens the mobile web app.
2. Citizen taps "Report Issue".
3. Citizen takes or uploads a photo.
4. App captures GPS coordinates.
5. AI detects issue type and confidence.
6. Citizen confirms or edits category.
7. Citizen submits report.
8. Citizen receives tracking ID.
9. Report appears on municipal dashboard.

Required screens:

- Landing page
- Report camera or upload screen
- AI result confirmation screen
- Submission success and tracking screen
- Optional citizen status lookup screen

Minimum backend entities:

- Report
- Image
- Detection
- Department
- TicketStatus
- AuditSource

## Phase 5: Street View 360-Degree Audit Agent

Agent goal:

Scan selected streets automatically and surface likely defects before citizens report them.

Workflow:

1. Input route, street segment, or bounding box.
2. Generate scan points every fixed distance, such as 20 to 50 meters.
3. For each point, request panorama metadata.
4. If a panorama exists, sample views around 360 degrees using headings such as `0`, `60`, `120`, `180`, `240`, and `300`.
5. Use one or more pitches, likely `-10`, `0`, and possibly `10`.
6. Fetch the selected Street View frame through the approved imagery API flow.
7. Pass the frame into the AI pipeline.
8. Use PaliGemma or the selected Gemma-based vision model to inspect the image for visible civic issues.
9. Use the detector pipeline to localize defects when bounding boxes are needed.
10. Convert detections into candidate issues.
11. Deduplicate nearby detections across headings and neighboring panoramas.
12. Assign severity and confidence.
13. Mark result as `AI-suggested`.
14. Send result to dashboard for municipal verification.

Demo mode:

- Pick one route
- Show the agent scanning frames
- Show bounding boxes or highlights
- Show generated map markers
- Show one-click conversion from AI suggestion to municipal ticket

Known limitations:

- Street View imagery may be outdated
- Kosovo coverage may be incomplete
- Broken streetlights are difficult to detect from daytime imagery
- Human verification remains necessary

## Phase 6: Municipal Dashboard

Core views:

- Map with issue markers
- List or table of reports
- Filters by type, status, severity, source, and department
- Report detail page with image, AI result, location, confidence, and citizen note
- Workflow controls:
  - New
  - Verified
  - Assigned
  - In Progress
  - Resolved
  - Rejected

Department routing:

- Pothole -> Roads/Public Works
- Garbage -> Sanitation
- Broken light -> Electrical/Infrastructure
- Sidewalk -> Urban Maintenance
- Sign or infrastructure damage -> Public Works

Analytics cards:

- Total reports
- Unresolved issues
- Average severity
- Top affected areas
- Reports by department

Standout dashboard feature:

- Dedicated "AI Street Audit" tab for automatically detected issues, separated from citizen-submitted reports

## Phase 7: AI Agent Layer

The agent should be more than a model call. It should perform multiple responsibilities.

Agent roles:

- Scout: scans route imagery
- Detector: runs visual defect detection
- Verifier: checks confidence, duplicate detections, and location consistency
- Router: assigns department and urgency
- Summarizer: creates municipal-ready ticket descriptions
- Analyst: identifies hotspots and recurring issue zones

Example generated ticket:

> Possible pothole detected on Bill Clinton Boulevard. Confidence: 82%. Visible road-surface depression near right lane. Suggested department: Roads/Public Works. Priority: Medium. Source: AI Street Audit.

## Phase 8: Demo Script

Pitch story:

1. Citizens see problems every day, but reporting is slow.
2. Municipalities receive messy and unstructured reports.
3. KoStreet turns every report into a structured, geolocated, AI-routed ticket.
4. Demo citizen submits a pothole photo.
5. AI classifies it and creates a ticket.
6. Municipality dashboard receives it instantly.
7. Then show the standout feature: KoStreet does not wait for citizens.
8. Run the Street Audit Agent over a Kosovo street segment.
9. Show AI-detected pothole or garbage marker.
10. Convert the detection into a municipal task.
11. End with transparent tracking from report to resolution.

Judge-facing message:

> This is not just reporting. It is a civic intelligence loop: detect, verify, route, resolve, and measure.

## Phase 9: Build Order

Recommended implementation order:

1. Repo setup and stack decision
2. Database schema
3. Report creation API
4. Mobile photo upload flow
5. AI inference endpoint
6. Dashboard map and list
7. Ticket workflow
8. Street View or 360-degree scan prototype
9. Detection visualization with bounding boxes
10. Analytics and hotspots
11. Seeded demo data
12. Pitch polish and full rehearsal

Rationale:

Build citizen reporting and the dashboard first. Then add the AI Street Audit Agent. This keeps the product aligned with the challenge while still giving the team a standout feature for the pitch.

## Phase 10: Pitch Assets

Required assets:

- 5 to 7 slide pitch deck
- 90-second product story
- 3-minute live demo
- Architecture diagram
- Before and after municipal workflow diagram
- Kosovo-specific map or demo route
- Clear impact metrics

Impact metrics to highlight:

- Faster civic issue reporting
- Better categorization
- Automatic municipal routing
- Reduced duplicate reports
- Proactive street issue discovery
- Transparent status tracking

## Key Risks

- Google Street View compliance may limit storage, bulk analysis, and ML usage
- Kosovo Street View coverage may be incomplete or not fresh enough
- Broken streetlights may require night imagery or citizen reports
- Model accuracy may vary across potholes, garbage, lighting, and road conditions
- Human verification is required for responsible municipal workflows
- Time pressure means the core reporting workflow must be prioritized before advanced scanning

## Recommended Direction

Build KoStreet as **citizen reporting first** and **AI Street Audit Agent second**.

This gives the project a strong foundation that matches the challenge, while adding a proactive AI capability that can make the demo memorable and competitive.

## Next Step Gate

Before implementation, the team should approve:

- Final technology stack
- MVP feature scope
- Demo location and route
- AI model approach
- Data source plan
- Pitch narrative

No code implementation should begin until this gate is approved.
