"""
Abstract base class for data loaders.

Defines a common interface for loading datasets from different storage backends.
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    """Abstract loader class for datasets."""

    @abstractmethod
    def load(self, storage_uri: str) -> pd.DataFrame:
        """Load data from a given storage URI into a Pandas DataFrame.

        Args:
            storage_uri (str): URI or path to the data source.

        Returns:
            pd.DataFrame: Loaded dataset.
        """
        ...
