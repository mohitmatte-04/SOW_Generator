"""API routes for SOW Generator REST API."""

import asyncio
import logging
import uuid
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .session_manager import GenerationStage, session_manager
from .config import SOW_TEMPLATE_GCS_URI, SOW_OUTPUT_GCS_URI

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
        log_dir / "api_routes.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════════════════════

class GenerateSOWRequest(BaseModel):
    """Request model for SOW generation."""
    proposalFolderUrl: str
    documentTitle: str = "Generated_SOW"


class GenerateSOWResponse(BaseModel):
    """Response model for SOW generation."""
    session_id: str
    status: str = "success"
    message: str


class ProgressResponse(BaseModel):
    """Response model for progress tracking."""
    session_id: str
    stage: str
    progress: int
    message: str
    sow_url: Optional[str] = None
    error: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# Background Processing
# ══════════════════════════════════════════════════════════════════════════════

async def process_sow_generation(session_id: str, proposal_url: str, document_title: str):
    """Background task to process SOW generation using the agent pipeline."""
    try:
        logger.info(f"Session {session_id}: Starting SOW generation")
        logger.info(f"{'=' * 80}")
        logger.info(f"📥 INPUT: {proposal_url}")
        logger.info(f"{'=' * 80}")

        # Import the root agent pipeline and ADK components
        from .agent import root_agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.adk.artifacts import InMemoryArtifactService
        from google.genai import types as genai_types

        # ══════════════════════════════════════════════════════════════════
        # Stage 1: Initialize Agent Session (0-20%)
        # ══════════════════════════════════════════════════════════════════
        session_manager.update_progress(
            session_id,
            GenerationStage.UPLOADING,
            10,
            "Initializing AI agent workflow..."
        )

        # Create ADK session service and artifact service
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()

        runner = Runner(
            agent=root_agent,
            app_name="sow_generator",
            session_service=session_service,
            artifact_service=artifact_service,
        )

        # Create a session
        adk_session = await session_service.create_session(
            app_name="sow_generator",
            user_id=session_id,
        )

        session_manager.update_progress(
            session_id,
            GenerationStage.UPLOADING,
            20,
            "Agent session created"
        )

        # ══════════════════════════════════════════════════════════════════
        # Stage 2: Run the Agent Pipeline (20-90%)
        # ══════════════════════════════════════════════════════════════════
        # The pipeline handles everything automatically:
        # 1. input_parser_agent - Parses the GCS URI or Google Drive URL
        # 2. extractor_agent - Converts PPTX to PDF and extracts SOW data
        # 3. sow_generation_agent - Generates the final SOW document

        session_manager.update_progress(
            session_id,
            GenerationStage.EXTRACTING,
            30,
            "Processing proposal with AI agents..."
        )

        logger.info(f"Session {session_id}: Running agent pipeline with input: {proposal_url}")

        # Construct the agent input message
        user_message = genai_types.Content(
            role="user",
            parts=[
                genai_types.Part(
                    text=f"Generate an SOW from {proposal_url}"
                )
            ],
        )

        # Run the pipeline and collect the result
        result_text = None
        async for event in runner.run_async(
            session_id=adk_session.id,
            user_id=session_id,
            new_message=user_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        result_text = part.text
                        logger.info(f"Session {session_id}: Agent text response: {part.text[:200]}...")
                        # Update progress to 60% during agent execution
                        session_manager.update_progress(
                            session_id,
                            GenerationStage.GENERATING,
                            60,
                            "AI agent processing document..."
                        )
                    if hasattr(part, 'function_call') and part.function_call:
                        logger.info(f"Session {session_id}: Agent calling tool: {part.function_call.name}")
                        # Update progress during tool execution
                        session_manager.update_progress(
                            session_id,
                            GenerationStage.EXTRACTING,
                            50,
                            f"Executing: {part.function_call.name}..."
                        )

        logger.info(f"Session {session_id}: Agent pipeline completed")
        if result_text:
            logger.info(f"Final result text length: {len(result_text)} characters")
        else:
            logger.warning(f"Session {session_id}: No text result from agent")

        # ══════════════════════════════════════════════════════════════════
        # Stage 3: Extract Result from Agent Output (90-100%)
        # ══════════════════════════════════════════════════════════════════
        session_manager.update_progress(
            session_id,
            GenerationStage.GENERATING,
            90,
            "Finalizing SOW document..."
        )

        # Extract the Google Drive URL and GCS URI from the agent's response
        import re
        generated_drive_url = None
        generated_sow_gcs_uri = None

        if result_text:
            logger.info(f"Agent response text: {result_text}")  # Added: Log full response

            # Try to parse as JSON first
            import json
            try:
                response_json = json.loads(result_text)
                if isinstance(response_json, dict):
                    generated_drive_url = response_json.get("sow_output_path") or response_json.get("drive_url")
                    logger.info(f"✅ Extracted from JSON: {generated_drive_url}")
            except (json.JSONDecodeError, ValueError):
                # Fallback to regex if not JSON
                # Match URL but stop at quotes, spaces, or closing braces
                drive_match = re.search(r'https://(?:docs|drive)\.google\.com/[^\s\'"}\]]+', result_text)
                if drive_match:
                    generated_drive_url = drive_match.group(0)
                    logger.info(f"✅ Extracted via regex: {generated_drive_url}")
                else:
                    logger.warning(f"Could not extract Google Drive URL from agent response")

            # Try to extract GCS URI - handles spaces in filenames
            # Matches from 'gs://' to '.docx' including any characters (including spaces)
            # gcs_match = re.search(r'gs://[^\n]+?\.docx', result_text)  # ✅ FIXED: Handles spaces!
            # if gcs_match:
            #     generated_sow_gcs_uri = gcs_match.group(0).strip()
            #     logger.info(f"✅ Successfully extracted GCS URI: {generated_sow_gcs_uri}")
            # gcs_match = re.search(r'gs://[^\n]+?\.docx', result_text)  # ✅ FIXED: Handles spaces!
            # if gcs_match:
            #     generated_sow_gcs_uri = gcs_match.group(0).strip()
            #     logger.info(f"✅ Successfully extracted GCS URI: {generated_sow_gcs_uri}")

        # If we couldn't extract URLs, use the configured output location
        # if not generated_sow_gcs_uri:
        #     generated_sow_gcs_uri = f"{SOW_OUTPUT_GCS_URI}{document_title}.docx"
        #     logger.warning(f"⚠️ Could not extract GCS URI from agent response, using configured location: {generated_sow_gcs_uri}")
        # if not generated_sow_gcs_uri:
        #     generated_sow_gcs_uri = f"{SOW_OUTPUT_GCS_URI}{document_title}.docx"
        #     logger.warning(f"⚠️ Could not extract GCS URI from agent response, using configured location: {generated_sow_gcs_uri}")

        # Enhanced logging for SOW save location
        logger.info(f"{'=' * 80}")
        logger.info(f"✅ SUCCESS! SOW generated and saved!")
        logger.info(f"Session: {session_id}")
        if generated_drive_url:
            logger.info(f"Google Drive: {generated_drive_url}")
        logger.info(f"{'=' * 80}")

        # Final stage - set result with URL (prefer Drive URL if available)
        final_url = generated_drive_url

        if not final_url:
            error_msg = "No valid URL extracted from agent response"
            logger.error(f"Session {session_id}: {error_msg}")
            session_manager.set_error(session_id, error_msg)
            return

        # Clean up the URL (remove any trailing quotes or brackets)
        final_url = final_url.rstrip('"}]')

        logger.info(f"Session {session_id}: Setting final URL: {final_url}")
        session_manager.set_result(
            session_id,
            result_url=final_url
        )

        logger.info(f"Session {session_id}: SOW generation completed successfully with URL: {final_url}")

    except Exception as e:
        logger.error(f"Session {session_id}: Error generating SOW - {e}", exc_info=True)
        session_manager.set_error(
            session_id,
            error=str(e)
        )
        session_manager.update_progress(
            session_id,
            GenerationStage.ERROR,
            0,
            f"Error: {str(e)}"
        )

# ══════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/api/generate-sow", response_model=GenerateSOWResponse)
async def generate_sow(request: GenerateSOWRequest):
    """
    Start SOW generation process.

    Args:
        request: Contains proposalFolderUrl (GCS URI or Google Drive URL) and documentTitle

    Returns:
        Session ID for tracking progress
    """
    try:
        # Create a new session
        session_id = session_manager.create_session(
            proposal_url=request.proposalFolderUrl,
            document_title=request.documentTitle
        )

        logger.info(f"Created session {session_id} for proposal: {request.proposalFolderUrl}")

        # Start background processing
        asyncio.create_task(
            process_sow_generation(
                session_id=session_id,
                proposal_url=request.proposalFolderUrl,
                document_title=request.documentTitle
            )
        )

        return GenerateSOWResponse(
            session_id=session_id,
            message="SOW generation started"
        )

    except Exception as e:
        logger.error(f"Error starting SOW generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sow-progress/{session_id}", response_model=ProgressResponse)
async def get_sow_progress(session_id: str):
    """
    Get the current progress of an SOW generation session.

    Args:
        session_id: The session ID returned from generate_sow endpoint

    Returns:
        Current stage, progress percentage, and status message
    """
    try:
        session_data = session_manager.get_session(session_id)

        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        return ProgressResponse(
            session_id=session_id,
            stage=session_data["stage"],
            progress=session_data["progress"],
            message=session_data.get("message", ""),
            sow_url=session_data.get("result_url"),
            error=session_data.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
