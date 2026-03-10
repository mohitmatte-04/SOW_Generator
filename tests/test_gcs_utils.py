"""Tests for GCS utility functions."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sow_generator.utils.gcs_utils import (
    GCSURIError,
    delete_gcs_blob,
    download_blob_to_tempfile,
    parse_gcs_uri,
    upload_file_to_gcs,
    upload_json_to_gcs,
)


class TestParseGCSURI:
    """Tests for parse_gcs_uri."""

    def test_valid_simple_uri(self) -> None:
        bucket, path = parse_gcs_uri("gs://my-bucket/path/to/file.pptx")
        assert bucket == "my-bucket"
        assert path == "path/to/file.pptx"

    def test_valid_single_level_path(self) -> None:
        bucket, path = parse_gcs_uri("gs://bucket/file.txt")
        assert bucket == "bucket"
        assert path == "file.txt"

    def test_valid_deep_path(self) -> None:
        bucket, path = parse_gcs_uri("gs://b/a/b/c/d/e.json")
        assert bucket == "b"
        assert path == "a/b/c/d/e.json"

    def test_invalid_no_gs_prefix(self) -> None:
        with pytest.raises(GCSURIError, match="must start with 'gs://'"):
            parse_gcs_uri("s3://bucket/path")

    def test_invalid_empty_bucket(self) -> None:
        with pytest.raises(GCSURIError, match="missing bucket or path"):
            parse_gcs_uri("gs:///path")

    def test_invalid_no_path(self) -> None:
        with pytest.raises(GCSURIError, match="missing bucket or path"):
            parse_gcs_uri("gs://bucket/")

    def test_invalid_bucket_only(self) -> None:
        with pytest.raises(GCSURIError, match="missing bucket or path"):
            parse_gcs_uri("gs://bucket")

    def test_invalid_empty_string(self) -> None:
        with pytest.raises(GCSURIError, match="must start with 'gs://'"):
            parse_gcs_uri("")


class TestDownloadBlobToTempfile:
    """Tests for download_blob_to_tempfile."""

    @patch("sow_generator.utils.gcs_utils.storage.Client")
    def test_downloads_to_temp_file(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_bucket = mock_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value

        result = download_blob_to_tempfile("gs://bucket/test.pptx", suffix=".pptx")

        assert result.suffix == ".pptx"
        mock_client.bucket.assert_called_once_with("bucket")
        mock_bucket.blob.assert_called_once_with("test.pptx")
        mock_blob.download_to_filename.assert_called_once_with(str(result))

        # Cleanup
        result.unlink(missing_ok=True)

    @patch("sow_generator.utils.gcs_utils.storage.Client")
    def test_infers_suffix_from_path(self, mock_client_cls: MagicMock) -> None:
        result = download_blob_to_tempfile("gs://bucket/file.pptx")
        assert result.suffix == ".pptx"
        result.unlink(missing_ok=True)


class TestUploadFileToGCS:
    """Tests for upload_file_to_gcs."""

    @patch("sow_generator.utils.gcs_utils.storage.Client")
    def test_uploads_file(
        self, mock_client_cls: MagicMock, tmp_path: Path
    ) -> None:
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        result = upload_file_to_gcs(test_file, "gs://bucket/output.pdf")

        assert result == "gs://bucket/output.pdf"
        mock_client = mock_client_cls.return_value
        mock_client.bucket.assert_called_once_with("bucket")
        blob = mock_client.bucket.return_value.blob.return_value
        blob.upload_from_filename.assert_called_once_with(str(test_file))


class TestUploadJsonToGCS:
    """Tests for upload_json_to_gcs."""

    @patch("sow_generator.utils.gcs_utils.storage.Client")
    def test_uploads_serialized_json(self, mock_client_cls: MagicMock) -> None:
        data = {"key": "value", "nested": {"a": 1}}
        result = upload_json_to_gcs(data, "gs://bucket/data.json")

        assert result == "gs://bucket/data.json"
        blob = mock_client_cls.return_value.bucket.return_value.blob.return_value
        call_args = blob.upload_from_string.call_args
        uploaded_bytes = call_args[0][0]
        assert json.loads(uploaded_bytes) == data
        assert call_args[1]["content_type"] == "application/json"


class TestDeleteGCSBlob:
    """Tests for delete_gcs_blob."""

    @patch("sow_generator.utils.gcs_utils.storage.Client")
    def test_deletes_blob(self, mock_client_cls: MagicMock) -> None:
        delete_gcs_blob("gs://bucket/to_delete.pdf")

        mock_client = mock_client_cls.return_value
        mock_client.bucket.assert_called_once_with("bucket")
        blob = mock_client.bucket.return_value.blob.return_value
        blob.delete.assert_called_once()
