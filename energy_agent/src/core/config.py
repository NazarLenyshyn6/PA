"""
Application configuration using Pydantic BaseSettings.

Defines structured configuration for PostgreSQL, Redis, local storage,
security, external services, and AI models. Supports environment-based
overrides from a `.env` file.
"""

from pathlib import Path
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration class for environment-based settings."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


class PostgresConfig(BaseConfig):
    """PostgreSQL database configuration."""

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def URL(self) -> str:
        """Generate the SQLAlchemy-compatible connection URL.

        Returns:
            str: PostgreSQL connection URL.
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisConfig(BaseConfig):
    """Redis cache configuration."""

    HOST: str
    PORT: int
    DB: int


class LocalStorageConfig(BaseConfig):
    """Local file storage configuration."""

    LOCAL_STORAGE_PATH: str


class SecurityConfig(BaseConfig):
    """Security and authentication configuration."""

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA(self) -> timedelta:
        """Access token expiration as a timedelta object.

        Returns:
            timedelta: Token expiration duration.
        """
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)


class AnthropicModelConfig(BaseConfig):
    """Configuration for Anthropic AI model access."""

    ANTHROPIC_API_KEY: str


class ExternalServicesConfig(BaseConfig):
    """Configuration for external service endpoints."""

    MLAgent: str
    InsightAgent: str


class Settings(BaseSettings):
    """Application-wide aggregated settings."""

    postgres: PostgresConfig = PostgresConfig()
    security: SecurityConfig = SecurityConfig()
    redis: RedisConfig = RedisConfig()
    local_storage: LocalStorageConfig = LocalStorageConfig()
    external_services: ExternalServicesConfig = ExternalServicesConfig()
    anthropic_model: AnthropicModelConfig = AnthropicModelConfig()


# Global settings instance for use throughout the application
settings = Settings()
