"""..."""

from agent.tools.talk2db import talk2db_agent


# Avaliables tools
tools = [talk2db_agent]

# Avaliable tools mapping
tools_mapping = {tool.name: tool for tool in tools}

# Tools description
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
