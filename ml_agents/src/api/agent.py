"""
Agent API router.

Defines endpoints for interacting with the agent, including sending questions
and receiving analysis reports and visualizations.
"""

from fastapi import APIRouter

from schemas.agent import AgentRequest
from services.agent import AgentService

# from services.agent import AgentService

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat")
def chat(agent_request: AgentRequest):
    """Handle chat requests to the agent.

    Receives a question and associated CSV data, invokes the agent, and
    returns the analysis report and optional visualization.
    """
    agent_response = AgentService.chat(
        question=agent_request.question,
        file_names=agent_request.file_names,  # Map file names to dataframes
        data_summaries=agent_request.data_summaries,  # Data summaries for agent guidance
        data=agent_request.data,  # Base64-encoded CSV data
    )
    return {
        "visualization": agent_response["visualization"],
        "analysis_report": agent_response["analysis_report"],
    }
