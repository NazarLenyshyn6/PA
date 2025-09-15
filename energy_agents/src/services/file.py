"""..."""

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
    """..."""

    file_cache: FileCacheManager

    STORAGE_MAPPING: ClassVar[Dict[StorageType, BaseStorage]] = {
        StorageType.LOCAL: LocalStorage
    }

    def get_files(
        self, db: Session, user_id: int, storage_type: StorageType = StorageType.LOCAL
    ) -> List[FileData]:

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

        # Return updated cache
        return list(self.file_cache.get_cached_files(user_id=user_id).values())

    def get_files_metadata(self, db: Session, user_id: int) -> List[FileData]:
        """..."""
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
        """..."""

        # Select storage backend
        storage = self.STORAGE_MAPPING[storage_type]

        # Save file to storage, get its URI and summary
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
        """
        ...
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
