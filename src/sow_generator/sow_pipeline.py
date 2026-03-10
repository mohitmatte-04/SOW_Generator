"""SOW Generator Sequential Pipeline."""

from google.adk.agents import SequentialAgent
from .proposal_extraction_agent import proposal_extraction_agent
from .sow_generation_agent import sow_generation_agent

sow_pipeline = SequentialAgent(
    name="sow_pipeline",
    description="Orchestrates the extraction of proposal details and generation of the Statement of Work.",
    sub_agents=[
        proposal_extraction_agent,
        sow_generation_agent,
    ],
)
