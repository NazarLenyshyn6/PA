"""
...
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic

from core.config import settings
from agent.tools.registry import tools


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
    """
    Factory for Anthropic chat models with sensible defaults.
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

model_with_tools = low_temp_model.bind_tools(tools, tool_choice="any")
