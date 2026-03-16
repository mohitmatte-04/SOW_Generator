"""Content Validation Agent."""

from pathlib import Path

from google.adk.agents import LlmAgent

from .config import FAST_MODEL, VALIDATION_CONFIG, VALIDATION_QUALITY_THRESHOLD
from .tools import validate_content

# Load prompt
PROMPT_FILE = Path(__file__).parent / "prompts" / "content_validation_agent_v1.md"
with PROMPT_FILE.open(encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

content_validation_agent = LlmAgent(
    name="content_validation_agent",
    model=FAST_MODEL,
    description="Evaluates the quality of generated SOW content and provides feedback.",
    instruction=PROMPT_TEMPLATE.replace("{VALIDATION_QUALITY_THRESHOLD}", str(VALIDATION_QUALITY_THRESHOLD)),
    tools=[validate_content],
    output_key="content_validation_result",
    generate_content_config=VALIDATION_CONFIG,
)
