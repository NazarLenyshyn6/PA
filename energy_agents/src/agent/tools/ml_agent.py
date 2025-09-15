"""..."""

from typing import Annotated
import json

import requests
from langchain_core.tools import tool, InjectedToolArg

from core.config import settings
from agent.state import AgentState
