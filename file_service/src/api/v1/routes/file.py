"""
File API routes.

This module defines FastAPI endpoints for managing user-uploaded files,
including retrieval, upload, deletion, and managing the active file per session.

It integrates with the `FileService` for business logic and enforces
user authentication via `get_current_user_id`.

Endpoints:
    - GET /files/: List all files for the authenticated user.
    - GET /files/active/{session}: Retrieve the active file for a session.
    - POST /files/active/{session}: Set a file as active for a session.
    - POST /files/: Upload a new file.
    - DELETE /files/{file_name}: Delete a file.
"""

from uuid import UUID
from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Form, UploadFile, File

from core.db import db_manager
from core.secutiry import get_current_user_id
from core.enums import StorageType
from schemas.file import FileRead, ActiveFile
from services.file import file_service

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/")
def get_files(
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
) -> List[FileRead]:
    """
    Retrieve all files for the authenticated user.

    Args:
        db: SQLAlchemy session dependency.
        user_id: ID of the currently authenticated user.

    Returns:
        List[FileRead]: Metadata of all files belonging to the user.
    """
    return file_service.get_files(db=db, user_id=user_id)


@router.get("/active/{session}")
def get_active_file(
    session: UUID,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
) -> FileRead:
    """
    Retrieve the currently active file for a given session.

    Args:
        session: UUID of the session.
        db: SQLAlchemy session dependency.
        user_id: ID of the currently authenticated user.

    Returns:
        FileRead: Metadata of the active file.

    Raises:
        HTTPException: If no active file is set for the session.
    """
    return file_service.get_active_file(db=db, user_id=user_id, session_id=session)


@router.post("/active/{session}")
def set_active_file(
    active_file: ActiveFile,
    session: UUID,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Set a specific file as the active file for a session.

    Args:
        active_file: Pydantic schema containing the file name to set active.
        session: UUID of the session.
        db: SQLAlchemy session dependency.
        user_id: ID of the currently authenticated user.

    Raises:
        HTTPException: If the specified file does not exist for the user.
    """
    file_service.set_active_file(
        db=db, user_id=user_id, session_id=session, file_name=active_file.file_name
    )


@router.post("/")
def upload_file(
    file_name: str = Form(),
    session_id: UUID = Form(),
    file: UploadFile = File(...),
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
) -> FileRead:
    """
    Upload a new file for the authenticated user.

    The uploaded file is stored in the configured storage backend,
    metadata is persisted in the database, and it is cached as the
    active file for the session.

    Args:
        file_name: Name of the file (without extension).
        session_id: UUID of the session.
        description: Description of the file content.
        file: File object uploaded via FastAPI.
        db: SQLAlchemy session dependency.
        user_id: ID of the currently authenticated user.

    Returns:
        FileRead: Metadata of the uploaded file.

    Raises:
        HTTPException: If the file upload or caching fails.
    """
    return file_service.upload_file(
        db=db,
        file_name=file_name,
        storage_type=StorageType.LOCAL,
        user_id=user_id,
        session_id=session_id,
        file=file,
    )


@router.delete("/{file_name}")
def delete_file(
    file_name: str,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
    storage_type=StorageType.LOCAL,
):
    """
    Delete a file for the authenticated user.

    This removes both the file metadata from the database and the
    physical file from the storage backend.

    Args:
        file_name: Name of the file to delete.
        db: SQLAlchemy session dependency.
        user_id: ID of the currently authenticated user.

    Raises:
        HTTPException: If the file does not exist for the user.
    """
    return file_service.delete_file(
        db=db, user_id=user_id, file_name=file_name, storage_type=storage_type
    )
