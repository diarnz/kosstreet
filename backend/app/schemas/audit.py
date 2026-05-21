from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditRunStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class AuditRunCreate(BaseModel):
    municipality: str = Field(default="Prishtina", min_length=1)
    route_name: str = Field(min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=1000)


class AuditRunRead(AuditRunCreate):
    id: UUID = Field(default_factory=uuid4)
    status: AuditRunStatus = AuditRunStatus.queued
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

