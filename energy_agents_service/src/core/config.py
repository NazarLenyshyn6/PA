"""
Configuration module for managing application settings.

This module centralizes configuration for the application, including database
(Postgres), caching (Redis), and third-party integration (Anthropic model API)
settings. It leverages `pydantic_settings.BaseSettings` for type-safe
environment variable parsing and validation.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Base configuration class that loads environment variables from a `.env` file.

    This class provides a reusable configuration foundation by extending
    Pydantic's `BaseSettings`. It enforces type safety, environment-based
    overrides, and ignores any extra undefined environment variables.

    Attributes:
        model_config: Configuration specifying the path to
            the `.env` file and behavior for handling extra variables.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


class PostgresConfig(BaseConfig):
    """
    Configuration class for PostgreSQL database settings.

    Attributes:
        DB_HOST: Hostname or IP address of the PostgreSQL server.
        DB_PORT: Port number for connecting to PostgreSQL.
        DB_USER: Username for database authentication.
        DB_PASS: Password for database authentication.
        DB_NAME: Name of the target PostgreSQL database.
    """

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def URL(self) -> str:
        """
        Construct the full PostgreSQL connection URL.

        Returns:
            str: A formatted PostgreSQL connection string in the form:
                 `postgresql://<user>:<password>@<host>:<port>/<database>`.
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisConfig(BaseConfig):
    """
    Configuration class for Redis server settings.

    Attributes:
        HOST: Hostname or IP address of the Redis server.
        PORT: Port number for connecting to Redis.
        DB: Redis database index to use (default is 0).
    """

    HOST: str
    PORT: int
    DB: int


class AnthropicModelConfig(BaseConfig):
    """
    Configuration class for Anthropic model API integration.

    Attributes:
        ANTHROPIC_API_KEY: API key for authenticating requests
            to Anthropic's services.
    """

    ANTHROPIC_API_KEY: str


class Settings(BaseSettings):
    """
    Aggregated application settings class.

    This class bundles together all individual configurations
    (Postgres, Redis, and Anthropic) into a single entry point for
    accessing environment-driven application settings.

    Attributes:
        postgres: Database-related configuration.
        redis: Redis-related configuration.
        anthropic_model: Anthropic model API configuration.
    """

    anthropic_model: AnthropicModelConfig = AnthropicModelConfig()
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()


# Global settings instance for use throughout the application
settings = Settings()
