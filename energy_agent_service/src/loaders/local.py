"""
Local file data loader module.

This module provides a concrete implementation of `BaseLoader` for loading
tabular data from local files. Currently, it supports CSV files and can be
extended to support additional formats by updating the `_data_loaders` mapping.
"""

from typing_extensions import override
from typing import ClassVar, Dict
from pathlib import Path

import pandas as pd

from loaders.base import BaseLoader


class LocalLoader(BaseLoader):
    """
    Data loader for local file storage.

    This loader reads tabular data from local files and returns it as
    a Pandas DataFrame. Supported file formats are defined in the
    `_data_loaders` class variable.

    Attributes:
        _data_loaders: Mapping of file extensions to
            Pandas loader functions (e.g., "csv" -> `pd.read_csv`).
    """

    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @override
    @classmethod
    def load(cls, storage_uri: str) -> pd.DataFrame:
        """
        Load a local file into a Pandas DataFrame.

        Parameters:
            storage_uri: URI pointing to the local file. The prefix
                `local://` will be stripped to obtain the file path.

        Raises:
            ValueError: If the file extension is not supported.

        Returns:
            pd.DataFrame: Data read from the local file.
        """

        path = Path(storage_uri.replace("local://", ""))
        extension = path.suffix.lstrip(".").lower()
        data_loader = cls._data_loaders.get(extension)
        if not data_loader:
            raise ValueError(f"Unsupported file extension: {extension}")
        df = data_loader(path)
        return df
