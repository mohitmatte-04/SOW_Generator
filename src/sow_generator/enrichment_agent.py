"""Enrichment Agent — enriches extracted SOW data using golden templates.

This agent is the heart of the SOW generation system. It receives:
1. Extracted data from the extractor agent (may be incomplete)
2. Golden template JSON (loaded by before_model_callback based on category)

The agent intelligently identifies what's missing or incomplete in the extracted
data and enriches it using the golden template to create a comprehensive SOW structure.
"""

from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

from .config import REASONING_MODEL
from .enrichment_callbacks import before_enrichment_model_callback


class ProjectMetadata(BaseModel):
    title: str
    customer_name: str
    msa_date: str


class SowContent(BaseModel):
    opportunity: str
    solution_overview: str | list[dict]
    activities: str | list[dict]
    deliverables: str | list[dict]
    out_of_scope: str | list[dict]
    limitations: str | list[dict]
    success_criteria: str | list[dict]
    technical_assumptions: str | list[dict]
    payment_schedule: str | list[dict]
    add_appendix_details: str | list[dict]


class EnrichmentSchema(BaseModel):
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
            "The SOW category that matches the golden template used for enrichment. "
            "This should be the same category from the extractor agent output."
        )
    )


# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "enrichment_agent_v3.md"

with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

enrichment_agent = LlmAgent(
    name="enrichment_agent",
    model=REASONING_MODEL,
    description=(
        "Enriches extracted SOW data by intelligently identifying and filling "
        "missing information using category-specific golden templates. This is "
        "the heart of the SOW generation pipeline."
    ),
    instruction=PROMPT,
    tools=[],
    output_key="enrichment_agent_result",
    output_schema=EnrichmentSchema,
    before_model_callback=before_enrichment_model_callback,
)
