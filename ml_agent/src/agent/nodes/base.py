"""
Base node module.

This module defines the `BaseNode` abstract class, which serves as the
foundation for building LangChain-based graph nodes. A node encapsulates
a `ChatPromptTemplate` and a `Runnable` model into a reusable execution chain,
optionally enforcing structured output via Pydantic models.

Responsibilities:
    - Combine prompts and models into executable chains.
    - Support structured or unstructured model outputs.
    - Provide a consistent base class for agent graph nodes.

This design enforces modularity and reusability when constructing AI-driven
agent workflows, enabling consistent interaction with memory and execution logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Type


from pydantic import BaseModel, PrivateAttr, ConfigDict
from langchain_core.runnables import Runnable
from langchain.prompts import ChatPromptTemplate

from agent.state import AgentState


class BaseNode(ABC, BaseModel):
    """
    Abstract base class for agent graph nodes.

    A `BaseNode` encapsulates:
        - A `ChatPromptTemplate` (input format).
        - A `Runnable` model (execution engine).
        - Optional structured output enforcement (via Pydantic models).

    Each node builds its execution chain (`_chain`) by composing
    the prompt with the model, with or without structured output.

    Subclasses must implement the `invoke` method to define
    how the node processes an `AgentState`.

    Attributes:
        model: The underlying model to execute.
        prompt: Prompt used to format input.
        structured_output: Optional Pydantic model
            for enforcing structured output validation.
        _chain: Private composed execution chain.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Runnable
    prompt: ChatPromptTemplate
    structured_output: Optional[Type[BaseModel]] = None

    _chain: Runnable = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """
        Initialize the execution chain after model instantiation.

        If `structured_output` is provided, the chain enforces structured
        model responses via a Pydantic schema. Otherwise, a standard
        prompt → model chain is used.

        Args:
            __context (Any): Initialization context (unused but required by Pydantic).
        """
        if self.structured_output is None:
            self._chain = self.prompt | self.model
        else:
            self._chain = self.prompt | self.model.with_structured_output(
                self.structured_output
            )

    @abstractmethod
    def invoke(self, state: AgentState):
        """
        Execute the node's logic on the given state.

        Subclasses must implement this method to define how the node
        consumes and mutates the `AgentState`.

        Args:
            state (AgentState): The current agent execution state.

        Returns:
            Any: The result of executing the node (implementation-specific).
        """
        ...
