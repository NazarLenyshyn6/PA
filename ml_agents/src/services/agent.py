"""
Agent service module.

Provides the AgentService class to convert base64 CSVs to DataFrames
and interact with agent for analysis and visualization.
"""

import base64
from io import StringIO
from typing import List

import pandas as pd
from langchain_core.messages import HumanMessage

from agent.builder import agent
from agent.tools.registry import tools_description


# Predefined dependencies for dynamic code execution
dependencies = [
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "statsmodels.api",
    "joblib",
    "torch",
    "torchvision",
    "lightgbm",
    "xgboost",
    "optuna",
    "sentence_transformers",
    "gensim==4.3.2",
    "matplotlib.pyplot",
    "seaborn",
    "nltk",
    "spacy",
    "tqdm",
    "networkx",
    "prophet>=1.2",
    "nltk>=3.9",
    "plotly",
]


class AgentService:
    """Service to handle CSV data and interact with the agent."""

    @staticmethod
    def _get_dfs(data: List[str]) -> List[pd.DataFrame]:
        """Convert base64 CSV strings to Pandas DataFrames."""
        dfs = []
        for df in data:
            csv_bytes = base64.b64decode(df)
            csv_str = csv_bytes.decode("utf-8")
            dfs.append(pd.read_csv(StringIO(csv_str)))
        return dfs

    @classmethod
    def chat(
        cls,
        question: str,
        file_names: List[str],
        data_summaries: List[str],
        data: List[str],
    ):
        """Send question and data to agent; return analysis report and visualization."""
        # Convert input data to DataFrames
        dfs = cls._get_dfs(data)

        # Map DataFrames to their corresponding file names
        variables = {file_name: df for file_name, df in zip(file_names, dfs)}

        # Invoke agent with question, data, and dependencies
        response = agent.invoke(
            {
                "question": question,
                "variables": variables,
                "data_summaries": data_summaries,
                "dependencies": dependencies,
                "tools": tools_description,
                "agent_scratchpad": [HumanMessage(content=question)],
                "visualization": None,
                "interactive_visualization": None,
            }
        )

        return {
            "visualization": response["visualization"],
            "interactive_visualization": response["interactive_visualization"],
            "analysis_report": response["agent_scratchpad"][-1].content,
        }
