"""
This module defines the `AnalysisResponseNode`, responsible for converting
raw analysis outputs into a polished, human-readable report.

Responsibilities:
- Format structured analysis data (lists, dictionaries) into readable text.
- Invoke a high-temperature language model to generate a concise,
  structured response suitable for end-user presentation.
"""

from typing import override
from pprint import pformat

from agent.nodes.base import BaseNode
from agent.state import AgentState
from agent.prompts.analysis_response import analysis_response_prompt
from agent.chat_models import high_temp_model


class AnalysisResponseNode(BaseNode):
    """
    Node for generating structured, human-readable analysis reports
    from the agent's raw analysis results.

    Attributes:
        model: The language model used for generating final report text.
        prompt: The prompt template guiding report formatting and content.
    """

    @staticmethod
    def _parse_analysis_response(analysis_response: list) -> str:
        """
        Convert a raw analysis report list into a formatted string.

        Args:
            analysis_response: List of analysis steps, where each step
                                    may be a string or a dictionary.

        Returns:
            str: Formatted, human-readable string of the analysis report.
        """

        lines = []
        for i, entry in enumerate(analysis_response, 1):
            lines.append(f"Step {i}:")
            if isinstance(entry, dict):
                # Format dictionary entries with indentation for readability
                for key, value in entry.items():
                    formatted_value = pformat(value, indent=4, width=80)
                    lines.append(f"  {key}: {formatted_value}")
            else:
                lines.append(f"  {entry}")
            lines.append("")

        return "\n".join(lines)

    @override
    def invoke(self, state: AgentState):
        """
        Generate a polished analysis report and update the agent state.

        Steps:
        1. Parse and format the raw analysis response.
        2. Invoke the language model chain to generate a structured report.

        Args:
            state : Current agent state containing question
                                and analysis_response.

        Returns:
            AgentState: Updated agent state (analysis_response processed
                        and formatted for reporting).
        """

        # Format raw analysis report for clarity
        analysis_response = self._parse_analysis_response(state.analysis_response)

        # Generate a polished report using the model chain
        self._chain.invoke(
            {
                "question": state.question,
                "analysis_response": analysis_response,
            }
        ).content

        return state


# Preconfigured instance of AnalysisResponseNode for integration into the agent graph
analysis_response_node = AnalysisResponseNode(
    model=high_temp_model, prompt=analysis_response_prompt
)
