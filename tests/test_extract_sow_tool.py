"""Tests for the extract_sow_from_presentation tool."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sow_generator.tools.extract_sow_from_presentation import (
    _build_extraction_prompt,
    _merge_into_schema,
    _parse_llm_json,
    extract_sow_from_presentation,
)


class TestBuildExtractionPrompt:
    """Tests for _build_extraction_prompt."""

    def test_contains_schema(self) -> None:
        prompt = _build_extraction_prompt()
        assert "sow_structure" in prompt
        assert "1.0_executive_summary" in prompt
        assert "10.0_fees_and_expenses" in prompt

    def test_contains_instructions(self) -> None:
        prompt = _build_extraction_prompt()
        assert "Extract ONLY information present" in prompt


class TestParseLLMJson:
    """Tests for _parse_llm_json."""

    def test_parses_clean_json(self) -> None:
        raw = '{"key": "value"}'
        result = _parse_llm_json(raw)
        assert result == {"key": "value"}

    def test_parses_json_with_markdown_fences(self) -> None:
        raw = '```json\n{"key": "value"}\n```'
        result = _parse_llm_json(raw)
        assert result == {"key": "value"}

    def test_parses_json_with_generic_fences(self) -> None:
        raw = '```\n{"key": "value"}\n```'
        result = _parse_llm_json(raw)
        assert result == {"key": "value"}

    def test_handles_whitespace_padding(self) -> None:
        raw = '\n  \n{"key": "value"}\n  \n'
        result = _parse_llm_json(raw)
        assert result == {"key": "value"}

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse"):
            _parse_llm_json("this is not json")


class TestMergeIntoSchema:
    """Tests for _merge_into_schema."""

    def test_merges_matching_keys(self) -> None:
        template = {"a": "NA", "b": "NA"}
        extracted = {"a": "extracted_a"}
        result = _merge_into_schema(extracted, template)
        assert result["a"] == "extracted_a"
        assert result["b"] == "NA"

    def test_merges_nested_dicts(self) -> None:
        template = {"section": {"sub1": "NA", "sub2": "NA"}}
        extracted = {"section": {"sub1": "found"}}
        result = _merge_into_schema(extracted, template)
        assert result["section"]["sub1"] == "found"
        assert result["section"]["sub2"] == "NA"

    def test_ignores_extra_keys_in_extracted(self) -> None:
        template = {"a": "NA"}
        extracted = {"a": "val", "extra": "should be ignored"}
        result = _merge_into_schema(extracted, template)
        assert result == {"a": "val"}

    def test_preserves_template_structure(self) -> None:
        template = {"a": {"nested": "NA"}, "b": "NA"}
        extracted = {}
        result = _merge_into_schema(extracted, template)
        assert result == {"a": {"nested": "NA"}, "b": "NA"}


class TestExtractSOWFromPresentation:
    """Integration tests for extract_sow_from_presentation with mocks."""

    @pytest.fixture
    def mock_sow_response(self) -> dict:
        return {
            "sow_structure": {
                "1.0_executive_summary": {
                    "1.1_opportunity": "Migrate to GCP",
                    "1.2_solution_overview": "Lift and shift approach",
                },
                "3.0_success_criteria": "95% uptime SLA",
            }
        }

    @patch(
        "sow_generator.tools.extract_sow_from_presentation.delete_gcs_blob"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.upload_json_to_gcs"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.upload_file_to_gcs"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.convert_pptx_to_pdf"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.download_blob_to_tempfile"
    )
    @patch("sow_generator.tools.extract_sow_from_presentation.genai.Client")
    async def test_successful_pdf_extraction(
        self,
        mock_genai_client_cls: MagicMock,
        mock_download: MagicMock,
        mock_convert: MagicMock,
        mock_upload_file: MagicMock,
        mock_upload_json: MagicMock,
        mock_delete: MagicMock,
        mock_sow_response: dict,
        tmp_path: Path,
    ) -> None:
        # Setup mocks
        pptx_file = tmp_path / "test.pptx"
        pptx_file.write_text("fake pptx")
        mock_download.return_value = pptx_file

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("fake pdf")
        mock_convert.return_value = pdf_file

        mock_upload_file.return_value = "gs://bucket/_tmp_extraction/test.pdf"
        mock_upload_json.return_value = (
            "gs://bucket/processed_metadata/test_sow_extracted.json"
        )

        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_sow_response)
        mock_client = mock_genai_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_response

        result = await extract_sow_from_presentation(
            "gs://bucket/proposals/test.pptx"
        )

        assert result["status"] == "success"
        assert result["data"]["sow_structure"]["3.0_success_criteria"] == "95% uptime SLA"
        assert "metadata_uri" in result
        mock_upload_json.assert_called_once()
        mock_delete.assert_called_once()

    @patch(
        "sow_generator.tools.extract_sow_from_presentation.download_blob_to_tempfile"
    )
    async def test_returns_error_on_download_failure(
        self,
        mock_download: MagicMock,
    ) -> None:
        mock_download.side_effect = Exception("GCS access denied")

        result = await extract_sow_from_presentation("gs://bucket/bad.pptx")

        assert result["status"] == "error"
        assert "GCS access denied" in result["error"]

    @patch(
        "sow_generator.tools.extract_sow_from_presentation.delete_gcs_blob"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.upload_json_to_gcs"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.extract_text_from_pptx"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.convert_pptx_to_pdf"
    )
    @patch(
        "sow_generator.tools.extract_sow_from_presentation.download_blob_to_tempfile"
    )
    @patch("sow_generator.tools.extract_sow_from_presentation.genai.Client")
    async def test_falls_back_to_text_extraction(
        self,
        mock_genai_client_cls: MagicMock,
        mock_download: MagicMock,
        mock_convert: MagicMock,
        mock_extract_text: MagicMock,
        mock_upload_json: MagicMock,
        mock_delete: MagicMock,
        mock_sow_response: dict,
        tmp_path: Path,
    ) -> None:
        from sow_generator.utils.pptx_converter import ConversionError

        pptx_file = tmp_path / "test.pptx"
        pptx_file.write_text("fake pptx")
        mock_download.return_value = pptx_file

        mock_convert.side_effect = ConversionError("No LibreOffice")
        mock_extract_text.return_value = "Slide 1 text content"

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_sow_response)
        mock_client = mock_genai_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_response

        mock_upload_json.return_value = (
            "gs://bucket/processed_metadata/test_sow_extracted.json"
        )

        result = await extract_sow_from_presentation(
            "gs://bucket/proposals/test.pptx"
        )

        assert result["status"] == "success"
        mock_extract_text.assert_called_once()
        # No PDF upload should happen in text fallback path
        mock_delete.assert_not_called()
