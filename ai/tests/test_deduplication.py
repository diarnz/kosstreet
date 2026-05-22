from __future__ import annotations

import pytest

from kostreet_ai.geospatial.deduplication import (
    compute_centroid,
    deduplicate_and_filter,
    deduplicate_detections,
    filter_by_confidence,
)
from kostreet_ai.schemas import DetectionWithLocation, IssueCategory, IssueSeverity
from kostreet_ai.street_audit.planner import haversine_meters


def _det(
    category: IssueCategory,
    confidence: float,
    lat: float,
    lng: float,
) -> DetectionWithLocation:
    return DetectionWithLocation(
        category=category,
        confidence=confidence,
        severity=IssueSeverity.medium,
        description="test",
        is_civic_issue=True,
        latitude=lat,
        longitude=lng,
        heading=0,
        pitch=0,
    )


# ---------------------------------------------------------------------------
# haversine
# ---------------------------------------------------------------------------

def test_haversine_known_distance() -> None:
    d = haversine_meters(42.6629, 21.1655, 42.6638, 21.1655)
    assert 95 < d < 105


def test_haversine_same_point_is_zero() -> None:
    assert haversine_meters(42.66, 21.16, 42.66, 21.16) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# deduplicate_detections
# ---------------------------------------------------------------------------

def test_deduplicate_collapses_nearby_same_category() -> None:
    detections = [
        _det(IssueCategory.pothole, 0.91, 42.6629, 21.1655),
        _det(IssueCategory.pothole, 0.74, 42.6630, 21.1656),  # ~12m away
    ]
    result = deduplicate_detections(detections, radius_meters=20.0)
    assert len(result) == 1
    assert result[0].confidence == pytest.approx(0.91)


def test_deduplicate_keeps_far_same_category() -> None:
    detections = [
        _det(IssueCategory.pothole, 0.91, 42.6629, 21.1655),
        _det(IssueCategory.pothole, 0.74, 42.6680, 21.1700),  # ~60m away
    ]
    result = deduplicate_detections(detections, radius_meters=20.0)
    assert len(result) == 2


def test_deduplicate_keeps_different_categories_at_same_location() -> None:
    detections = [
        _det(IssueCategory.pothole, 0.80, 42.6629, 21.1655),
        _det(IssueCategory.garbage, 0.75, 42.6629, 21.1655),
    ]
    result = deduplicate_detections(detections, radius_meters=20.0)
    assert len(result) == 2


def test_deduplicate_empty_list() -> None:
    assert deduplicate_detections([], radius_meters=20.0) == []


def test_deduplicate_highest_confidence_survives() -> None:
    detections = [
        _det(IssueCategory.garbage, 0.60, 42.6629, 21.1655),
        _det(IssueCategory.garbage, 0.95, 42.6629, 21.1655),  # same spot, higher conf
        _det(IssueCategory.garbage, 0.40, 42.6629, 21.1655),
    ]
    result = deduplicate_detections(detections, radius_meters=20.0)
    assert len(result) == 1
    assert result[0].confidence == pytest.approx(0.95)


# ---------------------------------------------------------------------------
# filter_by_confidence
# ---------------------------------------------------------------------------

def test_filter_by_confidence_keeps_at_threshold() -> None:
    d = _det(IssueCategory.pothole, 0.55, 42.66, 21.16)
    result = filter_by_confidence([d], threshold=0.55)
    assert len(result) == 1


def test_filter_by_confidence_drops_below_threshold() -> None:
    d = _det(IssueCategory.pothole, 0.54, 42.66, 21.16)
    result = filter_by_confidence([d], threshold=0.55)
    assert len(result) == 0


# ---------------------------------------------------------------------------
# deduplicate_and_filter
# ---------------------------------------------------------------------------

def test_deduplicate_and_filter_full_pipeline() -> None:
    detections = [
        _det(IssueCategory.pothole, 0.91, 42.6629, 21.1655),
        _det(IssueCategory.pothole, 0.74, 42.6630, 21.1656),  # near + weaker
        _det(IssueCategory.garbage, 0.30, 42.6629, 21.1655),  # below threshold
    ]
    result = deduplicate_and_filter(detections, radius_meters=20.0, confidence_threshold=0.55)
    assert len(result) == 1
    assert result[0].category == IssueCategory.pothole
    assert result[0].confidence == pytest.approx(0.91)


def test_deduplicate_result_sorted_by_confidence_descending() -> None:
    detections = [
        _det(IssueCategory.pothole,  0.60, 42.6629, 21.1655),
        _det(IssueCategory.garbage,  0.90, 42.6680, 21.1700),
        _det(IssueCategory.damaged_sign, 0.75, 42.6700, 21.1750),
    ]
    result = deduplicate_and_filter(detections, radius_meters=20.0, confidence_threshold=0.55)
    confidences = [r.confidence for r in result]
    assert confidences == sorted(confidences, reverse=True)


# ---------------------------------------------------------------------------
# compute_centroid
# ---------------------------------------------------------------------------

def test_compute_centroid_two_points() -> None:
    result = compute_centroid([(42.66, 21.16), (42.68, 21.18)])
    assert result[0] == pytest.approx(42.67)
    assert result[1] == pytest.approx(21.17)


def test_compute_centroid_raises_on_empty_list() -> None:
    with pytest.raises(ValueError):
        compute_centroid([])
