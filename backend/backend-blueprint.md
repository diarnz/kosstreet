# KoStreet Backend Blueprint

> **Status:** Implementation guide — get developer green-light before building.
>
> **Scope:** Everything inside `backend/`. The frontend contract (what URLs and shapes it expects) is
> fixed. The AI service contract (OpenRouter + Google Street View) is defined here and implemented
> here. This document is the single source of truth for every file that will be created or modified.

---

## 1. Technology Stack

| Layer | Technology | Version floor |
|---|---|---|
| Runtime | Python | 3.11 |
| Web framework | FastAPI | 0.115 |
| Validation | Pydantic v2 | 2.10 |
| ORM | SQLAlchemy (async, 2.x style) | 2.0 |
| Migrations | Alembic | 1.14 |
| Database | PostgreSQL + PostGIS | PG 15, PostGIS 3.4 |
| DB driver | asyncpg (async) | 0.30 |
| Sync driver (Alembic) | psycopg2-binary | 2.9 |
| Image upload | python-multipart | 0.0.20 |
| Storage abstraction | local filesystem (Protocol boundary) | — |
| HTTP client (AI calls) | httpx | 0.28 |
| ASGI server | uvicorn[standard] | 0.34 |
| Settings | pydantic-settings | 2.7 |
| Geospatial types | geoalchemy2 | 0.16 |
| Task queue | FastAPI BackgroundTasks (MVP) | built-in |

---

## 2. Environment Variables

All variables are read from the root `.env` file via `pydantic-settings`.
The prefix is `KOSTREET_`. Add the following to `.env`:

```dotenv
# Core
KOSTREET_ENV=development
KOSTREET_API_V1_PREFIX=/api/v1
KOSTREET_CORS_ORIGINS=http://localhost:5173

# PostgreSQL (PostGIS enabled)
KOSTREET_DATABASE_URL=postgresql+asyncpg://kostreet:kostreet@localhost:5432/kostreet
KOSTREET_DATABASE_URL_SYNC=postgresql+psycopg2://kostreet:kostreet@localhost:5432/kostreet

# Storage
KOSTREET_UPLOAD_DIR=backend/uploads
KOSTREET_MAX_UPLOAD_BYTES=10485760

# AI Service (OpenRouter)
KOSTREET_AI_OPENROUTER_API_KEY=<your key>
KOSTREET_AI_MODEL_NAME=google/gemma-4-26b-a4b-it
KOSTREET_AI_CONFIDENCE_THRESHOLD=0.55
KOSTREET_AI_DUPLICATE_RADIUS_METERS=20.0
KOSTREET_AI_MAX_IMAGE_SIZE_PX=1024
KOSTREET_AI_SERVICE_PORT=8001

# Street Imagery (Google Street View Static API)
GOOGLE_MAPS_API_KEY=<your key>
KOSTREET_GSV_FRAME_SIZE=640
```

`Settings` class in `app/core/config.py` exposes typed properties.
`cors_origins` is a `list[str]` split on commas from `KOSTREET_CORS_ORIGINS`.
`database_url_sync` is used only by Alembic; the application always uses async.

---

## 3. Final Directory Structure

```
backend/
├── alembic/
│   ├── env.py                        ← async-aware Alembic env
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial.py           ← first migration
├── app/
│   ├── main.py                       ← create_app(), lifespan
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py             ← mounts all sub-routers
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── health.py         ← GET /health, GET /api/v1/health
│   │           ├── reports.py        ← all /reports/* endpoints
│   │           └── audit.py          ← all /audit-runs/* and /audit-suggestions/*
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                 ← Settings (pydantic-settings)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py                 ← async engine + sessionmaker
│   │   └── base.py                   ← DeclarativeBase
│   ├── models/
│   │   ├── __init__.py               ← re-exports all ORM models
│   │   ├── report.py                 ← Report, ReportWorkflowEvent
│   │   ├── audit.py                  ← AuditRun, AuditSuggestion
│   │   └── enums.py                  ← all shared SQLAlchemy Enum columns
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── report.py                 ← ReportCreate, ReportRead, ReportDetail, StatusUpdate
│   │   ├── audit.py                  ← AuditRunCreate, AuditRunRead, AuditSuggestion*
│   │   └── ai.py                     ← ImageAnalysisResult, AuditFrameResult
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── report_repository.py      ← async CRUD for reports + workflow events
│   │   └── audit_repository.py       ← async CRUD for runs + suggestions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── report_service.py         ← business logic, department routing
│   │   ├── audit_service.py          ← orchestrates run lifecycle
│   │   └── ai_service.py             ← OpenRouter vision calls
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── street_imagery.py         ← StreetImageryClient (Protocol + GSV impl)
│   │   └── openrouter.py             ← OpenRouter HTTP client wrapper
│   ├── storage/
│   │   ├── __init__.py
│   │   └── local.py                  ← LocalFileStorage (save, url_for)
│   └── seeds/
│       ├── __init__.py
│       └── demo.py                   ← idempotent seed from audit_results.json + demo reports
├── tests/
│   ├── test_health.py
│   ├── test_reports.py
│   └── test_audit.py
├── uploads/                          ← gitignored, created at startup
└── pyproject.toml
```

