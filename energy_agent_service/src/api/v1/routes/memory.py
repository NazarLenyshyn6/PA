"""
FastAPI routes for managing agent memory.

This module exposes HTTP endpoints for retrieving and persisting
agent memory data. It leverages the `MemoryService` to interact with
the cache and database layers, ensuring efficient memory access.

Routes:
    GET /memory/: Retrieve the conversation history for a given user,
        session, and file.
    POST /memory/: Persist cached memory for a given user, session,
        and file.
    DELETE /memory/: Remove memory for a given user, session, and file.
"""

from uuid import UUID


from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from core.db import db_manager
from services.memory import memory_service
from schemas.memory import MemorySave, MemoryDelete

router = APIRouter(prefix="/memory", tags=["AgentMemory"])


# Note: Open after conversation_memory done on memory service
# @router.get("/")
# def get_conversation_memory(
#     user_id: int,
#     session_id: UUID,
#     file_name: str,
#     storage_uri: str,
#     db: Session = Depends(db_manager.get_db),
# ):
#     """
#     Retrieve conversation memory for a user session.

#     This endpoint fetches the conversation history from cache or
#     database using the `MemoryService`. If no memory exists, a new
#     memory record is created.

#     Args:
#         user_id: Identifier of the user.
#         session_id: Unique identifier of the session.
#         file_name: Name of the file or context.
#         storage_uri: Path or URI to the source data.
#         db: SQLAlchemy session injected by FastAPI.

#     Returns:
#         Any: Unpickled conversation object (e.g., list of messages).
#     """
#     return memory_service.get_conversation_memory(
#         db=db,
#         user_id=user_id,
#         session_id=session_id,
#         file_name=file_name,
#         storage_uri=storage_uri,
#     )


@router.post("/")
def save_memory(
    memory_save: MemorySave,
    db: Session = Depends(db_manager.get_db),
):
    """
    Persist cached memory into the database.

    This endpoint retrieves the cached memory for a given user,
    session, and file, and saves it to the database via
    `MemoryService`.

    Args:
        memory_save: Minimal memory metadata containing
            user_id, session_id, and file_name.
        db: SQLAlchemy session injected by FastAPI.
    """
    memory_service.save_memory(
        db=db,
        user_id=memory_save.user_id,
        session_id=memory_save.session_id,
        file_name=memory_save.file_name,
    )


@router.delete("/")
def delete_memory(
    memory_delete: MemoryDelete, db: Session = Depends(db_manager.get_db)
):
    """
    Delete memory for a user session.

    This endpoint removes a specific memory record from the cache and/or
    database using the `MemoryService`.

    Args:
        memory_delete (MemoryDelete): Metadata specifying which memory to delete.
            Includes user_id, session_id, and file_name.
        db (Session): SQLAlchemy session injected by FastAPI.

    Returns:
        None
    """
    memory_service.delete_memory(
        db=db, user_id=memory_delete.user_id, file_name=memory_delete.file_name
    )
