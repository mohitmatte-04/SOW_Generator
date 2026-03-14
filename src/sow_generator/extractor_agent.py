"""Extractor Agent — extracts SOW data from PPTX presentations in GCS.

This agent uses a two-tool workflow:
1. convert_slides_to_pdf: Downloads PPTX from GCS and converts to PDF using Google Slides API
2. extract_sow_from_pdf: Sends PDF to Gemini for structured SOW extraction

PDF artifacts are managed via callbacks:
- After-tool callback: Saves PDF as artifact using ADK's artifact service
- Before-tool callback: Loads PDF artifact for extraction

The agent operates as an independent module in a SequentialAgent pipeline.
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import PRODUCTION_CONFIG, REASONING_MODEL
from .extractor_callbacks import after_convert_callback, before_extract_callback
from .tools.convert_slides_to_pdf import convert_slides_to_pdf
from .tools.extract_sow_from_pdf import extract_sow_from_pdf

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "extractor_agent_v1.md"
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
    tools=[convert_slides_to_pdf, extract_sow_from_pdf],
    output_key="extractor_agent_context",
    generate_content_config=PRODUCTION_CONFIG,
    after_tool_callbacks=[after_convert_callback],
    before_tool_callbacks=[before_extract_callback],
)
