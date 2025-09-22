"""
File management API routes.

Provides endpoints for:
- Retrieving metadata of a user's files
- Uploading new files
- Deleting existing files

All routes require OAuth2 authentication via Bearer token.
"""

from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer

from core.db import db_manager
from core.secutiry import get_current_user_id
from core.enums import StorageType
from schemas.file import FileData
from services.file import file_service

router = APIRouter(prefix="/files", tags=["Files"])

# OAuth2 password bearer scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.get("/metadata")
def get_files_metadata(
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
) -> List[FileData]:
    """Retrieve metadata of all files for the authenticated user.

    Args:
        db (Session, optional): SQLAlchemy database session. Defaults via dependency injection.
        token (str, optional): OAuth2 bearer token. Defaults via dependency injection.

    Returns:
        List[FileData]: List of user's file metadata.
    """
    user_id = get_current_user_id(token)
    return file_service.get_files_metadata(db=db, user_id=user_id)


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    file_name: str = Form(),
    file_description: str = Form(),
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
) -> None:
    """Upload a new file for the authenticated user.

    Args:
        file (UploadFile): Uploaded file.
        file_name (str): Name to assign to the file.
        file_description (str): Description of the file.
        db (Session, optional): SQLAlchemy database session.
        token (str, optional): OAuth2 bearer token.
    """
    user_id = get_current_user_id(token)
    file_service.upload_file(
        db=db,
        file=file,
        user_id=user_id,
        file_name=file_name,
        file_description=file_description,
        storage_type=StorageType.LOCAL,
    )


@router.delete("/{file_name}")
def delete_file(
    file_name: str,
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
    storage_type=StorageType.LOCAL,
):
    """Delete a file for the authenticated user.

    Args:
        file_name (str): Name of the file to delete.
        db (Session, optional): SQLAlchemy database session.
        token (str, optional): OAuth2 bearer token.
        storage_type (StorageType, optional): Storage backend. Defaults to LOCAL.
    """
    user_id = get_current_user_id(token)
    return file_service.delete_file(
        db=db, user_id=user_id, file_name=file_name, storage_type=storage_type
    )
