"""Tool to generate a SOW document and store it in GCS."""

import io
import logging
import re
from datetime import datetime, timezone
from typing import Any

from docx import Document
from google.cloud import storage

logger = logging.getLogger(__name__)


def _sanitize_filename(title: str) -> str:
    """Convert a document title to a safe filename."""
    safe = re.sub(r"[^\w\s-]", "", title)
    safe = re.sub(r"[\s]+", "_", safe.strip())
    return safe


async def generate_sow_document(
    template_gcs_uri: str,
    placeholders: dict[str, str],
    document_title: str = "Generated Statement of Work",
    output_gcs_bucket: str = "sow-generator-testing-phase",
    output_gcs_folder: str = "sow",
) -> dict[str, Any]:
    """Generate a SOW by replacing placeholders in a DOCX template and uploading to GCS.

    Downloads a .docx template from GCS, replaces placeholder tags with
    generated content, and uploads the final document back to GCS.

    Args:
        template_gcs_uri: GCS URI to the .docx template
            (e.g., ``gs://bucket/template.docx``).
        placeholders: Dictionary of placeholders to replace
            (e.g., ``{"<<SCOPE>>": "..."}``).
        document_title: The title for the generated document.
        output_gcs_bucket: The GCS bucket to store the generated SOW.
        output_gcs_folder: The folder within the bucket to store the SOW.

    Returns:
        A dictionary containing status, the GCS URI of the generated
        document, and any error message.
    """
    try:
        # 1. Download template from GCS
        if not template_gcs_uri.startswith("gs://"):
            return {"status": "error", "error": "Invalid template GCS URI."}

        parts = template_gcs_uri.replace("gs://", "").split("/", 1)
        if len(parts) != 2:  # noqa: PLR2004
            return {"status": "error", "error": "Invalid template GCS URI format."}

        bucket_name, blob_name = parts

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not blob.exists():
            return {
                "status": "error",
                "error": f"Template not found: {template_gcs_uri}",
            }

        template_bytes = blob.download_as_bytes()

        # 2. Open the .docx template and replace placeholders
        doc = Document(io.BytesIO(template_bytes))

        # A robust way to replace text in python-docx is to clear the paragraph
        # and re-insert the text if we don't want to deal with complex run splitting.
        # But a simpler way when preserving some formatting is to just replace paragraph text
        # (which removes run-level formatting but works reliably for full-paragraph placeholders).
        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    # Simple paragraph-level replacement
                    paragraph.text = paragraph.text.replace(key, value)

        # Also check tables for placeholders
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for key, value in placeholders.items():
                            if key in paragraph.text:
                                paragraph.text = paragraph.text.replace(key, value)

        # 3. Save modified document to bytes
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        # 4. Upload to GCS
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_title = _sanitize_filename(document_title)
        output_blob_name = f"{output_gcs_folder}/{safe_title}_{timestamp}.docx"

        output_bucket = storage_client.bucket(output_gcs_bucket)
        output_blob = output_bucket.blob(output_blob_name)
        output_blob.upload_from_file(
            output_stream,
            content_type=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
        )

        output_gcs_uri = f"gs://{output_gcs_bucket}/{output_blob_name}"
        logger.info("SOW document uploaded to %s", output_gcs_uri)

        return {
            "status": "success",
            "data": {
                "gcs_uri": output_gcs_uri,
                "bucket": output_gcs_bucket,
                "blob_name": output_blob_name,
            },
        }

    except Exception:
        logger.exception("Failed to generate SOW document")
        return {"status": "error", "error": "Failed to generate SOW document."}
