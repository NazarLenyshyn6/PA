"""
Service layer for file management.

Handles uploading, retrieving, caching, and deleting user files
across supported storage backends (e.g., local storage).
"""

from dataclasses import dataclass
from typing import List, Dict, ClassVar

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from core.enums import StorageType
from cache.file import FileCacheManager, file_cache
from schemas.file import FileCreate, FileData
from storage.base import BaseStorage
from storage.local import LocalStorage
from repositories.file import FileRepository


@dataclass
class FileService:
    """Service class for managing file operations."""

    file_cache: FileCacheManager

    # Mapping of storage types to their backend implementations
    STORAGE_MAPPING: ClassVar[Dict[StorageType, BaseStorage]] = {
        StorageType.LOCAL: LocalStorage
    }

    def get_files(
        self, db: Session, user_id: int, storage_type: StorageType = StorageType.LOCAL
    ) -> List[FileData]:
        """Retrieve files for a user, preferring cache over database.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user requesting files.
            storage_type (StorageType, optional): Storage backend type.
                Defaults to local storage.

        Returns:
            List[FileData]: List of files belonging to the user.
        """
        # Try cache first
        cached_files = self.file_cache.get_cached_files(user_id=user_id)
        if cached_files:
            return list(cached_files.values())

        # Fallback: fetch from DB
        db_files = FileRepository.get_files(db=db, user_id=user_id)
        if not db_files:
            return []

        # Populate cache from DB results
        for file in db_files:
            self.file_cache.add_file_to_cache(
                user_id=user_id,
                file_name=file.file_name,
                file_data=FileData.model_validate(file),
            )

        # Return updated cache contents
        return list(self.file_cache.get_cached_files(user_id=user_id).values())

    def get_files_metadata(self, db: Session, user_id: int) -> List[FileData]:
        """Fetch metadata of user files directly from the database.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user.

        Returns:
            List[FileData]: File metadata objects.
        """
        db_files = FileRepository.get_files(db=db, user_id=user_id)
        return [FileData.model_validate(file) for file in db_files]

    def upload_file(
        self,
        db: Session,
        file: UploadFile,
        user_id: str,
        file_name: str,
        file_description: str,
        storage_type: StorageType = StorageType.LOCAL,
    ) -> None:
        """Upload a file, storing it in backend, DB, and cache.

        Args:
            db (Session): Active database session.
            file (UploadFile): File object to upload.
            user_id (str): ID of the uploading user.
            file_name (str): Desired name for the file.
            file_description (str): Description of the file.
            storage_type (StorageType, optional): Storage backend type.
                Defaults to local storage.
        """

        # Select storage backend
        storage = self.STORAGE_MAPPING[storage_type]

        # Save file to storage, get URI and auto-generated summary
        storage_uri, data_summary = storage.upload_file(
            file_name=file_name, user_id=user_id, file=file
        )

        # Build DB record
        file_create = FileCreate(
            user_id=user_id,
            file_name=file_name,
            file_description=file_description,
            storage_type=storage_type,
            storage_uri=storage_uri,
            data_summary=data_summary,
        )

        # Build cache record
        file_data = FileData(
            file_name=file_name,
            file_description=file_description,
            data_summary=data_summary,
            storage_uri=storage_uri,
        )

        # Store in DB
        FileRepository.create_file(db=db, file_data=file_create)

        # Store in cache
        self.file_cache.add_file_to_cache(
            user_id=user_id, file_name=file_name, file_data=file_data
        )

    def delete_file(
        self,
        db: Session,
        user_id: int,
        file_name: str,
        storage_type: StorageType = StorageType.LOCAL,
    ):
        """Delete a user file from storage, database, and cache.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user.
            file_name (str): Name of the file to delete.
            storage_type (StorageType, optional): Storage backend type.
                Defaults to local storage.

        Raises:
            HTTPException: If the file does not exist.
        """
        # Verify file exists in DB
        db_file = FileRepository.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_name}' does not exist for user.",
            )

        # Remove from DB
        FileRepository.delete_file(db=db, user_id=user_id, file_name=file_name)

        # Remove from cache
        self.file_cache.delete_file_from_cache(user_id=user_id, file_name=file_name)

        # Remove physical file from storage
        storage = self.STORAGE_MAPPING[storage_type]
        storage.delete_file(storage_uri=db_file.storage_uri)


# Instantiate a global file service with the configured file cache
file_service = FileService(file_cache)
