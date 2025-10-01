"""Application configuration using pydantic-settings.

Loads configuration from environment variables following 12-factor principles.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (comma-separated list)
    api_keys: str

    # Logging configuration
    log_level: str = "INFO"

    # Service configuration
    timeout_seconds: int = 30
    max_retries: int = 3
    host: str = "0.0.0.0"
    port: int = 8000

    # Application metadata
    app_version: str = "1.0.0"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
