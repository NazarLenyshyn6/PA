"""..."""

from agent.tools.talk2db import talk2db_agent
from agent.tools.ml_agent import ml_agent


# Avaliables tools
tools = [ml_agent]

# Avaliable tools mapping
tools_mapping = {tool.name: tool for tool in tools}

# Tools description
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
