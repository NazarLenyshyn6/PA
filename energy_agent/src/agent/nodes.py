"""..."""

from langchain_core.prompts import ChatPromptTemplate

from agent.tools.registry import tools_description, tools_mapping
from agent.state import AgentState
from agent.chat_models import model_with_tools


def tool_request(state: AgentState):
    """..."""
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """ROLE
You are a routing agent.

TASK
Select exactly one tool from the list below that is the most relevant to the user’s request.

TOOLS AVAILABLE
{tools}

ROUTING RULES
1. Always select exactly one tool.
2. Do not generate answers yourself — only pick a tool.
3. If the request is unclear, pick the closest matching tool.
""",
            ),
            ("human", "{question}"),
        ]
    )
    chain = prompt_template | model_with_tools
    tool_call_message = chain.invoke(
        {"tools": tools_description, "question": state["question"]},
        config={"metadata": {"stream": False}},
    )
    return {"tool_call_message": tool_call_message}


async def tool_execute(state: AgentState):
    """..."""

    # Get tool call
    tool_call = state["tool_call_message"].tool_calls[0]

    # Get actual tool
    tool = tools_mapping[tool_call["name"]]

    # Invoke
    await tool.ainvoke({"state": state})
