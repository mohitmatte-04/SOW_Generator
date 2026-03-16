"""Extractor Agent — extracts SOW data from PPTX presentations in GCS.
This agent uses a two-tool workflow:

1. convert_slides_to_pdf: Downloads PPTX from GCS and converts to PDF using Google Slides API

PDF artifacts are managed via callbacks:
- After-tool callback: Saves PDF as artifact using ADK's artifact service
- Before-tool callback: Loads PDF artifact for extraction

The agent operates as an independent module in a SequentialAgent pipeline.
"""


from pathlib import Path
from typing import List

from pydantic import BaseModel
from google.adk.agents import LlmAgent

from .config import PRODUCTION_CONFIG, REASONING_MODEL
from .extractor_callbacks import after_tool_callback, before_model_callback
from .tools.convert_slides_to_pdf import convert_slides_to_pdf


class ProjectMetadata(BaseModel):
    title: str
    customer_name: str
    msa_date: str


class SowContent(BaseModel):
    opportunity: str
    solution_overview: str | list
    activities: str | list
    deliverables: str | list
    out_of_scope: str | list
    limitations: str | list
    success_criteria: str | list
    technical_assumptions: str | list
    payment_schedule: str | list
    add_appendix_details: str | list


class ExtractorSchema(BaseModel):
    project_metadata: ProjectMetadata
    sow_content: SowContent

# Load promp

PROMPT_FILE = Path(__file__).parent / "prompts" / "extractor_agent_v2.md"

with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

extractor_agent = LlmAgent(
    name="extractor_agent",
    model=REASONING_MODEL,
    description=(
        "Extracts SOW-relevant structured data from PPTX presentations "
        "stored in Google Cloud Storage using a two-tool workflow: "
        "PDF conversion via Google Slides API and structured extraction via Gemini."
    ),
    instruction=PROMPT,
    tools=[],
    output_key="extractor_agent_context",
    output_schema=ExtractorSchema,
    # generate_content_config=PRODUCTION_CONFIG,
    after_tool_callback=after_tool_callback,
    before_model_callback=before_model_callback,
)

