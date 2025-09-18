"""
This module defines the available tools for the agent, creates a mapping
from tool names to tool objects, and compiles a description of all tools.
"""

from agent.tools.action_engine import action_engine


# List of all available agent tools
tools = [action_engine]

# Create a mapping from tool names to their corresponding tool objects
tools_mapping = {tool.name: tool for tool in tools}

# Generate a human-readable description of all tools
tools_description = "\n\n".join(f"* {tool.name}: {tool.description}" for tool in tools)
