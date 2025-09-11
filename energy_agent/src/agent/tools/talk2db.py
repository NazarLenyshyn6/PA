"""..."""

from typing import Annotated
import json

import requests
from langchain_core.tools import tool, InjectedToolArg

from core.config import settings
from agent.state import AgentState


@tool
def talk2db_agent(state: Annotated[AgentState, InjectedToolArg]):
    """
    Use this tool when the user asks any question related to data analysis.
    It is responsible for handling requests to analyze, query, or interpret data.
    """
    try:
        response = requests.post(
            url=settings.external_services.Talk2DB, json={"query": state["question"]}
        ).json()
        result = response["data"]["thoughts"]
        return f"data: {json.dumps({'type': 'text', 'data': result})}\n\n"

    except Exception:
        return f"data: {json.dumps({'type': 'text', 'data': "Talk2DB Failed"})}\n\n"
