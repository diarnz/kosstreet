from __future__ import annotations

import json
import logging
import re

from kostreet_ai.config import settings
from kostreet_ai.inference.client import OpenRouterClient
from kostreet_ai.inference.prompts import (
    ClassificationContext,
    build_second_pass_user_text,
    build_system_prompt,
    build_user_text,
    second_pass_alternatives,
)
from kostreet_ai.schemas import ClassificationResult, IssueCategory, IssueSeverity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Severity override table — applied after model response
# ---------------------------------------------------------------------------

_SEVERITY_FLOOR: dict[IssueCategory, IssueSeverity] = {
    IssueCategory.broken_streetlight: IssueSeverity.high,
    IssueCategory.pothole: IssueSeverity.medium,
    IssueCategory.garbage: IssueSeverity.medium,
}

_WEAK_CATEGORIES: frozenset[IssueCategory] = frozenset(
    {
        IssueCategory.garbage,
        IssueCategory.blocked_sidewalk,
        IssueCategory.damaged_sign,
        IssueCategory.other,
    }
)

_SECOND_PASS_CONFIDENCE_CUTOFF = 0.70
_WEAK_CATEGORY_CONFIDENCE_CUTOFF = 0.85

_POTHOLE_MISMATCH_KEYWORDS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsidewalk\b"),
    re.compile(r"\bpedestrian\b"),
    re.compile(r"\bwalkway\b"),
    re.compile(r"\bwalking path\b"),
    re.compile(r"\bgarbage\b"),
    re.compile(r"\blitter\b"),
    re.compile(r"\bwaste\b"),
    re.compile(r"\btrash\b"),
    re.compile(r"\bdumping\b"),
    re.compile(r"\bsign\b"),
    re.compile(r"\bsignage\b"),
)

_FALLBACK = ClassificationResult(
    category=IssueCategory.other,
    confidence=0.0,
    severity=IssueSeverity.low,
    description="Classification failed. Please review this image manually.",
    is_civic_issue=False,
)


def _apply_severity_floor(
    category: IssueCategory,
    severity: IssueSeverity,
) -> IssueSeverity:
    """Enforce minimum severity per category."""
    floor = _SEVERITY_FLOOR.get(category)
    if floor is None:
        return severity
    order = [IssueSeverity.low, IssueSeverity.medium, IssueSeverity.high]
    return floor if order.index(floor) > order.index(severity) else severity


def _coerce_category(raw: str) -> IssueCategory:
    try:
        return IssueCategory(raw)
    except ValueError:
        return IssueCategory.other


def _coerce_severity(raw: str) -> IssueSeverity:
    try:
        return IssueSeverity(raw)
    except ValueError:
        return IssueSeverity.low


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _parse_classification_payload(data: dict) -> ClassificationResult:
    category = _coerce_category(str(data.get("category", "other")))
    raw_severity = _coerce_severity(str(data.get("severity", "low")))
    severity = _apply_severity_floor(category, raw_severity)
    confidence = _clamp(float(data.get("confidence", 0.0)))
    description = str(data.get("description", "")).strip() or _FALLBACK.description
    is_civic_issue = bool(data.get("is_civic_issue", False))
    return ClassificationResult(
        category=category,
        confidence=confidence,
        severity=severity,
        description=description,
        is_civic_issue=is_civic_issue,
    )


def _apply_category_threshold(result: ClassificationResult) -> ClassificationResult:
    """Drop civic flag when confidence is below the category-specific minimum."""
    if not result.is_civic_issue:
        return result
    threshold = settings.get_category_threshold(result.category)
    if result.confidence < threshold:
        return result.model_copy(update={"is_civic_issue": False})
    return result


def _description_suggests_pothole_mismatch(description: str) -> bool:
    lowered = description.lower()
    return any(pattern.search(lowered) for pattern in _POTHOLE_MISMATCH_KEYWORDS)


def _needs_second_pass(result: ClassificationResult) -> bool:
    if result.confidence < _SECOND_PASS_CONFIDENCE_CUTOFF:
        return True
    if result.category in _WEAK_CATEGORIES and result.confidence < _WEAK_CATEGORY_CONFIDENCE_CUTOFF:
        return True
    if result.category == IssueCategory.pothole and _description_suggests_pothole_mismatch(
        result.description
    ):
        return True
    return False


def _should_prefer_second_pass(
    first: ClassificationResult,
    second: ClassificationResult,
) -> bool:
    if second.category != first.category and second.confidence >= settings.get_category_threshold(
        second.category
    ):
        return True
    return second.confidence > first.confidence


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class ImageClassifier:
    def __init__(
        self,
        client: OpenRouterClient,
        model_name: str,
        confidence_threshold: float,
    ) -> None:
        self.client = client
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold

    def classify(
        self,
        image_base64: str,
        *,
        context: ClassificationContext = ClassificationContext.citizen_upload,
    ) -> ClassificationResult:
        """
        Send the image to the vision model via OpenRouter and return a ClassificationResult.
        Never raises — any failure path returns _FALLBACK.
        """
        try:
            first_pass = self._run_pass(image_base64, context=context)
            if _needs_second_pass(first_pass):
                second_pass = self._run_second_pass(image_base64, context=context, first=first_pass)
                if _should_prefer_second_pass(first_pass, second_pass):
                    return _apply_category_threshold(second_pass)
            return _apply_category_threshold(first_pass)
        except Exception as exc:
            logger.warning("Classification failed: %s", exc)
            return _FALLBACK

    def _run_pass(
        self,
        image_base64: str,
        *,
        context: ClassificationContext,
        user_text: str | None = None,
    ) -> ClassificationResult:
        messages = self._build_messages(
            image_base64,
            context=context,
            user_text=user_text or build_user_text(context),
        )
        raw = self.client.chat(messages, response_format={"type": "json_object"})
        data = json.loads(raw)
        return _parse_classification_payload(data)

    def _run_second_pass(
        self,
        image_base64: str,
        *,
        context: ClassificationContext,
        first: ClassificationResult,
    ) -> ClassificationResult:
        alternatives = second_pass_alternatives(first.category)
        user_text = build_second_pass_user_text(first.category, first.confidence, alternatives)
        try:
            return self._run_pass(image_base64, context=context, user_text=user_text)
        except Exception as exc:
            logger.warning("Second-pass classification failed: %s", exc)
            return first

    def _build_messages(
        self,
        image_base64: str,
        *,
        context: ClassificationContext,
        user_text: str,
    ) -> list[dict]:
        return [
            {"role": "system", "content": build_system_prompt(context)},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ]


def get_classifier() -> ImageClassifier:
    """Factory — Gemma classifier, optionally wrapped with hybrid YOLO garbage detection."""
    client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.model_name,
    )
    gemma = ImageClassifier(
        client=client,
        model_name=settings.model_name,
        confidence_threshold=settings.confidence_threshold,
    )

    if not settings.hybrid_enabled:
        return gemma

    from kostreet_ai.inference.hybrid import HybridImageClassifier
    from kostreet_ai.inference.yolo_detector import try_create_detector

    detector = try_create_detector(
        settings.resolve_yolo_model_path(),
        settings.yolo_garbage_threshold,
    )
    if detector is None:
        logger.warning(
            "Hybrid mode enabled but YOLO model missing at %s — using Gemma only",
            settings.resolve_yolo_model_path(),
        )
        return gemma

    return HybridImageClassifier(gemma=gemma, detector=detector)
