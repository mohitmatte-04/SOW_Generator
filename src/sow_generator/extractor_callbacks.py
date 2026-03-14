"""Callbacks for extractor agent to manage PDF artifacts.

These callbacks handle saving and loading PDF artifacts between the two-tool
extraction workflow.
"""

import logging
from pathlib import Path
from typing import Any

from google.adk.agents import CallbackContext
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


async def after_convert_callback(
    context: CallbackContext,
    tool_name: str,
    tool_args: dict[str, Any],
    tool_result: dict[str, Any],
) -> None:
    """After-tool callback for convert_slides_to_pdf.

    Saves the generated PDF as an artifact using ADK's artifact service.
    Stores the artifact filename in session state for the next tool.

    Args:
        context: ADK CallbackContext for accessing artifact service and state.
        tool_name: Name of the tool that was executed.
        tool_args: Arguments passed to the tool.
        tool_result: Result returned by the tool.
    """
    # Only handle convert_slides_to_pdf tool
    if tool_name != "convert_slides_to_pdf":
        return

    # Check if conversion was successful
    if tool_result.get("status") != "success":
        logger.warning("Conversion failed, skipping artifact save")
        return

    pdf_path_str = tool_result.get("pdf_path")
    original_filename = tool_result.get("original_filename")

    if not pdf_path_str or not original_filename:
        logger.error("Missing pdf_path or original_filename in tool result")
        return

    try:
        # Read PDF bytes
        pdf_path = Path(pdf_path_str)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # Create artifact Part
        pdf_artifact = genai_types.Part.from_bytes(
            data=pdf_bytes, mime_type="application/pdf"
        )

        # Generate artifact filename
        artifact_filename = f"{original_filename}_converted.pdf"

        # Save using ADK artifact service
        logger.info("Saving PDF as artifact: %s", artifact_filename)
        version = await context.save_artifact(
            filename=artifact_filename, artifact=pdf_artifact
        )
        logger.info(
            "PDF artifact saved: %s (version %d)", artifact_filename, version
        )

        # Store artifact info in session state for next tool
        await context.set_state(
            "pdf_artifact_filename", artifact_filename
        )
        await context.set_state("pdf_artifact_version", version)
        await context.set_state("original_gcs_uri", tool_args.get("gcs_uri"))

        logger.info("Artifact info stored in session state")

        # Cleanup local PDF file
        if pdf_path.exists():
            pdf_path.unlink()
            # Try to remove temp directory
            try:
                pdf_path.parent.rmdir()
            except OSError:
                pass

    except Exception as exc:
        logger.error("Failed to save PDF artifact: %s", exc, exc_info=True)


async def before_extract_callback(
    context: CallbackContext,
    tool_name: str,
    tool_args: dict[str, Any],
) -> dict[str, Any]:
    """Before-tool callback for extract_sow_from_pdf.

    Loads the PDF artifact saved by convert_slides_to_pdf and constructs
    the GCS URI for Gemini.

    Args:
        context: ADK CallbackContext for accessing artifact service and state.
        tool_name: Name of the tool about to be executed.
        tool_args: Arguments to be passed to the tool.

    Returns:
        Modified tool arguments with pdf_gcs_uri added.
    """
    # Only handle extract_sow_from_pdf tool
    if tool_name != "extract_sow_from_pdf":
        return tool_args

    try:
        # Get artifact info from session state
        pdf_artifact_filename = await context.get_state("pdf_artifact_filename")
        original_gcs_uri = await context.get_state("original_gcs_uri")

        if not pdf_artifact_filename:
            logger.error("PDF artifact filename not found in session state")
            return tool_args

        if not original_gcs_uri:
            logger.error("Original GCS URI not found in session state")
            return tool_args

        # Construct the GCS URI for the artifact
        # ADK artifacts follow pattern: gs://bucket/artifacts/{app_name}/{user_id}/{session_id}/{filename}
        import os

        artifact_service_uri = os.getenv("ARTIFACT_SERVICE_URI", "")
        if artifact_service_uri.startswith("gs://"):
            app_name = context.app_name or "sow_generator"
            user_id = context.user_id or "default_user"
            session_id = context.session_id or "default_session"
            pdf_gcs_uri = f"{artifact_service_uri.rstrip('/')}/artifacts/{app_name}/{user_id}/{session_id}/{pdf_artifact_filename}"
        else:
            logger.error("ARTIFACT_SERVICE_URI not configured as GCS URI")
            return tool_args

        logger.info("Loading PDF artifact for extraction: %s", pdf_gcs_uri)

        # Add the PDF GCS URI to tool arguments
        modified_args = {
            **tool_args,
            "pdf_gcs_uri": pdf_gcs_uri,
            "original_gcs_uri": original_gcs_uri,
        }

        return modified_args

    except Exception as exc:
        logger.error(
            "Failed to prepare PDF artifact for extraction: %s",
            exc,
            exc_info=True,
        )
        return tool_args
