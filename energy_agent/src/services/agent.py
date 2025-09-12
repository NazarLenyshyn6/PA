"""..."""

import json

from agent.workflow import workflow
from agent.tools.registry import tools_description


class AgentService:
    @classmethod
    async def stream(cls, question: str, storage_uri: str) -> None:
        """..."""
        async for chunk in workflow.astream_events(
            {
                "tools": tools_description,
                "question": question,
                "storage_uri": storage_uri,
            }
        ):
            print(chunk)
            if chunk["event"] == "on_chat_model_stream":
                stream = chunk["metadata"].get("stream", True)
                if stream:
                    data = chunk["data"]["chunk"].text
                    yield f"data: {json.dumps({'type': 'text', 'data': data})}\n\n"

            # elif chunk["event"] == "on_tool_end":
            #     yield chunk["data"]["output"]

            elif chunk["event"] == "on_tool_end":
                output = chunk["data"]["output"]
                if hasattr(output, "__aiter__"):
                    async for sub_chunk in output:
                        yield sub_chunk
                else:
                    yield output
