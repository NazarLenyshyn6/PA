"""..."""

from typing import Annotated
import json

import requests
from langchain_core.tools import tool, InjectedToolArg

from core.config import settings
from agent.state import AgentState


@tool
def insight_agent(state: Annotated[AgentState, InjectedToolArg]):
    """
    A specialized tool for analyzing unstructured data.

    This tool is used exclusively to answer questions related to unstructured data.
    It should only be invoked when the user’s query involves unstructured data.
    """
    try:
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
        result = response["answer"]
        print(result)
        return f"data: {json.dumps({'type': 'text', 'data': result})}\n\n"
    except Exception:
        return f"data: {json.dumps({'type': 'text', 'data': "Failed"})}\n\n"
