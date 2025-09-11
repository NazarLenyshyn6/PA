"""
Anthropic model factory module.

This module provides a factory function to create preconfigured
Anthropic `ChatAnthropic` models with sensible defaults. It also defines
a set of shared and specialized model instances for common use cases
such as routing, reasoning, summarization, and code generation.

Responsibilities:
    - Centralize Anthropic model creation with consistent configuration.
    - Provide reusable low-, medium-, and high-temperature models.
    - Expose special-purpose models optimized for summarization and code generation.
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock

from core.config import settings


def init_anthropic_chat_model(
    *,
    temperature: float,
    max_tokens: int = 8000,
    streaming: Optional[bool] = False,
    stream_usage: Optional[bool] = False,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
):
    """
    Factory for Anthropic chat models with sensible defaults.
    Supports both direct Anthropic API and AWS Bedrock.
    """
    if settings.anthropic_model.USE_AWS_BEDROCK:
        # Use AWS Bedrock (region auto-detected by AWS SDK)
        model_kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Only add top_k and top_p if they have values
        if top_k is not None:
            model_kwargs["top_k"] = top_k
        if top_p is not None:
            model_kwargs["top_p"] = top_p

        return ChatBedrock(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs=model_kwargs,
            streaming=streaming,
        )
    else:
        # Use direct Anthropic API
        if not settings.anthropic_model.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when not using AWS Bedrock")

        return ChatAnthropic(
            model_name="claude-sonnet-4-20250514",
            anthropic_api_key=settings.anthropic_model.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            stream_usage=stream_usage,
            top_k=top_k,
            top_p=top_p,
        )


# --- General-purpose shared models ---
low_temp_model = init_anthropic_chat_model(
    temperature=0.0,  # deterministic / routing / summarization
)

medium_temp_model = init_anthropic_chat_model(
    temperature=0.2,  # balanced reasoning
)

high_temp_model = init_anthropic_chat_model(
    temperature=0.3,  # more creative / explorative
)


# --- Special-purpose overrides ---
code_generation_model = init_anthropic_chat_model(
    temperature=0.0,
    max_tokens=50000,
    streaming=True,
    top_p=1,
)

code_debugging_model = init_anthropic_chat_model(
    temperature=0.25,
    max_tokens=50000,
    streaming=True,
    top_p=1,
)

code_summarization_model = init_anthropic_chat_model(
    temperature=0.0,
    max_tokens=40000,
    top_p=1,
)
