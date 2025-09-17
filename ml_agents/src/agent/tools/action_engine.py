"""..."""

from typing import Annotated
import importlib
from pprint import pformat

from langchain_core.tools import tool, InjectedToolArg
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from agent.state import AgentState
from agent.chat_models import code_generation_model
from agent.schemas import GeneratedCode


def _code_generation(
    generation_instruction: str, data_summaries: str, dependencies: str
):
    """..."""
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                """
You are a **professional ML engineer and data scientist**.  
Your sole role is to **translate detailed time series analysis, modeling, and visualization action plans into highly efficient, production-ready Python code**.  
You must **execute every step and sub-step in the provided plan exactly as written, with zero deviation or omission**.  

The user is performing **time series analysis, modeling, and visualization tasks** 
with data that is **already available** in the system.

__  
## HIGH-QUALITY EXECUTION PRINCIPLES

### ABSOLUTE RULES
- **STRICT COMPLIANCE** — Follow the task instructions and action plan **literally and completely**.  
  - Do not skip, alter, or reinterpret steps.  
  - Do not add extra processing or commentary.  
  - Execute **all steps and sub-steps exactly as stated**.  
- **PROPHET PRIORITY** — The Prophet model must always be used as the **first and primary forecasting model**.  
  - Use other models only if:  
    1. Explicitly required in the plan, OR  
    2. Prophet demonstrates poor performance (must be logged in analysis_report).  
- **STRICT PREDICTION START** — All Prophet forecasts must **start strictly from the latest timestamp in the dataset**.  
  - Do not generate predictions from any earlier point in time.  
  - Ensure alignment with the last known `ds` value in the dataset.  
- ** Never include or write code for data loading. Never user pd.read_csv(), all data is avalible and any data ingestion will lead to error. SO NEVER DO THAT.

### SHARED PRINCIPLES
1. **High-Quality Code** — Python code must be clear, efficient, maintainable, and production-ready.
   - Solve the task directly, robustly, and efficiently.
   - Use advanced libraries and techniques when required.
2. **Execution & Variable Safety**
   - Initialize all variables before use.
   - **Never initialize variables that are not used.**
   - Use safe dictionary/column access (e.g., .get(key, default) or if key in dict).
   - Never overwrite previous variables unless explicitly instructed.
3. **Library & Execution Flexibility**
   - Use only libraries required for the task.
   - **Never import libraries not used in the code.**
   - Import all libraries at the start, only once.
   - Do not load new datasets — only use provided data.
   - **Never create, mock, or shortcut data. Always operate on the full provided dataset.**
   - All outputs must be in a single python block.
4. **STRICT STRUCTURE & NAMING**
   - Access dataset columns exactly as named in context.
   - Never invent or rename variables.
   - Absolutely no syntax or naming errors.
5. **GLOBAL ERROR-PREVENTION**
   - No runtime errors allowed.
   - Validate variable names, types, and scope.
   - Guard against None, NaN, empty data, or missing keys.
   - Reuse variables only if they exist and are type-correct.
   - **When computing metrics or residuals, always align forecast and actual data by timestamp (e.g., 'ds') to prevent broadcasting, shape, or alignment errors.**
6. **STRICT DICTIONARY & KEY ACCESS**
   - Never assume keys exist.
   - Always check using .get() or if key in dict.
   - Log skips in analysis_report when data is missing.
7. **MANDATORY analysis_report HANDLING**
   - Always start with: `analysis_report = []`.
   - All results, metrics, predictions, transformation results, and safe skips must append to analysis_report.
   - **Every numeric value, prediction, and transformation output must be appended.**
   - analysis_report must never be empty.
8. **RESULT-ORIENTED EXECUTION**
   - Code must yield the requested outputs, nothing else.
   - Visualizations generated only if explicitly required.
   - Intermediate steps only if contributing to final results.
   - All predictions must use best-suited models/methods, Prophet first.

---

### MODE-SPECIFIC RULES

#### Time Series Visualization Mode
- Translate instructions into **time series visualization code only**.
- Use line plots, trend plots, or time series-specific plots.
- All plots in a single figure with grid layout.
- Legends must not overlap.
- Initialize `image = None` (mandatory).
- Save figure to buffer, encode as base64, assign to `image`.
- Use headless backend:
  ```python
  import matplotlib
  matplotlib.use("Agg")
  
#### STRICT VISUALIZATION SPACING RULES
    - Subplots, their titles, axis labels, tick labels, legends, and any text must never overlap.
    - Use automatic layout managers (e.g., plt.tight_layout(), constrained_layout=True) to guarantee spacing.
    - Subplots must be evenly spaced with clear separation at all times.
    - Overlapping of subplot boundaries, labels, or legends is strictly forbidden.

**DATASETS CONTEXT:**  
{data_summaries}
    """
            ),
            HumanMessagePromptTemplate.from_template(
                """
    **NEW INSTRUCTION:**  
    {generation_instruction}

    IMPORTANT EXECUTION RULES
        - Treat the task as a step-by-step action plan.
        - ALL STEPS AND SUB-STEPS MUST BE TRANSLATED INTO EXECUTABLE PYTHON CODE.
        - Follow exact variable names, step order, and sub-step details.
        - Ensure analysis_report is fully populated with results, numeric values, predictions, or safe skips.
        - Always initialize analysis_report = [] and image = None where required.
        - Import only required libraries at the start.
        - Never import unused libraries.
        - Never initialize variables that are not used.
        - When computing residuals, errors, or evaluation metrics, always merge or align forecasted values with actuals by timestamp to prevent broadcasting or length mismatch errors.
        - Never mock or shortcut data. Always operate on the provided dataset.
        - All outputs must be in a single python block.
        - Code must run immediately, be robust, production-level, and error-free.
        - Always use Prophet as top-priority forecasting model unless the plan specifies otherwise or Prophet performs poorly.
        - **Prophet predictions must start strictly from the last/latest timestamp in the dataset.**
    """
            ),
        ]
    )
    chain = prompt | code_generation_model
    generated_code: GeneratedCode = chain.invoke(
        {
            "generation_instruction": generation_instruction,
            "data_summaries": data_summaries,
            "dependencies": dependencies,
        }
    ).code
    return generated_code


