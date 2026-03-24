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
from google.genai import types # For types.Content

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Golden templates base directory
GOLDEN_TEMPLATES_DIR = Path(__file__).parent / "golden_templates"


# --- 1. Define the Callback Function ---
def before_enrichment_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:

    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    logger.info(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
    logger.info(f"[Callback] Current State: {current_state}")
    
    if agent_name != "enrichment_agent":
        return None

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

    # Sections to read
    sections = ['assumptions', 'deliverables', 'out_of_scope', 'scope_activities']
    golden_template_sections = {}

    for section in sections:
        # Construct filename: <category>-<section>.md
        # Note: lowercase files are expected
        md_file = category_dir / f"{category}-{section}.md"
        
        if md_file.exists():
            logger.info(f"Reading section '{section}' from: {md_file}")
            with md_file.open(encoding="utf-8") as f:
                content = f.read()
            callback_context.state[section] = content
        else:
            logger.warning(f"Markdown file for section '{section}' not found: {md_file}")
            # Store empty string or handle as error
            callback_context.state[section] = ""

    # Store golden template sections in state for enrichment agent
    callback_context.state["golden_template_category"] = category

    logger.info(f"Golden template sections loaded successfully for category: {category}")
    logger.info(f"Loaded sections: {sections}")

    return None

# async def before_enrichment_model_callback(
#     callback_context: CallbackContext,
#     llm_request: LlmRequest,
# ) -> Optional[LlmResponse]:
#     """Before-model callback to load golden template based on category.

#     Reads the category from extractor_agent_context in state, finds the
#     corresponding golden template JSON file, and adds it to state for
#     the enrichment agent to use.

#     Args:
#         callback_context: ADK CallbackContext for accessing state.
#         llm_request: The LLM request that will be sent to the model.

#     Returns:
#         None to allow the request to proceed, or LlmResponse to short-circuit.
#     """
#     try:
#         agent_name = callback_context.agent_name
#         if agent_name != "enrichment_agent":
#             return None
#         # Get the extractor agent output from state
#         logger.info(f"Before enrichment model callback for agent {agent_name}")
#         extractor_context = callback_context.state.get("extractor_agent_context")

#         if not extractor_context:
#             logger.error("No extractor_agent_context found in state")
#             return None

#         # Extract category from the extractor output
#         # category = extractor_context.get("category")
#         category = "teradata"

#         if not category:
#             logger.error("No category field found in extractor_agent_context")
#             return None

#         logger.info(f"Loading golden template for category: {category}")

#         # Find the golden template directory for this category
#         category_dir = GOLDEN_TEMPLATES_DIR / category

#         if not category_dir.exists():
#             logger.error(f"Golden template directory not found: {category_dir}")
#             return None

#         # Sections to read
#         sections = ['assumptions', 'deliverables', 'out-of-scope', 'scope-activities']
#         golden_template_sections = {}

#         for section in sections:
#             # Construct filename: <category>-<section>.md
#             # Note: lowercase files are expected
#             md_file = category_dir / f"{category}-{section}.md"
            
#             if md_file.exists():
#                 logger.info(f"Reading section '{section}' from: {md_file}")
#                 with md_file.open(encoding="utf-8") as f:
#                     content = f.read()
#                 golden_template_sections[section] = content
#             else:
#                 logger.warning(f"Markdown file for section '{section}' not found: {md_file}")
#                 # Store empty string or handle as error
#                 golden_template_sections[section] = ""

#         # Store golden template sections in state for enrichment agent
#         callback_context.state["golden_template_sections"] = golden_template_sections
#         callback_context.state["golden_template_category"] = category

#         logger.info(f"Golden template sections loaded successfully for category: {category}")
#         logger.info(f"Loaded sections: {list(golden_template_sections.keys())}")

#         return None

#     except Exception as exc:
#         logger.error(
#             "Failed to load golden template: %s",
#             exc,
#             exc_info=True,
#         )
#         return None
