from __future__ import annotations

import json

import pytest

from kostreet_ai.inference.classifier import (
    ImageClassifier,
    _FALLBACK,
    _apply_category_threshold,
    _needs_second_pass,
    get_classifier,
)
from kostreet_ai.inference.client import OpenRouterClient
from kostreet_ai.inference.prompts import ClassificationContext
from kostreet_ai.schemas import ClassificationResult, IssueCategory, IssueSeverity


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


def test_needs_second_pass_on_low_confidence() -> None:
    result = ClassificationResult(
        category=IssueCategory.garbage,
        confidence=0.65,
        severity=IssueSeverity.medium,
        description="Small litter visible.",
        is_civic_issue=True,
    )
    assert _needs_second_pass(result) is True


def test_needs_second_pass_on_weak_category_below_cutoff() -> None:
    result = ClassificationResult(
        category=IssueCategory.other,
        confidence=0.80,
        severity=IssueSeverity.medium,
        description="Flooded road section.",
        is_civic_issue=True,
    )
    assert _needs_second_pass(result) is True


def test_needs_second_pass_on_pothole_description_mismatch() -> None:
    result = ClassificationResult(
        category=IssueCategory.pothole,
        confidence=0.95,
        severity=IssueSeverity.medium,
        description="Cracked sidewalk along the pedestrian path.",
        is_civic_issue=True,
    )
    assert _needs_second_pass(result) is True


def test_needs_second_pass_skips_confident_pothole() -> None:
    result = ClassificationResult(
        category=IssueCategory.pothole,
        confidence=0.95,
        severity=IssueSeverity.medium,
        description="Large pothole in the right traffic lane.",
        is_civic_issue=True,
    )
    assert _needs_second_pass(result) is False


def test_apply_category_threshold_clears_low_confidence_civic_flag() -> None:
    result = ClassificationResult(
        category=IssueCategory.other,
        confidence=0.40,
        severity=IssueSeverity.medium,
        description="Flooded street.",
        is_civic_issue=True,
    )
    adjusted = _apply_category_threshold(result)
    assert adjusted.is_civic_issue is False


def test_classify_runs_second_pass_when_first_is_uncertain(monkeypatch) -> None:
    calls: list[str] = []

    def fake_chat(self, messages, response_format=None):
        user_text = messages[1]["content"][0]["text"]
        calls.append(user_text)
        if len(calls) == 1:
            return _valid_json(category="other", confidence=0.60, is_civic_issue=True)
        return _valid_json(category="other", confidence=0.88, is_civic_issue=True)

    monkeypatch.setattr(OpenRouterClient, "chat", fake_chat)
    result = get_classifier().classify("fake_b64")
    assert len(calls) == 2
    assert "Re-examine ONLY" in calls[1]
    assert result.category == IssueCategory.other
    assert result.confidence == pytest.approx(0.88)


def test_classify_uses_street_audit_context_in_system_prompt(monkeypatch) -> None:
    captured: list[str] = []

    def fake_chat(self, messages, response_format=None):
        captured.append(messages[0]["content"])
        return _valid_json()

    monkeypatch.setattr(OpenRouterClient, "chat", fake_chat)
    get_classifier().classify("fake_b64", context=ClassificationContext.street_audit)
    assert "Street audit context" in captured[0]


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
