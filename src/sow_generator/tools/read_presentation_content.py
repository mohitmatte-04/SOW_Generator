"""Tool to read content from Google Slides or local PPTX files."""

import logging
import os
from typing import Any, Dict, Optional
from pptx import Presentation
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.auth

logger = logging.getLogger(__name__)

async def read_presentation_content(
    presentation_source: str,
) -> Dict[str, Any]:
    """
    Reads and extracts text content from a Google Slides URL or a local .pptx file.

    Args:
        presentation_source: URL to Google Slides or local path to a .pptx file.

    Returns:
        A dictionary containing the status, extracted text, and any error message.
        Example: {"status": "success", "data": {"text": "...", "slides": [...]}}
    """
    try:
        if "docs.google.com/presentation" in presentation_source:
            return await _read_google_slides(presentation_source)
        elif presentation_source.lower().endswith(".pptx"):
            return await _read_local_pptx(presentation_source)
        else:
            return {
                "status": "error",
                "error": "Unsupported presentation source. Must be a Google Slides URL or a local .pptx file.",
            }
    except Exception as e:
        logger.error(f"Failed to read presentation: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

async def _read_google_slides(url: str) -> Dict[str, Any]:
    """Reads content from Google Slides using the Slides API."""
    try:
        # Extract presentation ID from URL
        # URL format: https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit...
        parts = url.split("/")
        if "d" not in parts:
             return {"status": "error", "error": "Invalid Google Slides URL format."}
        presentation_id = parts[parts.index("d") + 1]

        # Authenticate
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/presentations.readonly"]
        )
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build("slides", "v1", credentials=credentials)
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        slides = presentation.get("slides", [])

        extracted_slides = []
        full_text = []

        for i, slide in enumerate(slides):
            slide_text = []
            for element in slide.get("pageElements", []):
                if "shape" in element and "text" in element["shape"]:
                    text_content = element["shape"]["text"].get("textElements", [])
                    for text_element in text_content:
                        if "textRun" in text_element:
                            slide_text.append(text_element["textRun"]["content"])
            
            content = "".join(slide_text).strip()
            extracted_slides.append({"slide_number": i + 1, "content": content})
            full_text.append(content)

        return {
            "status": "success",
            "data": {
                "text": "\n\n".join(full_text),
                "slides": extracted_slides,
                "title": presentation.get("title", "Untitled Presentation")
            }
        }

    except Exception as e:
        logger.error(f"Error reading Google Slides: {e}")
        return {"status": "error", "error": f"Google Slides API error: {str(e)}"}

async def _read_local_pptx(path: str) -> Dict[str, Any]:
    """Reads content from a local .pptx file."""
    try:
        if not os.path.exists(path):
            return {"status": "error", "error": f"File not found: {path}"}

        prs = Presentation(path)
        extracted_slides = []
        full_text = []

        for i, slide in enumerate(prs.slides):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    slide_text.append(shape.text)
            
            content = "\n".join(slide_text).strip()
            extracted_slides.append({"slide_number": i + 1, "content": content})
            full_text.append(content)

        return {
            "status": "success",
            "data": {
                "text": "\n\n".join(full_text),
                "slides": extracted_slides,
            }
        }
    except Exception as e:
        logger.error(f"Error reading local PPTX: {e}")
        return {"status": "error", "error": f"PPTX parsing error: {str(e)}"}
