"""Tests for the generate_sow_document tool."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from docx import Document

from sow_generator.tools.generate_sow_document import (
    _insert_table_at_paragraph,
    _process_table_placeholders,
    _replace_placeholder_in_paragraph,
    _replace_placeholders_in_document,
    _replace_placeholders_in_table,
    _set_run_text_with_breaks,
    generate_sow_document,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc_with_paragraph(text: str) -> Document:
    """Create a minimal Document with a single paragraph containing *text*."""
    doc = Document()
    doc.add_paragraph(text)
    return doc


def _make_doc_with_table(rows: list[list[str]]) -> Document:
    """Create a minimal Document with a table populated from *rows*."""
    doc = Document()
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_text in enumerate(row_data):
            table.cell(r_idx, c_idx).text = cell_text
    return doc


# ---------------------------------------------------------------------------
# _set_run_text_with_breaks
# ---------------------------------------------------------------------------

class TestSetRunTextWithBreaks:
    """Tests for the line-break insertion helper."""

    def test_single_line_no_break(self) -> None:
        doc = _make_doc_with_paragraph("placeholder")
        run = doc.paragraphs[0].runs[0]
        _set_run_text_with_breaks(run, "simple text")
        assert run.text == "simple text"

    def test_multiline_inserts_breaks(self) -> None:
        doc = _make_doc_with_paragraph("placeholder")
        run = doc.paragraphs[0].runs[0]
        _set_run_text_with_breaks(run, "Line 1\nLine 2\nLine 3")
        assert "Line 1" in run.text
        assert "Line 2" in run.text
        assert "Line 3" in run.text

    def test_multiline_creates_br_elements(self) -> None:
        from docx.oxml.ns import qn

        doc = _make_doc_with_paragraph("placeholder")
        run = doc.paragraphs[0].runs[0]
        _set_run_text_with_breaks(run, "A\nB\nC")
        br_count = len(run._element.findall(qn("w:br")))
        assert br_count == 2  # two \n → two <w:br/>


# ---------------------------------------------------------------------------
# _replace_placeholder_in_paragraph
# ---------------------------------------------------------------------------

class TestReplacePlaceholderInParagraph:
    """Unit tests for the paragraph-level replacement helper."""

    def test_replaces_single_placeholder(self) -> None:
        doc = _make_doc_with_paragraph("Hello {{NAME}}, welcome!")
        para = doc.paragraphs[0]
        result = _replace_placeholder_in_paragraph(para, "{{NAME}}", "Alice")
        assert result is True
        assert "Hello Alice, welcome!" in para.text

    def test_returns_false_when_placeholder_absent(self) -> None:
        doc = _make_doc_with_paragraph("No placeholders here.")
        para = doc.paragraphs[0]
        result = _replace_placeholder_in_paragraph(para, "{{MISSING}}", "X")
        assert result is False
        assert para.text == "No placeholders here."

    def test_replaces_multiple_occurrences_in_same_paragraph(self) -> None:
        doc = _make_doc_with_paragraph("{{X}} and {{X}} again")
        para = doc.paragraphs[0]
        result = _replace_placeholder_in_paragraph(para, "{{X}}", "YES")
        assert result is True
        assert "YES and YES again" in para.text

    def test_multiline_replacement(self) -> None:
        doc = _make_doc_with_paragraph("Scope: {{SCOPE}}")
        para = doc.paragraphs[0]
        result = _replace_placeholder_in_paragraph(
            para, "{{SCOPE}}", "Item 1\nItem 2\nItem 3"
        )
        assert result is True
        assert "Item 1" in para.text
        assert "Item 2" in para.text


# ---------------------------------------------------------------------------
# _replace_placeholders_in_document
# ---------------------------------------------------------------------------

class TestReplacePlaceholdersInDocument:
    """Tests for full-document replacement across paragraphs."""

    def test_replaces_in_body_paragraphs(self) -> None:
        doc = _make_doc_with_paragraph("Scope: {{SCOPE}}")
        count = _replace_placeholders_in_document(
            doc, {"{{SCOPE}}": "Build the widget"}
        )
        assert count == 1
        assert "Build the widget" in doc.paragraphs[0].text

    def test_replaces_multiple_placeholders(self) -> None:
        doc = Document()
        doc.add_paragraph("Problem: {{PROBLEM}}")
        doc.add_paragraph("Solution: {{SOLUTION}}")
        placeholders = {
            "{{PROBLEM}}": "Legacy system",
            "{{SOLUTION}}": "Cloud migration",
        }

        count = _replace_placeholders_in_document(doc, placeholders)
        assert count == 2
        assert "Legacy system" in doc.paragraphs[0].text
        assert "Cloud migration" in doc.paragraphs[1].text


# ---------------------------------------------------------------------------
# _replace_placeholders_in_table
# ---------------------------------------------------------------------------

class TestReplacePlaceholdersInTable:
    """Tests for table-cell replacement."""

    def test_replaces_in_table_cells(self) -> None:
        doc = _make_doc_with_table(
            [["Header", "{{VALUE}}"], ["Row", "{{OTHER}}"]]
        )
        table = doc.tables[0]
        count = _replace_placeholders_in_table(
            table, {"{{VALUE}}": "Filled", "{{OTHER}}": "Done"}
        )
        assert count == 2
        assert "Filled" in table.cell(0, 1).text
        assert "Done" in table.cell(1, 1).text


# ---------------------------------------------------------------------------
# Dynamic table insertion
# ---------------------------------------------------------------------------

class TestProcessTablePlaceholders:
    """Tests for {{TABLE:KEY}} placeholder processing."""

    def test_inserts_table_from_json(self) -> None:
        doc = Document()
        doc.add_paragraph("Before table")
        doc.add_paragraph("{{TABLE:MILESTONES}}")
        doc.add_paragraph("After table")

        table_json = json.dumps({
            "headers": ["Phase", "Duration", "Cost"],
            "rows": [
                ["Assessment", "2 weeks", "$10,000"],
                ["Migration", "8 weeks", "$50,000"],
            ],
        })

        count = _process_table_placeholders(
            doc, {"{{TABLE:MILESTONES}}": table_json}
        )

        assert count == 1
        assert len(doc.tables) == 1
        table = doc.tables[0]
        assert table.cell(0, 0).text == "Phase"
        assert table.cell(0, 1).text == "Duration"
        assert table.cell(1, 0).text == "Assessment"
        assert table.cell(2, 0).text == "Migration"

    def test_preserves_surrounding_content(self) -> None:
        doc = Document()
        doc.add_paragraph("Before table")
        doc.add_paragraph("{{TABLE:DATA}}")
        doc.add_paragraph("After table")

        table_json = json.dumps({
            "headers": ["Col1"],
            "rows": [["Val1"]],
        })

        _process_table_placeholders(doc, {"{{TABLE:DATA}}": table_json})

        # Check that surrounding paragraphs are still present
        para_texts = [p.text for p in doc.paragraphs]
        assert "Before table" in para_texts
        assert "After table" in para_texts

    def test_skips_missing_table_data(self) -> None:
        doc = Document()
        doc.add_paragraph("{{TABLE:UNKNOWN}}")

        count = _process_table_placeholders(doc, {})
        assert count == 0

    def test_skips_invalid_json(self) -> None:
        doc = Document()
        doc.add_paragraph("{{TABLE:BAD}}")

        count = _process_table_placeholders(
            doc, {"{{TABLE:BAD}}": "not json"}
        )
        assert count == 0

    def test_skips_empty_headers(self) -> None:
        doc = Document()
        doc.add_paragraph("{{TABLE:EMPTY}}")

        table_json = json.dumps({"headers": [], "rows": []})
        count = _process_table_placeholders(
            doc, {"{{TABLE:EMPTY}}": table_json}
        )
        assert count == 0

    def test_accepts_dict_value_directly(self) -> None:
        """Table data can also be passed as a dict (not just JSON string)."""
        doc = Document()
        doc.add_paragraph("{{TABLE:DIRECT}}")

        table_data = {
            "headers": ["Name", "Role"],
            "rows": [["Alice", "PM"]],
        }

        # Pass as dict instead of JSON string
        count = _process_table_placeholders(
            doc, {"{{TABLE:DIRECT}}": table_data}
        )
        assert count == 1
        assert doc.tables[0].cell(0, 0).text == "Name"
        assert doc.tables[0].cell(1, 0).text == "Alice"


# ---------------------------------------------------------------------------
# generate_sow_document (async, with mocks)
# ---------------------------------------------------------------------------

class TestGenerateSOWDocument:
    """Integration-level tests for the async generate_sow_document function."""

    @patch("sow_generator.tools.generate_sow_document.upload_file_to_gcs")
    @patch("sow_generator.tools.generate_sow_document.Document")
    @patch("sow_generator.tools.generate_sow_document._TEMPLATE_PATH")
    async def test_successful_generation(
        self,
        mock_template_path: MagicMock,
        mock_document_cls: MagicMock,
        mock_upload: MagicMock,
    ) -> None:
        mock_template_path.exists.return_value = True
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_doc.sections = []
        mock_document_cls.return_value = mock_doc
        mock_upload.return_value = "gs://bucket/output/SOW.docx"

        result = await generate_sow_document(
            output_gcs_uri="gs://bucket/output/SOW.docx",
            placeholders={"{{SCOPE}}": "Test scope"},
        )

        assert result["status"] == "success"
        assert result["data"]["output_gcs_uri"] == "gs://bucket/output/SOW.docx"
        mock_upload.assert_called_once()

    @patch("sow_generator.tools.generate_sow_document.upload_file_to_gcs")
    @patch("sow_generator.tools.generate_sow_document.Document")
    @patch("sow_generator.tools.generate_sow_document._TEMPLATE_PATH")
    async def test_returns_error_on_upload_failure(
        self,
        mock_template_path: MagicMock,
        mock_document_cls: MagicMock,
        mock_upload: MagicMock,
    ) -> None:
        mock_template_path.exists.return_value = True
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_doc.sections = []
        mock_document_cls.return_value = mock_doc
        mock_upload.side_effect = Exception("GCS upload failed")

        result = await generate_sow_document(
            output_gcs_uri="gs://bucket/output/SOW.docx",
            placeholders={},
        )

        assert result["status"] == "error"
        assert "GCS upload failed" in result["error"]

    @patch("sow_generator.tools.generate_sow_document._TEMPLATE_PATH")
    async def test_returns_error_on_missing_template(
        self,
        mock_template_path: MagicMock,
    ) -> None:
        mock_template_path.exists.return_value = False

        result = await generate_sow_document(
            output_gcs_uri="gs://bucket/output/SOW.docx",
            placeholders={},
        )

        assert result["status"] == "error"
        assert "template not found" in result["error"].lower()

    @patch("sow_generator.tools.generate_sow_document.upload_file_to_gcs")
    async def test_end_to_end_with_real_docx(
        self,
        mock_upload: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Create a real temp DOCX template and verify both text and table placeholders."""
        template_doc = Document()
        template_doc.add_paragraph("Problem: {{BUSINESS_PROBLEM}}")
        template_doc.add_paragraph("{{TABLE:TIMELINE}}")
        template_doc.add_paragraph("Solution: {{PROPOSED_SOLUTION}}")
        template_path = tmp_path / "SOW_Template.docx"
        template_doc.save(str(template_path))

        mock_upload.return_value = "gs://bucket/output/SOW.docx"

        timeline_json = json.dumps({
            "headers": ["Phase", "Weeks"],
            "rows": [["Setup", "2"], ["Build", "6"]],
        })

        with patch(
            "sow_generator.tools.generate_sow_document._TEMPLATE_PATH",
            template_path,
        ):
            result = await generate_sow_document(
                output_gcs_uri="gs://bucket/output/SOW.docx",
                placeholders={
                    "{{BUSINESS_PROBLEM}}": "Legacy infra costs too much",
                    "{{PROPOSED_SOLUTION}}": "Phase 1: Assessment\nPhase 2: Migration",
                    "{{TABLE:TIMELINE}}": timeline_json,
                },
            )

        assert result["status"] == "success"
        upload_call_args = mock_upload.call_args
        uploaded_path = upload_call_args[0][0]
        assert str(uploaded_path).endswith(".docx")
