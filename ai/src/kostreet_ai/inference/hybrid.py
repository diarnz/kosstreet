from __future__ import annotations

import logging

from kostreet_ai.config import settings
from kostreet_ai.inference.classifier import ImageClassifier, _apply_category_threshold
from kostreet_ai.inference.prompts import ClassificationContext
from kostreet_ai.inference.yolo_detector import GarbageYoloDetector, GarbageYoloHit
from kostreet_ai.preprocessing.image import decode_base64_to_bytes
from kostreet_ai.schemas import ClassificationResult, IssueCategory, IssueSeverity

logger = logging.getLogger(__name__)

_YOLO_OVERRIDE_CONFIDENCE = 0.72


def merge_gemma_yolo(
    gemma_result: ClassificationResult,
    yolo_hit: GarbageYoloHit | None,
    *,
    threshold: float,
    confidence_boost: float,
) -> ClassificationResult:
    """
    Combine Gemma classification with a local garbage detector.

    Rules (Phase 11 blueprint):
    - YOLO garbage + Gemma not civic or wrong category → override to garbage
    - Gemma garbage + YOLO agrees → boost confidence
    - Otherwise → keep Gemma result unchanged
    """
    if yolo_hit is None or yolo_hit.confidence < threshold:
        return gemma_result

    if not gemma_result.is_civic_issue or gemma_result.category != IssueCategory.garbage:
        override_confidence = max(yolo_hit.confidence, _YOLO_OVERRIDE_CONFIDENCE)
        description = (
            f"Local waste detector flagged litter (YOLO {yolo_hit.confidence:.2f}). "
            f"{gemma_result.description}"
        )
        return ClassificationResult(
            category=IssueCategory.garbage,
            confidence=min(1.0, override_confidence),
            severity=IssueSeverity.medium,
            description=description.strip(),
            is_civic_issue=True,
        )

    if gemma_result.category == IssueCategory.garbage:
        return gemma_result.model_copy(
            update={"confidence": min(1.0, gemma_result.confidence + confidence_boost)}
        )

    return gemma_result


class HybridImageClassifier:
    """Gemma vision classifier augmented with a local garbage YOLO detector."""

    def __init__(
        self,
        gemma: ImageClassifier,
        detector: GarbageYoloDetector,
    ) -> None:
        self.gemma = gemma
        self.detector = detector
        self.model_name = f"{gemma.model_name}+yolo"
        self.confidence_threshold = gemma.confidence_threshold

    def classify(
        self,
        image_base64: str,
        *,
        context: ClassificationContext = ClassificationContext.citizen_upload,
    ) -> ClassificationResult:
        gemma_result = self.gemma.classify(image_base64, context=context)
        try:
            image_bytes = decode_base64_to_bytes(image_base64)
            yolo_hit = self.detector.detect(image_bytes)
        except Exception as exc:
            logger.warning("Hybrid YOLO pass skipped: %s", exc)
            return gemma_result

        merged = merge_gemma_yolo(
            gemma_result,
            yolo_hit,
            threshold=settings.yolo_garbage_threshold,
            confidence_boost=settings.yolo_confidence_boost,
        )
        return _apply_category_threshold(merged)
