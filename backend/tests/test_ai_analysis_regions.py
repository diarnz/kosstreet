from app.schemas.report import (
    ImageAnalysisResult,
    sanitize_detection_regions,
)


def test_sanitize_detection_regions_clamps_coordinates_and_radius() -> None:
    regions = sanitize_detection_regions(
        [{"center_x": 1.5, "center_y": -0.2, "radius": 0.5}],
        "high",
    )

    assert regions is not None
    assert len(regions) == 1
    assert regions[0].center_x == 1.0
    assert regions[0].center_y == 0.0
    assert regions[0].radius == 0.18


def test_sanitize_detection_regions_uses_severity_default_radius() -> None:
    regions = sanitize_detection_regions(
        [{"center_x": 0.4, "center_y": 0.6}],
        "low",
    )

    assert regions is not None
    assert regions[0].radius == 0.06


def test_sanitize_detection_regions_keeps_primary_region_only() -> None:
    regions = sanitize_detection_regions(
        [
            {"center_x": 0.2, "center_y": 0.3, "radius": 0.08},
            {"center_x": 0.7, "center_y": 0.8, "radius": 0.1},
        ],
        "medium",
    )

    assert regions is not None
    assert len(regions) == 1
    assert regions[0].center_x == 0.2


def test_image_analysis_result_parses_regions_for_civic_issue() -> None:
    result = ImageAnalysisResult.from_model_payload(
        {
            "is_civic_issue": True,
            "category": "pothole",
            "confidence": 0.91,
            "severity": "high",
            "description": "Large pothole in the right lane.",
            "regions": [{"center_x": 0.42, "center_y": 0.68, "radius": 0.12}],
        }
    )

    assert result.is_civic_issue is True
    assert result.regions is not None
    assert result.regions[0].center_x == 0.42
    assert result.regions[0].radius == 0.12


def test_image_analysis_result_clears_regions_when_not_civic_issue() -> None:
    result = ImageAnalysisResult.from_model_payload(
        {
            "is_civic_issue": False,
            "regions": [{"center_x": 0.5, "center_y": 0.5, "radius": 0.1}],
        }
    )

    assert result.is_civic_issue is False
    assert result.regions is None


def test_image_analysis_result_allows_missing_regions() -> None:
    result = ImageAnalysisResult.from_model_payload(
        {
            "is_civic_issue": True,
            "category": "garbage",
            "confidence": 0.8,
            "severity": "medium",
            "description": "Trash bags on the sidewalk.",
            "regions": None,
        }
    )

    assert result.is_civic_issue is True
    assert result.regions is None


def test_image_analysis_result_invalid_payload_falls_back_to_empty() -> None:
    result = ImageAnalysisResult.from_model_payload({"confidence": "not-a-number"})

    assert result.is_civic_issue is False
    assert result.regions is None
