"""..."""

import importlib

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langgraph.graph import END

from agent.workflow.state import WorkflowState
from agent.chat_models import code_generation_model

dependencies = [
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "statsmodels.api",
    "joblib",
    "torch",
    "torchvision",
    "lightgbm",
    "xgboost",
    "optuna",
    "sentence_transformers",
    "gensim==4.3.2",
    "matplotlib.pyplot",
    "seaborn",
    "nltk",
    "spacy",
    "tqdm",
    "networkx",
    "prophet>=1.2",
    "nltk>=3.9",
]


def code_generation(state: WorkflowState):
    code_generation_prompt = ChatPromptTemplate.from_messages(
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

    **DATASET CONTEXT:**  
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
    chain = code_generation_prompt | code_generation_model
    generated_code = chain.invoke(
        {
            "generation_instruction": state["generation_instruction"],
            "data_summaries": state["data_summaries"],
            "dependencies": state["dependencies"],
            "error_message": state["error_message"],
        }
    )
    return {"code": generated_code.code}


def code_execution(state: WorkflowState):

    # Import libraries
    global_context = {}
    for package_name in dependencies:
        try:
            module = importlib.import_module(package_name)
            global_context[package_name] = module
        except Exception:
            # Ignore import errors for missing packages
            ...

    # Extend with dataframes
    local_context = state["variables"].copy()
    global_context.update(local_context)

    # Execute generated code
    try:
        exec(state["code"], global_context)
        return {
            "analysis_report": global_context.get("analysis_report"),
            "visualization": global_context.get("visualization"),
        }

    except Exception:
        return


def should_continue(state: WorkflowState):
    if state["error_message"]:
        return "Error"
    return END
