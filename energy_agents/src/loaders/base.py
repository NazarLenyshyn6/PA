"""
...
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    """
    ...
    """

    @abstractmethod
    def load(self, storage_uri: str) -> pd.DataFrame:
        """
        ...
        """
        ...
