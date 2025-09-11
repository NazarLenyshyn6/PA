"""
This module defines the `CodeGenerationNode`, responsible for generating
executable Python code based on the agent's task, dataset, dependencies,
and current code variables.

Responsibilities:
- Transform a high-level task description into safe, executable code.
- Ensure generated code respects all dataset and variable constraints.
- Interface with a language model to produce beginner-friendly, error-free code.
"""

from typing import override

from agent.nodes.base import BaseNode
from agent.state import AgentState
from agent.prompts.code.generation import code_generation_prompt
from agent.chat_models import code_generation_model


class CodeGenerationNode(BaseNode):
    """
    Node for generating executable Python code for time series or
    data analysis tasks based on the agent's current state.

    Attributes:
        model: The language model used to generate code.
        prompt: The prompt template guiding code generation.
    """

    @override
    def invoke(self, state: AgentState):
        """
        Generate Python code for the agent's task and update the state.

        Steps:
        2. Invoke the language model chain with task, dataset summary,
           dependencies, and current code variables.
        3. Store the generated code in the `state.code` attribute.

        Args:
            state (AgentState): Current agent state containing task,
                                dataset summary, dependencies, and code variables.

        Returns:
            AgentState: Updated agent state with `code` set to generated Python code.
        """
        state.code = self._chain.invoke(
            {
                "dependencies": state.dependencies,
                "dataset_summary": state.dataset_summary,
                "code_variables": state.code_variables,
                "task": state.task,
            }
        ).content

        return state


# Preconfigured instance of CodeGenerationNode for integration into the agent graph
code_generation_node = CodeGenerationNode(
    model=code_generation_model, prompt=code_generation_prompt
)
