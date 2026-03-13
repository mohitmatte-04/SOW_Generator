"""SOW Generator Sequential Pipeline."""

from google.adk.agents import SequentialAgent

from .extractor_agent import extractor_agent
from .sow_generation_agent import sow_generation_agent

sow_pipeline = SequentialAgent(
    name="sow_pipeline",
    description=(
        "Orchestrates the extraction of proposal details "
        "and generation of the Statement of Work."
    ),
    sub_agents=[
        extractor_agent,
        sow_generation_agent,
    ],
)