def _code_execution(code: str, state: AgentState):
    """..."""
    global_context = {}
    for package_name in state["dependencies"]:
        try:
            module = importlib.import_module(package_name)
            global_context[package_name] = module
        except Exception:
            ...
    local_context = state["variables"].copy()
    global_context.update(local_context)

    try:
        exec(code, global_context)
        return global_context["analysis_report"], global_context.get("image")

    except Exception as e:
        return (
            f"""
Execution Status: Failed
Result: None

--- ERROR MESSAGE ---
{str(e)}
""",
            None,
        )


@tool
def action_engine(
    generation_instruction: str, state: Annotated[AgentState, InjectedToolArg]
):
    """
    This tool executes planned actions by transforming a structured generation_instruction into Python code and running it.

    Key Rules:
        - The generation_instruction must be provided by the agent.
        - It must be formatted as a numbered structured list (1., 2., 3., ...).
        - It must clearly define:
            1. What code must be written.
            2. What data operations must be performed (data is already available in memory as pandas DataFrames).
            3. What the code must achieve (outputs, transformations, or analysis goals).
        - If previous executions failed, the generation_instruction must include an additional numbered section:
            - Explicitly describe how to correct the error and prevent it in future runs.
        - Instructions must be concise and efficient, avoiding unnecessary detail.

    When to Use:
        - A structured generation_instruction exists.
        - The agent needs to execute code to achieve the defined goal.
        - Previous failures must be addressed by including corrective steps in the list.

    Args:
        generation_instruction (str): A structured, numbered plan containing:
            1. Code that must be written.
            2. Data operations to perform (using in-memory DataFrames).
            3. Outputs or deliverables expected.
            4. Error correction guidance (only if previous execution failed).

    Mandatory requirements:
        - Plans must always begin with a short title providing context for the subtask.
        - Deliverables and acceptance criteria must always be explicitly included.
        - Each step must be part of a structured numbered list.
        - Plans must be clear, concise, and directly executable.
        - No unnecessary steps or verbose detail should be included.
        - Failure handling instructions must only appear if a previous execution failed.

    Returns:
        str: Execution results of the generated code.
             Includes corrective analysis only if error handling instructions were provided.
    """
    code = _code_generation(
        generation_instruction=generation_instruction,
        data_summaries=state["data_summaries"],
        dependencies=state["dependencies"],
    )
    print("=" * 100)
    print("* GENERATION INSTRUCTION:\n\n")
    print(generation_instruction)
    print("=" * 100)
    print("* GENERATED CODE:\n\n")
    print(code)
    analysis_report, image = _code_execution(code, state)

    print("=" * 100)
    print("* ANALYSIS REPORT:\n\n")
    print(analysis_report)

    return analysis_report, image
