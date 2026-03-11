"""Tool to generate a SOW document by merging a DOCX template with placeholders.

Uses ``python-docx`` to perform targeted placeholder replacement.  Only
paragraphs (and table cells) that actually contain a placeholder string are
modified — the rest of the document, including all formatting, is left
completely untouched.

Multi-line replacement values (containing ``\\n``) are handled by inserting
DOCX line-break elements (``<w:br/>``) so that line-breaks render correctly
while preserving the paragraph's original style.

Dynamic table support
---------------------
Placeholders of the form ``{{TABLE:KEY}}`` are replaced with a full Word
table.  The corresponding value in the *placeholders* dict must be a **JSON
string** encoding an object with ``headers`` (list of strings) and ``rows``
(list of lists of strings)::

    {
      "headers": ["Phase", "Duration", "Cost"],
      "rows": [
        ["Assessment", "2 weeks", "$10,000"],
        ["Migration",  "8 weeks", "$50,000"]
      ]
    }
"""

import json
import logging
import re
import tempfile
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph

from sow_generator.utils.gcs_utils import upload_file_to_gcs

logger = logging.getLogger(__name__)

# Resolve the bundled template once at module level.
_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "SOW_Template.docx"

# Pattern to identify table placeholders: {{TABLE:KEY_NAME}}
_TABLE_PLACEHOLDER_RE = re.compile(r"\{\{TABLE:(\w+)\}\}")


# ---------------------------------------------------------------------------
# Line-break handling helpers
# ---------------------------------------------------------------------------

def _set_run_text_with_breaks(run: Any, text: str) -> None:
    """Set *run*'s text to *text*, converting ``\\n`` into ``<w:br/>`` elements.

    This preserves the run's existing formatting (font, size, colour, etc.)
    while supporting multi-line content.
    """
    lines = text.split("\n")

    # Clear existing text content from the run element — but keep
    # run-properties (<w:rPr>) that hold formatting.
    for child in list(run._element):
        if child.tag != qn("w:rPr"):
            run._element.remove(child)

    for i, line in enumerate(lines):
        t_elem = OxmlElement("w:t")
        t_elem.text = line
        t_elem.set(qn("xml:space"), "preserve")
        run._element.append(t_elem)

        if i < len(lines) - 1:
            br_elem = OxmlElement("w:br")
            run._element.append(br_elem)


# ---------------------------------------------------------------------------
# Text placeholder replacement
# ---------------------------------------------------------------------------

def _replace_placeholder_in_paragraph(
    paragraph: Paragraph, placeholder: str, replacement: str
) -> bool:
    """Replace *placeholder* with *replacement* inside a single paragraph.

    Handles the common case where Word splits a placeholder across
    multiple runs.  Returns ``True`` if a replacement was made.

    If *replacement* contains ``\\n``, line-break elements are inserted so
    multi-line content renders correctly while keeping the paragraph's
    original style.
    """
    full_text = paragraph.text
    if placeholder not in full_text:
        return False

    new_text = full_text.replace(placeholder, replacement)

    if paragraph.runs:
        first_run = paragraph.runs[0]
        _set_run_text_with_breaks(first_run, new_text)
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        new_run = paragraph.add_run()
        _set_run_text_with_breaks(new_run, new_text)

    return True


def _replace_placeholders_in_document(
    doc: Document, placeholders: dict[str, str]
) -> int:
    """Replace all *placeholders* throughout *doc*.

    Searches body paragraphs, table cells, and header/footer paragraphs.
    Only paragraphs that contain a placeholder string are modified —
    everything else is left untouched.

    Returns the total number of individual replacements made.
    """
    count = 0

    for paragraph in doc.paragraphs:
        for key, value in placeholders.items():
            if _replace_placeholder_in_paragraph(paragraph, key, value):
                count += 1

    for table in doc.tables:
        count += _replace_placeholders_in_table(table, placeholders)

    for section in doc.sections:
        for header_footer in (section.header, section.footer):
            for paragraph in header_footer.paragraphs:
                for key, value in placeholders.items():
                    if _replace_placeholder_in_paragraph(paragraph, key, value):
                        count += 1

    return count


