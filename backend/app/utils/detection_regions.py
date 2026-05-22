from typing import Any

SEVERITY_DEFAULT_RADIUS: dict[str, float] = {
    "low": 0.06,
    "medium": 0.09,
    "high": 0.12,
    "critical": 0.14,
}

MIN_RADIUS = 0.04
MAX_RADIUS = 0.18


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def sanitize_detection_region(
    region: dict[str, Any],
    severity: str | None = None,
) -> dict[str, float] | None:
    try:
        center_x = float(region["center_x"])
        center_y = float(region["center_y"])
    except (KeyError, TypeError, ValueError):
        return None

    radius_raw = region.get("radius")
    if radius_raw is None:
        radius = SEVERITY_DEFAULT_RADIUS.get(severity or "medium", 0.09)
    else:
        try:
            radius = float(radius_raw)
        except (TypeError, ValueError):
            radius = SEVERITY_DEFAULT_RADIUS.get(severity or "medium", 0.09)

    return {
        "center_x": _clamp(center_x, 0.0, 1.0),
        "center_y": _clamp(center_y, 0.0, 1.0),
        "radius": _clamp(radius, MIN_RADIUS, MAX_RADIUS),
    }


def sanitize_detection_regions(
    regions: list[Any] | None,
    severity: str | None = None,
) -> list[dict[str, float]]:
    if not regions:
        return []

    for region in regions:
        if not isinstance(region, dict):
            continue
        cleaned = sanitize_detection_region(region, severity)
        if cleaned is not None:
            return [cleaned]

    return []


def regions_to_json(regions: list[dict[str, float]] | None) -> list[dict[str, float]] | None:
    if not regions:
        return None
    return regions


def primary_detection_region(
    regions: list[dict[str, float]] | None,
) -> dict[str, float] | None:
    if not regions:
        return None
    return regions[0]
