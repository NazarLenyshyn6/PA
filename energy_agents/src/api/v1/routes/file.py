"""
...
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
    """
    ...
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
    """
    ...
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
    """
    ...
    """
    user_id = get_current_user_id(token)
    return file_service.delete_file(
        db=db, user_id=user_id, file_name=file_name, storage_type=storage_type
    )
