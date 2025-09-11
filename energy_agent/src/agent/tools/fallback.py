"""..."""

from typing import Annotated
import json

import requests
from langchain_core.tools import tool, InjectedToolArg
from agent.state import AgentState


@tool
def fallback(state: Annotated[AgentState, InjectedToolArg]):
    """..."""
    ...
