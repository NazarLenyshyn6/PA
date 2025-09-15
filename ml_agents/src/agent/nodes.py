"""..."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langgraph.graph import END

from agent.state import AgentState


def model_call(state: AgentState):
    return state


def tool_execute(state: AgentState):
    return state


def should_continue(state: AgentState):
    ai_message = state["agent_scratchpad"][-1]
    if ai_message.tool_calls:
        return "Action"
    return END
