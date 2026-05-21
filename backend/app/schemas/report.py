from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IssueCategory(StrEnum):
    pothole = "pothole"
    garbage = "garbage"
    broken_streetlight = "broken_streetlight"
    blocked_sidewalk = "blocked_sidewalk"
    damaged_sign = "damaged_sign"
    other = "other"


class TicketStatus(StrEnum):
    new = "new"
    verified = "verified"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


class ReportSource(StrEnum):
    citizen = "citizen"
    street_audit = "street_audit"


class ReportCreate(BaseModel):
    category: IssueCategory
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    source: ReportSource = ReportSource.citizen
    description: str | None = Field(default=None, max_length=1000)
    confidence: float | None = Field(default=None, ge=0, le=1)


class ReportRead(ReportCreate):
    id: UUID = Field(default_factory=uuid4)
    status: TicketStatus = TicketStatus.new
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

