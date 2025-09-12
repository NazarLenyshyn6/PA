"""..."""

from pathlib import Path
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    ...
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


class PostgresConfig(BaseConfig):
    """
    ...
    """

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def URL(self) -> str:
        """
        ...
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisConfig(BaseConfig):
    """
    ...
    """

    HOST: str
    PORT: int
    DB: int


class LocalStorageConfig(BaseConfig):
    """
    ...
    """

    LOCAL_STORAGE_PATH: str


class SecurityConfig(BaseConfig):
    """
    ...
    """

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA(self) -> timedelta:
        """
        ...
        """
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)


class AnthropicModelConfig(BaseConfig):
    """
    Configuration class for Anthropic model API integration.

    Attributes:
        ANTHROPIC_API_KEY: API key for authenticating requests
            to Anthropic's services.
    """

    ANTHROPIC_API_KEY: str


class ExternalServicesConfig(BaseConfig):
    """Configuration class for external service URLS.

    Attributes:
        Talk2DB: .
    """

    Talk2DB: str
    MLAgent: str


class Settings(BaseSettings):
    """
    ...
    """

    postgres: PostgresConfig = PostgresConfig()
    security: SecurityConfig = SecurityConfig()
    redis: RedisConfig = RedisConfig()
    local_storage: LocalStorageConfig = LocalStorageConfig()
    external_services: ExternalServicesConfig = ExternalServicesConfig()
    anthropic_model: AnthropicModelConfig = AnthropicModelConfig()


# Global settings instance for use throughout the application
settings = Settings()
