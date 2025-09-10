"""
This module defines the `AgentRequest` data model using Pydantic's BaseModel.
It represents a structured request for an AI agent, containing all necessary
information for processing a user's question, session, and associated dataset.

Classes:
    AgentRequest: Pydantic model encapsulating user query details and metadata.
"""

from uuid import UUID

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    Data model representing a request to an AI agent.

    Attributes:
        question: The user's question or query to be processed by the agent.
        user_id: Unique identifier of the user making the request.
        session_id: Unique identifier for the user's session.
        file_name: Name of the file associated with the request (if any).
        storage_uri: URI or path to the storage location of relevant data or files.
    """

    question: str
    user_id: int
    session_id: UUID
    file_name: str
    storage_uri: str
