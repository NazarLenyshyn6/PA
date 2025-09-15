"""
...
"""

from typing_extensions import override
from typing import ClassVar, Dict
from pathlib import Path

import pandas as pd

from loaders.base import BaseLoader


class LocalLoader(BaseLoader):
    """
    ...
    """

    _data_loaders: ClassVar[Dict] = {"csv": pd.read_csv}

    @override
    @classmethod
    def load(cls, storage_uri: str) -> pd.DataFrame:
        """
        ...
        """

        path = Path(storage_uri.replace("local://", ""))
        extension = path.suffix.lstrip(".").lower()
        data_loader = cls._data_loaders.get(extension)
        if not data_loader:
            raise ValueError(f"Unsupported file extension: {extension}")
        df = data_loader(path)
        return df
