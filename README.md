# KoStreet

**AI-enhanced civic issue reporting for Kosovo municipalities.**

KoStreet is a platform that connects citizens, municipal teams, and computer vision into one street-level operations loop: report an issue, triage it on a map, route it through workflow, and proactively scan corridors with AI Street Audit.

Built for hackathon and pilot deployments, it is scoped for Kosovo-wide geography (not a single-city demo) and designed to feel credible in front of municipal stakeholders.

---

## What it does

### Citizen reporting (`/report`)

Citizens capture a photo, share their location, and submit a structured report. The backend can classify the issue with AI, store photos in Supabase or local disk, and return a tracking page at `/report/status/:id`.

### Municipal dashboard (`/dashboard`)

Operations staff get a Kosovo-centered map, a filterable report queue, workflow status, department routing hints, and metrics — all tuned for quick triage on desktop and mobile.

### AI Street Audit (`/audit`)

Municipal reviewers run or inspect proactive street scans: timeline navigation, evidence frames with detection overlays, confidence and severity cues, and a path from AI suggestion to municipal ticket. Demo runs and pitch mode are available when live backend data is sparse.

### Notifications

In-app notifications surface new reports and workflow events for dashboard users.

---

## How it is organized

KoStreet is a monorepo with three engineering areas:

| Area | Path | Role |
|------|------|------|
| **Frontend** | `frontend/` | Vue 3 + Vite UI — citizen flow, dashboard, audit workspace |
| **Backend** | `backend/` | FastAPI REST API, persistence, uploads, audit orchestration |
| **AI** | `ai/` | Detection pipelines, street-audit planning, model evaluation |

Shared design and API docs live in `docs/`. See [architecture](docs/architecture.md) and [API reference](docs/api.md) for deeper detail.

---

## Tech stack

- **Frontend:** Vue 3, TypeScript, Vite, Vue Router, Pinia, MapLibre GL
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL + PostGIS
- **Storage:** Supabase Storage (recommended for report photos) or local `backend/uploads/`
- **AI:** Python package with OpenCV / optional PyTorch & Ultralytics model deps

---

## Key routes

| Route | Purpose |
|-------|---------|
| `/` | Landing and product overview |
| `/report` | Citizen report flow |
| `/report/status/:id` | Report tracking |
| `/dashboard` | Municipal command center |
| `/audit` | AI Street Audit workspace |
| `/__kostreet-admin/reports` | Hidden admin surface (requires `KOSTREET_ADMIN_SECRET`) |

**API docs (local):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **PostgreSQL** 15+ with **PostGIS** extension
- *(Optional)* Supabase project for durable report photo storage — see [supabase-storage-setup.md](docs/supabase-storage-setup.md)
- *(Optional)* `GOOGLE_MAPS_API_KEY` / `MAPBOX_ACCESS_TOKEN` for Street View and map imagery integrations
- *(Optional)* `KOSTREET_AI_OPENROUTER_API_KEY` for live AI classification via OpenRouter

---

## Getting started

### 1. Clone and configure environment

```bash
git clone https://github.com/diarnz/kosstreet.git
cd kosstreet
cp .env.example .env
```

Edit `.env` at the repo root. Minimum for local dev:

```env
KOSTREET_ENV=development
KOSTREET_DATABASE_URL=postgresql+asyncpg://kostreet:kostreet@localhost:5432/kostreet
KOSTREET_DATABASE_URL_SYNC=postgresql+psycopg2://kostreet:kostreet@localhost:5432/kostreet
KOSTREET_CORS_ORIGINS=http://localhost:5173,http://localhost:5174
KOSTREET_ADMIN_SECRET=change-me-to-a-long-random-secret
```

Leave `VITE_API_BASE_URL` unset during local development — the Vite dev server proxies `/api` to the backend and avoids CORS issues.

### 2. Database

Create the database and enable PostGIS:

```sql
CREATE USER kostreet WITH PASSWORD 'kostreet';
CREATE DATABASE kostreet OWNER kostreet;
\c kostreet
CREATE EXTENSION IF NOT EXISTS postgis;
```

Run migrations from the backend directory:

```bash
cd backend
python -m venv .venv
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
```

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
```

### 3. Start the backend

From `backend/` with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

Backend listens on **http://localhost:8000**. On startup it seeds demo data and migrates any legacy local uploads.

Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend listens on **http://localhost:5173** and proxies API calls to the backend.

Open the app at [http://localhost:5173](http://localhost:5173).

### 5. Optional — AI package

Only needed for AI pipeline work or model evaluation, not for the standard web demo:

```bash
cd ai
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
# For model weights / inference:
pip install -e ".[models]"
```

### 6. Optional — report photos on every device

Without Supabase, photos are stored under `backend/uploads/` and served through the backend image proxy (`GET /api/v1/reports/{id}/image`). That works locally but not across deployed devices.

For production or multi-device testing, configure Supabase Storage — full steps in [docs/supabase-storage-setup.md](docs/supabase-storage-setup.md).

### Quick reference

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |

**Demo / pitch flow:** see [docs/demo-script.md](docs/demo-script.md) — use `?demo=1` on dashboard and audit routes when you want labeled demo scenarios.

**Helper script:** `scripts/run_local.sh` prints the same startup commands if you prefer a checklist in the terminal.

---

## Further reading

- [API reference](docs/api.md)
- [Architecture](docs/architecture.md)
- [Supabase photo storage](docs/supabase-storage-setup.md)
- [Demo script](docs/demo-script.md)
- [Frontend style guide](docs/frontend-style-guide.md)

---

## License

See repository license terms. Platform imagery (e.g. Google Street View) may be subject to separate provider terms — use audit and training features accordingly.
