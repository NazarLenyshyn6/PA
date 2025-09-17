"""..."""

from agent.tools.insight import insight_agent
from agent.tools.ml_agent import ml_agent


# Avaliables tools
tools = [insight_agent, ml_agent]

# Avaliable tools mapping
tools_mapping = {tool.name: tool for tool in tools}

# Tools description
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
