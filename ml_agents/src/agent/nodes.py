"""
Agent model interaction and tool execution.

Provides functions to:
- Invoke the AI model with data context.
- Execute tools called by the AI.
- Decide whether the agent should continue or stop based on scratchpad state.
"""

from langchain_core.messages import ToolMessage
from langgraph.graph import END

from agent.state import AgentState
from agent.tools.registry import tools_mapping
from agent.chains.agent import agent_chain


def model_call(state: AgentState):
    """Invoke the agent model with the current state.

    Args:
        state (AgentState): Current agent state containing question, data, and scratchpad.

    Returns:
        dict: Updated agent_scratchpad with the model's response.
    """
    response = agent_chain.invoke(
        {
            "question": state["question"],
            "data_summaries": state["data_summaries"],
            "tools": state["tools"],
            "agent_scratchpad": state["agent_scratchpad"],
        }
    )
    return {"agent_scratchpad": [response]}


def tool_execute(state: AgentState):
    """Execute the tool specified in the last agent message.

    Args:
        state (AgentState): Current agent state containing tool call information.

    Returns:
        dict: Contains updated agent_scratchpad with tool output and optional visualization.
    """
    tool_call = state["agent_scratchpad"][-1].tool_calls[0]
    tool = tools_mapping[tool_call["name"]]

    # Copy and update arguments to include the current state
    args = tool_call["args"].copy()
    args.update({"state": state})

    analysis_report, image, interactive_image = tool.invoke(args)
    return {
        "agent_scratchpad": [
            ToolMessage(content=analysis_report, tool_call_id=tool_call["id"])
        ],
        "visualization": image,
        "interactive_visualization": interactive_image,
    }


def should_continue(state: AgentState):
    """Determine if the agent should continue or terminate.

    Args:
        state (AgentState): Current agent state.

    Returns:
        str: "Action" if further tool execution is needed, otherwise END.
    """
    ai_message = state["agent_scratchpad"][-1]
    if ai_message.tool_calls:
        return "Action"
    return END
