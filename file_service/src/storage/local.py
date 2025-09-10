"""
Local file storage backend.

This module implements a `LocalStorage` class for storing files
on the local filesystem. It extends `BaseStorage` and provides
methods for uploading and deleting files, along with automatic
validation.

Files are namespaced per user and stored under the configured
local storage path. URIs returned use the `local://` scheme.
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
    Local filesystem storage implementation of `BaseStorage`.

    Attributes:
        base_path: Base directory for storing files locally.
    """

    base_path: Path = Path(settings.local_storage.LOCAL_STORAGE_PATH)

    @classmethod
    def _initialize_storage(cls) -> None:
        """
        Ensure the local storage directory exists.

        Creates the base storage directory if it does not exist,
        including any necessary parent directories.
        """
        if not cls.base_path.exists():
            cls.base_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    @override
    def upload_file(cls, user_id: int, file_name: str, file: UploadFile) -> str:
        """
        Upload a file to local storage.

        Args:
            user_id: ID of the user uploading the file.
            file_name: Name of the file (without extension).
            file: Uploaded file object from FastAPI.

        Raises:
            UnsupportedFileExtensionError: If the file extension is not allowed.
            OSError: If writing the file fails.

        Returns:
            str: - URI of the stored file (using "local://" scheme)
        """
        # Ensure the storage folder exists
        cls._initialize_storage()

        # Extract and validate file extension
        file_extension = cls.get_file_extension(file.filename)
        cls.validate_file_extension(file_extension)
        path = cls.base_path / f"{user_id}_{file_name}.{file_extension}"

        # Write file content to disk
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return the URI
        return f"local://{path}"

    @staticmethod
    @override
    def delete_file(storage_uri: str) -> None:
        """
        Delete a file from local storage.

        Args:
            storage_uri: URI of the file to delete (expects "local://" scheme).

        Raises:
            FileNotFoundError: If the file does not exist.
            OSError: If file deletion fails.
        """
        path = Path(storage_uri.replace("local://", ""))
        if path.exists():
            path.unlink()
