"""
File service layer.

This module defines the `FileService` class which encapsulates
business logic for managing files, including uploading, deleting,
retrieving all files for a user, and managing the active file per session.

It integrates with:
- `FileRepository` for database persistence.
- `LocalStorage` (or other storage backends) for file storage.
- `FileCacheManager` for caching active file metadata.
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
    Service layer for file management.

    Attributes:
        file_cache: Instance of `FileCacheManager` to manage active
                    file caching per session.
    """

    file_cache: FileCacheManager

    STORAGE_MAPPING: ClassVar[Dict[StorageType, BaseStorage]] = {
        StorageType.LOCAL: LocalStorage
    }

    def get_files(self, db: Session, user_id: int) -> List[FileRead]:
        """
        Retrieve all files for a specific user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user whose files to retrieve.

        Returns:
            List[FileRead]: List of file metadata for the user.
        """
        db_files = FileRepository.get_files(db=db, user_id=user_id)
        return [FileRead.model_validate(file) for file in db_files]

    def get_active_file(
        self, db: Session, user_id: int, session_id: UUID
    ) -> Union[dict, FileRead]:
        """
        Retrieve the currently active file for a given session.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            session_id: UUID of the session.

        Raises:
            HTTPException: If no active file is found for the session.

        Returns:
            Union[dict, FileRead]: Active file metadata from cache.
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
        Upload a new file, persist metadata, and cache it as active.

        Steps:
            1. Upload file to storage backend and obtain URI.
            2. Create a FileCreate schema with metadata.
            3. Persist the file metadata to the database.
            4. Cache the file as the active file for the session.

        Args:
            db: SQLAlchemy session object.
            file_name: Name of the file (without extension).
            storage_type: Type of storage backend.
            user_id: ID of the user uploading the file.
            session_id: UUID of the session.
            file: File object uploaded via FastAPI.

        Returns:
            FileRead: Metadata of the uploaded file.

        Raises:
            HTTPException: If the file cannot be cached or saved.
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
        Set a specific file as the active file for a session.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            session_id: UUID of the session.
            file_name: Name of the file to set as active.

        Raises:
            HTTPException: If the file does not exist.
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
        Delete a file both from database and storage.

        Steps:
            1. Verify file exists in the database.
            2. Delete metadata from the database.
            3. Delete the physical file from storage backend.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            file_name: Name of the file to delete.

        Raises:
            HTTPException: If the file does not exist.
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
