"""
Configuration module.

Defines application settings using Pydantic BaseSettings, including
environment-based configuration and model-specific settings.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Base configuration with environment file support.

    Loads environment variables from a `.env` file located three levels up
    from this file and ignores extra values.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


class AnthropicModelConfig(BaseConfig):
    """Configuration for Anthropic AI model access."""

    ANTHROPIC_API_KEY: str


class Settings(BaseSettings):
    """
    Application-wide settings container.
    """

    anthropic_model: AnthropicModelConfig = AnthropicModelConfig()


# Global settings instance for use throughout the application
settings = Settings()
