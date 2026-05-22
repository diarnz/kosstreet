import base64
import json
from io import BytesIO
from typing import Any

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings
from app.integrations.openrouter import OpenRouterClient
from app.schemas.report import ImageAnalysisResult

CIVIC_ISSUE_PROMPT = """
You are analyzing a street-level image for a municipal issue detection system
in Prishtina, Kosovo.

Identify whether the image contains a civic street issue that needs municipal attention.
Respond ONLY with a single valid JSON object - no explanation, no markdown:

{
  "is_civic_issue": true or false,
  "category": one of "pothole" | "garbage" | "broken_streetlight" | "blocked_sidewalk" | "damaged_sign" | "other" | null,
  "confidence": a float between 0.0 and 1.0,
  "severity": one of "low" | "medium" | "high" | "critical" | null,
  "description": a single sentence describing exactly what you see | null
}

Rules:
- Set is_civic_issue to false for clean streets, normal traffic, buildings, or people with no issue.
- confidence reflects how certain you are that the detected issue is genuinely present.
- severity reflects urgency and impact on citizens using the street.
- description must be specific: name what you see, not just the category label.
- If category is null, set is_civic_issue to false.
"""


class AIService:
    def __init__(self, settings: Settings) -> None:
        self.openrouter = OpenRouterClient(api_key=settings.ai_openrouter_api_key)
        self.model_name = settings.ai_model_name
        self.max_image_size_px = settings.ai_max_image_size_px

    async def analyze_image_bytes(self, image_bytes: bytes) -> ImageAnalysisResult:
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
            return ImageAnalysisResult(is_civic_issue=False)

        try:
            return ImageAnalysisResult(**payload)
        except ValueError:
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
