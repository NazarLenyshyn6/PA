"""
Application configuration module.

This module defines configuration classes for the application, leveraging Pydantic
BaseSettings to load environment variables. It provides structured access to
database, security, and Redis configuration values, with additional computed
properties for convenience.

Classes:
    - BaseConfig: Base class for all configurations, loading environment variables.
    - SecurityConfig: Configuration for JWT-based authentication and security.
    - Settings: Aggregated settings container for all configuration categories.
"""

from pathlib import Path
from datetime import timedelta

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


class SecurityConfig(BaseConfig):
    """
    Configuration class for application security and JWT authentication.

    Attributes:
        SECRET_KEY (str): Secret key used for signing JWT tokens.
        ALGORITHM (str): Cryptographic algorithm used for JWT token encoding.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Expiration time of access tokens in minutes.
    """

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA(self) -> timedelta:
        """
        Convert the access token expiration time into a `timedelta` object.

        Returns:
            timedelta: The expiration time as a timedelta for direct use in JWT utilities.
        """
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)


class Settings(BaseSettings):
    """
    Aggregated settings container.

    This class combines PostgresConfig, SecurityConfig, and RedisConfig
    to provide a single entry point for application configuration.

    Attributes:
        postgres (PostgresConfig): PostgreSQL configuration instance.
        security (SecurityConfig): Security and JWT configuration instance.
        redis (RedisConfig): Redis configuration instance.
    """

    security: SecurityConfig = SecurityConfig()


settings = Settings()
