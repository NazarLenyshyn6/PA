"""
Pydantic model for agent requests.

Defines the structure of a request sent to the agent, including the question,
associated file names, data summaries, and base64-encoded CSV data.
"""

from typing import List

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    Request schema for interacting with the agent.

    Attributes:
        question (str): The user's question for the agent.
        file_names (List[str]): Names of the files corresponding to the data.
        data_summaries (str): Summaries of the datasets.
        data (List[str]): Base64-encoded CSV data.
    """

    question: str
    file_names: List[str]
    data_summaries: str
    data: List[str]
