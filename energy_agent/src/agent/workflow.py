"""..."""

from langgraph.graph import START, END, StateGraph


from agent.state import AgentState
from agent.nodes import tool_request, tool_execute


# Initialize Graph
workflow_builder = StateGraph(AgentState)

# Add nodes
workflow_builder.add_node("tool_request", tool_request)
workflow_builder.add_node("tool_execute", tool_execute)

# Add edges
workflow_builder.add_edge(START, "tool_request")
workflow_builder.add_edge("tool_request", "tool_execute")
workflow_builder.add_edge("tool_execute", END)

# Compile
workflow = workflow_builder.compile()
