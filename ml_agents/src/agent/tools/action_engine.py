"""
This module provides tools for generating and executing production-ready
time-series analysis or forecasting pipelines. It includes code generation,
execution, and integrated failure handling.
"""

from typing import Annotated
import importlib

from langchain_core.tools import tool, InjectedToolArg

from agent.state import AgentState
from agent.schemas import GeneratedCode
from agent.chains.code import code_generation_chain


def _code_generation(
    generation_instruction: str, data_summaries: str, dependencies: str
):
    """
    Generate Python code from a structured generation instruction.

    Args:
        generation_instruction: Instructions for full-task pipeline.
        data_summaries: Summary of datasets in memory.
        dependencies: Required package dependencies.

    Returns:
        str: Generated Python code ready for execution.
    """
    generated_code: GeneratedCode = code_generation_chain.invoke(
        {
            "generation_instruction": generation_instruction,
            "data_summaries": data_summaries,
            "dependencies": dependencies,
        }
    ).code
    print("")
    print()
    print()
    print("=" * 100)
    print(generated_code)
    print()
    print()
    return generated_code


def _code_execution(code: str, state: AgentState):
    """
    Execute generated Python code in an isolated state-aware context.

    Args:
        code: Python code to execute.
        state: AgentState containing variables and dependencies.

    Returns:
        Tuple[str, Optional[Any]]: Analysis report and optional image.
    """
    # Prepare a clean global execution context
    global_context = {}

    # Import all dependencies dynamically and add to global context
    for package_name in state["dependencies"]:
        try:
            module = importlib.import_module(package_name)
            global_context[package_name] = module
        except Exception:
            ...

    # Copy local variables from state into execution context
    local_context = state["variables"].copy()
    global_context.update(local_context)

    try:
        exec(code, global_context)

        # Extract outputs expected from the executed code
        return (
            global_context["analysis_report"],
            global_context.get("image"),
            global_context.get("interactive_image"),
        )

    except Exception as e:
        return (
            f"""
Execution Status: Failed
Result: None

--- ERROR MESSAGE ---
{str(e)}
""",
            None,
            None,
        )


@tool
def action_engine(
    generation_instruction: str, state: Annotated[AgentState, InjectedToolArg]
):
    """
    Executes a full, production-ready structured time-series analysis or Prophet forecasting pipeline on datasets fully available in memory.

    MANDATORY: This must produce a **complete, end-to-end action plan** to accomplish the **entire task in one execution**, not just a single subtask.

    Key Rules:
        - Only run after a production-ready plan exists.
        - Execute the **entire task in one go**, producing all steps from preprocessing to final forecasting, diagnostics, and model selection.
        - Use **Prophet only for forecasting**.
        - **All data is fully available in memory**; never plan, mention, or perform ingestion/loading.
        - **Strictly forbidden:** Any instructions for data loading, parsing, or structure display.
        - Steps must be **concrete, directly executable, concise, and focused** on completing the full task.
        - Include **minimal preprocessing only for necessary steps** (mapping ds/y, regressors, handling missing values/outliers).
        - **All zero values (`0`) must be considered missing** and imputed together with other missing values, **always**.
        - Visualizations only if explicitly requested, with **maximum 4 subplots**.
        - **Mandatory Conditional Failure Handling:**
            - Only trigger if previous code execution failed:
                - Analyze the failed code and identify the error.
                - Rethink the plan to fix it.
                - Provide **instructional guidance** to prevent the same error in future iterations (do not include code).
            - If no previous failure exists, **omit failure guidance entirely**.

    When to Use:
        - Computation required: stats, forecasting, cross-validation, diagnostics, or requested plots.
        - A plan exists; execute **the entire task in one execution**.
        - **Never use this for data ingestion, loading, or preparation.**

    Args:
        generation_instruction (str): The full-task plan, including:
            - Step-by-step action plan
            - Deliverables (in-memory)
            - Acceptance Criteria (if any)
            - Conditional failure guidance **only if previous code failed**

    Requirements:
        - Each step must be:
            - Directly executable
            - Prophet-based for modeling/forecasting
            - Focused **on completing the full task**
            - Include minimal preprocessing (without touching ingestion/loading)
            - **Zero values (`0`) must always be treated as missing and imputed**
            - Concise to produce only required outputs
            - **Include failure guidance only if previous code failed**

    Returns:
        str: Execution results of the full task, including failure analysis and preventive instructions **only if previous code failed**.

    Additional Instructions for Forecasting/Model Training:
        - If the user requests **forecasting/model training**, produce a **single, production-ready, step-by-step action plan** that is **directly executable by a code-generation model**.
        - The plan must include:
            - In-depth Prophet configuration
            - **Minimalistic hyperparameter tuning** for fast execution (do not exhaustively explore all parameters; only check a small, essential set)
            - Time-aware cross-validation
            - Best-model selection
            - All necessary preprocessing steps
            - **Zero values (`0`) treated as missing and imputed like other NaNs**
        - The trained model must be **top-performing**; do not leave Prophet at default parameters.
    """
    # Generate executable Python code
    code = _code_generation(
        generation_instruction=generation_instruction,
        data_summaries=state["data_summaries"],
        dependencies=state["dependencies"],
    )

    # Execute the generated code in an isolated context
    analysis_report, image, interactive_image = _code_execution(code, state)

    # Return the analysis report and optional visualization
    return analysis_report, image, interactive_image
