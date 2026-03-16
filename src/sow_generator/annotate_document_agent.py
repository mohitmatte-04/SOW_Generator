"""Annotate Document Agent."""

from pathlib import Path
from google.adk.agents import LlmAgent
from .config import FAST_MODEL, VALIDATION_CONFIG
from .tools import annotate_sow_document

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "annotate_document_agent_v1.md"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

annotate_document_agent = LlmAgent(
    name="annotate_document_agent",
    model=FAST_MODEL,
    description="Orchestrates document annotation for low-quality sections identified during validation.",
    instruction=PROMPT,
    tools=[annotate_sow_document],
    output_key="annotate_document_result",
    generate_content_config=VALIDATION_CONFIG,
)
