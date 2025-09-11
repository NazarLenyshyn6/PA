"""
...
"""

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    ...
    """

    question: str
    data: str
