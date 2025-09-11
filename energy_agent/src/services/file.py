"""
...
"""

from uuid import UUID
from dataclasses import dataclass
from typing import List, Union, Dict, ClassVar

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from core.enums import StorageType
from cache.file import FileCacheManager, file_cache
from schemas.file import FileRead, FileCreate
from storage.base import BaseStorage
from storage.local import LocalStorage
from repositories.file import FileRepository


@dataclass
class FileService:
    """
    ...
    """

    file_cache: FileCacheManager

    STORAGE_MAPPING: ClassVar[Dict[StorageType, BaseStorage]] = {
        StorageType.LOCAL: LocalStorage
    }

    def get_files(self, db: Session, user_id: int) -> List[FileRead]:
        """
        ...
        """
        db_files = FileRepository.get_files(db=db, user_id=user_id)
        return [FileRead.model_validate(file) for file in db_files]

    def get_active_file(
        self, db: Session, user_id: int, session_id: UUID
    ) -> Union[dict, FileRead]:
        """
        ...
        """
        cached_file = self.file_cache.get_active_file_data(
            user_id=user_id, session_id=session_id
        )
        if not cached_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active file found for session. Set it first.",
            )
        return FileRead(**cached_file)

    def upload_file(
        self,
        db: Session,
        file_name: str,
        user_id: int,
        session_id: UUID,
        file: UploadFile,
        storage_type: StorageType = StorageType.LOCAL,
    ) -> FileRead:
        """
        ...
        """

        # Get storage
        storage = self.STORAGE_MAPPING[storage_type]

        # Upload the file to storage and get its URI
        storage_uri = storage.upload_file(
            file_name=file_name, user_id=user_id, file=file
        )

        # Build metadata object
        file_data = FileCreate(
            file_name=file_name,
            storage_uri=storage_uri,
            storage_type=storage_type,
            user_id=user_id,
        )

        # Persist metadata to database
        db_file = FileRepository.create_file(db=db, file_data=file_data)

        # Cache metadata  as active file for the session
        self.file_cache.cache_active_file_data(
            user_id=user_id,
            session_id=session_id,
            file_data=file_data.model_dump(),
        )

        return FileRead.model_validate(db_file)

    def set_active_file(
        self, db: Session, user_id: int, session_id: UUID, file_name: str
    ) -> None:
        """
        ...
        """
        # Fetch file metadata from database
        db_file = FileRepository.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_name}' not found for user.",
            )

        # Validate and cache the file as the active file
        file_data = FileCreate.model_validate(db_file)
        self.file_cache.cache_active_file_data(
            user_id=user_id,
            session_id=session_id,
            file_data=file_data.model_dump(),
        )

    def delete_file(
        self,
        db: Session,
        user_id: int,
        file_name: str,
        storage_type: StorageType = StorageType.LOCAL,
    ):
        """
        ...
        """
        # Check if the file exists before attempting deletion
        db_file = FileRepository.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_name}' does not exist for user.",
            )

        # Delete metadata from DB
        FileRepository.delete_file(db=db, user_id=user_id, file_name=file_name)

        # Get storage
        storage = self.STORAGE_MAPPING[storage_type]

        # Delete the physical file from storage
        storage.delete_file(storage_uri=db_file.storage_uri)


# Instantiate a global file service with the configured file cache
file_service = FileService(file_cache)