def _replace_placeholders_in_table(
    table: Table, placeholders: dict[str, str]
) -> int:
    """Replace placeholders inside every cell of *table*.

    Handles nested tables recursively.  Returns the replacement count.
    """
    count = 0
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for key, value in placeholders.items():
                    if _replace_placeholder_in_paragraph(paragraph, key, value):
                        count += 1
            for nested_table in cell.tables:
                count += _replace_placeholders_in_table(nested_table, placeholders)
    return count


# ---------------------------------------------------------------------------
# Dynamic table insertion
# ---------------------------------------------------------------------------

def _set_cell_border(cell: Any, **kwargs: dict) -> None:
    """Set borders on a table cell.

    Each keyword argument is a border name (``top``, ``bottom``, ``start``,
    ``end``) mapped to a dict of attributes:
    ``{"sz": "4", "val": "single", "color": "000000"}``.
    """
    tc = cell._element
    tc_pr = tc.find(qn("w:tcPr"))
    if tc_pr is None:
        tc_pr = OxmlElement("w:tcPr")
        tc.insert(0, tc_pr)

    tc_borders = tc_pr.find(qn("w:tcBorders"))
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)

    for edge, attrs in kwargs.items():
        element = OxmlElement(f"w:{edge}")
        for attr_name, attr_val in attrs.items():
            element.set(qn(f"w:{attr_name}"), str(attr_val))
        tc_borders.append(element)


def _style_table(table: Table) -> None:
    """Apply a clean, professional look to *table*.

    * Borders on all cells.
    * Bold white-on-dark header row.
    * Alternating light-grey shading on data rows.
    """
    border_attrs = {"sz": "4", "val": "single", "color": "BFBFBF", "space": "0"}

    for r_idx, row in enumerate(table.rows):
        for cell in row.cells:
            # Borders
            _set_cell_border(
                cell,
                top=border_attrs,
                bottom=border_attrs,
                start=border_attrs,
                end=border_attrs,
            )

            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)

                    if r_idx == 0:
                        # Header row: bold, white text
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

            if r_idx == 0:
                # Header background: dark blue-grey
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "4472C4")
                shading.set(qn("w:val"), "clear")
                cell._element.find(qn("w:tcPr")).append(shading) if cell._element.find(qn("w:tcPr")) is not None else None
                # Ensure tcPr exists
                tc_pr = cell._element.find(qn("w:tcPr"))
                if tc_pr is None:
                    tc_pr = OxmlElement("w:tcPr")
                    cell._element.insert(0, tc_pr)
                shading_el = OxmlElement("w:shd")
                shading_el.set(qn("w:fill"), "4472C4")
                shading_el.set(qn("w:val"), "clear")
                tc_pr.append(shading_el)

            elif r_idx % 2 == 0:
                # Alternating row shading
                tc_pr = cell._element.find(qn("w:tcPr"))
                if tc_pr is None:
                    tc_pr = OxmlElement("w:tcPr")
                    cell._element.insert(0, tc_pr)
                shading_el = OxmlElement("w:shd")
                shading_el.set(qn("w:fill"), "F2F2F2")
                shading_el.set(qn("w:val"), "clear")
                tc_pr.append(shading_el)


def _insert_table_at_paragraph(
    doc: Document,
    paragraph: Paragraph,
    headers: list[str],
    rows: list[list[str]],
) -> None:
    """Replace *paragraph* with a Word table containing *headers* and *rows*.

    The table is inserted at the exact position of the placeholder paragraph,
    which is then removed from the document body.
    """
    num_cols = len(headers)
    num_rows = 1 + len(rows)  # header row + data rows

    # Create the table
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Fill header row
    for c_idx, header in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = header

    # Fill data rows
    for r_idx, row_data in enumerate(rows):
        for c_idx, value in enumerate(row_data):
            if c_idx < num_cols:
                cell = table.cell(r_idx + 1, c_idx)
                cell.text = str(value)

    # Apply styling
    _style_table(table)

    # Move the table XML element to the position of the placeholder paragraph
    paragraph._element.addnext(table._tbl)

    # Remove the placeholder paragraph
    parent = paragraph._element.getparent()
    parent.remove(paragraph._element)

    # Remove the table from the end of the document (where add_table put it)
    # — it's already been moved via addnext above.
    # The table._tbl element was moved, so the trailing copy (if any) is gone.


