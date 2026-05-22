from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.audit import AuditFrame, AuditSuggestion
from app.models.enums import (
    AuditRunStatus,
    AuditScanSource,
    AuditSuggestionSeverity,
    AuditSuggestionStatus,
    IssueCategory,
)


class AuditRunCreate(BaseModel):
    municipality: str = Field(default="Prishtina", min_length=1, max_length=200)
    route_name: str | None = Field(default=None, min_length=1, max_length=200)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_route_or_coordinates(self) -> "AuditRunCreate":
        has_route = bool(self.route_name and self.route_name.strip())
        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None

        if has_route:
            return self

        if has_latitude and has_longitude:
            return self

        raise ValueError("Provide either a route name or both latitude and longitude")


class AuditSuggestionReview(BaseModel):
    status: Literal["accepted", "rejected", "needs_manual_review"]
    reviewer_note: str | None = None


class AuditRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    municipality: str
    route_name: str
    scan_latitude: float | None = None
    scan_longitude: float | None = None
    notes: str | None
    status: AuditRunStatus
    frames_total: int
    frames_done: int
    created_at: datetime


class DetectionRegionRead(BaseModel):
    center_x: float
    center_y: float
    radius: float


class AuditSuggestionRead(BaseModel):
    id: UUID
    audit_run_id: UUID
    category: IssueCategory
    status: AuditSuggestionStatus
    latitude: float
    longitude: float
    confidence: float
    severity: AuditSuggestionSeverity | None
    description: str | None
    model_name: str | None
    explanation: str | None
    image_attribution: str | None
    department: str | None
    heading: int | None
    pitch: int | None
    frame_index: int | None
    detection_regions: list[DetectionRegionRead]
    frame_image_url: str
    converted_report_id: UUID | None
    reviewer_note: str | None
    created_at: datetime


class AuditFrameSummary(BaseModel):
    frame_index: int
    latitude: float
    longitude: float
    heading: int
    pitch: int
    is_civic_issue: bool
    category: IssueCategory | None
    confidence: float | None
    severity: AuditSuggestionSeverity | None
    description: str | None
    suggestion_id: UUID | None
    frame_image_url: str


class AuditFrameDetail(AuditFrameSummary):
    detection_regions: list[DetectionRegionRead]
    analysis_result: dict | None
    scan_source: AuditScanSource


class AuditScanPoint(BaseModel):
    frame_index: int
    latitude: float
    longitude: float
    heading: int
    pitch: int
    is_civic_issue: bool
    severity: AuditSuggestionSeverity | None = None
    suggestion_id: UUID | None = None
    scan_source: AuditScanSource = AuditScanSource.pipeline


class AnalyzeViewRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    heading: int = Field(ge=0, le=359)
    pitch: int = Field(ge=-90, le=90, default=0)


class OnDemandAnalyzeQuota(BaseModel):
    limit: int
    used: int
    remaining: int
    resets_at: datetime


class SuggestionConversionResult(BaseModel):
    report_id: UUID


def frame_image_proxy_url(run_id: UUID, frame_index: int) -> str:
    return f"/api/v1/audit-runs/{run_id}/frames/{frame_index}/image"


def suggestion_frame_image_proxy_url(suggestion_id: UUID) -> str:
    return f"/api/v1/audit-suggestions/{suggestion_id}/frame-image"


def _regions_from_json(
    regions: list[dict[str, float]] | None,
) -> list[DetectionRegionRead]:
    if not regions:
        return []
    return [DetectionRegionRead.model_validate(region) for region in regions]


def audit_suggestion_to_read(suggestion: AuditSuggestion) -> AuditSuggestionRead:
    return AuditSuggestionRead(
        id=suggestion.id,
        audit_run_id=suggestion.audit_run_id,
        category=suggestion.category,
        status=suggestion.status,
        latitude=suggestion.latitude,
        longitude=suggestion.longitude,
        confidence=suggestion.confidence,
        severity=suggestion.severity,
        description=suggestion.description,
        model_name=suggestion.model_name,
        explanation=suggestion.explanation,
        image_attribution=suggestion.image_attribution,
        department=suggestion.department,
        heading=suggestion.heading,
        pitch=suggestion.pitch,
        frame_index=suggestion.frame_index,
        detection_regions=_regions_from_json(suggestion.detection_regions),
        frame_image_url=suggestion_frame_image_proxy_url(suggestion.id),
        converted_report_id=suggestion.converted_report_id,
        reviewer_note=suggestion.reviewer_note,
        created_at=suggestion.created_at,
    )


def audit_frame_to_summary(frame: AuditFrame) -> AuditFrameSummary:
    category = IssueCategory(frame.category) if frame.category else None
    return AuditFrameSummary(
        frame_index=frame.frame_index,
        latitude=frame.latitude,
        longitude=frame.longitude,
        heading=frame.heading,
        pitch=frame.pitch,
        is_civic_issue=frame.is_civic_issue,
        category=category,
        confidence=frame.confidence,
        severity=frame.severity,
        description=frame.description,
        suggestion_id=frame.suggestion_id,
        frame_image_url=frame_image_proxy_url(frame.audit_run_id, frame.frame_index),
    )


def audit_frame_to_detail(frame: AuditFrame) -> AuditFrameDetail:
    summary = audit_frame_to_summary(frame)
    return AuditFrameDetail(
        **summary.model_dump(),
        detection_regions=_regions_from_json(frame.detection_regions),
        analysis_result=None,
        scan_source=frame.scan_source,
    )


def audit_frame_to_scan_point(frame: AuditFrame) -> AuditScanPoint:
    return AuditScanPoint(
        frame_index=frame.frame_index,
        latitude=frame.latitude,
        longitude=frame.longitude,
        heading=frame.heading,
        pitch=frame.pitch,
        is_civic_issue=frame.is_civic_issue,
        severity=frame.severity,
        suggestion_id=frame.suggestion_id,
        scan_source=frame.scan_source,
    )
