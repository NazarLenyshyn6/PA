"""

This module defines the CodeDebuggingNode, a specialized agent node responsible
for automatically correcting Python code that failed execution within the agent's
workflow. It leverages a high-temperature language model to generate corrected,
fully executable code based on the last error, dataset context, and available
variables. The node also tracks debugging attempts to avoid infinite retries.
"""

from typing import override

from agent.nodes.base import BaseNode
from agent.state import AgentState
from agent.prompts.code.debugging import code_debugging_prompt
from agent.chat_models import code_debugging_model


class CodeDebuggingNode(BaseNode):
    """
    Node responsible for automatically correcting code that failed execution.

    Responsibilities:
    - Receive the current code, error message, and execution context.
    - Generate corrected, fully executable Python code.
    - Update the agent's code in state.
    - Track debugging attempts to prevent infinite retries.
    """

    @override
    def invoke(self, state: AgentState):
        """
        Correct the user's code based on the last error and available context.

        Args:
            state (AgentState): The current agent state, including:
                - code: Current code snippet.
                - error_message: Last error message from execution.
                - code_variables: Currently available variables in execution context.
                - dependencies: Required Python packages.
                - dataset_summary: Summary of the dataset context.
                - question: Original user question/task.

        Returns:
            AgentState: Updated state with corrected code and incremented debugging attempt.
        """

        # Generate corrected code based on current code, error message, and context
        state.code = self._chain.invoke(
            {
                "question": state.question,
                "dependencies": state.dependencies,
                "dataset_summary": state.dataset_summary,
                "code": state.code,
                "error_message": state.error_message,
                "code_variables": state.code_variables.keys(),
            }
        ).content

        # Increment the debugging attempt counter
        state.current_debugging_attempt = state.current_debugging_attempt + 1

        return state


# Preconfigured instance of CodeDebuggingNode for integration into the agent graph
code_debugging_node = CodeDebuggingNode(
    model=code_debugging_model, prompt=code_debugging_prompt
)
