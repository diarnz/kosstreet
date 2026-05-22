from __future__ import annotations

import json
import logging

from kostreet_ai.config import settings
from kostreet_ai.inference.client import OpenRouterClient
from kostreet_ai.schemas import ClassificationResult, IssueCategory, IssueSeverity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — exact text sent to Gemma 4 on every request
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a civic infrastructure quality inspector working for Kosovo municipalities.
Your job is to analyze street-level photographs and identify visible civic issues that require municipal attention.

You must respond with ONLY a valid JSON object. No explanation, no markdown, no extra text before or after the JSON.
The JSON must follow this exact structure:

{
  "category": "<value>",
  "confidence": <float>,
  "severity": "<value>",
  "description": "<text>",
  "is_civic_issue": <boolean>
}

Allowed values for category:
- pothole             : road surface crack, depression, hole, or damaged asphalt
- garbage             : bags, litter, scattered waste, illegal dumping, overflowing bins
- broken_streetlight  : damaged light pole, missing fixture, visibly dark lamp
- blocked_sidewalk    : cracked pavement, obstacles, obstructions on walking paths
- damaged_sign        : bent, missing, graffitied, or fallen road or street signs
- other               : any civic issue not covered above

Allowed values for severity:
- high   : immediate safety risk, large damage, major obstruction
- medium : noticeable issue that needs attention within days
- low    : minor cosmetic issue, early-stage problem

confidence must be a float from 0.0 to 1.0 representing how certain you are.

If you do not see any civic issue, respond with:
{
  "category": "other",
  "confidence": 0.0,
  "severity": "low",
  "description": "No civic issue detected in this image.",
  "is_civic_issue": false
}"""

_USER_TEXT = "Analyze this street-level photograph for civic infrastructure issues."

# ---------------------------------------------------------------------------
# Severity override table — applied after model response
# Ensures consistent severity for the demo regardless of model output
# ---------------------------------------------------------------------------

_SEVERITY_FLOOR: dict[IssueCategory, IssueSeverity] = {
    IssueCategory.broken_streetlight: IssueSeverity.high,
    IssueCategory.pothole: IssueSeverity.medium,
    IssueCategory.garbage: IssueSeverity.medium,
}

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

    def classify(self, image_base64: str) -> ClassificationResult:
        """
        Send the image to Gemma 4 via OpenRouter and return a ClassificationResult.
        Never raises — any failure path returns _FALLBACK.
        """
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _USER_TEXT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ]

        try:
            raw = self.client.chat(messages, response_format={"type": "json_object"})
            data = json.loads(raw)

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

        except Exception as exc:
            logger.warning("Classification failed: %s", exc)
            return _FALLBACK


def get_classifier() -> ImageClassifier:
    """Factory — creates a fresh classifier backed by the current settings."""
    client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.model_name,
    )
    return ImageClassifier(
        client=client,
        model_name=settings.model_name,
        confidence_threshold=settings.confidence_threshold,
    )