---

## 4. Database Schema

### 4.1 PostGIS Setup

The initial Alembic migration enables the PostGIS extension:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

Geographic coordinates are stored as `GEOGRAPHY(POINT, 4326)` columns using
`geoalchemy2.types.Geography`. This enables true great-circle distance queries in metres with
`ST_DWithin` for duplicate detection.

### 4.2 Table: `reports`

```
Column             Type                    Constraints
─────────────────────────────────────────────────────
id                 UUID                    PK, default gen_random_uuid()
category           VARCHAR(50)             NOT NULL  (enum: issue categories)
status             VARCHAR(30)             NOT NULL, default 'new'
source             VARCHAR(30)             NOT NULL, default 'citizen'
location           GEOGRAPHY(POINT,4326)   NOT NULL
latitude           DOUBLE PRECISION        NOT NULL  (denormalised for fast reads)
longitude          DOUBLE PRECISION        NOT NULL  (denormalised for fast reads)
description        TEXT
confidence         DOUBLE PRECISION        CHECK(confidence BETWEEN 0 AND 1)
image_path         TEXT                    (relative path under UPLOAD_DIR)
resolution_note    TEXT
rejection_reason   TEXT
created_at         TIMESTAMPTZ             NOT NULL, default now()
updated_at         TIMESTAMPTZ             NOT NULL, default now()
```

Indexes:
- `idx_reports_status` on `(status)`
- `idx_reports_category` on `(category)`
- `idx_reports_created_at` on `(created_at DESC)`
- `idx_reports_location` (GIST) on `(location)` — enables PostGIS spatial queries

### 4.3 Table: `report_workflow_events`

```
Column        Type            Constraints
────────────────────────────────────────
id            UUID            PK
report_id     UUID            FK → reports.id ON DELETE CASCADE
from_status   VARCHAR(30)     NULLABLE
to_status     VARCHAR(30)     NOT NULL
note          TEXT
actor_type    VARCHAR(30)     NOT NULL  ('municipality' | 'system')
actor_label   TEXT            NOT NULL
created_at    TIMESTAMPTZ     NOT NULL, default now()
```

Index: `idx_workflow_events_report_id` on `(report_id, created_at ASC)`

### 4.4 Table: `audit_runs`

```
Column        Type            Constraints
────────────────────────────────────────
id            UUID            PK
municipality  VARCHAR(200)    NOT NULL, default 'Prishtina'
route_name    VARCHAR(200)    NOT NULL
notes         TEXT
status        VARCHAR(30)     NOT NULL, default 'queued'
frames_total  INTEGER         default 0
frames_done   INTEGER         default 0
created_at    TIMESTAMPTZ     NOT NULL, default now()
updated_at    TIMESTAMPTZ     NOT NULL, default now()
```

Index: `idx_audit_runs_status` on `(status)`

### 4.5 Table: `audit_suggestions`

```
Column               Type                    Constraints
────────────────────────────────────────────────────────
id                   UUID                    PK
audit_run_id         UUID                    FK → audit_runs.id ON DELETE CASCADE
category             VARCHAR(50)             NOT NULL
status               VARCHAR(40)             NOT NULL, default 'pending_review'
location             GEOGRAPHY(POINT,4326)   NOT NULL
latitude             DOUBLE PRECISION        NOT NULL
longitude            DOUBLE PRECISION        NOT NULL
confidence           DOUBLE PRECISION        NOT NULL
severity             VARCHAR(20)             ('low'|'medium'|'high'|'critical')
description          TEXT
model_name           TEXT
explanation          TEXT
image_url            TEXT
image_attribution    TEXT
department           VARCHAR(100)
heading              INTEGER
pitch                INTEGER
converted_report_id  UUID                    FK → reports.id NULLABLE
reviewer_note        TEXT
created_at           TIMESTAMPTZ             NOT NULL, default now()
```

Indexes:
- `idx_suggestions_run_id` on `(audit_run_id, created_at ASC)`
- `idx_suggestions_status` on `(status)`
- `idx_suggestions_location` (GIST) on `(location)`

---

## 5. ORM Models

### 5.1 `app/models/enums.py`

All Python enums used as `SQLAlchemy.Enum` column types:

