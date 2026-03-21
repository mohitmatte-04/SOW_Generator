"""Tool to convert PPTX/Google Slides presentations to PDF.


Downloads a PPTX or Google Slides file from Google Drive, converts it to PDF

using Google Slides API, and returns the local path. The PDF will be saved as

an artifact by an after-tool callback.
"""

import logging
import os
import re

import sys

from pathlib import Path

from typing import Any


# Handle both direct execution and module import

if __name__ == "__main__":

    # Add parent directory to path for direct execution

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from sow_generator.utils.google_slides_to_pdf_converter import (

        ConversionError,

        GoogleSlidesConverter,
    )

else:

    # Use relative imports when imported as a module
    from ..utils.google_slides_to_pdf_converter import (

        ConversionError,

        GoogleSlidesConverter,
    )


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

    log_dir = Path(__file__).parent.parent.parent.parent / "logs"

    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(

        log_dir / "convert_slides_to_pdf.log",

        maxBytes=10*1024*1024,  # 10MB

        backupCount=5
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


    logger.setLevel(logging.INFO)



def _extract_drive_file_id(drive_url: str) -> str | None:

    """Extract file ID from a Google Drive URL.


    Supports various Google Drive URL formats:

    - https://drive.google.com/file/d/{FILE_ID}/view

    - https://docs.google.com/presentation/d/{FILE_ID}/edit

    - https://drive.google.com/open?id={FILE_ID}

    - Direct file ID


    Args:

        drive_url: Google Drive URL or file ID.


    Returns:

        Extracted file ID or None if not found.
    """

    # Pattern 1: /file/d/{FILE_ID}/ or /presentation/d/{FILE_ID}/

    pattern1 = r"/(file|presentation)/d/([a-zA-Z0-9_-]+)"

    match = re.search(pattern1, drive_url)

    if match:

        return match.group(2)


    # Pattern 2: ?id={FILE_ID}

    pattern2 = r"[?&]id=([a-zA-Z0-9_-]+)"

    match = re.search(pattern2, drive_url)

    if match:

        return match.group(1)


    # Pattern 3: Assume it's already a file ID

    if re.match(r"^[a-zA-Z0-9_-]+$", drive_url):
        return drive_url


    return None



async def convert_slides_to_pdf(drive_url: str) -> dict[str, Any]:

    """Convert a Google Slides presentation or PPTX file from Google Drive to PDF.


    This tool extracts the file ID from a Google Drive URL, converts the

    presentation to PDF using Google Slides API, and returns the PDF bytes.

    An after-tool callback will save the PDF as an artifact.


    Args:

        drive_url: Google Drive URL or file ID pointing to a Google Slides

            presentation or PPTX file. Supported formats:

            - https://drive.google.com/file/d/{FILE_ID}/view

            - https://docs.google.com/presentation/d/{FILE_ID}/edit

            - https://drive.google.com/open?id={FILE_ID}

            - Direct file ID string


    Returns:

        A dictionary containing:

        - ``status``: "success" or "error"

        - ``pdf_bytes``: PDF file content as bytes (on success)

        - ``original_filename``: Name of the presentation (on success)

        - ``error``: Error message (on failure)
    """

    try:

        # Step 1: Extract file ID from Drive URL

        logger.info("Starting conversion for: %s", drive_url)

        file_id = _extract_drive_file_id(drive_url)


        if not file_id:

            msg = f"Invalid Google Drive URL format: {drive_url}"
            logger.error(msg)

            return {"status": "error", "error": msg}


        logger.info("Extracted file ID: %s", file_id)


        # Step 2: Convert to PDF using Google Slides API

        try:

            # Get credentials from environment - can be file path or JSON string

            credentials = os.getenv("sow-generator-sa")


            if not credentials:

                msg = "Missing credentials: 'sow-generator-sa' environment variable not set"
                logger.error(msg)

                return {"status": "error", "error": msg}


            logger.info("Initializing Google Slides converter")

            # Pass credentials directly - GoogleSlidesConverter will detect if it's a file path or JSON string

            converter = GoogleSlidesConverter(credentials)


            logger.info("Converting Google Drive file to PDF using Google Slides API")

            pdf_bytes, original_filename = converter.convert_slides_to_pdf(

                file_id, cleanup=False  # Don't delete the source file from Drive
            )

            logger.info("PDF conversion successful: %d bytes", len(pdf_bytes))


        except (ConversionError, FileNotFoundError) as conv_err:

            msg = f"PDF conversion failed: {conv_err}"
            logger.error(msg)

            return {"status": "error", "error": msg}


        return {

            "status": "success",

            "pdf_bytes": pdf_bytes,

            "original_filename": original_filename,

        }


    except Exception as exc:

        logger.error("Conversion failed: %s", exc, exc_info=True)

        return {"status": "error", "error": str(exc)}



async def main() -> None:

    """Main function to test Google Drive to PDF conversion.


    Usage:

        python -m sow_generator.tools.convert_slides_to_pdf \

            --drive-url "https://docs.google.com/presentation/d/FILE_ID/edit"
    """
    import argparse

    import asyncio


    # Setup logging

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


    # Parse command-line arguments

    parser = argparse.ArgumentParser(

        description="Convert Google Slides or PPTX from Google Drive to PDF"
    )
    parser.add_argument(

        "--drive-url",

        type=str,

        required=True,

        help="Google Drive URL or file ID (e.g., 'https://docs.google.com/presentation/d/FILE_ID/edit' or just 'FILE_ID')"
    )


    args = parser.parse_args()


    try:

        # Convert to PDF

        logger.info("Starting conversion for: %s", args.drive_url)

        result = await convert_slides_to_pdf(args.drive_url)


        # Display results

        print("\n" + "=" * 70)

        if result.get("status") == "success":

            print("Conversion Complete")

            print("=" * 70)

            print(f"\nDrive URL:        {args.drive_url}")

            print(f"Filename:         {result.get('original_filename')}")

            print(f"PDF Size:         {len(result.get('pdf_bytes', b'')):,} bytes")

            print("\n" + "=" * 70)

        else:

            print("Conversion Failed")

            print("=" * 70)

            print(f"\nError: {result.get('error')}")

            print("\n" + "=" * 70)


    except Exception as e:

        logger.exception("Unexpected error: %s", e)



if __name__ == "__main__":

    import asyncio

    asyncio.run(main())

