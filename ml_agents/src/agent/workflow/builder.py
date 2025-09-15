"""..."""

from langgraph.graph import START, END, StateGraph

from agent.workflow.state import WorkflowState
from agent.workflow.nodes import code_generation, code_execution, should_continue


# Initialize Graph
workflow_builder = StateGraph(WorkflowState)

# Add nodes
workflow_builder.add_node("code_generation", code_generation)
workflow_builder.add_node("code_execution", code_execution)

# Add edges
workflow_builder.add_edge(START, "code_generation")
workflow_builder.add_edge("code_generation", "code_execution")
workflow_builder.add_conditional_edges(
    "code_execution", should_continue, {"Failed": "code_generation", END: END}
)


# Compile graph
workflow = workflow_builder.compile()


from IPython.display import Image, display

display(Image(workflow.get_graph().draw_mermaid_png()))