```python
from enum import StrEnum

class IssueCategory(StrEnum):
    pothole            = "pothole"
    garbage            = "garbage"
    broken_streetlight = "broken_streetlight"
    blocked_sidewalk   = "blocked_sidewalk"
    damaged_sign       = "damaged_sign"
    other              = "other"

class TicketStatus(StrEnum):
    new        = "new"
    verified   = "verified"
    assigned   = "assigned"
    in_progress = "in_progress"
    resolved   = "resolved"
    rejected   = "rejected"

class ReportSource(StrEnum):
    citizen      = "citizen"
    street_audit = "street_audit"

class AuditRunStatus(StrEnum):
    queued    = "queued"
    running   = "running"
    completed = "completed"
    failed    = "failed"

class AuditSuggestionStatus(StrEnum):
    pending_review      = "pending_review"
    accepted            = "accepted"
    rejected            = "rejected"
    needs_manual_review = "needs_manual_review"
    converted_to_report = "converted_to_report"

class AuditSuggestionSeverity(StrEnum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"

class ActorType(StrEnum):
    municipality = "municipality"
    system       = "system"
```

### 5.2 `app/models/report.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.db.base import Base
from app.models.enums import IssueCategory, TicketStatus, ReportSource, ActorType


class Report(Base):
    __tablename__ = "reports"

    id:               Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category:         Mapped[str]               = mapped_column(String(50), nullable=False)
    status:           Mapped[str]               = mapped_column(String(30), nullable=False, default=TicketStatus.new)
    source:           Mapped[str]               = mapped_column(String(30), nullable=False, default=ReportSource.citizen)
    location:         Mapped[object]            = mapped_column(Geography("POINT", srid=4326), nullable=False)
    latitude:         Mapped[float]             = mapped_column(Float, nullable=False)
    longitude:        Mapped[float]             = mapped_column(Float, nullable=False)
    description:      Mapped[str | None]        = mapped_column(Text)
    confidence:       Mapped[float | None]      = mapped_column(Float)
    image_path:       Mapped[str | None]        = mapped_column(Text)
    resolution_note:  Mapped[str | None]        = mapped_column(Text)
    rejection_reason: Mapped[str | None]        = mapped_column(Text)
    created_at:       Mapped[datetime]          = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at:       Mapped[datetime]          = mapped_column(DateTime(timezone=True), nullable=False)

    workflow_events:  Mapped[list["ReportWorkflowEvent"]] = relationship(
        "ReportWorkflowEvent", back_populates="report",
        cascade="all, delete-orphan", order_by="ReportWorkflowEvent.created_at"
    )


class ReportWorkflowEvent(Base):
    __tablename__ = "report_workflow_events"

    id:          Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id:   Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[str | None]    = mapped_column(String(30))
    to_status:   Mapped[str]           = mapped_column(String(30), nullable=False)
    note:        Mapped[str | None]    = mapped_column(Text)
    actor_type:  Mapped[str]           = mapped_column(String(30), nullable=False)
    actor_label: Mapped[str]           = mapped_column(Text, nullable=False)
    created_at:  Mapped[datetime]      = mapped_column(DateTime(timezone=True), nullable=False)

    report: Mapped["Report"] = relationship("Report", back_populates="workflow_events")
```

### 5.3 `app/models/audit.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.db.base import Base
from app.models.enums import AuditRunStatus, AuditSuggestionStatus, AuditSuggestionSeverity


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    municipality: Mapped[str]       = mapped_column(String(200), nullable=False, default="Prishtina")
    route_name:   Mapped[str]       = mapped_column(String(200), nullable=False)
    notes:        Mapped[str | None]= mapped_column(Text)
    status:       Mapped[str]       = mapped_column(String(30), nullable=False, default=AuditRunStatus.queued)
    frames_total: Mapped[int]       = mapped_column(Integer, default=0)
    frames_done:  Mapped[int]       = mapped_column(Integer, default=0)
    created_at:   Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at:   Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)

    suggestions: Mapped[list["AuditSuggestion"]] = relationship(
        "AuditSuggestion", back_populates="audit_run",
        cascade="all, delete-orphan", order_by="AuditSuggestion.created_at"
    )


class AuditSuggestion(Base):
    __tablename__ = "audit_suggestions"

    id:                  Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_run_id:        Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.id", ondelete="CASCADE"), nullable=False)
    category:            Mapped[str]            = mapped_column(String(50), nullable=False)
    status:              Mapped[str]            = mapped_column(String(40), nullable=False, default=AuditSuggestionStatus.pending_review)
    location:            Mapped[object]         = mapped_column(Geography("POINT", srid=4326), nullable=False)
    latitude:            Mapped[float]          = mapped_column(Float, nullable=False)
    longitude:           Mapped[float]          = mapped_column(Float, nullable=False)
    confidence:          Mapped[float]          = mapped_column(Float, nullable=False)
    severity:            Mapped[str | None]     = mapped_column(String(20))
    description:         Mapped[str | None]     = mapped_column(Text)
    model_name:          Mapped[str | None]     = mapped_column(Text)
    explanation:         Mapped[str | None]     = mapped_column(Text)
    image_url:           Mapped[str | None]     = mapped_column(Text)
    image_attribution:   Mapped[str | None]     = mapped_column(Text)
    department:          Mapped[str | None]     = mapped_column(String(100))
    heading:             Mapped[int | None]     = mapped_column(Integer)
    pitch:               Mapped[int | None]     = mapped_column(Integer)
    converted_report_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    reviewer_note:       Mapped[str | None]     = mapped_column(Text)
    created_at:          Mapped[datetime]       = mapped_column(DateTime(timezone=True), nullable=False)

    audit_run: Mapped["AuditRun"] = relationship("AuditRun", back_populates="suggestions")
