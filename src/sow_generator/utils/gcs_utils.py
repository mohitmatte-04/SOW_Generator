"""Google Cloud Storage utility functions.

Provides helpers for downloading, uploading, and managing GCS blobs
used by the extractor agent pipeline.
"""

import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSURIError(ValueError):
    """Raised when a GCS URI is malformed."""


def parse_gcs_uri(gcs_uri: str) -> tuple[str, str]:
    """Parse a GCS URI into bucket name and blob path.

    Args:
        gcs_uri: A URI in the format ``gs://bucket-name/path/to/object``.

    Returns:
        A tuple of (bucket_name, blob_path).

    Raises:
        GCSURIError: If the URI does not start with ``gs://`` or is missing
            the bucket or path components.
    """
    if not gcs_uri.startswith("gs://"):
        msg = f"Invalid GCS URI (must start with 'gs://'): {gcs_uri}"
        raise GCSURIError(msg)

    without_scheme = gcs_uri[len("gs://") :]
    parts = without_scheme.split("/", 1)

    if len(parts) < 2 or not parts[0] or not parts[1]:  # noqa: PLR2004
        msg = f"Invalid GCS URI (missing bucket or path): {gcs_uri}"
        raise GCSURIError(msg)

    return parts[0], parts[1]


def download_blob_to_tempfile(
    gcs_uri: str,
    *,
    suffix: str | None = None,
) -> Path:
    """Download a GCS blob to a temporary local file.

    Args:
        gcs_uri: Full ``gs://…`` URI to the object.
        suffix: Optional file suffix for the temp file (e.g. ``.pptx``).

    Returns:
        Path to the downloaded temporary file. Caller is responsible for
        cleanup.
    """
    bucket_name, blob_path = parse_gcs_uri(gcs_uri)

    if suffix is None:
        suffix = Path(blob_path).suffix or ""

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)

    logger.info("Downloading gs://%s/%s → %s", bucket_name, blob_path, tmp_path)
    blob.download_to_filename(str(tmp_path))

    return tmp_path


def upload_file_to_gcs(local_path: Path, gcs_uri: str) -> str:
    """Upload a local file to GCS.

    Args:
        local_path: Path to the local file to upload.
        gcs_uri: Target ``gs://…`` URI.

    Returns:
        The GCS URI of the uploaded object.
    """
    bucket_name, blob_path = parse_gcs_uri(gcs_uri)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    logger.info("Uploading %s → gs://%s/%s", local_path, bucket_name, blob_path)
    blob.upload_from_filename(str(local_path))

    return gcs_uri


def upload_json_to_gcs(data: dict[str, Any], gcs_uri: str) -> str:
    """Serialize a dictionary to JSON and upload it to GCS.

    Args:
        data: The dictionary to serialize.
        gcs_uri: Target ``gs://…`` URI for the JSON file.

    Returns:
        The GCS URI of the uploaded JSON file.
    """
    bucket_name, blob_path = parse_gcs_uri(gcs_uri)
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    logger.info(
        "Uploading JSON (%d bytes) → gs://%s/%s",
        len(json_bytes),
        bucket_name,
        blob_path,
    )
    blob.upload_from_string(json_bytes, content_type="application/json")

    return gcs_uri


def delete_gcs_blob(gcs_uri: str) -> None:
    """Delete a blob from GCS.

    Args:
        gcs_uri: The ``gs://…`` URI of the blob to delete.
    """
    bucket_name, blob_path = parse_gcs_uri(gcs_uri)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    logger.info("Deleting gs://%s/%s", bucket_name, blob_path)
    blob.delete()
