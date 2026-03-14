"""Input Parser Agent — extracts Google Drive URL from user input.

This agent parses user input to extract the Google Drive presentation URL
and stores it in session state for downstream agents.
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import FAST_MODEL

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "input_parser_agent_v1.md"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

input_parser_agent = LlmAgent(
    name="input_parser_agent",
    model=FAST_MODEL,
    description=(
        "Parses user input to extract Google Drive presentation URL "
        "and validates the format."
    ),
    instruction=PROMPT,
    output_key="presentation_source",
)
