"""SOW Generator Sequential Pipeline."""

from google.adk.agents import SequentialAgent
from .proposal_extraction_agent import proposal_extraction_agent
from .sow_generation_agent import sow_generation_agent
from .content_validation_agent import content_validation_agent
from .annotate_document_agent import annotate_document_agent

sow_pipeline = SequentialAgent(
    name="sow_pipeline",
    description="Orchestrates extraction, generation, validation, and annotation of the Statement of Work.",
    sub_agents=[
        proposal_extraction_agent,
        sow_generation_agent,
        content_validation_agent,
        annotate_document_agent,
    ],
)
