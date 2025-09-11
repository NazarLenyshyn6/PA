"""
...
"""

from typing import Any, Type

from pydantic import BaseModel, ConfigDict, PrivateAttr
from langgraph.graph import StateGraph, START, END


from agent.state import AgentState
from agent.nodes.task_decomposition import (
    TaskDecompositionNode,
    task_decomposition_node,
)
from agent.nodes.code.generation import CodeGenerationNode, code_generation_node
from agent.nodes.code.debugging import CodeDebuggingNode, code_debugging_node
from agent.nodes.code.execution import CodeExecutionNode
from agent.nodes.visualization_display import VisualizationDisplayNode
from agent.nodes.analysis_response import (
    AnalysisResponseNode,
    analysis_response_node,
)
from agent.nodes.fallback_handling import (
    FallbackHandlingNode,
    fallback_handling_node,
)
from agent.nodes.conditional_routing import routing_from_code_executor


class WorkflowBuilder(BaseModel):
    """
    ...
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    state: Type[AgentState]
    task_decomposition_node: TaskDecompositionNode
    code_generation_node: CodeGenerationNode
    code_debagging_node: CodeDebuggingNode
    analysis_response_node: AnalysisResponseNode
    fallback_handling_node: FallbackHandlingNode

    _graph: StateGraph = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """
        ...
        """
        self._graph = StateGraph(self.state)

    def _add_nodes(self):
        """
        ...
        """
        self._graph.add_node("task_decomposer", self.task_decomposition_node.invoke)
        self._graph.add_node("code_generator", self.code_generation_node.invoke)
        self._graph.add_node("code_executor", CodeExecutionNode.invoke)
        self._graph.add_node("code_debugger", self.code_debagging_node.invoke)
        self._graph.add_node("analysis_responder", self.analysis_response_node.invoke)
        self._graph.add_node("fallback_handler", self.fallback_handling_node.invoke)
        self._graph.add_node("visualization_display", VisualizationDisplayNode.invoke)

    def _add_edges(self):
        """
        ...
        """
        self._graph.add_edge(START, "task_decomposer")
        self._graph.add_edge("task_decomposer", "code_generator")
        self._graph.add_edge("code_generator", "code_executor")
        self._graph.add_edge("code_debugger", "code_executor")
        self._graph.add_edge("visualization_display", "analysis_responder")
        self._graph.add_edge("analysis_responder", END)
        self._graph.add_edge("fallback_handler", END)

    def _add_conditional_edges(self):
        """
        ...
        """
        self._graph.add_conditional_edges(
            "code_executor",
            routing_from_code_executor,
            {
                "visualization_display": "visualization_display",
                "analysis_responder": "analysis_responder",
                "fallback_handler": "fallback_handler",
                "code_debugger": "code_debugger",
            },
        )

    def build(self):
        """
        ...
        """
        self._add_nodes()
        self._add_edges()
        self._add_conditional_edges()

        return self._graph.compile()


# Preconfigured workflow
workflow = WorkflowBuilder(
    state=AgentState,
    task_decomposition_node=task_decomposition_node,
    code_generation_node=code_generation_node,
    code_debagging_node=code_debugging_node,
    analysis_response_node=analysis_response_node,
    fallback_handling_node=fallback_handling_node,
).build()
