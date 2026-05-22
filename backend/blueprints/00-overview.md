# KoStreet Backend — Build Plan Overview

> One document per phase. Read each before approving work on that phase.
> No code is written until you approve the phase document.

---

## Current State (Phase 0 — already implemented)

The following files have already been created and are correct:

| File | What it does |
|---|---|
| `app/db/base.py` | `DeclarativeBase` for all ORM models |
| `app/db/engine.py` | Async SQLAlchemy engine + `get_db()` FastAPI dependency |
| `app/db/__init__.py` | Re-exports `Base`, `engine`, `get_db` |
| `app/models/enums.py` | All shared `StrEnum` types used across models and schemas |
| `app/models/report.py` | `Report` + `ReportWorkflowEvent` ORM tables with PostGIS |
| `app/models/audit.py` | `AuditRun` + `AuditSuggestion` ORM tables with PostGIS |
| `app/models/__init__.py` | Re-exports all models and enums |
| `app/core/config.py` | `Settings` with every env var (DB URLs, AI keys, GSV key, upload dir) |
| `app/schemas/report.py` | Pydantic v2 request/response shapes for reports |
| `app/schemas/audit.py` | Pydantic v2 request/response shapes for audit runs and suggestions |
| `app/schemas/__init__.py` | Re-exports all schemas |
| `app/repositories/report_repository.py` | Async DB access for reports and workflow events |
| `app/repositories/audit_repository.py` | Async DB access for audit runs and suggestions |
| `app/repositories/__init__.py` | Re-exports all repositories |
| `app/storage/local.py` | Saves uploaded files to disk, returns relative path and URL |
| `app/storage/__init__.py` | Re-exports `LocalFileStorage` |

`.env` was also updated with the two PostgreSQL connection strings.

---

## Phase Index

| Phase | Document | What gets built |
|---|---|---|
| 1 | `01-integrations.md` | OpenRouter HTTP client, Google Street View client |
| 2 | `02-ai-service.md` | AI image analysis service (wraps OpenRouter) |
| 3 | `03-report-service.md` | Report business logic, department routing, status transitions |
| 4 | `04-audit-service.md` | Audit run orchestration, background pipeline |
| 5 | `05-routes.md` | All 10 API endpoints wired to services |
| 6 | `06-seeder-main.md` | Demo data seeder, FastAPI lifespan, static files |
| 7 | `07-alembic.md` | Alembic migration, pyproject.toml final state |

---

## Dependency Chain

```
Phase 0 (done)
    ↓
Phase 1: Integrations (OpenRouter client, GSV client)
    ↓
Phase 2: AI Service (uses OpenRouter client from Phase 1)
    ↓
Phase 3: Report Service (uses repositories from Phase 0, AI service from Phase 2)
    ↓
Phase 4: Audit Service (uses GSV from Phase 1, AI from Phase 2, Report Service from Phase 3)
    ↓
Phase 5: Routes (wires all services from Phases 3 & 4 to HTTP endpoints)
    ↓
Phase 6: Seeder + main.py (uses all of the above)
    ↓
Phase 7: Alembic migration (creates the actual PostgreSQL tables)
```

---

## Environment Prerequisites (before running)

1. PostgreSQL 15+ with PostGIS 3.4 extension installed and running
2. Database created: `CREATE DATABASE kostreet;`
3. User created: `CREATE USER kostreet WITH PASSWORD 'kostreet';`
4. PostGIS enabled: `CREATE EXTENSION postgis;` (the migration also does this)
5. `.env` already has both `KOSTREET_DATABASE_URL` and `KOSTREET_DATABASE_URL_SYNC`
