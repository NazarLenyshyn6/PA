"""
...
"""

import pandas as pd


def dataset_summarization(df: pd.DataFrame) -> str:
    """
    ...
    """

    rows, columns = df.shape
    feature_lines = "\n".join(
        f"- **{col}**: `{dtype}`" for col, dtype in df.dtypes.items()
    )

    return (
        f"The dataset has **{rows} rows** and **{columns} columns**.\n\n"
        f"It contains the following features:\n\n{feature_lines}"
    )
