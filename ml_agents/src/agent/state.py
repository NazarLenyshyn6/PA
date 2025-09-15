"""..."""

from typing import TypedDict, Annotated, List

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """..."""

    question: str
    tools: str
    agent_scratchpad: Annotated[List[AnyMessage], add_messages]
