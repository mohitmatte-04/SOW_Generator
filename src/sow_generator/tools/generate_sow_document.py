"""Tool to generate a SOW document in Google Docs format."""

import logging
import os
from typing import Any, Dict, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.cloud import storage
import google.auth
from google.auth.transport.requests import Request
import io

logger = logging.getLogger(__name__)

# async def generate_sow_document(
#     template_gcs_uri: str,
#     placeholders: Dict[str, str],
#     document_title: str,
# ) -> Dict[str, Any]:
#     """
#     Generates a Statement of Work (SOW) by duplicating a template from GCS,
#     converting it to Google Docs, and replacing placeholders.

#     Args:
#         template_gcs_uri: GCS URI to the .docx template (e.g., gs://bucket/template.docx).
#         placeholders: Dictionary of placeholders to replace (e.g., {"{{SCOPE}}": "..."}).
#         document_title: The title for the generated Google Doc.

#     Returns:
#         A dictionary containing status, the URL of the generated document, and any error message.
#     """
#     try:
#         # 1. Download from GCS
#         bucket_name = template_gcs_uri.split("/")[2]
#         blob_name = "/".join(template_gcs_uri.split("/")[3:])
        
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(blob_name)
        
#         file_stream = io.BytesIO()
#         blob.download_to_file(file_stream)
#         file_stream.seek(0)

#         # 2. Authenticate Google Drive and Docs
#         credentials, project = google.auth.default(
#             scopes=[
#                 "https://www.googleapis.com/auth/drive",
#                 "https://www.googleapis.com/auth/documents"
#             ]
#         )
#         if credentials.expired and credentials.refresh_token:
#             credentials.refresh(Request())

#         drive_service = build("drive", "v3", credentials=credentials)
#         docs_service = build("docs", "v1", credentials=credentials)

#         # 3. Upload to Drive and convert to Google Doc
#         file_metadata = {
#             "name": document_title,
#             "mimeType": "application/vnd.google-apps.document"
#         }
#         media = MediaFileUpload(
#             blob_name, # Not really used but needed for API
#             mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#             resumable=True
#         )
        
#         # We use MediaIoBaseUpload for the stream
#         from googleapiclient.http import MediaIoBaseUpload
#         media = MediaIoBaseUpload(file_stream, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", resumable=True)

#         uploaded_file = drive_service.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields="id"
#         ).execute()
        
#         doc_id = uploaded_file.get("id")

#         # 4. Batch update placeholders in Google Doc
#         requests = []
#         for key, value in placeholders.items():
#             requests.append({
#                 "replaceAllText": {
#                     "containsText": {
#                         "text": key,
#                         "matchCase": False
#                     },
#                     "replaceText": value,
#                 }
#             })

#         if requests:
#             docs_service.documents().batchUpdate(
#                 documentId=doc_id,
#                 body={"requests": requests}
#             ).execute()

#         doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

#         return {
#             "status": "success",
#             "data": {
#                 "document_id": doc_id,
#                 "document_url": doc_url
#             }
#         }

#     except Exception as e:
#         logger.error(f"Failed to generate SOW document: {e}", exc_info=True)
#         return {"status": "error", "error": str(e)}


async def generate_sow_document(
    template_gcs_uri: str,
    placeholders: Dict[str, str],
    document_title: str,
    output_gcs_uri: str
) -> Dict[str, Any]:
    """
    Generates a Statement of Work (SOW) by reading a DOCX template from GCS,
    replacing placeholders, and writing the final document back to GCS.

    Args:
        template_gcs_uri: GCS URI to the DOCX template (gs://bucket/template.docx)
        placeholders: Dictionary containing placeholder replacements
        document_title: Name of the generated document
        output_gcs_uri: GCS URI where the final document should be saved

    Returns:
        Status and GCS URI of generated document
    """

    try:
        storage_client = storage.Client()

        # -------------------------
        # 1. Download template
        # -------------------------

        template_bucket = template_gcs_uri.split("/")[2]
        template_blob_path = "/".join(template_gcs_uri.split("/")[3:])

        bucket = storage_client.bucket(template_bucket)
        blob = bucket.blob(template_blob_path)

        template_stream = io.BytesIO()
        blob.download_to_file(template_stream)
        template_stream.seek(0)

        # -------------------------
        # 2. Load DOCX template
        # -------------------------

        document = Document(template_stream)

        # -------------------------
        # 3. Replace placeholders
        # -------------------------

        def replace_text_in_paragraphs(paragraphs):
            for paragraph in paragraphs:
                for key, value in placeholders.items():
                    if key in paragraph.text:
                        paragraph.text = paragraph.text.replace(key, value)

        # Replace in paragraphs
        replace_text_in_paragraphs(document.paragraphs)

        # Replace in tables
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_text_in_paragraphs(cell.paragraphs)

        # -------------------------
        # 4. Save modified doc
        # -------------------------

        output_stream = io.BytesIO()
        document.save(output_stream)
        output_stream.seek(0)

        # -------------------------
        # 5. Upload generated doc to GCS
        # -------------------------

        output_bucket = output_gcs_uri.split("/")[2]
        output_path_prefix = "/".join(output_gcs_uri.split("/")[3:])

        output_bucket_obj = storage_client.bucket(output_bucket)

        final_blob_path = f"{output_path_prefix}/{document_title}.docx"

        output_blob = output_bucket_obj.blob(final_blob_path)

        output_blob.upload_from_file(
            output_stream,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        final_gcs_uri = f"gs://{output_bucket}/{final_blob_path}"

        return {
            "status": "success",
            "data": {
                "document_title": document_title,
                "gcs_uri": final_gcs_uri
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate SOW document: {e}", exc_info=True)

        return {
            "status": "error",
            "error": str(e)
        }