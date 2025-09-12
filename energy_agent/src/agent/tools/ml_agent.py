"""..."""

from typing import Annotated
import base64

import httpx
from langchain_core.tools import tool, InjectedToolArg

from loaders.local import LocalLoader
from core.config import settings
from agent.state import AgentState


@tool
async def ml_agent(state: Annotated[AgentState, InjectedToolArg]):
    """
    Use this tool when the user asks any question related to machine learning and data visualization, it stays top priority for analysis and visualization tasks.
    It is responsible for handling requests to analyze, visualize and predict data.
    """

    # Load data
    df = LocalLoader.load(state["storage_uri"])

    # Convert DataFrame to CSV bytes
    csv_str = df.to_csv(index=False)
    csv_bytes = csv_str.encode("utf-8")

    # Encode as Base64
    encoded_data = base64.b64encode(csv_bytes).decode("utf-8")

    # Create payload
    payload = {"question": state["question"], "data": encoded_data}

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST", settings.external_services.MLAgent, json=payload
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
