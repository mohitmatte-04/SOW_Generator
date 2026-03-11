"""SOW Generation Agent."""

from pathlib import Path
from google.adk.agents import LlmAgent
from .config import REASONING_MODEL, PRODUCTION_CONFIG
from .tools import read_from_gcs, generate_sow_document

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "sow_generation_agent_v1.md"
with open(PROMPT_FILE, encoding="utf-8") as f:
    PROMPT = f.read()

sow_generation_agent = LlmAgent(
    name="sow_generation_agent",
    model=REASONING_MODEL,
    description="Reads proposal context and SOW template from GCS, uses LLM intelligence to generate professional SOW content, and merges into the template.",
    instruction=PROMPT,
    tools=[read_from_gcs, generate_sow_document],
    output_key="sow_generation_agent_result",
    generate_content_config=PRODUCTION_CONFIG,
)
