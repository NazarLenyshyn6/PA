"""..."""

from typing import Annotated

from langchain_core.tools import tool, InjectedToolArg

from agents.workflow.builder import workflow
from agents.state import AgentState


@tool
def action_engine(
    generation_instruction: str, state: Annotated[AgentState, InjectedToolArg]
):
    """
    Tool used to gain knowledge based on instruction

    Args:
        generation_instruction: Very detailed structured instruction what must be done to gaind requeid infomraiotn on current step,
        This instruction will be provided for code generation, so must be very structured and include all substeps required to
        gain all information needed.
        Generation instruction never include data loading. All data is already avalibel, so always skip that part.
        It is mandatory and any data ingestoin planing will break all pipeline.
    """
    # Set generation instruction
    state["generation_instruction"] = generation_instruction
    return workflow.invoke(state)
