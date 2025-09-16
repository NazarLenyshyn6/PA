"""..."""

import base64
from io import StringIO
from typing import List

import pandas as pd
from langchain_core.messages import HumanMessage

from agents.builder import agent
from agents.tools.registry import tools_description

# Predefined list of dependencies that the agent may use when executing dynamic code
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
]


class AgentService:
    @staticmethod
    def _get_dfs(data: List[str]) -> List[pd.DataFrame]:
        """..."""
        dfs = []
        for df in data:
            csv_bytes = base64.b64decode(data)
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
        dfs = cls._get_dfs(data)
        variables = {file_name: df for file_name, df in zip(file_names, dfs)}
        return agent.invoke(
            {
                "question": question,
                "tools": tools_description,
                "agent_scratchpad": [HumanMessage(content=question)],
                "variables": variables,
                "data_summaries": data_summaries,
                "dependencies": dependencies,
                "current_debugging_attempt": 1,
                "max_debugging_attemps": 5,
            }
        )
