from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_prefix="KOSTREET_AI_",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "google/gemma-4-26b-a4b-it"
    confidence_threshold: float = 0.55
    duplicate_radius_meters: float = 20.0
    max_image_size_px: int = 1024
    service_port: int = 8001
    offline_mode: bool = False


@lru_cache
def get_settings() -> AISettings:
    return AISettings()


settings = get_settings()
