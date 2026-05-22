"""Tests for on-demand analyze quota and suggestion conversion."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.routes.audit import get_audit_service
from app.main import app
from app.models.audit import AuditSuggestion
from app.models.enums import AuditSuggestionStatus, IssueCategory
from app.schemas.audit import SuggestionConversionResult


def test_get_on_demand_analyze_quota() -> None:
    run_id = uuid4()
    resets_at = datetime.now(timezone.utc)

    service = AsyncMock()
    service.get_on_demand_quota.return_value = {
        "limit": 10,
        "used": 3,
        "remaining": 7,
        "resets_at": resets_at,
    }
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    response = client.get(f"/api/v1/audit-runs/{run_id}/on-demand-quota")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 10
    assert payload["used"] == 3
    assert payload["remaining"] == 7
    service.get_on_demand_quota.assert_awaited_once()


def test_convert_suggestion_preserves_geo_and_frame_reference() -> None:
    suggestion_id = uuid4()
    report_id = uuid4()
    run_id = uuid4()

    suggestion = AuditSuggestion(
        id=suggestion_id,
        audit_run_id=run_id,
        category=IssueCategory.pothole,
        status=AuditSuggestionStatus.pending_review,
        latitude=42.6596,
        longitude=21.1545,
        confidence=0.91,
        severity="high",
        description="Large pothole in travel lane",
        model_name="test-model",
        explanation="Detected during audit",
        image_url="https://example.com/frame.jpg",
        image_attribution="Google Street View",
        department="Roads / Public Works",
        heading=120,
        pitch=0,
        frame_index=4,
        detection_regions=[{"center_x": 0.4, "center_y": 0.6, "radius": 0.12}],
        created_at=datetime.now(timezone.utc),
    )

    service = AsyncMock()
    service.convert_to_report.return_value = SuggestionConversionResult(report_id=report_id)
    service.get_suggestion.return_value = suggestion
    app.dependency_overrides[get_audit_service] = lambda: service

    client = TestClient(app)
    response = client.post(f"/api/v1/audit-suggestions/{suggestion_id}/convert-to-report")

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["report_id"] == str(report_id)
    service.convert_to_report.assert_awaited_once_with(suggestion_id)

    assert suggestion.latitude == 42.6596
    assert suggestion.longitude == 21.1545
    assert suggestion.frame_index == 4
