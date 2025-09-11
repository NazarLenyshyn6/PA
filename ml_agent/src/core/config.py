""" """

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    ...
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


class AnthropicModelConfig(BaseConfig):
    """
    ...
    """

    ANTHROPIC_API_KEY: str | None = None
    USE_AWS_BEDROCK: bool = False


class Settings(BaseSettings):
    """
    ....
    """

    anthropic_model: AnthropicModelConfig = AnthropicModelConfig()


# Global settings instance for use throughout the application
settings = Settings()
