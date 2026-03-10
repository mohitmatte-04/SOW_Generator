"""Main agent entry point for SOW Generator."""

from google.adk.agents import Agent
from .sow_pipeline import sow_pipeline

# Export the root agent
root_agent: Agent = sow_pipeline

__all__ = ["root_agent"]
