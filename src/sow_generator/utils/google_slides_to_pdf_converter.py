"""PPTX to PDF converter utilities using Google Slides API.


Provides conversion from PowerPoint to PDF format for downstream

multimodal processing with Gemini. Uses Google Drive/Slides API

for native, high-quality conversion.
"""


import json
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


    def __init__(self, credentials_file: str | Path | dict):

        """Initialize with service account credentials.


        Args:

            credentials_file: Service account credentials in one of these formats:

                - str/Path: Path to service account JSON file

                - str: JSON string containing service account data

                - dict: Parsed service account JSON data
        """

        scopes = [

            "https://www.googleapis.com/auth/drive",

            "https://www.googleapis.com/auth/presentations.readonly"

        ]


        # Handle different credential formats
        if isinstance(credentials_file, dict):

            # Already a parsed JSON dict

            creds = service_account.Credentials.from_service_account_info(

                credentials_file,

                scopes=scopes

            )

        elif isinstance(credentials_file, (str, Path)):

            # Check if it's a file path or JSON string

            credentials_path = Path(credentials_file) if isinstance(credentials_file, str) else credentials_file


            if credentials_path.exists() and credentials_path.is_file():

                # It's a file path

                creds = service_account.Credentials.from_service_account_file(

                    str(credentials_file),

                    scopes=scopes

                )

            else:

                # Assume it's a JSON string

                try:

                    credentials_dict = json.loads(str(credentials_file))

                    creds = service_account.Credentials.from_service_account_info(

                        credentials_dict,

                        scopes=scopes

                    )

                except json.JSONDecodeError as e:

                    raise ValueError(

                        f"Invalid credentials: not a valid file path or JSON string: {e}"

                    ) from e

        else:

            raise TypeError(

                f"credentials_file must be str, Path, or dict, got {type(credentials_file)}"

            )


        self.creds = creds

        self.drive_service = build("drive", "v3", credentials=creds)

        self.slides_service = build("slides", "v1", credentials=creds)


    def convert_slides_to_pdf(

        self,

        file_id: str,

        cleanup: bool = False

    ) -> tuple[bytes, str]:

        """Convert a Google Drive file (Google Slides or PPTX) to PDF.


        Args:

            file_id: Google Drive file ID.

            cleanup: If True, delete the source file from Google Drive after conversion.

                    (Default: False - preserve the original file)


        Returns:

            Tuple of (PDF bytes, original filename stem).


        Raises:

            ConversionError: If the conversion fails.
        """

        try:

            # Step 1: Get file metadata to determine name and type

            logger.info("Getting metadata for file ID: %s", file_id)

            file_metadata = self.drive_service.files().get(

                fileId=file_id,

                fields="name,mimeType",

                supportsAllDrives=True

            ).execute()


            original_name = file_metadata.get("name", "presentation")

            mime_type = file_metadata.get("mimeType", "")

            logger.info("File name: %s, MIME type: %s", original_name, mime_type)


            # Remove file extension from name for PDF naming

            original_stem = Path(original_name).stem


            # # Step 2: Check if file needs conversion to Google Slides format

            # if mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":

            #     # It's a PPTX file - need to convert to Google Slides first

            #     logger.info("File is PPTX format, converting to Google Slides")


            #     # Create a copy as Google Slides

            #     copy_metadata = {

            #         "name": f"{original_stem}_temp",

            #         "mimeType": "application/vnd.google-apps.presentation"

            #     }


            #     copy_file = self.drive_service.files().copy(

            #         fileId=file_id,

            #         body=copy_metadata

            #     ).execute()


            #     slides_id = copy_file.get("id")

            #     should_cleanup_temp = True

            #     logger.info("Created temporary Google Slides: %s", slides_id)


            # elif mime_type == "application/vnd.google-apps.presentation":

            #     # Already a Google Slides presentation

            #     logger.info("File is already Google Slides format")

            #     slides_id = file_id

            #     should_cleanup_temp = False

            # else:

            #     msg = f"Unsupported file type: {mime_type}. Expected Google Slides or PPTX."

            #     raise ConversionError(msg)


            # Step 3: Export as PDF and download to memory

            logger.info("Exporting to PDF")

            request = self.drive_service.files().export_media(

                fileId=file_id,

                mimeType="application/pdf"

            )


            # Step 4: Download PDF to memory (BytesIO)
            import io

            pdf_buffer = io.BytesIO()

            downloader = MediaIoBaseDownload(pdf_buffer, request)

            done = False

            while not done:

                status, done = downloader.next_chunk()

                if status:

                    logger.info("Download progress: %d%%", int(status.progress() * 100))


            pdf_bytes = pdf_buffer.getvalue()

            logger.info("PDF downloaded to memory: %d bytes", len(pdf_bytes))


            # Step 5: Cleanup temporary files if needed

            # if should_cleanup_temp:

            #     try:

            #         self.drive_service.files().delete(fileId=slides_id).execute()

            #         logger.info("Deleted temporary Google Slides: %s", slides_id)

            #     except Exception as e:

            #         logger.warning("Failed to delete temporary file: %s", e)


            # if cleanup:

            #     try:

            #         self.drive_service.files().delete(fileId=file_id).execute()

            #         logger.info("Deleted source file: %s", file_id)

            #     except Exception as e:

            #         logger.warning("Failed to delete source file: %s", e)


            return pdf_bytes, original_stem


        except Exception as e:

            from googleapiclient.errors import HttpError

            if isinstance(e, HttpError) and "exportSizeLimitExceeded" in str(e):

                logger.info("File too large for standard Drive API export. Trying direct Slides export URL.")

                import google.auth.transport.requests

                import requests
                

                request = google.auth.transport.requests.Request()

                self.creds.refresh(request)

                token = self.creds.token
                

                url = f"https://docs.google.com/presentation/d/{file_id}/export/pdf"

                headers = {"Authorization": f"Bearer {token}"}
                

                response = requests.get(url, headers=headers)

                if response.status_code == 200:

                    pdf_bytes = response.content

                    logger.info("PDF downloaded via direct URL: %d bytes", len(pdf_bytes))

                    return pdf_bytes, original_stem

                else:

                    msg = f"Direct Slides export HTTP failed: {response.status_code} {response.text}"

                    logger.error(msg, ex)

                    raise ConversionError(msg) from e

            else:

                msg = f"Google Slides conversion failed: {e}"

                logger.error(msg, exc_info=True)

                raise ConversionError(msg) from e


    # def convert_pptx_to_pdf(

    #     self,

    #     pptx_path: Path,

    #     cleanup: bool = True

    # ) -> Path:

    #     """Convert a PPTX file to PDF using Google Slides API.


    #     Args:

    #         pptx_path: Path to the source .pptx file.

    #         cleanup: If True, delete temporary Google Drive files.


    #     Returns:

    #         Path to the generated PDF file.


    #     Raises:

    #         ConversionError: If the conversion fails.

    #         FileNotFoundError: If the source PPTX file does not exist.

    #     """

    #     if not pptx_path.exists():

    #         msg = f"PPTX file not found: {pptx_path}"

    #         raise FileNotFoundError(msg)


    #     slides_id = None

    #     try:

    #         # Step 1: Upload PPTX to Google Drive as Google Slides

    #         logger.info("Uploading %s to Google Drive", pptx_path)


    #         file_metadata = {

    #             "name": pptx_path.stem,

    #             "mimeType": "application/vnd.google-apps.presentation"

    #         }


    #         media = MediaFileUpload(

    #             str(pptx_path),

    #             mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",

    #             resumable=True

    #         )


    #         slides_file = self.drive_service.files().create(

    #             body=file_metadata,

    #             media_body=media,

    #             fields="id"

    #         ).execute()


    #         slides_id = slides_file.get("id")

    #         logger.info("Uploaded as Google Slides: %s", slides_id)


    #         # Step 2: Export as PDF

    #         logger.info("Exporting to PDF")

    #         request = self.drive_service.files().export_media(

    #             fileId=slides_id,

    #             mimeType="application/pdf"

    #         )


    #         # Step 3: Download PDF to temp file

    #         outdir = Path(tempfile.mkdtemp(prefix="sow_pptx_"))

    #         pdf_path = outdir / f"{pptx_path.stem}.pdf"


    #         with open(pdf_path, "wb") as fh:

    #             downloader = MediaIoBaseDownload(fh, request)

    #             done = False

    #             while not done:

    #                 status, done = downloader.next_chunk()

    #                 if status:

    #                     logger.info("Download progress: %d%%", int(status.progress() * 100))


    #         logger.info("PDF created: %s", pdf_path)

    #         return pdf_path


    #     except Exception as e:

    #         msg = f"Google Slides conversion failed: {e}"

    #         logger.error(msg)

    #         raise ConversionError(msg) from e


    #     finally:

    #         # Step 4: Cleanup temporary Google Drive file

    #         if cleanup and slides_id:

    #             try:

    #                 self.drive_service.files().delete(fileId=slides_id).execute()

    #                 logger.info("Deleted temporary Google Slides: %s", slides_id)

    #             except Exception as e:

    #                 logger.warning("Failed to delete temporary file: %s", e)



