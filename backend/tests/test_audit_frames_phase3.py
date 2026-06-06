from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import asyncio

from fastapi.testclient import TestClient
from app.api.v1.routes.audit import get_audit_service
from app.main import app
from app.models.audit import AuditFrame, AuditRun, AuditSuggestion
from app.models.enums import AuditSuggestionStatus, IssueCategory
from app.schemas.audit import audit_frame_to_detail, audit_frame_to_summary, audit_suggestion_to_read
from app.schemas.report import ImageAnalysisResult
from app.services.audit_service import AuditService
from app.utils.detection_regions import sanitize_detection_region, sanitize_detection_regions


def test_sanitize_detection_region_clamps_coordinates() -> None:
    region = sanitize_detection_region(
        {"center_x": 1.4, "center_y": -0.2, "radius": 0.25},
        "high",
    )

    assert region == {"center_x": 1.0, "center_y": 0.0, "radius": 0.18}


def test_sanitize_detection_regions_uses_severity_default_radius() -> None:
    regions = sanitize_detection_regions([{"center_x": 0.5, "center_y": 0.5}], "low")

    assert regions == [{"center_x": 0.5, "center_y": 0.5, "radius": 0.06}]


def test_image_analysis_result_regions_flow_into_json_storage() -> None:
    result = ImageAnalysisResult(
        is_civic_issue=True,
        category=IssueCategory.pothole,
        confidence=0.91,
        severity="high",
        description="Large pothole in the right lane.",
        regions=[{"center_x": 0.42, "center_y": 0.68, "radius": 0.12}],
    )

    payload = result.model_dump()
    assert payload["regions"][0]["radius"] == 0.12


def test_audit_suggestion_read_hides_raw_image_url() -> None:
    suggestion_id = uuid4()
    run_id = uuid4()
    suggestion = AuditSuggestion(
        id=suggestion_id,
        audit_run_id=run_id,
        category=IssueCategory.pothole,
        status=AuditSuggestionStatus.pending_review,
        location=None,
        latitude=42.66,
        longitude=21.16,
        confidence=0.9,
        severity="high",
        description="Pothole",
        model_name="test-model",
        explanation="test",
        image_url="https://maps.googleapis.com/maps/api/streetview?key=secret",
        image_attribution="Google Street View",
        department="Roads",
        heading=90,
        pitch=0,
        frame_index=3,
        detection_regions=[{"center_x": 0.4, "center_y": 0.6, "radius": 0.12}],
        created_at=datetime.now(timezone.utc),
    )

    read_model = audit_suggestion_to_read(suggestion)

    assert read_model.frame_index == 3
    assert read_model.detection_regions[0].radius == 0.12
    assert read_model.frame_image_url.endswith(f"/audit-suggestions/{suggestion_id}/frame-image")
    assert "image_url" not in read_model.model_dump()


def test_audit_frame_summary_from_model() -> None:
    run_id = uuid4()
    frame = AuditFrame(
        id=uuid4(),
        audit_run_id=run_id,
        frame_index=7,
        latitude=42.66,
        longitude=21.16,
        heading=180,
        pitch=0,
        is_civic_issue=True,
        category=IssueCategory.garbage,
        confidence=0.8,
        severity="medium",
        description="Trash bags on sidewalk.",
        image_url="https://example.com/frame.jpg",
        model_name="test-model",
        detection_regions=[{"center_x": 0.5, "center_y": 0.5, "radius": 0.09}],
        scan_source="pipeline",
        suggestion_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    summary = audit_frame_to_summary(frame)

    assert summary.frame_index == 7
    assert summary.frame_image_url.endswith(f"/audit-runs/{run_id}/frames/7/image")


def test_audit_frame_detail_from_model() -> None:
    run_id = uuid4()
    frame = AuditFrame(
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
        image_url=None,
        scan_source="pipeline",
        model_name=None,
        suggestion_id=None,
        created_at=datetime.now(timezone.utc),
    )

    detail = audit_frame_to_detail(frame)

    assert detail.is_civic_issue is False
    assert detail.detection_regions == []
    assert detail.scan_source == "pipeline"


def test_get_audit_frame_image_proxies_bytes() -> None:
    service = AsyncMock()
    service.get_frame_image.return_value = (b"fakejpeg", "image/jpeg")
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    run_id = uuid4()
    response = client.get(f"/api/v1/audit-runs/{run_id}/frames/2/image")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.content == b"fakejpeg"
    assert response.headers["content-type"].startswith("image/jpeg")


def test_list_audit_frames_returns_summary_with_proxy_url() -> None:
    run_id = uuid4()
    frame = AuditFrame(
        id=uuid4(),
        audit_run_id=run_id,
        frame_index=0,
        latitude=42.66,
        longitude=21.16,
        heading=0,
        pitch=0,
        is_civic_issue=False,
        category=None,
        confidence=None,
        severity=None,
        description=None,
        image_url=None,
        scan_source="pipeline",
        model_name=None,
        detection_regions=None,
        suggestion_id=None,
        created_at=datetime.now(timezone.utc),
    )
    service = AsyncMock()
    service.list_frames.return_value = [frame]
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    response = client.get(f"/api/v1/audit-runs/{run_id}/frames")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["frame_image_url"].endswith(f"/audit-runs/{run_id}/frames/0/image")


def test_resolve_waypoints_prefers_scan_coordinates_over_route_name() -> None:
    service = AuditService(MagicMock())
    service._expand_scan_waypoints = MagicMock(return_value=[(42.213502, 20.741404)])
    run = AuditRun(
        id=uuid4(),
        municipality="Kosovo",
        route_name="Naim Buduri, Kosovo",
        scan_latitude=42.2137,
        scan_longitude=20.7397,
        notes=None,
        status="queued",
        frames_total=0,
        frames_done=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    waypoints = asyncio.run(service._resolve_waypoints(run))

    service._expand_scan_waypoints.assert_called_once_with(42.2137, 20.7397)
    assert waypoints == [(42.213502, 20.741404)]


def test_is_no_imagery_placeholder_detects_small_payloads() -> None:
    from app.integrations.street_imagery import is_no_imagery_placeholder

    assert is_no_imagery_placeholder(b"x" * 8_000) is True
    assert is_no_imagery_placeholder(b"x" * 80_000) is False
