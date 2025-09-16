"""..."""

from langchain_core.tools import tool

from agents.workflow.builder import workflow
from agents.state import AgentState


@tool
def action_engine(state: AgentState):
    """Tool used to gain knowledge based on instruction"""
    return workflow.invoke(state)
