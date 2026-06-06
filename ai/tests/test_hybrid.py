from __future__ import annotations

from kostreet_ai.inference.hybrid import merge_gemma_yolo
from kostreet_ai.inference.yolo_detector import GarbageYoloHit
from kostreet_ai.schemas import ClassificationResult, IssueCategory, IssueSeverity


def _gemma(
    *,
    category: IssueCategory = IssueCategory.other,
    confidence: float = 0.3,
    is_civic_issue: bool = False,
) -> ClassificationResult:
    return ClassificationResult(
        category=category,
        confidence=confidence,
        severity=IssueSeverity.low,
        description="No civic issue detected in this image.",
        is_civic_issue=is_civic_issue,
    )


def test_merge_overrides_non_garbage_when_yolo_fires() -> None:
    result = merge_gemma_yolo(
        _gemma(),
        GarbageYoloHit(confidence=0.81),
        threshold=0.40,
        confidence_boost=0.15,
    )
    assert result.category == IssueCategory.garbage
    assert result.is_civic_issue is True
    assert result.confidence >= 0.72


def test_merge_boosts_agreeing_garbage_confidence() -> None:
    result = merge_gemma_yolo(
        _gemma(category=IssueCategory.garbage, confidence=0.70, is_civic_issue=True),
        GarbageYoloHit(confidence=0.85),
        threshold=0.40,
        confidence_boost=0.15,
    )
    assert result.category == IssueCategory.garbage
    assert result.confidence == 0.85


def test_merge_keeps_gemma_when_yolo_below_threshold() -> None:
    gemma = _gemma(category=IssueCategory.pothole, confidence=0.91, is_civic_issue=True)
    result = merge_gemma_yolo(
        gemma,
        GarbageYoloHit(confidence=0.20),
        threshold=0.40,
        confidence_boost=0.15,
    )
    assert result == gemma


def test_merge_keeps_pothole_when_yolo_absent() -> None:
    gemma = _gemma(category=IssueCategory.pothole, confidence=0.91, is_civic_issue=True)
    result = merge_gemma_yolo(gemma, None, threshold=0.40, confidence_boost=0.15)
    assert result.category == IssueCategory.pothole
