"""
Agent model interaction and tool execution.

Provides functions to:
- Invoke the AI model with structured/unstructured data context.
- Execute tools called by the AI.
- Decide whether the agent should continue or stop based on scratchpad state.
"""

from langchain_core.messages import ToolMessage
from langgraph.graph import END

from agent.state import AgentState
from agent.tools.registry import tools_mapping
from agent.chains import agent_chain


def model_call(state: AgentState):
    """Invoke the AI model using the current agent state.

    Combines structured data, unstructured data, available tools,
    and the agent scratchpad to generate the next AI response.

    Args:
        state (AgentState): Current agent state containing question,
            file info, tools, and scratchpad.

    Returns:
        dict: Updated agent scratchpad with the AI model response.
    """
    response = agent_chain.invoke(
        {
            "question": state["question"],
            "structured_data_info": state["structured_data_info"],
            "unstructured_data_info": state["unstructured_data_info"],
            "tools": state["tools"],
            "agent_scratchpad": state["agent_scratchpad"],
        }
    )
    return {"agent_scratchpad": [response]}


async def tool_execute(state: AgentState):
    """Execute the tool specified in the latest AI message.

    Retrieves the tool from the registry, merges its arguments
    with the current agent state, and asynchronously invokes it.

    Args:
        state (AgentState): Current agent state containing the scratchpad.

    Returns:
        dict: Updated agent scratchpad containing the tool's output.
    """
    tool_call = state["agent_scratchpad"][-1].tool_calls[0]
    tool = tools_mapping[tool_call["name"]]

    # Copy and update arguments to include the current state
    args = tool_call["args"].copy()
    args.update({"state": state})

    result = await tool.ainvoke(args)
    return {
        "agent_scratchpad": [ToolMessage(content=result, tool_call_id=tool_call["id"])]
    }


def should_continue(state: AgentState):
    """Decide whether the agent should continue or stop.

    Checks the latest AI message for pending tool calls.

    Args:
        state (AgentState): Current agent state.

    Returns:
        str or END: "Action" if a tool call exists, otherwise END.
    """
    ai_message = state["agent_scratchpad"][-1]
    if ai_message.tool_calls:
        return "Action"
    return END