```

---

## 6. Pydantic Schemas

### 6.1 `app/schemas/report.py`

All schemas that cross the HTTP boundary. The frontend TypeScript types are the authoritative
contract — these schemas must match exactly.

```python
# ── Enums (re-exported from models.enums, used in schemas) ─────────────────

# IssueCategory, TicketStatus, ReportSource  ← imported from app.models.enums

# ── Request schemas ─────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    category:    IssueCategory
    latitude:    float = Field(ge=-90,   le=90)
    longitude:   float = Field(ge=-180,  le=180)
    source:      ReportSource = ReportSource.citizen
    description: str | None   = Field(default=None, max_length=1000)
    confidence:  float | None = Field(default=None, ge=0, le=1)

class ReportStatusUpdate(BaseModel):
    status: TicketStatus
    note:   str | None = None

# ── Response schemas ────────────────────────────────────────────────────────

class WorkflowEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:          UUID
    report_id:   UUID
    from_status: TicketStatus | None
    to_status:   TicketStatus
    note:        str | None
    created_at:  datetime
    actor_type:  str
    actor_label: str

class ReportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:          UUID
    category:    IssueCategory
    status:      TicketStatus
    latitude:    float
    longitude:   float
    source:      ReportSource
    description: str | None
    confidence:  float | None
    created_at:  datetime

class ReportDetail(ReportSummary):
    updated_at:       datetime
    resolution_note:  str | None
    rejection_reason: str | None
    workflow_events:  list[WorkflowEventRead]

class ImageAnalysisResult(BaseModel):
    category:    IssueCategory | None
    confidence:  float | None
    description: str | None
    is_civic_issue: bool
```

### 6.2 `app/schemas/audit.py`

```python
# ── Request schemas ─────────────────────────────────────────────────────────

class AuditRunCreate(BaseModel):
    municipality: str  = Field(default="Prishtina", min_length=1, max_length=200)
    route_name:   str  = Field(min_length=1, max_length=200)
    notes:        str | None = Field(default=None, max_length=1000)

class AuditSuggestionReview(BaseModel):
    status:        Literal["accepted", "rejected", "needs_manual_review"]
    reviewer_note: str | None = None

# ── Response schemas ────────────────────────────────────────────────────────

class AuditRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:           UUID
    municipality: str
    route_name:   str
    notes:        str | None
    status:       AuditRunStatus
    frames_total: int
    frames_done:  int
    created_at:   datetime

class AuditSuggestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:                  UUID
    audit_run_id:        UUID
    category:            IssueCategory
    status:              AuditSuggestionStatus
    latitude:            float
    longitude:           float
    confidence:          float
    severity:            AuditSuggestionSeverity | None
    description:         str | None
    model_name:          str | None
    explanation:         str | None
    image_url:           str | None
    image_attribution:   str | None
    department:          str | None
    created_at:          datetime

class SuggestionConversionResult(BaseModel):
    report_id: UUID
```

---

## 7. API Endpoints — Complete Surface

### 7.1 Health

```
GET  /health              → {"status": "ok", "service": "kostreet-backend"}
GET  /api/v1/health       → {"status": "ok", "api": "v1"}
```

No DB dependency. Used by uptime checks and the frontend connection indicator.

### 7.2 Reports — full surface

```
GET    /api/v1/reports
       Query params: status, category, source (all optional filters)
       Response: list[ReportSummary]
       Notes: returns all reports ordered by created_at DESC

POST   /api/v1/reports
       Content-Type: multipart/form-data
       Form fields:
         data    (JSON string)  ← ReportCreate payload
         image   (file, optional) ← JPEG/PNG max 10 MB
       Response: 201 ReportSummary
       Notes: if image present, save to UPLOAD_DIR, set image_path;
              creates initial workflow event {to_status:"new", actor_type:"system"}

GET    /api/v1/reports/{report_id}
       Response: 200 ReportDetail  |  404
       Notes: includes workflow_events ordered ASC by created_at

PATCH  /api/v1/reports/{report_id}/status
       Body: ReportStatusUpdate {status, note?}
       Response: 200 ReportDetail  |  404  |  422 (invalid transition)
       Notes: validates transition, creates ReportWorkflowEvent,
              updates reports.updated_at; actor_type = "municipality"

POST   /api/v1/reports/analyze-image
       Content-Type: multipart/form-data
       Form field: image (file)
       Response: 200 ImageAnalysisResult
       Notes: resizes image → base64 → OpenRouter call → structured JSON back;
              does NOT persist anything; pure analysis utility
