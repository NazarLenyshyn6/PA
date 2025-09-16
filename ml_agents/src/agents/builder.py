"""..."""

from langgraph.graph import START, END, StateGraph

from agents.state import AgentState
from agents.nodes import model_call, tool_execute, should_continue

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


from IPython.display import Image, display

display(Image(agent.get_graph().draw_mermaid_png()))
