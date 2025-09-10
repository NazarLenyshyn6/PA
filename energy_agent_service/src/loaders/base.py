"""
Abstract data loader module.

This module defines the base interface for loading tabular data into
Pandas DataFrames from arbitrary storage backends. Concrete implementations
should provide the logic for reading data from specific storage URIs.
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    """
    Abstract base class for data loaders.

    Subclasses must implement the `load` method to fetch data from a given
    storage URI and return it as a Pandas DataFrame.

    Methods:
        load(storage_uri: str) -> pd.DataFrame:
            Abstract method to load data from the specified URI.
    """

    @abstractmethod
    def load(self, storage_uri: str) -> pd.DataFrame:
        """
        Load data from the specified storage URI.

        Attributes:
            storage_uri (str): URI or path pointing to the data source.

        Returns:
            pd.DataFrame: Loaded data as a Pandas DataFrame.
        """
        ...