```

Valid status transitions (enforced server-side):

```
new         → verified, rejected
verified    → assigned, rejected
assigned    → in_progress, rejected
in_progress → resolved, rejected
resolved    → (terminal)
rejected    → (terminal)
```

### 7.3 Audit Runs

```
GET   /api/v1/audit-runs
      Response: list[AuditRunSummary]
      Notes: ordered by created_at DESC

POST  /api/v1/audit-runs
      Body: AuditRunCreate {municipality, route_name, notes?}
      Response: 201 AuditRunSummary  (status = "queued")
      Notes: registers a BackgroundTask that runs the full pipeline;
             returns immediately without waiting for pipeline

GET   /api/v1/audit-runs/{run_id}
      Response: 200 AuditRunSummary  |  404
      Notes: frontend polls this to track queued→running→completed
```

### 7.4 Audit Suggestions

```
GET   /api/v1/audit-runs/{run_id}/suggestions
      Response: list[AuditSuggestionRead]
      Notes: all suggestions for a run, ordered by created_at ASC

PATCH /api/v1/audit-suggestions/{suggestion_id}
      Body: AuditSuggestionReview {status, reviewer_note?}
      Response: 200 AuditSuggestionRead  |  404  |  422
      Notes: status must be accepted | rejected | needs_manual_review;
             cannot review a suggestion already converted_to_report

POST  /api/v1/audit-suggestions/{suggestion_id}/convert-to-report
      Response: 201 SuggestionConversionResult {report_id}  |  404  |  409 (already converted)
      Notes: creates a Report from the suggestion (source = "street_audit");
             sets suggestion.status = "converted_to_report";
             sets suggestion.converted_report_id = new report.id;
             creates initial workflow event on the report
```

---

## 8. Database Layer

### 8.1 `app/db/engine.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.env == "development",
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

`get_db` is the FastAPI dependency used in every route that touches the DB.

### 8.2 `app/db/base.py`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### 8.3 Alembic `env.py` (async pattern)

Uses `run_async_migrations` with `asyncio.run`. Imports `Base` and all models so autogenerate
works. Uses `settings.database_url_sync` (psycopg2) because Alembic itself is synchronous.

---

## 9. Repository Layer

Repositories are pure async data-access objects. They receive an `AsyncSession` and return ORM
instances or raise `sqlalchemy` exceptions. They contain **no business logic**.

### 9.1 `app/repositories/report_repository.py`

```python
class ReportRepository:
    def __init__(self, db: AsyncSession) -> None: ...

    async def list(
        self, *, status=None, category=None, source=None
    ) -> list[Report]: ...

    async def get(self, report_id: UUID) -> Report | None: ...

    async def create(self, data: ReportCreate, *, image_path: str | None) -> Report: ...

    async def update_status(
        self, report: Report, new_status: str, *, note: str | None, actor_label: str
    ) -> Report:
        # updates report.status and report.updated_at
        # appends a ReportWorkflowEvent to report.workflow_events
        ...

    async def get_with_events(self, report_id: UUID) -> Report | None:
        # eagerly loads workflow_events
        ...
```

### 9.2 `app/repositories/audit_repository.py`

```python
class AuditRunRepository:
    def __init__(self, db: AsyncSession) -> None: ...

    async def list(self) -> list[AuditRun]: ...
    async def get(self, run_id: UUID) -> AuditRun | None: ...
    async def create(self, data: AuditRunCreate) -> AuditRun: ...
    async def set_status(self, run: AuditRun, status: str) -> None: ...
    async def increment_frames_done(self, run_id: UUID) -> None: ...

class AuditSuggestionRepository:
    def __init__(self, db: AsyncSession) -> None: ...

    async def list_for_run(self, run_id: UUID) -> list[AuditSuggestion]: ...
    async def get(self, suggestion_id: UUID) -> AuditSuggestion | None: ...
    async def create_bulk(self, suggestions: list[dict]) -> list[AuditSuggestion]: ...
    async def review(
        self, suggestion: AuditSuggestion, status: str, reviewer_note: str | None
    ) -> AuditSuggestion: ...
    async def convert_to_report(
        self, suggestion: AuditSuggestion, report_id: UUID
    ) -> AuditSuggestion: ...
```

---

## 10. Service Layer

Services own business logic. They compose repositories and integrations. They are
**called by routes** and **call repositories + external integrations**.

### 10.1 `app/services/report_service.py`

