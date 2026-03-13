"""Extractor Agent — extracts SOW data from PPTX presentations in GCS.

This agent accepts a GCS URI to a PPTX file, uses Gemini multimodal
to parse it against the SOW JSON schema, and returns the structured
extraction result. It operates as an independent module that can be
wired into a SequentialAgent pipeline.
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import PRODUCTION_CONFIG, REASONING_MODEL
from .tools.extract_sow_from_presentation import extract_sow_from_presentation

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "extractor_agent_v1.md"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

extractor_agent = LlmAgent(
    name="extractor_agent",
    model=REASONING_MODEL,
    description=(
        "Extracts SOW-relevant structured data from PPTX presentations "
        "stored in Google Cloud Storage using Gemini multimodal analysis."
    ),
    instruction=PROMPT,
    tools=[extract_sow_from_presentation],
    output_key="extractor_agent_context",
    generate_content_config=PRODUCTION_CONFIG,
)
