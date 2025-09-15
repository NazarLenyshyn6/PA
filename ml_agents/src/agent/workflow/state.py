"""..."""

from typing import TypedDict, List, Dict, Optional

import pandas as pd


class WorkflowState(TypedDict):
    """..."""

    generation_instruction: str

    data_summaries: List[str]
    variables: List[Dict[str, pd.DataFrame]]
    dependencies: List[str]

    code: str
    error_message: Optional[str]

    current_debugging_attempt: int
    max_debugging_attemps: int

    analysis_report: List
    visualization: Optional[str]