```python
DEPARTMENT_MAP: dict[str, str] = {
    "pothole":             "Roads / Public Works",
    "garbage":             "Sanitation",
    "broken_streetlight":  "Electrical / Infrastructure",
    "blocked_sidewalk":    "Roads / Public Works",
    "damaged_sign":        "Roads / Public Works",
    "other":               "General Services",
}

VALID_TRANSITIONS: dict[str, set[str]] = {
    "new":         {"verified", "rejected"},
    "verified":    {"assigned", "rejected"},
    "assigned":    {"in_progress", "rejected"},
    "in_progress": {"resolved", "rejected"},
    "resolved":    set(),
    "rejected":    set(),
}

class ReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ReportRepository(db)
        self.storage = LocalFileStorage(settings.upload_dir)

    async def list_reports(self, *, status, category, source) -> list[Report]: ...

    async def create_report(
        self,
        data: ReportCreate,
        image: UploadFile | None,
    ) -> Report:
        # 1. save image if present → get image_path
        # 2. repo.create(data, image_path=image_path)
        # 3. return report

    async def get_report_detail(self, report_id: UUID) -> Report:
        # repo.get_with_events or raise 404

    async def update_status(
        self, report_id: UUID, payload: ReportStatusUpdate
    ) -> Report:
        # 1. get report or 404
        # 2. validate transition or raise 422
        # 3. repo.update_status(report, payload.status, note=payload.note, actor_label="Municipal operator")
        # 4. return updated report

    async def analyze_image(self, image: UploadFile) -> ImageAnalysisResult:
        # 1. read bytes, resize via PIL to MAX_IMAGE_SIZE_PX
        # 2. base64 encode
        # 3. call ai_service.analyze_image_bytes(b64)
        # 4. return result
```

### 10.2 `app/services/audit_service.py`

```python
class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.run_repo  = AuditRunRepository(db)
        self.sugg_repo = AuditSuggestionRepository(db)
        self.ai        = AIService(settings)
        self.gsv       = GoogleStreetViewClient(settings.google_maps_api_key)

    async def list_runs(self) -> list[AuditRun]: ...

    async def get_run(self, run_id: UUID) -> AuditRun: ...

    async def create_run(
        self,
        data: AuditRunCreate,
        background_tasks: BackgroundTasks,
    ) -> AuditRun:
        run = await self.run_repo.create(data)
        background_tasks.add_task(self._run_pipeline, run.id)
        return run

    async def list_suggestions(self, run_id: UUID) -> list[AuditSuggestion]: ...

    async def review_suggestion(
        self, suggestion_id: UUID, payload: AuditSuggestionReview
    ) -> AuditSuggestion: ...

    async def convert_suggestion_to_report(
        self, suggestion_id: UUID, db: AsyncSession
    ) -> SuggestionConversionResult:
        # 1. get suggestion or 404
        # 2. if already converted → raise 409
        # 3. create Report (source=street_audit, confidence from suggestion)
        # 4. mark suggestion.converted_to_report + set converted_report_id
        # 5. return {report_id}

    async def _run_pipeline(self, run_id: UUID) -> None:
        # Runs inside BackgroundTasks — gets its own DB session
        # 1. set run.status = "running"
        # 2. resolve waypoints for run.route_name
        # 3. build AuditFrames (build_heading_plan per waypoint)
        # 4. set run.frames_total = len(frames)
        # 5. for each frame:
        #      a. gsv.fetch_frame(lat, lng, heading, pitch)
        #      b. ai.analyze_image_bytes(frame_bytes)
        #      c. if result.is_civic_issue and result.confidence >= threshold:
        #             sugg_repo.create(...)
        #      d. increment_frames_done
        # 6. set run.status = "completed"  (or "failed" on exception)
```

### 10.3 `app/services/ai_service.py`

```python
CIVIC_ISSUE_PROMPT = """
You are analyzing a Google Street View image for a municipal issue detection system
in Prishtina, Kosovo.

Identify if the image contains a civic street issue. Respond ONLY with valid JSON:
{
  "is_civic_issue": true | false,
  "category": "pothole" | "garbage" | "broken_streetlight" | "blocked_sidewalk" | "damaged_sign" | "other" | null,
  "confidence": <0.0 to 1.0>,
  "severity": "low" | "medium" | "high" | "critical" | null,
  "description": "<one sentence describing the issue>" | null
}

Rules:
- Set is_civic_issue=false for clean streets, normal traffic, buildings, or people.
- confidence reflects how certain you are that the identified issue is genuinely present.
- severity reflects the urgency/impact on citizens.
- description must be specific: mention what you see, not just the category name.
"""

class AIService:
    def __init__(self, settings: Settings) -> None:
        self.api_key    = settings.ai_openrouter_api_key
        self.model_name = settings.ai_model_name
        self.threshold  = settings.ai_confidence_threshold

    async def analyze_image_bytes(self, image_bytes: bytes) -> ImageAnalysisResult:
        # 1. base64-encode image_bytes
        # 2. POST to https://openrouter.ai/api/v1/chat/completions
        #    with model=self.model_name and messages=[
        #      {role:"user", content:[
        #        {type:"image_url", image_url:{url:"data:image/jpeg;base64,<b64>"}},
        #        {type:"text", text:CIVIC_ISSUE_PROMPT}
        #      ]}
        #    ]
        # 3. parse JSON from response.choices[0].message.content
        # 4. return ImageAnalysisResult
        ...
```

