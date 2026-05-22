from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.routes.audit import get_audit_service
from app.main import app
from app.schemas.audit import AuditFrameDetail, AuditFrameSummary, AuditSuggestionRead
from app.schemas.report import DetectionRegion


RUN_ID = UUID("11111111-1111-1111-1111-111111111111")
FRAME_ID = UUID("22222222-2222-2222-2222-222222222222")
SUGGESTION_ID = UUID("33333333-3333-3333-3333-333333333333")


@pytest.fixture(scope="module")
def client() -> TestClient:
    mock_service = AsyncMock()
    mock_service.get_run = AsyncMock(return_value=SimpleNamespace(id=RUN_ID))
    mock_service.list_frames = AsyncMock(
        return_value=[
            SimpleNamespace(
                id=FRAME_ID,
                audit_run_id=RUN_ID,
                frame_index=0,
                latitude=42.6596,
                longitude=21.1545,
                heading=0,
                pitch=0,
                is_civic_issue=True,
                category="pothole",
                confidence=0.91,
                severity="high",
                suggestion_id=SUGGESTION_ID,
                detection_regions=[
                    {"center_x": 0.46, "center_y": 0.72, "radius": 0.12},
                ],
                model_name="demo-model",
                description="Large pothole in the lane.",
                image_url="https://example.com/frame.jpg",
                created_at=datetime.now(timezone.utc),
            )
        ]
    )
    mock_service.get_frame = AsyncMock(return_value=mock_service.list_frames.return_value[0])
    mock_service.get_frame_image = AsyncMock(return_value=(b"fake-image-bytes", "image/jpeg"))
    mock_service.get_suggestion = AsyncMock(
        return_value=SimpleNamespace(
            id=SUGGESTION_ID,
            audit_run_id=RUN_ID,
            category="pothole",
            status="pending_review",
            latitude=42.6596,
            longitude=21.1545,
            confidence=0.91,
            severity="high",
            description="Large pothole in the lane.",
            model_name="demo-model",
            explanation="Seeded AI detection.",
            image_url="https://example.com/frame.jpg",
            image_attribution="Google Street View",
            department="Roads / Public Works",
            heading=0,
            pitch=0,
            frame_index=0,
            detection_regions=[{"center_x": 0.46, "center_y": 0.72, "radius": 0.12}],
            converted_report_id=None,
            reviewer_note=None,
            created_at=datetime.now(timezone.utc),
        )
    )
    mock_service.get_suggestion_frame_image = AsyncMock(
        return_value=(b"fake-image-bytes", "image/jpeg")
    )

    app.dependency_overrides[get_audit_service] = lambda: mock_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_list_audit_frames_returns_summary_with_proxy_url(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit-runs/{RUN_ID}/frames")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["frame_index"] == 0
    assert payload[0]["has_detection_regions"] is True
    assert payload[0]["frame_image_url"] == f"/api/v1/audit-runs/{RUN_ID}/frames/0/image"


def test_get_audit_frame_detail_includes_regions(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit-runs/{RUN_ID}/frames/0")

    assert response.status_code == 200
    payload = response.json()
    assert payload["detection_regions"][0]["center_x"] == 0.46
    assert payload["description"] == "Large pothole in the lane."


def test_get_audit_frame_image_proxies_bytes(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit-runs/{RUN_ID}/frames/0/image")

    assert response.status_code == 200
    assert response.content == b"fake-image-bytes"
    assert response.headers["content-type"].startswith("image/jpeg")


def test_get_audit_suggestion_includes_frame_metadata(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit-suggestions/{SUGGESTION_ID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["frame_index"] == 0
    assert payload["detection_regions"][0]["radius"] == 0.12
    assert payload["frame_image_url"] == f"/api/v1/audit-suggestions/{SUGGESTION_ID}/frame-image"
    assert payload["image_url"] is None


def test_audit_frame_schemas_validate_regions() -> None:
    frame = SimpleNamespace(
        id=FRAME_ID,
        audit_run_id=RUN_ID,
        frame_index=3,
        latitude=42.66,
        longitude=21.16,
        heading=90,
        pitch=0,
        is_civic_issue=True,
        category="garbage",
        confidence=0.82,
        severity="medium",
        suggestion_id=SUGGESTION_ID,
        detection_regions=[{"center_x": 0.3, "center_y": 0.6, "radius": 0.09}],
        model_name="demo-model",
        description="Garbage bags on sidewalk.",
        created_at=datetime.now(timezone.utc),
    )

    detail = AuditFrameDetail.from_model(frame)
    assert detail.detection_regions is not None
    assert detail.detection_regions[0].radius == 0.09

    summary = AuditFrameSummary.from_model(frame)
    assert summary.has_detection_regions is True


def test_detection_region_schema_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        DetectionRegion(center_x=1.5, center_y=-0.2, radius=0.5)
