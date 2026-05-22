from __future__ import annotations

from kostreet_ai.schemas import DetectionWithLocation
from kostreet_ai.street_audit.planner import haversine_meters


def filter_by_confidence(
    detections: list[DetectionWithLocation],
    threshold: float,
) -> list[DetectionWithLocation]:
    """Return only detections whose confidence is at or above threshold."""
    return [d for d in detections if d.confidence >= threshold]


def deduplicate_detections(
    detections: list[DetectionWithLocation],
    radius_meters: float = 20.0,
) -> list[DetectionWithLocation]:
    """
    Collapse nearby same-category detections into one, keeping the
    highest-confidence detection per spatial cluster per category.

    Algorithm — greedy confidence-first spatial merge:
    1. Sort by confidence descending so the best detection is always processed first.
    2. For each detection, check whether any already-kept detection shares
       the same category and is within radius_meters.
    3. If yes: discard (it is a lower-confidence duplicate).
    4. If no: keep it (new cluster or new category at this location).

    Different categories at the same location are always kept separately —
    a pothole and garbage at the same corner are two different tickets.
    """
    sorted_detections = sorted(detections, key=lambda d: d.confidence, reverse=True)
    kept: list[DetectionWithLocation] = []

    for candidate in sorted_detections:
        is_duplicate = any(
            kept_d.category == candidate.category
            and haversine_meters(
                kept_d.latitude, kept_d.longitude,
                candidate.latitude, candidate.longitude,
            ) <= radius_meters
            for kept_d in kept
        )
        if not is_duplicate:
            kept.append(candidate)

    return kept


def compute_centroid(
    points: list[tuple[float, float]],
) -> tuple[float, float]:
    """
    Return the arithmetic mean (lat, lng) of a list of coordinate pairs.
    Used to place a merged detection marker at the center of its cluster.
    """
    if not points:
        raise ValueError("Cannot compute centroid of an empty list.")
    avg_lat = sum(p[0] for p in points) / len(points)
    avg_lng = sum(p[1] for p in points) / len(points)
    return (avg_lat, avg_lng)


def deduplicate_and_filter(
    detections: list[DetectionWithLocation],
    radius_meters: float = 20.0,
    confidence_threshold: float = 0.55,
) -> list[DetectionWithLocation]:
    """
    Full pipeline: filter low-confidence detections, then deduplicate
    nearby same-category ones. Returns results sorted by confidence
    descending so the most important issues appear first.

    This is the function called by the audit API endpoint in Phase 6.
    """
    filtered = filter_by_confidence(detections, confidence_threshold)
    deduped = deduplicate_detections(filtered, radius_meters)
    return sorted(deduped, key=lambda d: d.confidence, reverse=True)
