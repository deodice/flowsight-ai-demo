from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./flowsight.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-change-me-please-32-chars"
    app_url: str = "http://localhost:3000"
    s3_endpoint: str | None = None
    s3_bucket: str = "flowsight"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    llm_provider: str = "deterministic"
    access_token_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
