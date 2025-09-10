"""
Agent memory schema definitions.

This module provides Pydantic models for validating and serializing agent
memory data. The schemas define both the complete memory representation
(`Memory`) and a minimal version for persistence requests
(`MemorySave`).

Classes:
    Memory: Full schema representing agent memory with optional
        conversation, variable, and code contexts.
    MemorySave: Lightweight schema for persisting minimal memory
        metadata (user, session, file).
"""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from schemas.base import BaseSchema


class Memory(BaseSchema):
    """
    Schema representing full agent memory state.

    This model captures all serialized memory components generated during
    an agent’s interaction with a user. Designed for read
    operations, API responses, and debugging workflows.

    Attributes:
        user_id: Identifier for the user associated with the memory.
        session_id: Unique identifier for the session.
        file_name: Name of the file or context tied to the memory.
        messages: .
        variables: Serialized snapshot of variables from the session.
    """

    user_id: int
    session_id: UUID
    file_name: str
    messages: Optional[bytes]
    variables: Optional[bytes]


class MemorySave(BaseModel):
    """
    Lightweight schema for persisting agent memory metadata.

    This model defines the minimal set of fields required to store
    a reference to agent memory, excluding large binary payloads.
    Typically used for save requests or index records.

    Attributes:
        user_id (int): Identifier for the user associated with the memory.
        session_id (UUID): Unique identifier for the session.
        file_name (str): Name of the file or context tied to the memory.
    """

    user_id: int
    session_id: UUID
    file_name: str


class MemoryDelete(BaseModel):
    """
    Schema for deleting a specific agent memory entry.

    This model is used to specify which memory record should be removed,
    typically via API delete requests.

    Attributes:
        user_id: Identifier for the user associated with the memory.
        file_name: Name of the file or context tied to the memory.
    """

    user_id: int
    file_name: str
