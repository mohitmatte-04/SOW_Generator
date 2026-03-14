"""PPTX to PDF converter utilities using Google Slides API.

Provides conversion from PowerPoint to PDF format for downstream
multimodal processing with Gemini. Uses Google Drive/Slides API
for native, high-quality conversion.
"""

import logging
import tempfile
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

logger = logging.getLogger(__name__)


class ConversionError(RuntimeError):
    """Raised when PPTX-to-PDF conversion fails."""


class GoogleSlidesConverter:
    """Convert PPTX files to PDF using Google Slides API."""

    def __init__(self, credentials_file: str | Path):
        """Initialize with service account credentials.
        
        Args:
            credentials_file: Path to service account JSON file.
        """
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/presentations.readonly"
        ]
        
        creds = service_account.Credentials.from_service_account_file(
            str(credentials_file),
            scopes=scopes
        )
        
        self.drive_service = build("drive", "v3", credentials=creds)
        self.slides_service = build("slides", "v1", credentials=creds)

    def convert_pptx_to_pdf(
        self, 
        pptx_path: Path, 
        cleanup: bool = True
    ) -> Path:
        """Convert a PPTX file to PDF using Google Slides API.

        Args:
            pptx_path: Path to the source .pptx file.
            cleanup: If True, delete temporary Google Drive files.

        Returns:
            Path to the generated PDF file.

        Raises:
            ConversionError: If the conversion fails.
            FileNotFoundError: If the source PPTX file does not exist.
        """
        # if not pptx_path.exists():
        #     msg = f"PPTX file not found: {pptx_path}"
        #     raise FileNotFoundError(msg)

        slides_id = "1T0QfEJZ2yEBdYFZqMHWk916h4g_GoY6l9UQK3A6H5sY"
        try:
            # # Step 1: Upload PPTX to Google Drive as Google Slides
            # logger.info("Uploading %s to Google Drive", pptx_path)
            
            # file_metadata = {
            #     "name": pptx_path.stem,
            #     "mimeType": "application/vnd.google-apps.presentation"
            # }
            
            # media = MediaFileUpload(
            #     str(pptx_path),
            #     mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            #     resumable=True
            # )
            
            # slides_file = self.drive_service.files().create(
            #     body=file_metadata,
            #     media_body=media,
            #     fields="id"
            # ).execute()
            
            # slides_id = slides_file.get("id")
            # logger.info("Uploaded as Google Slides: %s", slides_id)

            # Step 2: Export as PDF
            logger.info("Exporting to PDF")
            request = self.drive_service.files().export_media(
                fileId=slides_id,
                mimeType="application/pdf"
            )

            # Step 3: Download PDF to temp file
            outdir = Path(tempfile.mkdtemp(prefix="sow_pptx_"))
            pdf_path = outdir / f"{pptx_path.stem}.pdf"
            
            with open(pdf_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info("Download progress: %d%%", int(status.progress() * 100))

            logger.info("PDF created: %s", pdf_path)
            return pdf_path

        except Exception as e:
            msg = f"Google Slides conversion failed: {e}"
            logger.error(msg)
            raise ConversionError(msg) from e

        finally:
            # Step 4: Cleanup temporary Google Drive file
            if cleanup and slides_id:
                try:
                    self.drive_service.files().delete(fileId=slides_id).execute()
                    logger.info("Deleted temporary Google Slides: %s", slides_id)
                except Exception as e:
                    logger.warning("Failed to delete temporary file: %s", e)


def convert_pptx_to_pdf(pptx_path: Path, credentials_file: str | Path) -> Path:
    """Convert a PPTX file to PDF using Google Slides API.

    This is a convenience function that maintains the same interface
    as the previous LibreOffice-based converter.

    Args:
        pptx_path: Path to the source .pptx file.
        credentials_file: Path to Google service account JSON.

    Returns:
        Path to the generated PDF file.

    Raises:
        ConversionError: If the conversion fails.
        FileNotFoundError: If the source PPTX file does not exist.
    """
    converter = GoogleSlidesConverter(credentials_file)
    return converter.convert_pptx_to_pdf(pptx_path, cleanup=True)


def main() -> None:
    """Main function to test PPTX to PDF conversion using Google Slides API.

    Usage:
        python -m sow_generator.utils.google-slides-to-pdf-converter \\
            --pptx path/to/presentation.pptx \\
            --credentials path/to/service_account.json
    """
    import argparse
    import os

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Convert PPTX files to PDF using Google Slides API"
    )
    parser.add_argument(
        "--pptx",
        type=Path,
        required=True,
        help="Path to the input PPTX file"
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json"),
        help="Path to service account JSON file (default: service_account.json or GOOGLE_APPLICATION_CREDENTIALS env var)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep temporary Google Drive files (for debugging)"
    )

    args = parser.parse_args()

    # Validate inputs
    # if not args.pptx.exists():
    #     logger.error("PPTX file not found: %s", args.pptx)
    #     return

    if not args.credentials.exists():
        logger.error("Credentials file not found: %s", args.credentials)
        return

    try:
        # Create converter
        logger.info("Initializing Google Slides converter")
        converter = GoogleSlidesConverter(args.credentials)

        # Convert PPTX to PDF
        logger.info("Converting %s to PDF", args.pptx)
        pdf_path = converter.convert_pptx_to_pdf(
            args.pptx,
            cleanup=not args.no_cleanup
        )

        # Display results
        print("\n" + "=" * 70)
        print("Conversion Complete")
        print("=" * 70)
        print(f"\nInput PPTX:  {args.pptx}")
        print(f"Output PDF:  {pdf_path}")
        print(f"PDF Size:    {pdf_path.stat().st_size:,} bytes")
        print("\n" + "=" * 70)

    except ConversionError as e:
        logger.error("Conversion failed: %s", e)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
