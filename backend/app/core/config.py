import re
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILES = (
    PROJECT_ROOT / ".env",
    Path(__file__).resolve().parents[2] / ".env",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_prefix="KOSTREET_",
        extra="ignore",
    )

    env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:5174",
        alias="KOSTREET_CORS_ORIGINS",
    )

    # PostgreSQL — async driver for the app, sync driver for Alembic
    database_url: str = Field(
        default="postgresql+asyncpg://kostreet:kostreet@localhost:5432/kostreet",
        alias="KOSTREET_DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg2://kostreet:kostreet@localhost:5432/kostreet",
        alias="KOSTREET_DATABASE_URL_SYNC",
    )

    # Storage — local fallback when Supabase Storage is not configured
    upload_dir: str = "backend/uploads"
    max_upload_bytes: int = 10_485_760  # 10 MB
    supabase_url: str = Field(default="", alias="KOSTREET_SUPABASE_URL")
    supabase_service_role_key: str = Field(
        default="",
        alias="KOSTREET_SUPABASE_SERVICE_ROLE_KEY",
    )
    supabase_storage_bucket: str = Field(
        default="report-images",
        alias="KOSTREET_SUPABASE_STORAGE_BUCKET",
    )

    # AI / OpenRouter
    ai_openrouter_api_key: str = Field(default="", alias="KOSTREET_AI_OPENROUTER_API_KEY")
    ai_model_name: str = Field(
        default="google/gemma-4-26b-a4b-it", alias="KOSTREET_AI_MODEL_NAME"
    )
    ai_confidence_threshold: float = Field(
        default=0.55, alias="KOSTREET_AI_CONFIDENCE_THRESHOLD"
    )
    ai_duplicate_radius_meters: float = Field(
        default=20.0, alias="KOSTREET_AI_DUPLICATE_RADIUS_METERS"
    )
    ai_max_image_size_px: int = Field(
        default=1024, alias="KOSTREET_AI_MAX_IMAGE_SIZE_PX"
    )
    audit_on_demand_max_per_run_per_hour: int = Field(
        default=10, alias="KOSTREET_AUDIT_ON_DEMAND_MAX_PER_RUN_PER_HOUR"
    )

    # Google Street View
    google_maps_api_key: str = Field(default="", alias="GOOGLE_MAPS_API_KEY")
    gsv_frame_size: int = 640

    # Hidden admin CRUD (reports visibility) — KOSTREET_ADMIN_SECRET in .env
    admin_secret: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    @property
    def resolved_supabase_url(self) -> str:
        explicit = self.supabase_url.strip()
        if explicit:
            return explicit.rstrip("/")

        match = re.search(r"postgres\.([a-z0-9]+)", self.database_url)
        if match:
            return f"https://{match.group(1)}.supabase.co"
        return ""

    @property
    def supabase_storage_enabled(self) -> bool:
        return bool(self.resolved_supabase_url and self.supabase_service_role_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
