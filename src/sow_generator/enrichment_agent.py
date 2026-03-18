"""Enrichment Agent — enriches extracted SOW data using golden templates.

This agent is the heart of the SOW generation system. It receives:
1. Extracted data from the extractor agent (may be incomplete)
2. Golden template JSON (loaded by before_model_callback based on category)

The agent intelligently identifies what's missing or incomplete in the extracted
data and enriches it using the golden template to create a comprehensive SOW structure.
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import REASONING_MODEL
from .enrichment_callbacks import before_enrichment_model_callback
from .extractor_agent import ExtractorSchema  # Use same schema as extractor


# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "enrichment_agent_v1.md"

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
    output_schema=ExtractorSchema,  # Same schema as extractor agent
    before_model_callback=before_enrichment_model_callback,
)
