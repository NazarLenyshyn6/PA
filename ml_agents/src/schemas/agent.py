"""
...
"""

from typing import List

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    ...
    """

    question: str
    file_names: List[str]
    data_summaries: str
    data: List[str]
