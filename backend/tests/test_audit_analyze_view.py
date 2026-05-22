"""Tests for on-demand analyze-view endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.routes.audit import get_audit_service
from app.main import app
from app.models.audit import AuditFrame
from app.models.enums import AuditScanSource, IssueCategory


def test_analyze_audit_view_returns_frame_detail() -> None:
    run_id = uuid4()
    frame = AuditFrame(
        id=uuid4(),
        audit_run_id=run_id,
        frame_index=3,
        latitude=42.66,
        longitude=21.16,
        heading=120,
        pitch=0,
        is_civic_issue=True,
        category=IssueCategory.pothole,
        confidence=0.92,
        severity="high",
        description="Pothole detected",
        image_url="https://example.com/frame.jpg",
        detection_regions=[{"center_x": 0.4, "center_y": 0.6, "radius": 0.12}],
        scan_source=AuditScanSource.on_demand,
        model_name="test-model",
        suggestion_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    service = AsyncMock()
    service.analyze_view.return_value = frame
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    response = client.post(
        f"/api/v1/audit-runs/{run_id}/analyze-view",
        json={
            "latitude": 42.66,
            "longitude": 21.16,
            "heading": 120,
            "pitch": 0,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["frame_index"] == 3
    assert payload["is_civic_issue"] is True
    assert payload["scan_source"] == "on_demand"
    assert payload["detection_regions"][0]["radius"] == 0.12
    service.analyze_view.assert_awaited_once()


def test_find_matching_frame_uses_coordinate_and_heading_tolerance() -> None:
    from app.services.audit_service import AuditService

    frames = [
        AuditFrame(
            id=uuid4(),
            audit_run_id=uuid4(),
            frame_index=0,
            latitude=42.65989424,
            longitude=21.15496238,
            heading=52,
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
        )
    ]

    matched = AuditService._find_matching_frame(frames, 42.65989, 21.15496, 60, 0)
    assert matched is frames[0]

    unmatched = AuditService._find_matching_frame(frames, 42.67, 21.16, 60, 0)
    assert unmatched is None