HTTP calls via `httpx.AsyncClient`. Retry once on 429/503. Timeout 30 s.

---

## 11. Integrations

### 11.1 `app/integrations/street_imagery.py`

```python
# Protocol (already exists — keep as-is)
class StreetImageryClient(Protocol):
    def fetch_frame(self, request: StreetImageryFrameRequest) -> StreetImageryFrame: ...

# Concrete implementation
class GoogleStreetViewClient:
    BASE_URL = "https://maps.googleapis.com/maps/api/streetview"

    def __init__(self, api_key: str, size: int = 640) -> None: ...

    def fetch_frame(self, request: StreetImageryFrameRequest) -> StreetImageryFrame:
        # GET {BASE_URL}?size={size}x{size}&location={lat},{lng}
        #                &heading={heading}&pitch={pitch}&key={api_key}
        # Returns JPEG bytes wrapped in StreetImageryFrame
        ...
```

Note: GSV Static API calls are **synchronous** (`httpx` sync client) because they run inside a
`BackgroundTasks` coroutine that bridges via `asyncio.run_in_executor` if needed, or simply
via the existing sync `httpx.get`.

### 11.2 Route Waypoint Registry

A hardcoded dict in `app/services/audit_service.py` maps known route names to coordinate lists.
Bill Clinton Boulevard is pre-loaded from `ai/data/demo/audit_results.json` coordinates.
Unknown routes fall back to a single-point plan using Google Geocoding.

```python
KNOWN_ROUTES: dict[str, list[tuple[float, float]]] = {
    "Bill Clinton Boulevard": [
        (42.6596, 21.1545),
        (42.65989, 21.15496),
        (42.66019, 21.15542),
        (42.66048, 21.15589),
        (42.66078, 21.15635),
        (42.66107, 21.15681),
        (42.66137, 21.15727),
        (42.66166, 21.15774),
        (42.66205, 21.15830),
        (42.66236, 21.15875),
        (42.66267, 21.15919),
        (42.66298, 21.15964),
        (42.66329, 21.16008),
        (42.66360, 21.16052),
        (42.66391, 21.16097),
        (42.664,   21.1611),
    ],
}
```

---

## 12. Storage Abstraction

### 12.1 `app/storage/local.py`

```python
class LocalFileStorage:
    def __init__(self, upload_dir: str) -> None:
        self.base_path = Path(upload_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile) -> str:
        # Generate path: uploads/{date}/{uuid}{ext}
        # Write bytes to disk
        # Return relative path string

    def url_for(self, path: str) -> str:
        # Returns /uploads/{relative_path}
        # The FastAPI static files mount serves this
```

FastAPI mounts `/uploads` as a `StaticFiles` directory from `UPLOAD_DIR` in `create_app()`.

---

## 13. Startup Seeding

### 13.1 `app/seeds/demo.py`

```python
async def seed_demo_data(db: AsyncSession) -> None:
    """
    Idempotent. Checks if data already exists before inserting.
    Runs once at application startup in the lifespan context.
    """
    # Guard: skip if reports table already has rows
    existing = await db.scalar(select(func.count()).select_from(Report))
    if existing > 0:
        return

    # 1. Create 5 demo citizen reports (matching frontend demo fixture IDs
    #    so the frontend seamlessly exits demo mode on first load)
    #    IDs: demo-report-pothole-001, demo-report-garbage-001, etc.

    # 2. Create AuditRun for Bill Clinton Boulevard
    #    ID: bill-clinton-blvd-001, status: completed

    # 3. Load ai/data/demo/audit_results.json
    #    Create one AuditSuggestion per detection entry

    # 4. Commit
```

The seeder is called from the FastAPI `lifespan` context manager in `app/main.py`.

### 13.2 `app/main.py` lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        await seed_demo_data(db)
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="KoStreet API", lifespan=lifespan, ...)
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    ...
```

---

## 14. Dependency Wiring

Routes receive services via FastAPI `Depends`. The pattern:

```python
# app/api/v1/routes/reports.py

def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)

@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    report = await service.get_report_detail(report_id)
    return ReportDetail.model_validate(report)
```

No global singleton services. Each request gets a fresh service + repository with the
request-scoped `AsyncSession`. This is safe for async PostgreSQL.

---

## 15. Alembic Setup

### 15.1 Initialise

```bash
cd backend
alembic init alembic
```

### 15.2 `alembic/env.py` key changes

```python
# Use sync URL for Alembic
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Import all models so autogenerate finds them
from app.models import report, audit  # noqa: F401
from app.db.base import Base
target_metadata = Base.metadata
```

### 15.3 First migration `0001_initial.py`

```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    # create reports, report_workflow_events, audit_runs, audit_suggestions tables
    # create all indexes including GIST spatial indexes

