"""Callbacks for enrichment agent to load golden template based on category.

This callback handles loading the appropriate golden template JSON file
based on the category extracted by the extractor agent.
"""

import logging
import json
from pathlib import Path
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest, LlmResponse

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Golden templates base directory
GOLDEN_TEMPLATES_DIR = Path(__file__).parent / "golden_templates"


async def before_enrichment_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Before-model callback to load golden template based on category.

    Reads the category from extractor_agent_context in state, finds the
    corresponding golden template JSON file, and adds it to state for
    the enrichment agent to use.

    Args:
        callback_context: ADK CallbackContext for accessing state.
        llm_request: The LLM request that will be sent to the model.

    Returns:
        None to allow the request to proceed, or LlmResponse to short-circuit.
    """
    try:
        # Get the extractor agent output from state
        logger.info("Before enrichment model callback")
        extractor_context = callback_context.state.get("extractor_agent_context")

        if not extractor_context:
            logger.error("No extractor_agent_context found in state")
            return None

        # Extract category from the extractor output
        category = extractor_context.get("category")

        if not category:
            logger.error("No category field found in extractor_agent_context")
            return None

        logger.info(f"Loading golden template for category: {category}")

        # Find the golden template directory for this category
        category_dir = GOLDEN_TEMPLATES_DIR / category

        if not category_dir.exists():
            logger.error(f"Golden template directory not found: {category_dir}")
            return None

        # Find the JSON file in the category directory
        json_files = list(category_dir.glob("*.json"))

        if not json_files:
            logger.error(f"No JSON file found in golden template directory: {category_dir}")
            return None

        if len(json_files) > 1:
            logger.warning(f"Multiple JSON files found in {category_dir}, using first one: {json_files[0]}")

        golden_template_file = json_files[0]
        logger.info(f"Loading golden template from: {golden_template_file}")

        # Load the golden template JSON
        with golden_template_file.open(encoding="utf-8") as f:
            golden_template_json = json.load(f)

        # Store golden template in state for enrichment agent
        callback_context.state["golden_template_json"] = golden_template_json
        callback_context.state["golden_template_category"] = category

        logger.info(f"Golden template loaded successfully for category: {category}")
        logger.info(f"Golden template keys: {list(golden_template_json.keys())}")

        return None

    except Exception as exc:
        logger.error(
            "Failed to load golden template: %s",
            exc,
            exc_info=True,
        )
        return None
