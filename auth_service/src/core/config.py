"""
Configuration module for managing application settings.

This module centralizes configuration for the application, including database
(Postgres) and security (JWT authentication) settings. It leverages
`pydantic_settings.BaseSettings` for type-safe environment variable parsing
and validation.
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


class PostgresConfig(BaseConfig):
    """
    Configuration class for PostgreSQL database settings.

    Attributes:
        DB_HOST (str): Hostname or IP address of the PostgreSQL server.
        DB_PORT (str): Port number for connecting to PostgreSQL.
        DB_USER (str): Username for database authentication.
        DB_PASS (str): Password for database authentication.
        DB_NAME (str): Name of the target PostgreSQL database.
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
    Aggregated application settings class.

    This class bundles together the Postgres and Security configurations
    into a single entry point for accessing all environment-driven
    application settings.

    Attributes:
        postgres (PostgresConfig): Database-related configuration.
        security (SecurityConfig): Security-related configuration.
    """

    postgres: PostgresConfig = PostgresConfig()
    security: SecurityConfig = SecurityConfig()


# Global settings instance for use throughout the application
settings = Settings()
