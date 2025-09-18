"""
Service layer for handling agent interactions.

Provides streaming responses from the agent by orchestrating
structured/unstructured data context and tool usage.
"""

import json
from typing import List, Dict

import pandas as pd
from langchain_core.messages import HumanMessage

from agent.builder import agent
from agent.tools.registry import tools_description


class AgentService:
    """Service for streaming responses from the agent."""

    @classmethod
    async def stream(
        cls,
        question: str,
        file_names: List[str],
        structured_data_info: str,
        unstructured_data_info: str,
        storage_uris: List[str],
        tools: str = tools_description,
    ) -> None:
        """Stream agent responses as server-sent events (SSE).

        Args:
            question (str): User query.
            file_names (List[str]): List of associated file names.
            structured_data_info (str): Metadata about structured data.
            unstructured_data_info (str): Metadata about unstructured data.
            storage_uris (List[str]): URIs of related stored files.
            tools (str, optional): Available tool descriptions.
                Defaults to `tools_description`.

        Yields:
            str: Server-sent event (SSE) messages containing either text
            or image data.
        """
        async for chunk in agent.astream_events(
            {
                "question": question,
                "file_names": file_names,
                "structured_data_info": structured_data_info,
                "unstructured_data_info": unstructured_data_info,
                "storage_uris": storage_uris,
                "tools": tools,
                "agent_scratchpad": [HumanMessage(content=question)],
            }
        ):
            # Yield image at the end of a chain
            if (
                chunk["metadata"].get("image", False)
                and chunk["event"] == "on_chain_end"
                and chunk["data"].get("output", False)
            ):
                data = chunk["data"]["output"].content
                yield f"data: {json.dumps({'type': 'image', 'data': data})}\n\n"

            # Stream incremental text outputs
            if chunk["event"] == "on_chat_model_stream":
                data = chunk["data"]["chunk"].content[0].get("text", "")
                yield f"data: {json.dumps({'type': 'text', 'data': f"{data}"})}\n\n"
