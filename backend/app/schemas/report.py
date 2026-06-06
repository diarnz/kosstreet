from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AuditSuggestionSeverity, IssueCategory, ReportSource, TicketStatus


class ReportCreate(BaseModel):
    category: IssueCategory
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    source: ReportSource = ReportSource.citizen
    description: str | None = Field(default=None, max_length=1000)
    confidence: float | None = Field(default=None, ge=0, le=1)


class ReportStatusUpdate(BaseModel):
    status: TicketStatus
    note: str | None = None


class WorkflowEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    from_status: TicketStatus | None
    to_status: TicketStatus
    note: str | None
    created_at: datetime
    actor_type: str
    actor_label: str


class ReportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category: IssueCategory
    status: TicketStatus
    latitude: float
    longitude: float
    source: ReportSource
    description: str | None
    confidence: float | None
    is_visible: bool = True
    image_url: str | None = None
    created_at: datetime


class ReportDetail(ReportSummary):
    updated_at: datetime
    resolution_note: str | None
    rejection_reason: str | None
    workflow_events: list[WorkflowEventRead]


class DetectionRegion(BaseModel):
    center_x: float = Field(ge=0, le=1)
    center_y: float = Field(ge=0, le=1)
    radius: float = Field(ge=0.04, le=0.18)


class ReportAdminUpdate(BaseModel):
    category: IssueCategory | None = None
    status: TicketStatus | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    source: ReportSource | None = None
    description: str | None = Field(default=None, max_length=1000)
    confidence: float | None = Field(default=None, ge=0, le=1)
    is_visible: bool | None = None


class ImageAnalysisResult(BaseModel):
    category: IssueCategory | None = None
    confidence: float | None = None
    severity: AuditSuggestionSeverity | None = None
    description: str | None = None
    is_civic_issue: bool = False
    regions: list[DetectionRegion] = Field(default_factory=list)
