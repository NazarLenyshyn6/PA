"""
Abstract base class for file storage backends.

Defines the common interface and utility methods for managing
file uploads, validation, and summarization across different
storage implementations.
"""

from typing import ClassVar, Set, Dict
from abc import ABC, abstractmethod
from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from core.exceptions import UnsupportedFileExtensionError


class BaseStorage(ABC):
    """Abstract base class for storage backends.

    Subclasses must implement methods to upload and delete files.
    """

    # Allowed file extensions for upload
    allowed_file_extensions: ClassVar[Set[str]] = {"csv"}

    # Mapping of file extensions to corresponding Pandas loaders
    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @classmethod
    def _load_data(cls, file: UploadFile, extension: str) -> pd.DataFrame:
        """Load file data into a Pandas DataFrame.

        Args:
            file (UploadFile): File to load.
            extension (str): File extension to determine the loader.

        Returns:
            pd.DataFrame: Parsed dataset.
        """
        file.file.seek(0)
        contents = file.file.read()
        file_like = BytesIO(contents)

        # Use the appropriate loader based on extension
        data_loader = cls._data_loaders[extension]
        df = data_loader(file_like)

        return df

    @staticmethod
    def get_file_extension(path: str) -> str:
        """Extract file extension from a path.

        Args:
            path (str): File path or name.

        Returns:
            str: Lowercased file extension without the dot.
        """
        return Path(path).suffix.lstrip(".").lower()

    @classmethod
    def validate_file_extension(cls, file_extension: str) -> None:
        """Validate whether a file extension is supported.

        Args:
            file_extension (str): Extension to validate.

        Raises:
            UnsupportedFileExtensionError: If the extension is not allowed.
        """
        if file_extension not in cls.allowed_file_extensions:
            allowed = ", ".join(sorted(cls.allowed_file_extensions))
            raise UnsupportedFileExtensionError(
                f"Invalid file extension: .{file_extension}. Allowed: {allowed}"
            )

    @classmethod
    def summarize_file(cls, file: UploadFile, extension: str) -> str:
        """Generate a human-readable summary of a dataset.

        Args:
            file (UploadFile): Dataset file to summarize.
            extension (str): Extension used to parse the dataset.

        Returns:
            str: Summary including dataset size and features.
        """
        # Load dataset into DataFrame
        df = cls._load_data(file=file, extension=extension)
        rows, columns = df.shape
        feature_lines = "\n".join(
            f"- **{col}**: `{dtype}`" for col, dtype in df.dtypes.items()
        )

        return (
            f"The dataset has **{rows} rows** and **{columns} columns**.\n\n"
            f"It contains the following features:\n\n{feature_lines}"
        )

    @classmethod
    @abstractmethod
    def upload_file(cls, user_id: int, file_name: str, file: UploadFile) -> str:
        """Upload a file to the storage backend.

        Args:
            user_id (int): ID of the user uploading the file.
            file_name (str): Name to assign to the file.
            file (UploadFile): File object to upload.

        Returns:
            str: URI of the stored file.
        """
        ...

    @staticmethod
    @abstractmethod
    def delete_file(storage_uri: str) -> None:
        """Delete a file from the storage backend.

        Args:
            storage_uri (str): URI of the file to delete.
        """
        ...
