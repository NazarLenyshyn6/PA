"""..."""

from typing import Annotated
import json
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
        data = []
        for storage_uri in state["storage_uris"]:
            # Load data
            df = LocalLoader.load(storage_uri)

            # Convert DataFrame to CSV bytes
            csv_str = df.to_csv(index=False)
            csv_bytes = csv_str.encode("utf-8")

            # Encode as Base64
            encoded_data = base64.b64encode(csv_bytes).decode("utf-8")

            # Append to data
            data.append(encoded_data)

        # Send request to ml agent
        response = requests.post(
            url=settings.external_services.MLAgent,
            json={
                "question": task,
                "file_names": state["file_names"],
                "data_summaries": state["structured_data_info"],
                "data": data,
            },
        ).json()
        analysis_report, visualization = (
            response["analysis_report"],
            response["visualization"],
        )

        print("* analysis report:", analysis_report)
        print("\n* visualization:", visualization)

        # Display visualization if exists, invoke it and retrive fromo on_tool_end
        if visualization:
            visualization_display_model = RunnableLambda(
                lambda _: AIMessage(
                    content=visualization, additional_kwargs={}, response_metadata={}
                )
            )
            visualization_display_model.invoke(
                "...", config={"metadata": {"image": True}}
            )

        # Return textual analysis report back to agent
        return analysis_report

    except Exception:
        return f"data: {json.dumps({'type': 'text', 'data': "Failed"})}\n\n"
