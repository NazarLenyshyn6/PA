"""
Agent state data structure.

Defines the inputs and context for the AI agent, including:
- User question
- File references
- Structured and unstructured data
- Tools available to the agent
- Scratchpad for ongoing conversation messages
"""

from typing import TypedDict, Annotated, List, Dict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """TypedDict representing the current state of an AI agent session.

    Attributes:
        question (str): The user’s question for the agent.
        file_names (List[str]): Names of the files available for reference.
        structured_data_info (str): Summaries/descriptions of structured data files.
        unstructured_data_info (str): Summaries/descriptions of unstructured data.
        storage_uris (List[str]): URIs to access the stored files.
        tools (str): Serialized description of available tools for the agent.
        agent_scratchpad (Annotated[List[AnyMessage], add_messages]): Scratchpad messages for the agent,
            annotated to automatically register messages in the LangGraph framework.
    """

    question: str
    file_names: List[str]
    structured_data_info: str
    unstructured_data_info: str
    storage_uris: List[str]
    tools: str
    agent_scratchpad: Annotated[List[AnyMessage], add_messages]
