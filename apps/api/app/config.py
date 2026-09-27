from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://nano_r1:nano_r1@localhost:5432/nano_r1"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    inference_service_url: str = "http://localhost:8001"
    inference_api_key: str = "change-me"

    cors_origins: list[str] = ["http://localhost:3000"]

    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
