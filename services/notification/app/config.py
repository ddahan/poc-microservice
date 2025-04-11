from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parents[3]

    RABBITMQ_URL: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_ignore_empty=True,
        case_sensitive=True,
        extra="allow",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
