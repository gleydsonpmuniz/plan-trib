from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(...)
    db_user: str = Field(...)
    db_password: str = Field(...)

    jwt_secret: str = Field(...)
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 7

    gemini_api_key: str = Field(default="")
    gemini_model: str = "gemini-2.5-flash"
    openrouter_api_key: str = Field(default="")
    openrouter_model: str = "google/gemini-2.5-flash"

    uploads_dir: Path = Path("/uploads")
    kb_dir: Path = Path("/app/kb")

    app_domain: str = "plantrib.safion.com.br"
    max_upload_size_mb: int = 50
    log_level: str = "INFO"
    tz: str = "America/Sao_Paulo"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
