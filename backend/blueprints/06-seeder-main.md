# Phase 6 — Seeder + main.py

> **Files to create / modify:**
> - `app/seeds/__init__.py` — new file
> - `app/seeds/demo.py` — new file
> - `app/main.py` — updated (lifespan + static files mount)

> **Depends on:** All previous phases

---

## What this phase does

Two things:

1. **Demo seeder** — populates the database with realistic starting data on first boot so the frontend exits demo mode immediately and shows live data instead of fixtures.
2. **main.py lifespan** — runs the seeder at startup, mounts the `/uploads` static file server.

---

## File 1: `app/seeds/demo.py`

### Idempotency rule

The seeder checks if the `reports` table has any rows before inserting. If rows exist, it returns immediately without doing anything. This means:

- First boot: seeds everything
- Every subsequent restart: does nothing
- Safe to restart the dev server at any time without data duplication

### What gets seeded

#### 5 citizen reports

These use the same IDs as the frontend `demoReports.ts` fixtures. When the frontend calls `GET /api/v1/reports` and receives these IDs in the response, it recognises them and exits demo mode.

| ID | Category | Status |
|---|---|---|
| `demo-report-pothole-001` | pothole | in_progress |
| `demo-report-garbage-001` | garbage | assigned |
| `demo-report-light-001` | broken_streetlight | verified |
| `demo-report-sidewalk-001` | blocked_sidewalk | new |
| `demo-report-sign-001` | damaged_sign | resolved |

Each report also gets its full `workflow_events` history seeded (matching the frontend fixture history) so the workflow timeline panel shows real data immediately.

#### 1 audit run

```
id:           bill-clinton-blvd-001   (UUID literal)
route_name:   Bill Clinton Boulevard
municipality: Prishtina
status:       completed
frames_total: 64
frames_done:  64
created_at:   2026-05-22T00:00:00Z
```

#### 36 audit suggestions from the real AI run

Source: `ai/data/demo/audit_results.json` (read relative to the project root at seed time).

Each detection in the JSON becomes one `AuditSuggestion` row:

| JSON field | DB column |
|---|---|
| `category` | `category` |
| `confidence` | `confidence` |
| `severity` | `severity` |
| `description` | `description` |
| `latitude` | `latitude` + `location` |
| `longitude` | `longitude` + `location` |
| `department` | `department` |
| `heading` | `heading` |
| `pitch` | `pitch` |
| `source` (always `"street_audit"`) | ← not stored, implicit from audit run |
| model name | `settings.ai_model_name` |
| status | always `pending_review` |

The `image_url` for each suggestion is constructed as the Google Street View static URL using the GPS coordinates, heading, and pitch from the detection — so the municipality dashboard can show the actual street view image alongside the AI suggestion.

```
image_url = (
    f"https://maps.googleapis.com/maps/api/streetview"
    f"?size=640x640"
    f"&location={lat},{lng}"
    f"&heading={heading}"
    f"&pitch={pitch}"
    f"&key={settings.google_maps_api_key}"
)
```

---

## File 2: `app/main.py` — updated

### Changes from current state

1. Add `lifespan` context manager that runs the seeder
2. Mount `/uploads` as a static file server so uploaded images are served
3. Keep everything else (CORS, router mount) exactly as-is

### Structure

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with AsyncSessionLocal() as db:
        await seed_demo_data(db)
        await db.commit()
    yield
    # shutdown (nothing to clean up for now)

def create_app() -> FastAPI:
    app = FastAPI(
        title="KoStreet API",
        version="0.1.0",
        description="Backend API for KoStreet civic issue reporting and street audit workflows.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve uploaded citizen report images
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.upload_dir, check_dir=False),
        name="uploads",
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "kostreet-backend"}

    return app

app = create_app()
```

`check_dir=False` on `StaticFiles` prevents a crash if `uploads/` does not exist yet at startup — it gets created the first time a file is saved.

---

## What this phase does NOT do

- Does not run Alembic migrations — tables must already exist (Phase 7 handles that)
- Does not re-seed on every restart — idempotency guard prevents that
- Does not add authentication — out of scope for this hackathon build
