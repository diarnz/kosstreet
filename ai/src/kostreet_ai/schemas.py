from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class IssueCategory(StrEnum):
    pothole = "pothole"
    garbage = "garbage"
    broken_streetlight = "broken_streetlight"
    blocked_sidewalk = "blocked_sidewalk"
    damaged_sign = "damaged_sign"
    other = "other"


class IssueSeverity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


# ---------------------------------------------------------------------------
# Citizen classification
# ---------------------------------------------------------------------------


class ClassificationRequest(BaseModel):
    image_base64: str = Field(description="Base64-encoded JPEG or PNG image.")
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ClassificationResult(BaseModel):
    category: IssueCategory
    confidence: float = Field(ge=0.0, le=1.0)
    severity: IssueSeverity
    description: str
    is_civic_issue: bool


class ClassificationResponse(BaseModel):
    category: IssueCategory
    confidence: float = Field(ge=0.0, le=1.0)
    severity: IssueSeverity
    description: str
    is_civic_issue: bool
    model: str


# ---------------------------------------------------------------------------
# Street audit planner
# ---------------------------------------------------------------------------


class Waypoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class FramePlan(BaseModel, frozen=True):
    latitude: float
    longitude: float
    heading: int = Field(ge=0, le=359)
    pitch: int = Field(ge=-90, le=90)


class AuditPlanRequest(BaseModel):
    waypoints: list[Waypoint] = Field(min_length=2)
    step_meters: float = Field(default=30.0, gt=0)
    headings: list[int] = Field(default=[0, 60, 120, 180, 240, 300])
    pitches: list[int] = Field(default=[-10, 0])


class AuditPlanResponse(BaseModel):
    scan_points: list[FramePlan]
    total_frames: int


# ---------------------------------------------------------------------------
# Street audit frame analysis
# ---------------------------------------------------------------------------


class FrameAnalysisRequest(BaseModel):
    image_base64: str = Field(description="Base64-encoded JPEG or PNG image.")
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    heading: int = Field(ge=0, le=359)
    pitch: int = Field(ge=-90, le=90)


class DetectionWithLocation(BaseModel):
    category: IssueCategory
    confidence: float = Field(ge=0.0, le=1.0)
    severity: IssueSeverity
    description: str
    is_civic_issue: bool
    latitude: float
    longitude: float
    heading: int
    pitch: int


class FrameAnalysisResponse(BaseModel):
    detections: list[DetectionWithLocation]
    frame_latitude: float
    frame_longitude: float
    heading: int
    pitch: int