def _process_table_placeholders(
    doc: Document, placeholders: dict[str, str]
) -> int:
    """Find and replace ``{{TABLE:KEY}}`` placeholders with Word tables.

    Returns the number of tables inserted.
    """
    count = 0

    # Build a snapshot of paragraphs to iterate safely while mutating.
    paragraphs_snapshot = list(doc.paragraphs)

    for paragraph in paragraphs_snapshot:
        text = paragraph.text.strip()
        match = _TABLE_PLACEHOLDER_RE.search(text)
        if not match:
            continue

        table_key = f"{{{{TABLE:{match.group(1)}}}}}"
        json_data = placeholders.get(table_key)

        if json_data is None:
            logger.warning("No data provided for table placeholder %s", table_key)
            continue

        try:
            table_data = json.loads(json_data) if isinstance(json_data, str) else json_data
        except json.JSONDecodeError:
            logger.error("Invalid JSON for table placeholder %s", table_key)
            continue

        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if not headers:
            logger.warning("Table placeholder %s has no headers", table_key)
            continue

        _insert_table_at_paragraph(doc, paragraph, headers, rows)
        count += 1
        logger.info("Inserted table for %s (%d cols × %d rows)", table_key, len(headers), len(rows))

    return count


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def generate_sow_document(
    output_gcs_uri: str,
    placeholders: dict[str, str],
) -> dict[str, Any]:
    """Generate a Statement of Work by merging placeholders into the DOCX template.

    The function loads the bundled ``SOW_Template.docx``, replaces every
    placeholder key found in *placeholders* with its value, and uploads
    the resulting ``.docx`` file to *output_gcs_uri*.

    Supports two types of placeholders:

    **Text placeholders** — e.g. ``{{SCOPE}}``.  The placeholder is replaced
    with the provided string.  Multi-line values (``\\n``) are rendered with
    DOCX line-breaks.

    **Table placeholders** — e.g. ``{{TABLE:MILESTONES}}``.  The placeholder
    paragraph is replaced with a styled Word table.  The value must be a JSON
    string with ``headers`` and ``rows`` keys::

        {"headers": ["Phase", "Duration"], "rows": [["Setup", "2 wks"]]}

    Args:
        output_gcs_uri: Target GCS URI for the final document
            (e.g. ``gs://bucket/output/Final_SOW.docx``).
        placeholders: Mapping of placeholder strings to their replacement
            text or table JSON.

    Returns:
        A dictionary with ``status`` and ``data`` on success, or
        ``status`` and ``error`` on failure.
    """
    try:
        if not _TEMPLATE_PATH.exists():
            msg = f"SOW template not found at {_TEMPLATE_PATH}"
            raise FileNotFoundError(msg)

        logger.info("Loading SOW template from %s", _TEMPLATE_PATH)
        doc = Document(str(_TEMPLATE_PATH))

        # 1. Process table placeholders first (they remove paragraphs).
        table_count = _process_table_placeholders(doc, placeholders)
        logger.info("Inserted %d dynamic table(s)", table_count)

        # 2. Process text placeholders.
        text_count = _replace_placeholders_in_document(doc, placeholders)
        logger.info("Replaced %d text placeholder(s)", text_count)

        # Save to a temporary file, then upload to GCS.
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        doc.save(str(tmp_path))
        logger.info("Saved merged document to %s", tmp_path)

        uploaded_uri = upload_file_to_gcs(tmp_path, output_gcs_uri)
        logger.info("Uploaded final SOW to %s", uploaded_uri)

        # Clean up temp file.
        tmp_path.unlink(missing_ok=True)

        return {
            "status": "success",
            "data": {
                "output_gcs_uri": uploaded_uri,
            },
        }

    except Exception as e:
        logger.error("Failed to generate SOW document: %s", e, exc_info=True)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import asyncio
    import sys
    import json
    import logging
    import argparse
    from typing import Any

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Generate a Statement of Work document.")
    parser.add_argument("--output_gcs_uri", required=True, help="GCS URI for the final document")
    parser.add_argument("--placeholders", required=True, help="JSON string of placeholders")
    args = parser.parse_args()

    placeholders = json.loads(args.placeholders)

    result = asyncio.run(generate_sow_document(args.output_gcs_uri, placeholders))

    if result["status"] == "error":
        logger.error("Failed to generate SOW document: %s", result["error"])
        sys.exit(1)

    logger.info("Generated SOW document: %s", result["data"]["output_gcs_uri"])
    sys.exit(0)
