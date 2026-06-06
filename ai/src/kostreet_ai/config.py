from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from kostreet_ai.schemas import IssueCategory

_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
_AI_ROOT = Path(__file__).resolve().parents[2]

_DEFAULT_CATEGORY_THRESHOLDS: dict[IssueCategory, float] = {
    IssueCategory.pothole: 0.55,
    IssueCategory.garbage: 0.50,
    IssueCategory.blocked_sidewalk: 0.55,
    IssueCategory.damaged_sign: 0.55,
    IssueCategory.broken_streetlight: 0.55,
    IssueCategory.other: 0.45,
}


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_prefix="KOSTREET_AI_",
        extra="ignore",
        populate_by_name=True,
    )

    google_maps_api_key: str = Field(default="", validation_alias="GOOGLE_MAPS_API_KEY")
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "google/gemma-4-26b-a4b-it"
    confidence_threshold: float = 0.55
    duplicate_radius_meters: float = 20.0
    max_image_size_px: int = 1024
    service_port: int = 8001
    offline_mode: bool = False
    hybrid_enabled: bool = False
    yolo_model_path: str = "models/garbage_yolov8n.pt"
    yolo_garbage_threshold: float = 0.40
    yolo_confidence_boost: float = 0.15

    def resolve_yolo_model_path(self) -> Path:
        """Resolve YOLO weights relative to the ai/ package root."""
        path = Path(self.yolo_model_path)
        if path.is_absolute():
            return path
        return _AI_ROOT / path

    def get_category_threshold(self, category: IssueCategory) -> float:
        """Minimum confidence required to treat a detection as a civic issue."""
        return _DEFAULT_CATEGORY_THRESHOLDS.get(category, self.confidence_threshold)


@lru_cache
def get_settings() -> AISettings:
    return AISettings()


settings = get_settings()
