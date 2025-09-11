"""..."""

from typing import TypedDict, List, Union

from langchain_core.messages import HumanMessage, AIMessage


class AgentState(TypedDict):
    """..."""

    question: str
    user_id: str
    session_id: str
    file_name: str
    storage_uri: str
    messages: List[Union[HumanMessage, AIMessage]]
