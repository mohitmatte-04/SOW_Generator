"""SOW Generation Agent."""

from pathlib import Path


from google.adk.agents import LlmAgent

from .config import REASONING_MODEL, SOW_GENERATION_CONFIG
from .tools import generate_sow_document, read_gcs_json

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "sow_generation_agent_v1.txt"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT = f.read()

sow_generation_agent = LlmAgent(
    name="sow_generation_agent",
    model=REASONING_MODEL,
    description=(
        "Expands proposal details into professional SOW sections "
        "and generates the document."
    ),
    instruction=PROMPT,
    tools=[generate_sow_document, read_gcs_json],
    output_key="sow_generation_agent_result",
    generate_content_config=SOW_GENERATION_CONFIG,
)

