"""
This module defines a specialized tool for analyzing unstructured data
using an external InsightAgent service.
"""

from typing import Annotated

import requests
from langchain_core.tools import tool, InjectedToolArg

from core.config import settings
from agent.state import AgentState


@tool
def insight_agent(task: str, state: Annotated[AgentState, InjectedToolArg]):
    """
    A specialized tool for analyzing unstructured data.

    This tool is used exclusively to answer questions related to unstructured data.
    It should only be invoked when the user’s query involves unstructured data.

    Args:
        task (str): The specific operation to perform. The task must be limited to:
            - Retrieving data from unstructured files (e.g., text, PDFs, images).
            - Querying information contained within these files (e.g., extracting coordinates, metadata, or textual details).

            The task must not involve:
            - Querying or analyzing information unrelated to the file’s content (e.g., gas production or other external topics).
    """
    try:
        # Send the user's question to the external InsightAgent service
        response = requests.post(
            url=settings.external_services.InsightAgent,
            json={
                "user_input": state["question"],
                "chat_history": [],
                "username": "string",
                "session_id": "string",
                "testing": "true",
                "kb_slug": "test",
                "response_style": "string",
            },
        ).json()

        # Extract the answer from the service response
        result = response["answer"]
        return result

    except Exception as e:
        return "Failed"
