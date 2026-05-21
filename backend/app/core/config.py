from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="KOSTREET_",
        extra="ignore",
    )

    env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins_raw: str = Field(default="http://localhost:5173", alias="KOSTREET_CORS_ORIGINS")
    database_url: str = "sqlite:///./kostreet.db"
    upload_dir: str = "backend/uploads"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

