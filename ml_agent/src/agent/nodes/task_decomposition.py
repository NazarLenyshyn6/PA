"""

This module defines the `TaskDecompositionNode`, which is responsible for
decomposing a user question into a single actionable task that can be directly
processed by downstream nodes in the agent workflow.

Responsibilities:
- Convert high-level user questions into concrete, executable tasks.
- Leverage a pre-configured language model and task decomposition prompt.
- Update the agent state with the derived task for further processing.
"""

from typing import override


from agent.nodes.base import BaseNode
from agent.state import AgentState
from agent.prompts.task_decomposition import task_decomposition_prompt
from agent.chat_models import medium_temp_model


class TaskDecompositionNode(BaseNode):
    """
    Node that performs task decomposition within the agent workflow.

    Attributes:
        model: The language model instance used for task decomposition.
        prompt: The prompt template guiding the task decomposition.
    """

    @override
    def invoke(self, state: AgentState):
        """
        Decompose the user's question into a single, actionable task.

        Args:
            state: Current agent state containing the user question.

        Returns:
            AgentState: Updated agent state with the `task` attribute populated.
        """

        state.task = self._chain.invoke(
            {"question": state.question},
            config={"metadata": {"stream": False}},
        ).content

        print("Task:", state.task)

        return state


# Preconfigured instance of TaskDecompositionNode for use in the agent graph
task_decomposition_node = TaskDecompositionNode(
    model=medium_temp_model,
    prompt=task_decomposition_prompt,
)
