"""..."""

from typing import TypedDict, Annotated, List, Dict

import pandas as pd
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """..."""

    question: str
    file_names: List[str]
    structured_data_info: str
    unstructured_data_info: str
    storage_uris: List[str]
    tools: str
    agent_scratchpad: Annotated[List[AnyMessage], add_messages]
