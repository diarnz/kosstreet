from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.audit import (
    AuditFrameDetail,
    AuditFrameSummary,
    AuditSuggestionRead,
    regions_from_json,
    regions_to_json,
)
from app.schemas.report import DetectionRegion, ImageAnalysisResult


def test_regions_to_json_round_trip() -> None:
    regions = [DetectionRegion(center_x=0.4, center_y=0.6, radius=0.09)]
    payload = regions_to_json(regions)
    assert payload == [{"center_x": 0.4, "center_y": 0.6, "radius": 0.09}]
    assert regions_from_json(payload) == regions


def test_audit_suggestion_read_hides_raw_image_url() -> None:
    suggestion = SimpleNamespace(
        id=uuid4(),
        audit_run_id=uuid4(),
        category="pothole",
        status="pending_review",
        latitude=42.66,
        longitude=21.16,
        confidence=0.91,
        severity="high",
        description="Large pothole",
        model_name="test-model",
        explanation="AI street-audit frame analysis.",
        image_url="https://maps.googleapis.com/example?key=secret",
        image_attribution="Google Street View",
        department="Public Works",
        heading=90,
        pitch=0,
        frame_index=3,
        detection_regions=[{"center_x": 0.42, "center_y": 0.68, "radius": 0.12}],
        converted_report_id=None,
        reviewer_note=None,
        created_at=datetime.now(timezone.utc),
    )

    read = AuditSuggestionRead.from_model(suggestion)

    assert read.image_url is None
    assert read.frame_index == 3
    assert read.frame_image_url == f"/api/v1/audit-suggestions/{suggestion.id}/frame-image"
    assert read.detection_regions is not None
    assert read.detection_regions[0].center_x == 0.42


def test_audit_frame_summary_from_model() -> None:
    run_id = uuid4()
    frame = SimpleNamespace(
        id=uuid4(),
        audit_run_id=run_id,
        frame_index=7,
        latitude=42.66,
        longitude=21.16,
        heading=180,
        pitch=0,
        is_civic_issue=True,
        category="garbage",
        confidence=0.82,
        severity="medium",
        suggestion_id=uuid4(),
        detection_regions=[{"center_x": 0.5, "center_y": 0.5, "radius": 0.09}],
        created_at=datetime.now(timezone.utc),
    )

    read = AuditFrameSummary.from_model(frame)

    assert read.has_detection_regions is True
    assert read.frame_image_url == f"/api/v1/audit-runs/{run_id}/frames/7/image"


def test_audit_frame_detail_from_model() -> None:
    run_id = uuid4()
    frame = SimpleNamespace(
        id=uuid4(),
        audit_run_id=run_id,
        frame_index=1,
        latitude=42.66,
        longitude=21.16,
        heading=0,
        pitch=0,
        is_civic_issue=False,
        category=None,
        confidence=None,
        severity=None,
        description=None,
        detection_regions=None,
        model_name="test-model",
        suggestion_id=None,
        created_at=datetime.now(timezone.utc),
    )

    read = AuditFrameDetail.from_model(frame)

    assert read.description is None
    assert read.detection_regions is None
    assert read.frame_image_url == f"/api/v1/audit-runs/{run_id}/frames/1/image"


def test_image_analysis_result_regions_flow_into_json_storage() -> None:
    result = ImageAnalysisResult.from_model_payload(
        {
            "is_civic_issue": True,
            "category": "pothole",
            "confidence": 0.9,
            "severity": "high",
            "description": "Pothole ahead",
            "regions": [{"center_x": 0.3, "center_y": 0.7, "radius": 0.12}],
        }
    )

    stored = regions_to_json(result.regions)
    assert stored is not None
    assert stored[0]["radius"] == 0.12
