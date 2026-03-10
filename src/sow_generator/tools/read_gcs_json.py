"""Tool to read a JSON file from Google Cloud Storage."""

import json
import logging
from typing import Any

from google.cloud import storage

logger = logging.getLogger(__name__)


async def read_gcs_json(gcs_uri: str) -> dict[str, Any]:
    """Read a JSON file from Google Cloud Storage.

    Args:
        gcs_uri: The GCS URI to the JSON file
            (e.g., ``gs://bucket-name/path/to/file.json``).

    Returns:
        A dictionary containing the status and the parsed JSON data.
    """
    try:
        if not gcs_uri.startswith("gs://"):
            return {
                "status": "error",
                "error": "Invalid GCS URI. Must start with gs://",
            }

        # Parse bucket and blob name
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        if len(parts) != 2:  # noqa: PLR2004
            return {"status": "error", "error": "Invalid GCS URI format."}

        bucket_name, blob_name = parts

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not blob.exists():
            return {"status": "error", "error": f"File not found: {gcs_uri}"}

        content = blob.download_as_text()
        data = json.loads(content)

        return {"status": "success", "data": data}

    except Exception:
        logger.exception("Failed to read GCS JSON: %s", gcs_uri)
        return {"status": "error", "error": f"Failed to read {gcs_uri}"}

