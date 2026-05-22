from __future__ import annotations

import json

import pytest

from kostreet_ai.inference.classifier import ImageClassifier, _FALLBACK, get_classifier
from kostreet_ai.inference.client import OpenRouterClient
from kostreet_ai.schemas import IssueCategory, IssueSeverity


def _make_classifier(monkeypatch, response_json: str) -> ImageClassifier:
    """Return a classifier whose HTTP client is replaced with a fixed JSON response."""
    monkeypatch.setattr(
        OpenRouterClient,
        "chat",
        lambda self, messages, response_format=None: response_json,
    )
    return get_classifier()


def _valid_json(**overrides) -> str:
    base = {
        "category": "pothole",
        "confidence": 0.87,
        "severity": "medium",
        "description": "Road surface depression visible in the right lane.",
        "is_civic_issue": True,
    }
    base.update(overrides)
    return json.dumps(base)


def test_classify_returns_correct_category(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(category="pothole", confidence=0.87))
    result = clf.classify("fake_b64")
    assert result.category == IssueCategory.pothole
    assert result.confidence == pytest.approx(0.87)
    assert result.is_civic_issue is True


def test_classify_returns_fallback_on_invalid_json(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, "this is not json at all")
    result = clf.classify("fake_b64")
    assert result.category == IssueCategory.other
    assert result.confidence == 0.0
    assert result.is_civic_issue is False


def test_classify_returns_fallback_on_empty_json_object(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, "{}")
    result = clf.classify("fake_b64")
    assert result.category == IssueCategory.other
    assert result.confidence == 0.0


def test_classify_coerces_unknown_category_to_other(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(category="road_crack"))
    result = clf.classify("fake_b64")
    assert result.category == IssueCategory.other


def test_classify_clamps_confidence_above_one(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(confidence=1.5))
    result = clf.classify("fake_b64")
    assert result.confidence == pytest.approx(1.0)


def test_classify_clamps_confidence_below_zero(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(confidence=-0.3))
    result = clf.classify("fake_b64")
    assert result.confidence == pytest.approx(0.0)


def test_severity_floor_broken_streetlight_upgrades_to_high(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(category="broken_streetlight", severity="low"))
    result = clf.classify("fake_b64")
    assert result.severity == IssueSeverity.high


def test_severity_floor_pothole_upgrades_low_to_medium(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(category="pothole", severity="low"))
    result = clf.classify("fake_b64")
    assert result.severity == IssueSeverity.medium


def test_severity_floor_does_not_downgrade_high(monkeypatch) -> None:
    clf = _make_classifier(monkeypatch, _valid_json(category="pothole", severity="high"))
    result = clf.classify("fake_b64")
    assert result.severity == IssueSeverity.high


def test_classify_returns_fallback_on_network_error(monkeypatch) -> None:
    import httpx

    monkeypatch.setattr(
        OpenRouterClient,
        "chat",
        lambda self, messages, response_format=None: (_ for _ in ()).throw(
            httpx.ConnectError("connection refused")
        ),
    )
    clf = get_classifier()
    result = clf.classify("fake_b64")
    assert result.category == IssueCategory.other
    assert result.confidence == 0.0
    assert result.is_civic_issue is False
