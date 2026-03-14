"""API routes for SOW generation frontend integration.

This module provides FastAPI endpoints for the React frontend to interact
with the SOW generation backend.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .session_manager import session_manager, GenerationStage
from .config import SOW_OUTPUT_FOLDER_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sow-generation"])


class GenerateSOWRequest(BaseModel):
    """Request model for SOW generation."""

    proposal_file_url: str  # Google Drive URL to proposal file
    document_title: str = "Generated_SOW"  # Optional title for the document


class GenerateSOWResponse(BaseModel):
    """Response model for SOW generation request."""

    session_id: str
    status: str
    message: str


class ProgressResponse(BaseModel):
    """Response model for progress check."""

    session_id: str
    stage: str
    progress: int
    message: str
    sow_url: str | None = None
    error: str | None = None


async def process_sow_generation(
    session_id: str,
    proposal_url: str,
    document_title: str
):
    """Background task to process SOW generation.

    This function runs in the background and updates session progress
    as it goes through different stages.

    Args:
        session_id: Unique session identifier
        proposal_url: Google Drive URL to proposal file
        document_title: Title for the generated document
    """
    try:
        # ══════════════════════════════════════════════════════════════════
        # Stage 1: UPLOADING (10-30%)
        # ══════════════════════════════════════════════════════════════════
        logger.info(f"Session {session_id}: Starting SOW generation")
        session_manager.update_progress(
            session_id,
            GenerationStage.UPLOADING,
            10,
            "Accessing proposal file..."
        )

        # Determine if input is GCS URI or Google Drive URL
        logger.info("=" * 80)
        logger.info(f"📥 INPUT: {proposal_url}")
        logger.info("=" * 80)

        if proposal_url.startswith("gs://"):
            # GCS URI - can use directly
            logger.info(f"✅ GCS URI detected - using directly")
            logger.info(f"Proposal file: {proposal_url}")
            proposal_gcs_uri = proposal_url
        else:
            # Google Drive URL - needs conversion
            # TODO (Manager): Download from Google Drive and upload to GCS
            # from .utils.gdrive_utils import download_drive_file_to_gcs
            # proposal_gcs_uri = await download_drive_file_to_gcs(proposal_url)
            logger.warning(f"⚠️ Google Drive URL detected (not yet implemented)")
            logger.warning(f"Workflow will run in SIMULATION mode only")
            proposal_gcs_uri = None  # Will use simulation for now

        # Simulate file access
        await asyncio.sleep(2)
        session_manager.update_progress(
            session_id,
            GenerationStage.UPLOADING,
            30,
            "Proposal file accessed successfully"
        )

        # ══════════════════════════════════════════════════════════════════
        # Stage 2: EXTRACTING (30-60%)
        # ══════════════════════════════════════════════════════════════════
        session_manager.update_progress(
            session_id,
            GenerationStage.EXTRACTING,
            40,
            "Extracting proposal details..."
        )

        # If GCS URI is available, call the actual extraction tool
        if proposal_gcs_uri:
            from .tools.extract_sow_from_presentation import extract_sow_from_presentation

            # Update progress during extraction
            session_manager.update_progress(
                session_id,
                GenerationStage.EXTRACTING,
                45,
                "Analyzing proposal content with AI..."
            )

            logger.info(f"Session {session_id}: Calling extraction tool with GCS URI")
            extraction_result = await extract_sow_from_presentation(proposal_gcs_uri)

            if extraction_result.get("status") != "success":
                raise Exception(f"Extraction failed: {extraction_result.get('error', 'Unknown error')}")

            raw_data = extraction_result.get("data", {})
            logger.info(f"Session {session_id}: Extraction successful")
            logger.info(f"Session {session_id}: Raw extraction data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'N/A'}")

            # Unwrap the nested structure - extraction returns {"statement_of_work_template": {...}}
            # but we need just the inner dict
            if "statement_of_work_template" in raw_data:
                placeholders = raw_data["statement_of_work_template"]
                logger.info(f"Session {session_id}: Unwrapped placeholders, keys: {list(placeholders.keys()) if isinstance(placeholders, dict) else 'N/A'}")
            else:
                placeholders = raw_data
                logger.warning(f"Session {session_id}: No 'statement_of_work_template' key found, using raw data")

            # Update progress after extraction
            session_manager.update_progress(
                session_id,
                GenerationStage.EXTRACTING,
                55,
                "Processing extracted data..."
            )
        else:
            # Google Drive URL - TODO (Manager): Implement Google Drive download
            # For now, simulate extraction
            await asyncio.sleep(3)
            placeholders = None  # Will be populated when Google Drive is implemented

        session_manager.update_progress(
            session_id,
            GenerationStage.EXTRACTING,
            60,
            "Proposal details extracted successfully"
        )

        # ══════════════════════════════════════════════════════════════════
        # Stage 3: GENERATING (60-90%)
        # ══════════════════════════════════════════════════════════════════
        session_manager.update_progress(
            session_id,
            GenerationStage.GENERATING,
            70,
            "Generating Statement of Work document..."
        )

        # If placeholders are available (GCS path was used), call the actual generation tool
        if placeholders:
            from .tools.generate_sow_document import generate_sow_document
            from .config import SOW_TEMPLATE_GCS_URI, SOW_OUTPUT_GCS_URI

            # Update progress during generation
            session_manager.update_progress(
                session_id,
                GenerationStage.GENERATING,
                75,
                "Preparing SOW template..."
            )

            # Prepare output GCS URI
            output_gcs_uri = f"{SOW_OUTPUT_GCS_URI}/{document_title}.docx"

            logger.info("=" * 80)
            logger.info(f"Session {session_id}: Calling SOW generation tool")
            logger.info(f"Template: {SOW_TEMPLATE_GCS_URI}")
            logger.info(f"Output will be saved to: {output_gcs_uri}")
            logger.info("=" * 80)

            # Call the actual generation tool
            sow_result = await generate_sow_document(
                template_gcs_uri=SOW_TEMPLATE_GCS_URI,
                placeholders=placeholders,
                document_title=document_title,
                output_gcs_uri=output_gcs_uri
            )

            if sow_result.get("status") != "success":
                raise Exception(f"SOW generation failed: {sow_result.get('error', 'Unknown error')}")

            generated_sow_gcs_uri = sow_result.get("data", {}).get("gcs_uri")

            logger.info("=" * 80)
            logger.info(f"✅ SUCCESS! SOW generated and saved!")
            logger.info(f"Session: {session_id}")
            logger.info(f"File Location: {generated_sow_gcs_uri}")
            logger.info(f"View in Console: https://console.cloud.google.com/storage/browser/_details/{generated_sow_gcs_uri.replace('gs://', '')}")
            logger.info("=" * 80)

            # Update progress after generation
            session_manager.update_progress(
                session_id,
                GenerationStage.GENERATING,
                85,
                "Finalizing document..."
            )
        else:
            # Google Drive URL - simulate for now
            # TODO (Manager): Implement Google Drive workflow
            await asyncio.sleep(3)
            generated_sow_gcs_uri = None

        session_manager.update_progress(
            session_id,
            GenerationStage.GENERATING,
            90,
            "SOW document generated, uploading to output folder..."
        )

        # ══════════════════════════════════════════════════════════════════
        # Stage 4: COMPLETE (100%)
        # ══════════════════════════════════════════════════════════════════

        # Determine the result URL based on whether we used GCS or Google Drive
        if generated_sow_gcs_uri:
            # Real GCS generation happened - provide link to the generated file
            bucket_path = generated_sow_gcs_uri.replace("gs://", "")
            result_url = f"https://console.cloud.google.com/storage/browser/_details/{bucket_path}"
            logger.info(f"Session {session_id}: Generated SOW available at {result_url}")
        elif SOW_OUTPUT_FOLDER_URL.startswith("gs://"):
            # Simulation with GCS output folder - link to folder
            bucket_path = SOW_OUTPUT_FOLDER_URL.replace("gs://", "")
            result_url = f"https://console.cloud.google.com/storage/browser/{bucket_path}"
        else:
            # Google Drive folder URL (simulation)
            # TODO (Manager): Replace with actual Google Drive file URL when implemented
            result_url = SOW_OUTPUT_FOLDER_URL

        session_manager.set_result(
            session_id,
            result_url,
            metadata={
                "document_title": document_title,
                "output_folder": SOW_OUTPUT_FOLDER_URL
            }
        )

        logger.info(f"Session {session_id}: SOW generation completed successfully")

    except Exception as e:
        logger.error(f"Session {session_id}: Error generating SOW - {e}", exc_info=True)
        session_manager.set_error(session_id, str(e))


@router.post("/generate-sow", response_model=GenerateSOWResponse)
async def generate_sow(
    request: GenerateSOWRequest,
    background_tasks: BackgroundTasks
):
    """Start SOW generation process.

    This endpoint creates a new session and starts the SOW generation
    process in the background. The client can poll the progress endpoint
    to check status.

    Args:
        request: SOW generation request with proposal URL
        background_tasks: FastAPI background tasks

    Returns:
        Response with session ID for tracking progress
    """
    try:
        # Validate input
        if not request.proposal_file_url:
            raise HTTPException(
                status_code=400,
                detail="proposal_file_url is required"
            )

        # Create session
        session_id = session_manager.create_session(
            proposal_url=request.proposal_file_url,
            document_title=request.document_title
        )

        logger.info(f"Created session {session_id} for proposal: {request.proposal_file_url}")

        # Start background processing
        background_tasks.add_task(
            process_sow_generation,
            session_id,
            request.proposal_file_url,
            request.document_title
        )

        return GenerateSOWResponse(
            session_id=session_id,
            status="processing",
            message="SOW generation started successfully. Use the session_id to check progress."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting SOW generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sow-progress/{session_id}", response_model=ProgressResponse)
async def get_sow_progress(session_id: str):
    """Get the current progress of a SOW generation session.

    Args:
        session_id: Session ID to check

    Returns:
        Current progress information
    """
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )

    return ProgressResponse(
        session_id=session_id,
        stage=session["stage"],
        progress=session["progress"],
        message=session.get("message", f"Current stage: {session['stage']}"),
        sow_url=session.get("result_url"),
        error=session.get("error")
    )


@router.get("/sessions")
async def list_sessions():
    """List all active sessions (for debugging).

    Returns:
        Dictionary of all sessions
    """
    sessions = session_manager.get_all_sessions()
    return {
        "total": len(sessions),
        "sessions": list(sessions.values())
    }
