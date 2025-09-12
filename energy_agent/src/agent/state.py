"""..."""

from typing import TypedDict

from langchain_core.messages import AIMessage


class AgentState(TypedDict):
    """..."""

    question: str
    storage_uri: str
    tool_call_message: AIMessage
