"""
Base storage interface for file handling.

This module defines an abstract base class `BaseStorage` for file storage
implementations. It provides common utilities such as file validation,
loading. Specific storage backends (local filesystem,
cloud storage, etc.) should extend this class and implement the
`upload_file` and `delete_file` methods.

It also integrates with the application's custom exceptions to enforce
supported file types.
"""

from typing import ClassVar, Set, Dict
from abc import ABC, abstractmethod
from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from core.exceptions import UnsupportedFileExtensionError


class BaseStorage(ABC):
    """
    Abstract base class for file storage backends.

    Attributes:
        allowed_file_extensions: Set of allowed file extensions for uploads.
        _data_loaders: Mapping of file extensions to pandas data loader functions.
    """

    allowed_file_extensions: ClassVar[Set[str]] = {"csv"}
    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @classmethod
    def _load_data(cls, file: UploadFile, extension: str) -> pd.DataFrame:
        """
        Load file contents into a pandas DataFrame based on its extension.

        Args:
            file: Uploaded file object from FastAPI.
            extension: File extension (e.g., "csv").

        Raises:
            KeyError: If no loader is defined for the given extension.

        Returns:
            pd.DataFrame: Loaded data from the file.
        """
        file.file.seek(0)
        contents = file.file.read()
        file_like = BytesIO(contents)
        data_loader = cls._data_loaders[extension]
        df = data_loader(file_like)
        return df

    @staticmethod
    def get_file_extension(path: str) -> str:
        """
        Extract and normalize the file extension from a file path.

        Args:
            file_path: Path or filename.

        Returns:
            str: Lowercased file extension without the leading dot.
        """
        return Path(path).suffix.lstrip(".").lower()

    @classmethod
    def validate_file_extension(cls, file_extension: str) -> None:
        """
        Validate that a file extension is allowed.

        Args:
            file_extension: File extension to validate.

        Raises:
            UnsupportedFileExtensionError: If the extension is not supported.
        """
        if file_extension not in cls.allowed_file_extensions:
            allowed = ", ".join(sorted(cls.allowed_file_extensions))
            raise UnsupportedFileExtensionError(
                f"Invalid file extension: .{file_extension}. Allowed: {allowed}"
            )

    @classmethod
    @abstractmethod
    def upload_file(cls, user_id: int, file_name: str, file: UploadFile) -> str:
        """
        Upload a file to the storage backend.

        Args:
            user_id: ID of the user uploading the file.
            file_name: Name of the file.
            file: Uploaded file object.

        Raises:
            Exception: Backend-specific errors if upload fails.

        Returns:
            str: URI or path where the file is stored.
        """
        ...

    @staticmethod
    @abstractmethod
    def delete_file(storage_uri: str) -> None:
        """
        Delete a file from the storage backend.

        Args:
            storage_uri: URI or path of the file to delete.

        Raises:
            Exception: Backend-specific errors if deletion fails.
        """
        ...
