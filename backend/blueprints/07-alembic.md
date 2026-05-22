# Phase 7 — Alembic Migration + pyproject.toml

> **Files to create / modify:**
> - `alembic.ini` — new (Alembic config file, lives at `backend/`)
> - `alembic/env.py` — replaces the `.gitkeep` placeholder
> - `alembic/script.py.mako` — new (standard Alembic template)
> - `alembic/versions/0001_initial.py` — new (first migration)
> - `pyproject.toml` — updated with all new dependencies

> **Depends on:** Phase 0 (all ORM models and Base must exist)

---

## What this phase does

Creates the actual PostgreSQL tables. Alembic reads the ORM models defined in Phase 0 and generates the SQL to create every table, index, and constraint.

This is the last phase — by the time this runs, all code is written, and you just need the database tables to exist before starting the server.

---

## Prerequisites

Before running the migration, these must be true:

```sql
-- PostgreSQL running on localhost:5432
-- Database exists:
CREATE DATABASE kostreet;

-- User exists:
CREATE USER kostreet WITH PASSWORD 'kostreet';
GRANT ALL PRIVILEGES ON DATABASE kostreet TO kostreet;

-- PostGIS must be installed on the server.
-- The migration enables it automatically, but PostGIS must be installed.
-- On Ubuntu: sudo apt install postgresql-15-postgis-3
-- On macOS (brew): brew install postgis
```

---

## File 1: `alembic.ini`

Standard Alembic config file. Key setting:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = %(KOSTREET_DATABASE_URL_SYNC)s
```

The URL is read from the environment variable — not hardcoded — so it works in any environment.

---

## File 2: `alembic/env.py`

Key differences from the default Alembic `env.py`:

1. **Imports all ORM models** so `autogenerate` can see every table:
   ```python
   from app.models import report, audit  # noqa: F401
   from app.db.base import Base
   target_metadata = Base.metadata
   ```

2. **Reads URL from settings** (not from `alembic.ini`):
   ```python
   from app.core.config import settings
   config.set_main_option("sqlalchemy.url", settings.database_url_sync)
   ```

3. Uses the standard **sync** `run_migrations_online` pattern (Alembic itself is synchronous even though the app is async).

---

## File 3: `alembic/versions/0001_initial.py`

### `upgrade()` — what SQL this creates

```sql
-- Enable PostGIS (idempotent)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ── reports ──────────────────────────────────────────────────────────────
CREATE TABLE reports (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    category         VARCHAR(50)  NOT NULL,
    status           VARCHAR(30)  NOT NULL DEFAULT 'new',
    source           VARCHAR(30)  NOT NULL DEFAULT 'citizen',
    location         GEOGRAPHY(POINT, 4326) NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    description      TEXT,
    confidence       DOUBLE PRECISION,
    image_path       TEXT,
    resolution_note  TEXT,
    rejection_reason TEXT,
    created_at       TIMESTAMPTZ  NOT NULL,
    updated_at       TIMESTAMPTZ  NOT NULL
);

CREATE INDEX idx_reports_status      ON reports (status);
CREATE INDEX idx_reports_category    ON reports (category);
CREATE INDEX idx_reports_created_at  ON reports (created_at DESC);
CREATE INDEX idx_reports_location    ON reports USING GIST (location);

-- ── report_workflow_events ───────────────────────────────────────────────
CREATE TABLE report_workflow_events (
    id          UUID        PRIMARY KEY,
    report_id   UUID        NOT NULL REFERENCES reports (id) ON DELETE CASCADE,
    from_status VARCHAR(30),
    to_status   VARCHAR(30) NOT NULL,
    note        TEXT,
    actor_type  VARCHAR(30) NOT NULL,
    actor_label TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_workflow_report_id
    ON report_workflow_events (report_id, created_at ASC);

-- ── audit_runs ───────────────────────────────────────────────────────────
CREATE TABLE audit_runs (
    id           UUID         PRIMARY KEY,
    municipality VARCHAR(200) NOT NULL DEFAULT 'Prishtina',
    route_name   VARCHAR(200) NOT NULL,
    notes        TEXT,
    status       VARCHAR(30)  NOT NULL DEFAULT 'queued',
    frames_total INTEGER      DEFAULT 0,
    frames_done  INTEGER      DEFAULT 0,
    created_at   TIMESTAMPTZ  NOT NULL,
    updated_at   TIMESTAMPTZ  NOT NULL
);

CREATE INDEX idx_audit_runs_status ON audit_runs (status);

-- ── audit_suggestions ────────────────────────────────────────────────────
CREATE TABLE audit_suggestions (
    id                  UUID             PRIMARY KEY,
    audit_run_id        UUID             NOT NULL REFERENCES audit_runs (id) ON DELETE CASCADE,
    category            VARCHAR(50)      NOT NULL,
    status              VARCHAR(40)      NOT NULL DEFAULT 'pending_review',
    location            GEOGRAPHY(POINT, 4326) NOT NULL,
    latitude            DOUBLE PRECISION NOT NULL,
    longitude           DOUBLE PRECISION NOT NULL,
    confidence          DOUBLE PRECISION NOT NULL,
    severity            VARCHAR(20),
    description         TEXT,
    model_name          TEXT,
    explanation         TEXT,
    image_url           TEXT,
    image_attribution   TEXT,
    department          VARCHAR(100),
    heading             INTEGER,
    pitch               INTEGER,
    converted_report_id UUID             REFERENCES reports (id),
    reviewer_note       TEXT,
    created_at          TIMESTAMPTZ      NOT NULL
);

CREATE INDEX idx_suggestions_run_id
    ON audit_suggestions (audit_run_id, created_at ASC);
CREATE INDEX idx_suggestions_status
    ON audit_suggestions (status);
CREATE INDEX idx_suggestions_location
    ON audit_suggestions USING GIST (location);
```

### `downgrade()` — what SQL this reverses

```sql
DROP TABLE IF EXISTS audit_suggestions;
DROP TABLE IF EXISTS audit_runs;
DROP TABLE IF EXISTS report_workflow_events;
DROP TABLE IF EXISTS reports;
```

---

## File 4: `pyproject.toml` — final dependency list

```toml
[project]
dependencies = [
  "fastapi>=0.115.6",
  "pydantic-settings>=2.7.1",
  "python-multipart>=0.0.20",
  "sqlalchemy[asyncio]>=2.0.36",
  "alembic>=1.14.0",
  "asyncpg>=0.30.0",
  "psycopg2-binary>=2.9.10",
  "geoalchemy2>=0.16.0",
  "httpx>=0.28.1",
  "pillow>=11.1.0",
  "uvicorn[standard]>=0.34.0",
]

[project.optional-dependencies]
dev = [
  "httpx>=0.28.1",
  "pytest>=8.3.4",
  "pytest-asyncio>=0.24.0",
  "ruff>=0.9.2",
]
```

---

## How to run the migration

```bash
# From the backend/ directory:
cd backend
alembic upgrade head
```

On success you will see:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 0001, initial schema
```

To verify in psql:
```sql
\dt          -- lists: reports, report_workflow_events, audit_runs, audit_suggestions
\d reports   -- shows columns and indexes including the GIST spatial index
```

---

## After this phase — how to start the server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Expected startup log:
```
INFO:     Started server process
INFO:     KoStreet demo data seeder: seeding...
INFO:     KoStreet demo data seeder: done (5 reports, 1 audit run, 36 suggestions)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then open `http://localhost:8000/docs` to verify all endpoints appear.
