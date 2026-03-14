"""Tool to convert PPTX/Google Slides presentations to PDF.

Downloads a PPTX file from GCS, converts it to PDF using Google Slides API,
and returns the local path. The PDF will be saved as an artifact by an
after-tool callback.
"""

import logging
import os
from pathlib import Path
from typing import Any

from ..utils.gcs_utils import download_blob_to_tempfile, parse_gcs_uri
from ..utils.google_slides_to_pdf_converter import (
    ConversionError,
    GoogleSlidesConverter,
)

logger = logging.getLogger(__name__)


async def convert_slides_to_pdf(gcs_uri: str) -> dict[str, Any]:
    """Convert a PPTX file from GCS to PDF using Google Slides API.

    This tool performs the conversion and returns the local PDF path.
    An after-tool callback will save the PDF as an artifact.

    Args:
        gcs_uri: GCS URI to the PPTX file
            (e.g. ``gs://bucket-name/path/to/file.pptx``).

    Returns:
        A dictionary containing:
        - ``status``: "success" or "error"
        - ``pdf_path``: Local path to the generated PDF (on success)
        - ``original_filename``: Stem of the original PPTX filename (on success)
        - ``error``: Error message (on failure)
    """
    pptx_local: Path | None = None
    pdf_local: Path | None = None

    try:
        # Step 1: Download PPTX from GCS
        logger.info("Starting conversion for: %s", gcs_uri)
        pptx_local = download_blob_to_tempfile(gcs_uri, suffix=".pptx")

        # Step 2: Convert PPTX → PDF using Google Slides API
        try:
            # Get credentials file path from environment or use default
            credentials_file = os.getenv(
                "GOOGLE_APPLICATION_CREDENTIALS",
                str(
                    Path(__file__).parent.parent
                    / "prj-sandbox-presales-portal-b9a1ce61abb0.json"
                ),
            )

            logger.info("Initializing Google Slides converter")
            converter = GoogleSlidesConverter(credentials_file)

            logger.info("Converting PPTX to PDF using Google Slides API")
            pdf_local = converter.convert_pptx_to_pdf(
                pptx_local, cleanup=True  # Cleanup temporary Google Drive files
            )
            logger.info("PDF conversion successful: %s", pdf_local)

        except (ConversionError, FileNotFoundError) as conv_err:
            msg = f"PDF conversion failed: {conv_err}"
            logger.error(msg)
            return {"status": "error", "error": msg}

        # Extract original filename stem
        _, blob_path = parse_gcs_uri(gcs_uri)
        original_filename = Path(blob_path).stem

        return {
            "status": "success",
            "pdf_path": str(pdf_local),
            "original_filename": original_filename,
        }

    except Exception as exc:
        logger.error("Conversion failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}

    finally:
        # Cleanup PPTX file (PDF will be kept for artifact saving in callback)
        if pptx_local is not None and pptx_local.exists():
            pptx_local.unlink(missing_ok=True)
