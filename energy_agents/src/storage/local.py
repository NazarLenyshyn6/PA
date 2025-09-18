"""
Local file storage backend for handling file uploads and deletions.

Provides functionality to save, summarize, and delete user files
from a configurable local storage directory.
"""

from typing import Tuple
from typing_extensions import override
from pathlib import Path
import shutil

from fastapi import UploadFile

from core.config import settings
from storage.base import BaseStorage


class LocalStorage(BaseStorage):
    """
    Local storage implementation of the BaseStorage interface.

    Files are stored in a directory specified in application settings.
    """

    base_path: Path = Path(settings.local_storage.LOCAL_STORAGE_PATH)

    @classmethod
    def _initialize_storage(cls) -> None:
        """
        Ensure the local storage directory exists.
        """
        if not cls.base_path.exists():
            cls.base_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    @override
    def upload_file(
        cls, user_id: int, file_name: str, file: UploadFile
    ) -> Tuple[str, str]:
        """Upload a file to local storage.

        Args:
            user_id (int): Unique identifier of the user uploading the file.
            file_name (str): Name to assign to the stored file.
            file (UploadFile): File object to be uploaded.

        Returns:
            Tuple[str, str]: A tuple containing:
                - str: URI of the stored file.
                - str: Generated summary of the file.
        """

        # Ensure the storage folder exists
        cls._initialize_storage()

        # Extract and validate file extension
        file_extension = cls.get_file_extension(file.filename)
        cls.validate_file_extension(file_extension)

        # Construct full file path with user_id and provided file_name
        path = cls.base_path / f"{user_id}_{file_name}.{file_extension}"

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Generate a summary of the dataset for quick metadata access
        summary = cls.summarize_file(file, extension=file_extension)

        return f"local://{path}", summary

    @staticmethod
    @override
    def delete_file(storage_uri: str) -> None:
        """Delete a file from local storage.

        Args:
            storage_uri (str): URI of the file to be deleted.
        """
        # Remove local scheme prefix to extract actual file path
        path = Path(storage_uri.replace("local://", ""))

        if path.exists():
            path.unlink()
