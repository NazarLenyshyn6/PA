"""
This module defines and compiles a state graph for an agent using LangGraph.
The agent alternates between model calls and tool execution based on
conditional logic.
"""

from langgraph.graph import START, END, StateGraph


from agent.state import AgentState
from agent.nodes import model_call, tool_execute, should_continue


# Initialize Graph
agent_builder = StateGraph(AgentState)


# Add nodes
agent_builder.add_node("model_call", model_call)
agent_builder.add_node("tool_execute", tool_execute)

# Add edges
agent_builder.add_edge(START, "model_call")
agent_builder.add_conditional_edges(
    "model_call", should_continue, {"Action": "tool_execute", END: END}
)
agent_builder.add_edge("tool_execute", "model_call")


# Compile graph
agent = agent_builder.compile()
