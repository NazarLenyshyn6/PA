"""
Anthropic model factory module.

This module provides a factory function to create preconfigured
Anthropic `ChatAnthropic` models with sensible defaults.
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic

from core.config import settings
from agent.schemas import GeneratedCode


def init_anthropic_chat_model(
    *,
    model_name: str = "claude-sonnet-4-20250514",
    temperature: float,
    max_tokens: int = 8000,
    streaming: Optional[bool] = False,
    stream_usage: Optional[bool] = False,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
) -> ChatAnthropic:
    """Initializes an Anthropic Chat model with specified parameters.

    Args:
        model_name: Name of the Anthropic model.
        temperature: Sampling temperature controlling randomness.
        max_tokens: Maximum number of tokens for responses.
        streaming: Enable streaming responses if True.
        stream_usage: Track usage during streaming if True.
        top_k: Optional top-k sampling parameter.
        top_p: Optional top-p (nucleus) sampling parameter.

    Returns:
        An instance of `ChatAnthropic` configured with the provided settings.
    """
    return ChatAnthropic(
        model_name=model_name,
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
    temperature=0.0,
)

mid_temp_model = init_anthropic_chat_model(
    temperature=0.1,
)

# Code generation model
code_generation_model = init_anthropic_chat_model(
    temperature=0.0,
).with_structured_output(GeneratedCode)