# def convert_pptx_to_pdf(pptx_path: Path, credentials_file: str | Path) -> Path:

#     """Convert a PPTX file to PDF using Google Slides API.


#     This is a convenience function that maintains the same interface

#     as the previous LibreOffice-based converter.


#     Args:

#         pptx_path: Path to the source .pptx file.

#         credentials_file: Path to Google service account JSON.


#     Returns:

#         Path to the generated PDF file.


#     Raises:

#         ConversionError: If the conversion fails.

#         FileNotFoundError: If the source PPTX file does not exist.

#     """

#     converter = GoogleSlidesConverter(credentials_file)

#     return converter.convert_pptx_to_pdf(pptx_path, cleanup=True)



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

        description="Convert Google Slides or PPTX files to PDF using Google Slides API"

    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(

        "--pptx",

        type=Path,

        help="Path to the input PPTX file"

    )

    group.add_argument(

        "--slides-id",

        type=str,

        help="Google Slides file ID"

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


    if not args.credentials.exists():

        logger.error("Credentials file not found: %s", args.credentials)

        return


    try:

        # Create converter

        logger.info("Initializing Google Slides converter")

        converter = GoogleSlidesConverter(args.credentials)


        if args.slides_id:

            logger.info("Converting Google Slides ID %s to PDF", args.slides_id)

            pdf_bytes, stem = converter.convert_slides_to_pdf(args.slides_id)

            pdf_path = Path.cwd() / f"{stem}.pdf"

            with open(pdf_path, "wb") as f:

                f.write(pdf_bytes)
                

            print("\n" + "=" * 70)

            print("Conversion Complete")

            print("=" * 70)

            print(f"\nInput Slides ID: {args.slides_id}")

            print(f"Output PDF:      {pdf_path}")

            print(f"PDF Size:        {pdf_path.stat().st_size:,} bytes")

            print("\n" + "=" * 70)
            

        elif args.pptx:

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

