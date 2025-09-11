"""

This module defines `CodeExecutionNode`, responsible for executing Python code
produced by the agent, managing variable states, handling execution errors,
and updating analysis/visualization results in the agent's state.
"""

import re
import pickle
import importlib
from types import ModuleType
from typing import Optional, List, Any


from agent.state import AgentState


class CodeExecutionNode:
    """
    Node to execute Python code from the agent's state safely, capturing
    results, analysis reports, visualizations, and handling errors.

    Responsibilities:
    - Dynamically import required dependencies.
    - Execute code in a controlled environment combining previous variables.
    - Capture only pickle-serializable variables to avoid execution issues.
    - Update the agent state with new variables, visualizations, and analysis reports.
    - Track and report execution errors for debugging or fallback.
    """

    @staticmethod
    def _import_dependencies(dependencies: List[str]):
        """
        Dynamically import required Python packages.

        Args:
            dependencies: List of package/module names to import.

        Returns:
            dict: Mapping of package names to imported module objects.
        """
        imported_modules = {}
        for package_name in dependencies:
            try:
                module = importlib.import_module(package_name)
                imported_modules[package_name] = module
            except Exception:
                # Ignore import errors for missing packages
                ...
        return imported_modules

    @staticmethod
    def _is_pickle_serializable(obj: Any) -> bool:
        """
        Check if an object can be serialized with pickle.

        Args:
            obj (Any): Object to test for pickle serialization.

        Returns:
            bool: True if object can be pickled, False otherwise.
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception:
            return False

    @staticmethod
    def _extract_code(message: str) -> Optional[str]:
        """
        Extract Python code from a triple-backtick code block in a message.

        Args:
            message: Text containing Python code wrapped in ```python ... ```.

        Returns:
            Optional[str]: Extracted code if present; otherwise, None.
        """
        pattern = r"```python\s([\s\S]*?)```"
        match = re.search(pattern, message.strip(), re.DOTALL)

        if not match:
            return None

        text = match.group(1).strip()
        return text

    @classmethod
    def invoke(cls, state: AgentState) -> AgentState:
        """
        Execute the code from the agent state and update variables, errors, and summaries.

        Args:
            state: The current state of the agent, containing:
                - code: Code snippet to execute.
                - dependencies: Required Python packages.
                - variables: Existing variables to include in execution.
                - subtask_flow: Current subtask flow ("ANALYSIS" or "VISUALIZATION").
                - code_summary: Previous code summaries.

        Returns:
            AgentState: Updated state with executed variables, error messages, and summaries.
        """

        # Extract the Python code block from the state
        code = cls._extract_code(state.code)

        # Prepare execution contexts
        global_context = cls._import_dependencies(
            state.dependencies
        )  # Imported modules

        local_context = state.code_variables.copy()  # Existing variables
        global_context.update(local_context)  # Merge contexts

        try:
            # Execute the code in combined context
            exec(code, global_context)

            # Extract only pickle-serializable variables, ignoring modules and dependencies
            variables = {
                k: v
                for k, v in global_context.items()
                if k not in state.dependencies and not isinstance(v, ModuleType)
                if cls._is_pickle_serializable(v)
            }

            state.code_variables = variables

            # Update analysis response
            state.analysis_response = state.code_variables.get("analysis_report")

            # Update visualization if exists
            state.visualization = state.code_variables.get("image")

            # Clear previous error messages and reset debagging attemps counter
            state.error_message = None
            state.current_debugging_attempt = 0

        except Exception as e:
            # Capture any execution errors
            state.error_message = f"{e}"

        finally:
            return state
