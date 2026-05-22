from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from app.models.enums import AuditSuggestionSeverity, IssueCategory, ReportSource, TicketStatus

REGION_RADIUS_MIN = 0.04
REGION_RADIUS_MAX = 0.18

SEVERITY_DEFAULT_RADIUS: dict[AuditSuggestionSeverity, float] = {
    AuditSuggestionSeverity.low: 0.06,
    AuditSuggestionSeverity.medium: 0.09,
    AuditSuggestionSeverity.high: 0.12,
    AuditSuggestionSeverity.critical: 0.14,
}


def default_region_radius(severity: AuditSuggestionSeverity | None) -> float:
    if severity is None:
        return SEVERITY_DEFAULT_RADIUS[AuditSuggestionSeverity.medium]
    return SEVERITY_DEFAULT_RADIUS.get(
        severity,
        SEVERITY_DEFAULT_RADIUS[AuditSuggestionSeverity.medium],
    )


def _clamp_unit(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, numeric))


def _clamp_radius(value: Any, severity: AuditSuggestionSeverity | None) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default_region_radius(severity)
    return max(REGION_RADIUS_MIN, min(REGION_RADIUS_MAX, numeric))


def sanitize_detection_regions(
    raw_regions: Any,
    severity: AuditSuggestionSeverity | None,
) -> list["DetectionRegion"] | None:
    if not isinstance(raw_regions, list) or not raw_regions:
        return None

    sanitized: list[DetectionRegion] = []
    for item in raw_regions:
        if not isinstance(item, dict):
            continue

        center_x = _clamp_unit(item.get("center_x", item.get("x")))
        center_y = _clamp_unit(item.get("center_y", item.get("y")))
        if center_x is None or center_y is None:
            continue

        sanitized.append(
            DetectionRegion(
                center_x=center_x,
                center_y=center_y,
                radius=_clamp_radius(item.get("radius"), severity),
            )
        )

    if not sanitized:
        return None

    return [sanitized[0]]


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
    created_at: datetime


class ReportDetail(ReportSummary):
    updated_at: datetime
    resolution_note: str | None
    rejection_reason: str | None
    workflow_events: list[WorkflowEventRead]


class DetectionRegion(BaseModel):
    center_x: float = Field(ge=0, le=1)
    center_y: float = Field(ge=0, le=1)
    radius: float = Field(ge=REGION_RADIUS_MIN, le=REGION_RADIUS_MAX)

    @field_validator("center_x", "center_y", "radius", mode="before")
    @classmethod
    def coerce_float(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("value is required")
        return float(value)


class ImageAnalysisResult(BaseModel):
    category: IssueCategory | None = None
    confidence: float | None = None
    severity: AuditSuggestionSeverity | None = None
    description: str | None = None
    is_civic_issue: bool = False
    regions: list[DetectionRegion] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_regions(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        severity = data.get("severity")
        try:
            parsed_severity = (
                AuditSuggestionSeverity(severity) if severity is not None else None
            )
        except ValueError:
            parsed_severity = None

        data["regions"] = sanitize_detection_regions(data.get("regions"), parsed_severity)
        return data

    @model_validator(mode="after")
    def clear_regions_when_not_issue(self) -> "ImageAnalysisResult":
        if not self.is_civic_issue:
            self.regions = None
        return self

    @classmethod
    def from_model_payload(cls, payload: dict[str, Any]) -> "ImageAnalysisResult":
        try:
            return cls.model_validate(payload)
        except ValidationError:
            return cls(is_civic_issue=False)
