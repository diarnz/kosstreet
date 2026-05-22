from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from kostreet_ai.config import settings
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import (
    decode_base64_to_bytes,
    encode_image_to_base64,
    validate_image,
)
from kostreet_ai.schemas import (
    AuditPlanRequest,
    AuditPlanResponse,
    DetectionWithLocation,
    FrameAnalysisRequest,
    FrameAnalysisResponse,
)
from kostreet_ai.street_audit.planner import build_audit_scan_plan

router = APIRouter()


@router.post("/plan", response_model=AuditPlanResponse)
def plan_audit(request: AuditPlanRequest) -> AuditPlanResponse:
    """
    Generate the complete list of (lat, lng, heading, pitch) scan frames
    for a street route. Pure math — no model calls, responds instantly.
    """
    waypoints = [(w.lat, w.lng) for w in request.waypoints]
    frames = build_audit_scan_plan(
        waypoints=waypoints,
        step_meters=request.step_meters,
        headings=request.headings,
        pitches=request.pitches,
    )
    return AuditPlanResponse(scan_points=frames, total_frames=len(frames))


@router.post("/analyze-frame", response_model=FrameAnalysisResponse)
def analyze_frame(request: FrameAnalysisRequest) -> FrameAnalysisResponse:
    """
    Run AI classification on a single street audit frame.
    Returns a detection if a civic issue is found above the confidence threshold.
    Returns an empty detections list if no issue is found or confidence is too low.

    Deduplication across multiple frames is the backend's responsibility.
    """
    raw_bytes = decode_base64_to_bytes(request.image_base64)
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Empty image data.",
        )
    if not validate_image(raw_bytes):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or unreadable image.",
        )

    b64 = encode_image_to_base64(raw_bytes, settings.max_image_size_px)
    result = get_classifier().classify(b64)

    detections: list[DetectionWithLocation] = []
    if result.is_civic_issue and result.confidence >= settings.confidence_threshold:
        detections.append(
            DetectionWithLocation(
                category=result.category,
                confidence=result.confidence,
                severity=result.severity,
                description=result.description,
                is_civic_issue=True,
                latitude=request.latitude,
                longitude=request.longitude,
                heading=request.heading,
                pitch=request.pitch,
            )
        )

    return FrameAnalysisResponse(
        detections=detections,
        frame_latitude=request.latitude,
        frame_longitude=request.longitude,
        heading=request.heading,
        pitch=request.pitch,
    )
