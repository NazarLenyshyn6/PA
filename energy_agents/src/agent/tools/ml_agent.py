"""
This module defines a specialized tool for analyzing structured data
using an external MLAgent service.
"""

from typing import Annotated
import base64

import requests
from langchain_core.tools import tool, InjectedToolArg
from langchain.schema import AIMessage
from langchain.schema.runnable import RunnableLambda

from core.config import settings
from agent.state import AgentState
from loaders.local import LocalLoader


@tool
def ml_agent(task: str, state: Annotated[AgentState, InjectedToolArg]):
    """
    Use this tool when the user asks any question related to data analysis, data visualization, predictions, or any other ML tasks on structured data.

    Args:
        task: The task the ML agent must take into consideration and output results for. Strictly declarative, with a clear definition of what must be done.
    """
    try:
        encoded_data_list = []

        # Iterate over all stored data files and encode them for the ML agent
        for storage_uri in state["storage_uris"]:
            # Load data as DataFrame
            df = LocalLoader.load(storage_uri)

            # Convert DataFrame to CSV and then to bytes
            csv_bytes = df.to_csv(index=False).encode("utf-8")

            # Encode CSV bytes to Base64 for transmission
            encoded_data = base64.b64encode(csv_bytes).decode("utf-8")
            encoded_data_list.append(encoded_data)

        # Send task and data to the external ML agent service
        response = requests.post(
            url=settings.external_services.MLAgent,
            json={
                "question": task,
                "file_names": state["file_names"],
                "data_summaries": state["structured_data_info"],
                "data": encoded_data_list,
            },
        ).json()

        analysis_report, visualization = (
            response["analysis_report"],
            response["visualization"],
        )

        # If a visualization exists, display it using RunnableLambda
        if visualization:
            visualization_display_model = RunnableLambda(
                lambda _: AIMessage(
                    content=visualization, additional_kwargs={}, response_metadata={}
                )
            )
            visualization_display_model.invoke(
                "...", config={"metadata": {"image": True}}
            )

        # Return the textual analysis report
        return analysis_report

    except Exception:
        return "Failed"
