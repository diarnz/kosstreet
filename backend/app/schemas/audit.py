from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import (
    AuditRunStatus,
    AuditSuggestionSeverity,
    AuditSuggestionStatus,
    IssueCategory,
)
from app.schemas.report import DetectionRegion


def regions_from_json(raw: Any) -> list[DetectionRegion] | None:
    if not isinstance(raw, list) or not raw:
        return None
    regions: list[DetectionRegion] = []
    for item in raw:
        if isinstance(item, dict):
            try:
                regions.append(DetectionRegion.model_validate(item))
            except ValueError:
                continue
    return regions or None


def regions_to_json(regions: list[DetectionRegion] | None) -> list[dict[str, float]] | None:
    if not regions:
        return None
    return [region.model_dump() for region in regions]


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
    notes: str | None
    status: AuditRunStatus
    frames_total: int
    frames_done: int
    created_at: datetime


class AuditSuggestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    image_url: str | None = None
    image_attribution: str | None
    department: str | None
    heading: int | None
    pitch: int | None
    frame_index: int | None = None
    detection_regions: list[DetectionRegion] | None = None
    frame_image_url: str | None = None
    converted_report_id: UUID | None
    reviewer_note: str | None
    created_at: datetime

    @field_validator("detection_regions", mode="before")
    @classmethod
    def parse_detection_regions(cls, value: Any) -> list[DetectionRegion] | None:
        if value is None or isinstance(value, list) and not value:
            return None
        if isinstance(value, list) and value and isinstance(value[0], DetectionRegion):
            return value
        return regions_from_json(value)

    @classmethod
    def from_model(cls, suggestion: object) -> "AuditSuggestionRead":
        read = cls.model_validate(suggestion)
        frame_image_url = None
        if getattr(suggestion, "frame_index", None) is not None:
            frame_image_url = f"/api/v1/audit-suggestions/{read.id}/frame-image"
        return read.model_copy(update={"image_url": None, "frame_image_url": frame_image_url})


class AuditFrameSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_run_id: UUID
    frame_index: int
    latitude: float
    longitude: float
    heading: int
    pitch: int
    is_civic_issue: bool
    category: IssueCategory | None
    confidence: float | None
    severity: AuditSuggestionSeverity | None
    suggestion_id: UUID | None
    has_detection_regions: bool = False
    frame_image_url: str = ""
    created_at: datetime

    @classmethod
    def from_model(cls, frame: object) -> "AuditFrameSummary":
        read = cls.model_validate(frame)
        return read.model_copy(
            update={
                "has_detection_regions": bool(getattr(frame, "detection_regions", None)),
                "frame_image_url": (
                    f"/api/v1/audit-runs/{read.audit_run_id}/frames/{read.frame_index}/image"
                ),
            }
        )


class AuditFrameDetail(AuditFrameSummary):
    description: str | None
    detection_regions: list[DetectionRegion] | None = None
    model_name: str | None

    @field_validator("detection_regions", mode="before")
    @classmethod
    def parse_detection_regions(cls, value: Any) -> list[DetectionRegion] | None:
        return regions_from_json(value)

    @classmethod
    def from_model(cls, frame: object) -> "AuditFrameDetail":
        summary = AuditFrameSummary.from_model(frame)
        detail = cls.model_validate(frame)
        return detail.model_copy(
            update={
                **summary.model_dump(),
                "detection_regions": regions_from_json(
                    getattr(frame, "detection_regions", None)
                ),
            }
        )


class SuggestionConversionResult(BaseModel):
    report_id: UUID
