"""..."""

from typing import TypedDict

from langchain_core.messages import AIMessage


class AgentState(TypedDict):
    """..."""

    question: str
    tool_call_message: AIMessage
