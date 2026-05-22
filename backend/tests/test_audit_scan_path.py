from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.routes.audit import get_audit_service
from app.main import app
from app.models.audit import AuditFrame
from app.models.enums import AuditScanSource
from app.services.audit_service import AuditService, KNOWN_ROUTES
from app.utils.route_geometry import build_scan_frames, heading_along_route


def test_build_scan_frames_one_per_waypoint() -> None:
    waypoints = KNOWN_ROUTES["bill clinton boulevard"]
    frames = build_scan_frames(waypoints)

    assert len(frames) == len(waypoints)
    assert frames[0].index == 0
    assert frames[-1].index == len(waypoints) - 1


def test_build_frames_matches_waypoint_count() -> None:
    from unittest.mock import MagicMock

    service = AuditService(MagicMock())
    waypoints = KNOWN_ROUTES["bill clinton boulevard"]
    frames = service._build_frames(waypoints)

    assert len(frames) == len(waypoints)


def test_heading_along_route_uses_next_waypoint() -> None:
    waypoints = KNOWN_ROUTES["bill clinton boulevard"]
    first_heading = heading_along_route(waypoints, 0)
    last_heading = heading_along_route(waypoints, len(waypoints) - 1)

    assert 0 <= first_heading < 360
    assert 0 <= last_heading < 360
    assert first_heading != 0 or len(waypoints) == 1


def test_headings_vary_along_bill_clinton_route() -> None:
    waypoints = KNOWN_ROUTES["bill clinton boulevard"]
    headings = [heading_along_route(waypoints, index) for index in range(len(waypoints))]

    assert len(set(headings)) > 1


def test_list_audit_scan_path_returns_ordered_points() -> None:
    run_id = uuid4()
    frames = [
        AuditFrame(
            id=uuid4(),
            audit_run_id=run_id,
            frame_index=0,
            latitude=42.6596,
            longitude=21.1545,
            heading=52,
            pitch=0,
            is_civic_issue=True,
            category="pothole",
            confidence=0.91,
            severity="high",
            description="Pothole",
            image_url=None,
            detection_regions=None,
            scan_source=AuditScanSource.pipeline,
            model_name="test-model",
            suggestion_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        ),
        AuditFrame(
            id=uuid4(),
            audit_run_id=run_id,
            frame_index=1,
            latitude=42.659894,
            longitude=21.154962,
            heading=53,
            pitch=0,
            is_civic_issue=False,
            category=None,
            confidence=None,
            severity=None,
            description=None,
            image_url=None,
            detection_regions=None,
            scan_source=AuditScanSource.pipeline,
            model_name=None,
            suggestion_id=None,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    service = AsyncMock()
    service.list_scan_path.return_value = frames
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    response = client.get(f"/api/v1/audit-runs/{run_id}/scan-path")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["frame_index"] == 0
    assert payload[0]["is_civic_issue"] is True
    assert payload[0]["severity"] == "high"
    assert payload[0]["scan_source"] == "pipeline"
    assert payload[1]["is_civic_issue"] is False
    assert payload[1]["suggestion_id"] is None
