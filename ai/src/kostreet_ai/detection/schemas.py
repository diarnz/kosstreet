from enum import StrEnum

from pydantic import BaseModel, Field


class IssueCategory(StrEnum):
    pothole = "pothole"
    garbage = "garbage"
    broken_streetlight = "broken_streetlight"
    blocked_sidewalk = "blocked_sidewalk"
    damaged_sign = "damaged_sign"
    other = "other"


class BoundingBox(BaseModel):
    x_min: float = Field(ge=0, le=1)
    y_min: float = Field(ge=0, le=1)
    x_max: float = Field(ge=0, le=1)
    y_max: float = Field(ge=0, le=1)


class DetectionResult(BaseModel):
    category: IssueCategory
    confidence: float = Field(ge=0, le=1)
    severity: int = Field(ge=1, le=5)
    summary: str
    bounding_box: BoundingBox | None = None

