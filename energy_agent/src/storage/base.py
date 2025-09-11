"""
...
"""

from typing import ClassVar, Set, Dict
from abc import ABC, abstractmethod
from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from core.exceptions.file import UnsupportedFileExtensionError


class BaseStorage(ABC):
    """
    ...
    """

    allowed_file_extensions: ClassVar[Set[str]] = {"csv"}
    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @classmethod
    def _load_data(cls, file: UploadFile, extension: str) -> pd.DataFrame:
        """
        ...
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
        ...
        """
        return Path(path).suffix.lstrip(".").lower()

    @classmethod
    def validate_file_extension(cls, file_extension: str) -> None:
        """
        ...
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
        ...
        """
        ...

    @staticmethod
    @abstractmethod
    def delete_file(storage_uri: str) -> None:
        """
        ...
        """
        ...
