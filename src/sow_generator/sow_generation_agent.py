"""SOW Generation Agent."""

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel
from google.adk.agents import LlmAgent

from .config import REASONING_MODEL, SOW_GENERATION_CONFIG
from .tools import generate_sow_document
from .extractor_callbacks import after_agent_callback

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "sow_generation_agent_v7.md"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

class SowPlaceHolderOutput(BaseModel):
    title: str
    customer_name: str
    customer_short_name: str
    customer_name_bold: str
    provision_date: str
    enter_msa_date: str
    opportunity: str
    solution_overview: str | list[dict]
    activities: str | list[dict]
    deliverables: str | list[dict]
    out_of_scope: str | list[dict]
    limitations: str | list[dict]
    success_criteria: str | list[dict]
    technical_assumptions: str | list[dict]
    customer_dependencies: str | list[dict]
    payment_schedule: str | list[dict]
    add_appendix_details: str | list[dict]

class SowGenerationSchema(BaseModel):
    status: Literal['success', 'failed']
    sow_output_path:  Optional[str] = None   # path to the generated SOW document
    error_message: Optional[str] = None   # error message if status is failed

sow_generation_agent = LlmAgent(
    name="sow_generation_agent",
    model=REASONING_MODEL,
    description=(
        "Expands proposal details into professional SOW sections "
        "and generates the document."
    ),
    instruction=PROMPT,
    tools=[],
    output_key="sow_generation_agent_result",
    generate_content_config=SOW_GENERATION_CONFIG,
    output_schema=SowPlaceHolderOutput,
    after_agent_callback=after_agent_callback,
)

