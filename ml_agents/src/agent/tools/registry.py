"""..."""

from agent.tools.action_engine import action_engine


# Avaliables tools
tools = [action_engine]

# Avaliable tools mapping
tools_mapping = {tool.name: tool for tool in tools}

# Tools description
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
