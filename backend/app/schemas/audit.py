from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import (
    AuditRunStatus,
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
    image_url: str | None
    image_attribution: str | None
    department: str | None
    heading: int | None
    pitch: int | None
    converted_report_id: UUID | None
    reviewer_note: str | None
    created_at: datetime


class SuggestionConversionResult(BaseModel):
    report_id: UUID
