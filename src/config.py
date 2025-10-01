"""Application configuration using pydantic-settings.

Loads configuration from environment variables following 12-factor principles.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (comma-separated list)
    api_keys: str = "default_api_key"

    # Logging configuration
    log_level: str = "INFO"

    # Service configuration
    timeout_seconds: int = 30
    max_retries: int = 3
    host: str = "0.0.0.0"
    port: int = 8000

    # Proxy configuration
    proxy_username: str = ""
    proxy_password: str = ""

    # Application metadata
    app_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Global settings instance
settings = Settings()
