"""Callbacks for extractor agent to manage PDF artifacts.

These callbacks handle saving and loading PDF artifacts between the two-tool
extraction workflow.
"""

import logging
import json
from pathlib import Path
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.llm_agent import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.genai import types as genai_types

from .tools.convert_slides_to_pdf import convert_slides_to_pdf

# Configure logger with console and file handlers
logger = logging.getLogger(__name__)
if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    from logging.handlers import RotatingFileHandler
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "extractor_callbacks.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)


async def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> None:
    """After-tool callback for convert_slides_to_pdf.

    Saves the generated PDF as an artifact using ADK's artifact service.
    Stores the artifact filename in session state for the next tool.

    Args:
        tool: The tool function that was executed.
        args: Arguments passed to the tool.
        tool_context: ADK CallbackContext for accessing artifact service and state.
        tool_response: Result returned by the tool.
    """
    # Only handle convert_slides_to_pdf tool
    tool_name = tool.name
    logger.info(f"After tool callback for tool: {tool_name}")
    if tool_name != "convert_slides_to_pdf":
        return

    # Check if conversion was successful
    if tool_response.get("status") != "success":
        logger.warning("Conversion failed, skipping artifact save")
        return

    original_filename = tool_response.get("original_filename")
    pdf_bytes = tool_response.get("pdf_bytes")

    if not pdf_bytes:
        logger.error("Missing pdf_bytes in tool result")
        return

    try:
        # Create artifact Part from PDF bytes
        pdf_artifact = genai_types.Part.from_bytes(
            data=pdf_bytes, mime_type="application/pdf"
        )

        # Generate artifact filename
        artifact_filename = f"{original_filename}_converted.pdf"

        # Save using ADK artifact service
        logger.info("Saving PDF as artifact: %s (%d bytes)", artifact_filename, len(pdf_bytes))
        version = await tool_context.save_artifact(
            filename=artifact_filename, artifact=pdf_artifact
        )
        logger.info(
            "PDF artifact saved: %s (version %d)", artifact_filename, version
        )

        # Store artifact info in session state for next tool
        tool_context.state["pdf_artifact_filename"] = artifact_filename
        tool_context.state["pdf_artifact_version"] = version
        tool_context.state["original_drive_url"] = args.get("drive_url")
        logger.info("pdf_artifact_file_size: %d", len(pdf_bytes))
        logger.info("Artifact info stored in session state")

    except Exception as exc:
        logger.error("Failed to save PDF artifact: %s", exc, exc_info=True)


async def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Before-model callback to attach PDF artifact to model input.

    Loads the PDF artifact saved by convert_slides_to_pdf and adds it
    to the model's input contents so Gemini can analyze it directly.

    Args:
        callback_context: ADK CallbackContext for accessing artifact service and state.
        llm_request: The LLM request that will be sent to the model.

    Returns:
        None to allow the request to proceed, or LlmResponse to short-circuit.
    """
    try:
        # Get artifact info from session state
        pdf_artifact_filename = callback_context.state.get("pdf_artifact_filename")
        is_pdf_generated = callback_context.state.get("is_pdf_generated")
        if not is_pdf_generated:
            logger.info("PDF not generated, generating the PDF")
            drive_url = json.loads(callback_context.state.get('presentation_source'))['drive_url']
            logger.info(f"extracted drive url: {drive_url}")

            # Call convert_slides_to_pdf and get the result dictionary
            result = await convert_slides_to_pdf(drive_url)

            if result.get("status") != "success":
                logger.error(f"PDF conversion failed: {result.get('error')}")
                return None

            pdf_bytes = result.get("pdf_bytes")
            if not pdf_bytes:
                logger.error("No pdf_bytes in conversion result")
                return None
            
            original_file_name = result.get("original_filename")
            if not original_file_name:
                logger.error("No original_filename in conversion result")
                return None

            callback_context.state["is_pdf_generated"] = True

            pdf_part = genai_types.Part.from_bytes(
                data=pdf_bytes, mime_type="application/pdf"
            )

            # Add PDF to the last user message in the request contents
            if llm_request.contents:
                # Find the last user message and add the PDF to it
                for content in reversed(llm_request.contents):
                    if content.role == "user":
                        # Create a new parts list with existing parts + PDF
                        existing_parts = list(content.parts) if content.parts else []
                        content.parts = existing_parts + [pdf_part]
                        logger.info("PDF artifact attached to llm input")
                        return None
            else:
                logger.warning("Could not find user content to attach PDF artifact")
            
            return None

    except Exception as exc:
        logger.error(
            "Failed to attach PDF artifact to llm input: %s",
            exc,
            exc_info=True,
        )
        return None
