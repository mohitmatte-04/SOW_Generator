"""Extractor Agent — extracts SOW data from PPTX presentations in GCS.
This agent uses a two-tool workflow:

1. convert_slides_to_pdf: Downloads PPTX from GCS and converts to PDF using Google Slides API

PDF artifacts are managed via callbacks:
- After-tool callback: Saves PDF as artifact using ADK's artifact service
- Before-tool callback: Loads PDF artifact for extraction

The agent operates as an independent module in a SequentialAgent pipeline.
"""


from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

from .config import PRODUCTION_CONFIG, REASONING_MODEL
from .extractor_callbacks import after_tool_callback, before_model_callback
from .tools.convert_slides_to_pdf import convert_slides_to_pdf


class ProjectMetadata(BaseModel):
    title: str
    customer_name: str
    msa_date: str


class Assumptions(BaseModel):
    project_assumptions: str | list[dict]
    technical_assumptions: str | list[dict]


class CustomerRolesResponsibilities(BaseModel):
    project_roles: str | list[dict]
    responsibilities: str | list[dict]


class ProjectGovernance(BaseModel):
    location: str
    raid_management: str | list[dict]
    communication_plan: str | list[dict]


class ProjectSchedule(BaseModel):
    timeline: str | list[dict]
    phases: str | list[dict]


class SowContent(BaseModel):
    opportunity: str
    solution_overview: str | list[dict]
    strategy_architecture: str | list[dict] = Field(
        alias="strategy/architecture",
        description="High-level technical solution and approach summary"
    )
    activities: str | list[dict]
    deliverables: str | list[dict]
    out_of_scope: str | list[dict]
    limitations: str | list[dict]
    success_criteria: str | list[dict]
    assumptions: Assumptions
    customer_roles_responsibilities: CustomerRolesResponsibilities
    project_governance: ProjectGovernance
    project_schedule: ProjectSchedule
    payment_schedule: str | list[dict]
    add_appendix_details: str | list[dict]


class ExtractorSchema(BaseModel):
    project_metadata: ProjectMetadata
    sow_content: SowContent
    category: Literal[
        "snowflake_migration",
        "eagle_assessment_eagle_modernization",
        "datawarehouse_modernization",
        "teradata_migration",
        "teradata_migration_etl",
        "teradata_migration_etl_bi",
        "hadoop_migration"
    ] = Field(
        description=(
            "The category that best describes this proposal based on the content, "
            "technologies mentioned, and scope of work. Analyze the proposal to determine "
            "if it involves: Snowflake migration, Eagle assessment/modernization, "
            "Data warehouse modernization, Teradata migration (general), "
            "Teradata migration with ETL focus, Teradata migration with ETL and BI components, "
            "or Hadoop migration."
        )
    )

# Load prompt

PROMPT_FILE = Path(__file__).parent / "prompts" / "extractor_agent_v6.md"

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
    # output_schema=ExtractorSchema,
    # generate_content_config=PRODUCTION_CONFIG,
    # after_tool_callback=after_tool_callback,
    before_model_callback=before_model_callback,
)

