import base64
import json
import logging
from io import BytesIO
from typing import Any

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings
from app.integrations.openrouter import OpenRouterClient
from app.models.enums import AuditSuggestionSeverity, IssueCategory
from app.schemas.report import ImageAnalysisResult
from app.utils.detection_regions import sanitize_detection_regions

logger = logging.getLogger(__name__)

CIVIC_ISSUE_PROMPT = """
You are analyzing a street-level image for a municipal issue detection system
in Kosovo.

Identify whether the image contains a civic street issue that needs municipal attention.
Respond ONLY with a single valid JSON object - no explanation, no markdown:

{
  "is_civic_issue": true or false,
  "category": one of "pothole" | "garbage" | "broken_streetlight" | "blocked_sidewalk" | "damaged_sign" | "other" | null,
  "confidence": a float between 0.0 and 1.0,
  "severity": one of "low" | "medium" | "high" | "critical" | null,
  "description": a single sentence describing exactly what you see | null,
  "regions": [
    {
      "center_x": a float between 0.0 and 1.0 for the issue center on the image width,
      "center_y": a float between 0.0 and 1.0 for the issue center on the image height,
      "radius": an optional float between 0.04 and 0.18 for circle size relative to image size
    }
  ]
}

Rules:
- Set is_civic_issue to false for clean streets, normal traffic, buildings, or people with no issue.
- confidence reflects how certain you are that the detected issue is genuinely present.
- severity reflects urgency and impact on citizens using the street.
- description must be specific: name what you see, not just the category label.
- If category is null, set is_civic_issue to false.
- When is_civic_issue is true, include one primary region in regions[] pointing to where the issue appears.
- If you cannot estimate location, return an empty regions array.
"""


class AIService:
    def __init__(self, settings: Settings) -> None:
        self.openrouter = OpenRouterClient(api_key=settings.ai_openrouter_api_key)
        self.model_name = settings.ai_model_name
        self.max_image_size_px = settings.ai_max_image_size_px

    async def analyze_image_bytes(self, image_bytes: bytes) -> ImageAnalysisResult:
        try:
            image_bytes = self._resize_image(image_bytes)
        except ValueError:
            logger.warning("Skipping AI analysis for unsupported street imagery bytes")
            return ImageAnalysisResult(is_civic_issue=False)

        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                    {"type": "text", "text": CIVIC_ISSUE_PROMPT},
                ],
            }
        ]

        content = await self.openrouter.chat_completion(
            model=self.model_name,
            messages=messages,
        )
        payload = self._parse_json_payload(content)

        if payload is None:
            logger.warning("AI response was not valid JSON: %s", content[:240])
            return ImageAnalysisResult(is_civic_issue=False)

        payload = self._normalize_payload(payload)
        severity = payload.get("severity")
        raw_regions = payload.get("regions")
        sanitized_regions = sanitize_detection_regions(
            raw_regions if isinstance(raw_regions, list) else None,
            severity if isinstance(severity, str) else None,
        )
        payload["regions"] = sanitized_regions

        try:
            return ImageAnalysisResult(**payload)
        except ValueError:
            logger.warning("AI payload failed validation: %s", payload)
            return ImageAnalysisResult(is_civic_issue=False)

    async def analyze_upload(self, file: UploadFile) -> ImageAnalysisResult:
        image_bytes = await file.read()
        resized = self._resize_image(image_bytes)
        return await self.analyze_image_bytes(resized)

    def _resize_image(self, image_bytes: bytes) -> bytes:
        try:
            image = Image.open(BytesIO(image_bytes))
        except UnidentifiedImageError as exc:
            raise ValueError("Unsupported image format") from exc

        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail(
            (self.max_image_size_px, self.max_image_size_px),
            Image.Resampling.LANCZOS,
        )

        output = BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    def _parse_json_payload(self, content: str) -> dict[str, Any] | None:
        stripped = content.strip()

        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return None

        return parsed if isinstance(parsed, dict) else None

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)

        if "is_civic_issue" in normalized:
            normalized["is_civic_issue"] = bool(normalized["is_civic_issue"])

        confidence = normalized.get("confidence")
        if confidence is not None:
            try:
                normalized["confidence"] = float(confidence)
            except (TypeError, ValueError):
                normalized["confidence"] = None

        category = normalized.get("category")
        if isinstance(category, str):
            cleaned = category.strip().lower().replace("-", "_").replace(" ", "_")
            valid_categories = {item.value for item in IssueCategory}
            normalized["category"] = cleaned if cleaned in valid_categories else None

        severity = normalized.get("severity")
        if isinstance(severity, str):
            cleaned = severity.strip().lower()
            valid_severities = {item.value for item in AuditSuggestionSeverity}
            normalized["severity"] = cleaned if cleaned in valid_severities else None

        description = normalized.get("description")
        if isinstance(description, str):
            lowered = description.strip().lower()
            if lowered.startswith("no imagery") or "lack of available imagery" in lowered:
                normalized["is_civic_issue"] = False
                normalized["category"] = None

        return normalized
