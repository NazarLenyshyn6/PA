"""
This module defines the `FallbackHandlingNode`, which manages situations where
the agent is unable to produce a direct or successful response from prior nodes.

Responsibilities:
- Handle fallback scenarios gracefully.
- Attempt to resolve tasks that could not be processed by earlier nodes.
- Integrate with a high-temperature language model for creative/flexible responses.
"""

from typing import override

from agent.nodes.base import BaseNode
from agent.state import AgentState
from agent.prompts.fallback_handling import fallback_handling_prompt
from agent.chat_models import high_temp_model


class FallbackHandlingNode(BaseNode):
    """
    Node responsible for handling fallback or error recovery in the agent workflow.

    Attributes:
        model: The high-temperature language model used for fallback generation.
        prompt: The prompt template guiding fallback behavior.
    """

    @override
    def invoke(self, state: AgentState):
        """
        Execute fallback handling for the current task in the agent state.

        Args:
            state: The current state of the agent containing the task
                                that could not be completed by previous nodes.

        Returns:
            AgentState: The updated agent state (unchanged except that fallback
                        logic has been invoked).
        """
        self._chain.invoke({"question": state.task})

        return state


# Preconfigured instance of FallbackHandlingNode for integration into the agent graph
fallback_handling_node = FallbackHandlingNode(
    model=high_temp_model, prompt=fallback_handling_prompt
)
