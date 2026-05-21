# KoStreet Architecture

KoStreet is organized as a monorepo with three independent engineering areas.

## Frontend

Location: `frontend/`

Responsibilities:

- Mobile-first citizen report flow
- Municipality dashboard
- AI Street Audit review UI
- API client and frontend state
- Map and geolocation interactions

Primary stack:

- Vite.js
- Vue.js
- TypeScript
- Vue Router
- Pinia

## Backend

Location: `backend/`

Responsibilities:

- FastAPI application
- Versioned REST API
- Report and audit workflow orchestration
- Persistence layer boundaries
- Image upload and storage boundaries
- Street-imagery integration boundaries

Primary stack:

- Python
- FastAPI
- Pydantic
- SQLAlchemy or SQLModel when persistence is added

## AI Engineering

Location: `ai/`

Responsibilities:

- Image preprocessing
- Detection result contracts
- PaliGemma/Gemma-based image understanding integration
- Object detection pipeline integration
- Street audit planning
- Geospatial deduplication and scoring

Primary stack:

- Python
- PaliGemma/Gemma candidate model direction
- OpenCV
- Pillow
- PyTorch/Transformers or Ultralytics when model integration is added

## Data Flow

```text
Frontend upload or audit trigger
        ↓
Backend API
        ↓
Storage and orchestration
        ↓
AI inference pipeline
        ↓
Structured detection result
        ↓
Backend ticket/report workflow
        ↓
Municipal dashboard
```

## Team Ownership

- Frontend team owns everything inside `frontend/`.
- Backend team owns API contracts, persistence, uploads, and orchestration inside `backend/`.
- AI team owns model pipelines, image analysis, scan planning, and evaluation inside `ai/`.
- Shared documents live inside `docs/`.
- Utility scripts live inside `scripts/`.