def downgrade() -> None:
    op.drop_table("audit_suggestions")
    op.drop_table("audit_runs")
    op.drop_table("report_workflow_events")
    op.drop_table("reports")
```

Run migrations: `alembic upgrade head`

---

## 16. `pyproject.toml` Updated Dependencies

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
```

---

## 17. Implementation Order

Build in this exact sequence. Each step is independently testable before moving to the next.

### Step 1 — Database foundation

- [ ] Add `asyncpg`, `psycopg2-binary`, `geoalchemy2`, `alembic`, `httpx`, `pillow` to `pyproject.toml`
- [ ] `app/db/base.py` — `DeclarativeBase`
- [ ] `app/db/engine.py` — async engine + `get_db` dependency
- [ ] `app/models/enums.py` — all enums
- [ ] `app/models/report.py` — `Report`, `ReportWorkflowEvent`
- [ ] `app/models/audit.py` — `AuditRun`, `AuditSuggestion`
- [ ] `app/models/__init__.py` — re-export all
- [ ] `alembic/` — init + `env.py` + `0001_initial.py`
- [ ] Run `alembic upgrade head` — verify tables exist in psql

### Step 2 — Core config

- [ ] Update `app/core/config.py` — add `database_url`, `database_url_sync`, all AI + GSV + storage settings
- [ ] Update `.env` with `KOSTREET_DATABASE_URL` and `KOSTREET_DATABASE_URL_SYNC`

### Step 3 — Schemas

- [ ] `app/schemas/report.py` — all request/response schemas incl. `ImageAnalysisResult`
- [ ] `app/schemas/audit.py` — all audit schemas

### Step 4 — Repositories

- [ ] `app/repositories/report_repository.py`
- [ ] `app/repositories/audit_repository.py`

### Step 5 — Storage

- [ ] `app/storage/local.py` — `LocalFileStorage`

### Step 6 — AI + GSV integrations (stubs first, then real)

- [ ] `app/integrations/openrouter.py` — `OpenRouterClient` with `chat_completion`
- [ ] `app/integrations/street_imagery.py` — `GoogleStreetViewClient` implementation
- [ ] `app/services/ai_service.py` — `AIService.analyze_image_bytes`

### Step 7 — Services

- [ ] `app/services/report_service.py` — incl. status transition validation + department map
- [ ] `app/services/audit_service.py` — incl. `_run_pipeline` background task

### Step 8 — Routes

- [ ] `app/api/v1/routes/reports.py` — all 5 report endpoints
- [ ] `app/api/v1/routes/audit.py` — all 5 audit endpoints
- [ ] `app/api/v1/router.py` — mount audit-suggestions sub-router

### Step 9 — Seeder + lifespan

- [ ] `app/seeds/demo.py`
- [ ] `app/main.py` — lifespan, static files mount

### Step 10 — Verify end-to-end

- [ ] `uvicorn app.main:app --reload` — check `/docs`
- [ ] Confirm seeded data appears at `GET /api/v1/reports` and `GET /api/v1/audit-runs`
- [ ] Test `POST /api/v1/reports/analyze-image` with a pothole photo
- [ ] Test full audit pipeline with `POST /api/v1/audit-runs` → poll `GET /api/v1/audit-runs/{id}` → `GET /api/v1/audit-runs/{id}/suggestions`

---

## 18. Testing Strategy

Each test file in `backend/tests/` uses `pytest-asyncio` with a test database.

```
tests/
├── conftest.py          ← in-memory SQLite engine for tests, override get_db
├── test_health.py       ← exists, keep
├── test_reports.py      ← list, create, get_detail, status_update, transitions
└── test_audit.py        ← list_runs, create_run, list_suggestions, review, convert
```

Tests use `httpx.AsyncClient` with the FastAPI `TestClient` wrapper. No real OpenRouter or GSV
calls in tests — both are mocked via `unittest.mock.patch`.

---

## 19. Key Decisions & Rationale

| Decision | Rationale |
|---|---|
| Async SQLAlchemy + asyncpg | FastAPI is async-native; blocking DB calls on a sync driver defeats concurrency |
| PostGIS GEOGRAPHY type | True geodesic distance for duplicate detection (`ST_DWithin`); future spatial queries free |
| Denormalised lat/lng columns | Frontend and seeder read lat/lng directly without PostGIS client-side; GEOGRAPHY used only for spatial WHERE clauses |
| BackgroundTasks for audit pipeline | Zero infrastructure overhead for MVP; swap for Celery/ARQ later if audits need queuing |
| Idempotent seeder | Safe to restart the server in dev without data duplication |
| `analyze-image` as separate endpoint | Citizen report page can call it on photo selection to pre-fill category; decoupled from report creation |
| Sync GSV client inside background task | GSV Static API is a simple HTTP GET; full async for this one call adds complexity without benefit |
| `model_config = ConfigDict(from_attributes=True)` | Required for Pydantic v2 to read directly from SQLAlchemy ORM instances |
