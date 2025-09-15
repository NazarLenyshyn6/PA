"""..."""

import json

from langchain_core.messages import HumanMessage

from agent.builder import agent
from agent.tools.registry import tools_description


class AgentService:
    @classmethod
    async def stream(
        cls,
        question: str,
        structured_data_info: str,
        unstructured_data_info: str,
        tools: str = tools_description,
    ) -> None:
        """..."""
        async for chunk in agent.astream_events(
            {
                "question": question,
                "structured_data_info": structured_data_info,
                "unstructured_data_info": unstructured_data_info,
                "tools": tools,
                "agent_scratchpad": [HumanMessage(content=question)],
            }
        ):
            if chunk["event"] == "on_chat_model_stream":
                data = chunk["data"]["chunk"].content[0].get("text", "")
                yield f"data: {json.dumps({'type': 'text', 'data': f"{data}"})}\n\n"
