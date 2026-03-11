"""Proposal Extraction Agent."""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import PRODUCTION_CONFIG, REASONING_MODEL
from .tools import read_presentation_content

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "proposal_extraction_agent_v1.txt"
with open(PROMPT_FILE, encoding="utf-8") as f:
    PROMPT = f.read()

proposal_extraction_agent = LlmAgent(
    name="proposal_extraction_agent",
    model=REASONING_MODEL,
    description="Analyzes presentations and extracts core business proposal details.",
    instruction=PROMPT,
    tools=[read_presentation_content],
    output_key="proposal_extraction_agent_context",
    generate_content_config=PRODUCTION_CONFIG,
)
