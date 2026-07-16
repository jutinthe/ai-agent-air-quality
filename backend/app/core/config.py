from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Air Quality–Health Research Agent"
    app_environment: str = "development"

    storage_directory: Path = Path("storage")
    upload_directory: Path = Path("storage/uploads")
    processed_directory: Path = Path("storage/processed")

    maximum_pdf_size_mb: int = Field(default=50, ge=1, le=500)

    openai_api_key: str | None = None
    openai_extraction_model: str = "gpt-5-mini"
    openai_timeout_seconds: float = 180.0
    extraction_maximum_attempts: int = 3
    extraction_maximum_characters: int = 120_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def maximum_pdf_size_bytes(self) -> int:
        return self.maximum_pdf_size_mb * 1024 * 1024

    def create_storage_directories(self) -> None:
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.processed_directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.create_storage_directories()
    return settings
