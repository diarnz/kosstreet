from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, UploadFile, status

from kostreet_ai.config import settings
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import (
    decode_base64_to_bytes,
    encode_image_to_base64,
    validate_image,
)
from kostreet_ai.schemas import ClassificationRequest, ClassificationResponse, IssueCategory, IssueSeverity

router = APIRouter()

_OFFLINE_RESPONSE = ClassificationResponse(
    category=IssueCategory.pothole,
    confidence=0.91,
    severity=IssueSeverity.medium,
    description="[OFFLINE MODE] Pre-computed result: pothole detected.",
    is_civic_issue=True,
    model="offline",
)


def _classify_bytes(image_bytes: bytes) -> ClassificationResponse:
    """Shared classification logic for both endpoints."""
    if settings.offline_mode:
        return _OFFLINE_RESPONSE
    if not validate_image(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or unreadable image.",
        )
    b64 = encode_image_to_base64(image_bytes, settings.max_image_size_px)
    result = get_classifier().classify(b64)
    return ClassificationResponse(
        category=result.category,
        confidence=result.confidence,
        severity=result.severity,
        description=result.description,
        is_civic_issue=result.is_civic_issue,
        model=settings.model_name,
    )


@router.post("/classify", response_model=ClassificationResponse)
def classify_base64(request: ClassificationRequest) -> ClassificationResponse:
    """
    Classify a civic issue from a base64-encoded image.
    Accepts an optional data URI prefix (data:image/jpeg;base64,...).
    """
    raw_bytes = decode_base64_to_bytes(request.image_base64)
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Empty image data.",
        )
    return _classify_bytes(raw_bytes)


@router.post("/classify/upload", response_model=ClassificationResponse)
async def classify_upload(
    image: UploadFile,
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
) -> ClassificationResponse:
    """
    Classify a civic issue from a multipart file upload.
    This is the endpoint the frontend calls when a citizen submits a photo.
    """
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Empty file.",
        )
    return _classify_bytes(image_bytes)
