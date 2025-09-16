"""..."""

from typing import TypedDict, Annotated, List, Dict, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """..."""

    question: str
    variables: Dict[str, any]
    data_summaries: str
    dependencies: List[str]
    tools: str
    agent_scratchpad: Annotated[List[AnyMessage], add_messages]
    current_debugging_attempt: int
    max_debugging_attempts: int
    visualization: Optional[str]
