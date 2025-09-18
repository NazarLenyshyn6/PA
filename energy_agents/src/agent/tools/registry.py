"""
This module defines the available tools for the agent, creates a mapping
from tool names to tool objects, and compiles a description of all tools.
"""

from agent.tools.insight import insight_agent
from agent.tools.ml_agent import ml_agent


# List of all available agent tools
tools = [insight_agent, ml_agent]

# Create a mapping from tool names to their corresponding tool objects
tools_mapping = {tool.name: tool for tool in tools}

# Generate a human-readable description of all tools
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
