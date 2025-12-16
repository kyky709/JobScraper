"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    app_name: str = "JobScraper API"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS
    cors_origins: List[str] = ["*"]

    # Scraping Settings
    scraper_delay: float = 1.0
    max_retries: int = 3
    request_timeout: float = 30.0

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
