"""
...
"""

import json
import base64
from io import StringIO
from typing import List


import pandas as pd


from agent.workflow import workflow
from utils import dataset_summarization


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
    def _get_df(data: str) -> pd.DataFrame:
        csv_bytes = base64.b64decode(data)
        csv_str = csv_bytes.decode("utf-8")
        return pd.read_csv(StringIO(csv_str))

    @classmethod
    async def stream(cls, question: str, data: str, dependencies: List = dependencies):
        df = cls._get_df(data)
        code_variables = {"df": df}
        dataset_summary = dataset_summarization(df)

        async for chunk in workflow.astream_events(
            {
                "question": question,
                "dataset_summary": dataset_summary,
                "dependencies": dependencies,
                "code_variables": code_variables,
            },
        ):
            # Handle image outputs when the chain ends and output exists
            if (
                chunk["metadata"].get("image", False)
                and chunk["event"] == "on_chain_end"
                and chunk["data"].get("output", False)
            ):
                data = chunk["data"]["output"].content
                yield f"data: {json.dumps({'type': 'image', 'data': data})}\n\n"

            # Handle text streaming from the chat model
            if chunk["event"] == "on_chat_model_stream":
                stream = chunk["metadata"].get("stream", True)
                if stream:
                    data = chunk["data"]["chunk"].content
                    yield f"data: {json.dumps({'type': 'text', 'data': data})}\n\n"
