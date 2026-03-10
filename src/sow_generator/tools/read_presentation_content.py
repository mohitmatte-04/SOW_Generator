"""Tool to read content from Google Slides or local PPTX files."""

import logging
import os
from typing import Any, Dict, Optional
from pptx import Presentation
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.auth
from google.cloud import storage
from pptx import Presentation
import tempfile
import asyncio

logger = logging.getLogger(__name__)

# async def read_presentation_content(
#     presentation_source: str,
# ) -> Dict[str, Any]:
#     """
#     Reads and extracts text content from a Google Slides URL or a local .pptx file.

#     Args:
#         presentation_source: URL to Google Slides or local path to a .pptx file.

#     Returns:
#         A dictionary containing the status, extracted text, and any error message.
#         Example: {"status": "success", "data": {"text": "...", "slides": [...]}}
#     """
#     try:
#         if "docs.google.com/presentation" in presentation_source:
#             return await _read_google_slides(presentation_source)
#         elif presentation_source.lower().endswith(".pptx"):
#             return await _read_local_pptx(presentation_source)
#         else:
#             return {
#                 "status": "error",
#                 "error": "Unsupported presentation source. Must be a Google Slides URL or a local .pptx file.",
#             }
#     except Exception as e:
#         logger.error(f"Failed to read presentation: {e}", exc_info=True)
#         return {"status": "error", "error": str(e)}



# async def _read_google_slides(url: str) -> Dict[str, Any]:
#     """Reads content from Google Slides using the Slides API."""
#     try:
#         # Extract presentation ID from URL
#         # URL format: https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit...
#         parts = url.split("/")
#         if "d" not in parts:
#              return {"status": "error", "error": "Invalid Google Slides URL format."}
#         presentation_id = parts[parts.index("d") + 1]

#         # Authenticate
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/presentations.readonly"]
#         )
#         if credentials.expired and credentials.refresh_token:
#             credentials.refresh(Request())

#         service = build("slides", "v1", credentials=credentials)
#         presentation = service.presentations().get(presentationId=presentation_id).execute()
#         slides = presentation.get("slides", [])

#         extracted_slides = []
#         full_text = []

#         for i, slide in enumerate(slides):
#             slide_text = []
#             for element in slide.get("pageElements", []):
#                 if "shape" in element and "text" in element["shape"]:
#                     text_content = element["shape"]["text"].get("textElements", [])
#                     for text_element in text_content:
#                         if "textRun" in text_element:
#                             slide_text.append(text_element["textRun"]["content"])
            
#             content = "".join(slide_text).strip()
#             extracted_slides.append({"slide_number": i + 1, "content": content})
#             full_text.append(content)

#         return {
#             "status": "success",
#             "data": {
#                 "text": "\n\n".join(full_text),
#                 "slides": extracted_slides,
#                 "title": presentation.get("title", "Untitled Presentation")
#             }
#         }

#     except Exception as e:
#         logger.error(f"Error reading Google Slides: {e}, exc_info=True")
#         return {"status": "error", "error": f"Google Slides API error: {str(e)}"}


async def extract_slide_structure(slide):
    """
    Extracts structured content from a single PowerPoint slide.

    This function parses a slide to identify its title, bullet points (with levels),
    tables, and speaker notes.

    Args:
        slide: A pptx.slide.Slide object to extract content from.

    Returns:
        dict: A dictionary containing:
            - title (str): The text content of the title shape, if present.
            - bullets (list[dict]): A list of objects with 'level' (int) and 'text' (str).
            - tables (list[list[list[str]]]): A 3D list representing table data [table][row][cell].
            - text_blocks (list): Currently unused placeholder for additional text items.
            - notes (str): The text from the speaker notes slide, if present.
    """

    slide_data = {
        "title": "",
        "bullets": [],
        "tables": [],
        "text_blocks": [],
        "notes": ""
    }

    for shape in slide.shapes:

        # --- TITLE ---
        if shape == slide.shapes.title and shape.has_text_frame:
            slide_data["title"] = shape.text.strip()
            continue

        # --- TEXT / BULLETS ---
        if shape.has_text_frame:

            for paragraph in shape.text_frame.paragraphs:

                text = paragraph.text.strip()

                if not text:
                    continue

                bullet = {
                    "level": paragraph.level,
                    "text": text
                }

                slide_data["bullets"].append(bullet)

        # --- TABLES ---
        if shape.has_table:

            table_data = []

            for row in shape.table.rows:

                row_data = []

                for cell in row.cells:
                    row_data.append(cell.text.strip())

                table_data.append(row_data)

            slide_data["tables"].append(table_data)

    # --- SPEAKER NOTES ---
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        slide_data["notes"] = notes

    return slide_data


async def read_presentation_content(gcs_uri: str):
    """
    Extracts structured data (titles, bullets, tables, notes) including text from each slide of the presentation.

    Args:
        gcs_uri (str): The Google Cloud Storage URI of the .pptx file (e.g., "gs://bucket/path/file.pptx").

    Returns:
        dict: A dictionary with a "status" ("success" or "error"):
            - If "success": "data" contains:
                - title (str): Filename of the presentation.
                - slides (list[dict]): List of structured slide contents.
                - full_text (str): A flattened string of all extracted bullet text.
            - If "error": "error" contains the exception message.
    """

    try:

        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI. Expected format: gs://bucket/file.pptx")

        # Parse GCS path
        path = gcs_uri.replace("gs://", "")
        bucket_name, blob_path = path.split("/", 1)

        # Initialize client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        print(f"reading presentation from gcs: bucket {bucket}, path {blob_path}")
        blob = bucket.blob(blob_path)
        print(f"Read presentation from GCS: {blob}")

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.close() # Close the file handle for Windows compatibility

            try:
                blob.download_to_filename(temp_file_path)

                prs = Presentation(temp_file_path)

                slides_data = []
                all_text = []

                for i, slide in enumerate(prs.slides):

                    slide_struct = await extract_slide_structure(slide)

                    slides_data.append({
                        "slide_number": i + 1,
                        **slide_struct
                    })

                    # Flatten text for fallback LLM context
                    combined_text = " ".join(
                        [b["text"] for b in slide_struct["bullets"]]
                    )

                    all_text.append(combined_text)
            finally:
                # Always cleanup the temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return {
            "status": "success",
            "data": {
                "title": blob_path.split("/")[-1],
                "slides": slides_data,
                "full_text": "\n".join(all_text)
            }
        }

    except Exception as e:

        logger.error(f"Error reading presentation from GCS: {e}", exc_info=True)

        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    result = asyncio.run(read_presentation_content("gs://agent_engine_depoly/sow-generator/proposal-samples/Copy of Sony Proposal.pptx"))
    print(result)