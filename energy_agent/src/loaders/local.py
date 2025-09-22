"""
Local file loader for structured datasets.

Implements BaseLoader for loading CSV files from local storage URIs.
"""

from typing_extensions import override
from typing import ClassVar, Dict
from pathlib import Path

import pandas as pd

from loaders.base import BaseLoader


class LocalLoader(BaseLoader):
    """Loader for datasets stored locally."""

    # Mapping of file extensions to Pandas loaders
    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @override
    @classmethod
    def load(cls, storage_uri: str) -> pd.DataFrame:
        """Load a dataset from a local URI into a Pandas DataFrame.

        Args:
            storage_uri (str): URI of the local file (prefixed with "local://").

        Raises:
            ValueError: If the file extension is unsupported.

        Returns:
            pd.DataFrame: Loaded dataset.
        """
        # Convert URI to local file path
        path = Path(storage_uri.replace("local://", ""))
        extension = path.suffix.lstrip(".").lower()

        # Get corresponding Pandas loader
        data_loader = cls._data_loaders.get(extension)
        if not data_loader:
            raise ValueError(f"Unsupported file extension: {extension}")
        df = data_loader(path)

        # Load and return DataFrame
        return df
