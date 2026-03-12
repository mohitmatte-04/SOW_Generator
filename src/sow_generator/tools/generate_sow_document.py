"""Tool to generate a SOW document with rich formatting and store it in GCS."""

import io
import logging
import re
from datetime import UTC, datetime
from typing import Any

from docx import Document
from docx.shared import Inches, Pt
from google.cloud import storage

logger = logging.getLogger(__name__)


def _sanitize_filename(title: str) -> str:
    """Convert a document title to a safe filename."""
    safe = re.sub(r"[^\w\s-]", "", title)
    safe = re.sub(r"[\s]+", "_", safe.strip())
    return safe


# ---------------------------------------------------------------------------
# Rich-text helpers
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")


def _add_formatted_runs(paragraph, text: str) -> None:
    """Parse inline markdown (**bold**, *italic*) and add styled runs.

    Handles intermixed bold, italic, and plain text segments.
    """
    # Tokenise the text into segments: bold, italic, or plain
    # Pattern finds **bold** and *italic* spans
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*([^*]+?)\*)")
    last_end = 0

    for m in pattern.finditer(text):
        # Plain text before this match
        if m.start() > last_end:
            paragraph.add_run(text[last_end : m.start()])

        if m.group(2):  # **bold**
            run = paragraph.add_run(m.group(2))
            run.bold = True
        elif m.group(3):  # *italic*
            run = paragraph.add_run(m.group(3))
            run.italic = True

        last_end = m.end()

    # Trailing plain text
    if last_end < len(text):
        paragraph.add_run(text[last_end:])


def _set_bullet_style(paragraph) -> None:
    """Apply a bullet list style to a paragraph via XML manipulation.

    Works even when the template doesn't contain a 'List Bullet' style
    by injecting the correct numbering XML directly.
    """
    try:
        paragraph.style = paragraph.part.document.styles["List Bullet"]
    except KeyError:
        # Fallback: manually set indentation for a bullet-like look
        pf = paragraph.paragraph_format
        pf.left_indent = Inches(0.5)
        pf.first_line_indent = Inches(-0.25)
        # Prepend bullet character if not already present
        if paragraph.runs and not paragraph.runs[0].text.startswith("•"):
            paragraph.runs[0].text = "• " + paragraph.runs[0].text


def _replace_placeholder_with_rich_content(
    doc: Document,
    placeholder: str,
    content: str,
) -> bool:
    """Find a placeholder paragraph and replace it with rich-formatted content.

    The content string uses simple markdown conventions:
    - Lines starting with "• " or "- " become bullet paragraphs
    - **text** becomes bold
    - *text* becomes italic
    - Blank lines become paragraph breaks
    - Other lines become normal paragraphs

    Returns True if the placeholder was found and replaced.
    """
    found = False

    for paragraph in doc.paragraphs:
        if placeholder not in paragraph.text:
            continue

        found = True
        # Capture the style of the placeholder paragraph as base
        base_style = paragraph.style

        # Clear the placeholder paragraph
        paragraph.clear()

        # Split content into lines
        lines = content.split("\n")
        first_line = True

        for line in lines:
            stripped = line.strip()

            # Skip empty lines (paragraph breaks are implicit)
            if not stripped:
                continue

            if first_line:
                # Reuse the placeholder paragraph for the first line
                target_para = paragraph
                first_line = False
            else:
                # Insert a new paragraph after the current one
                new_para = doc.add_paragraph()
                # Move the new paragraph to right after the current block
                paragraph._element.addnext(new_para._element)
                target_para = new_para
                paragraph = new_para  # Track for next insertion

            # Detect bullet lines
            is_bullet = stripped.startswith(("• ", "- ", "* "))
            if is_bullet:
                # Remove the bullet marker from text
                bullet_text = re.sub(r"^[•\-\*]\s+", "", stripped)
                _add_formatted_runs(target_para, bullet_text)
                _set_bullet_style(target_para)
            else:
                # Normal paragraph with inline formatting
                _add_formatted_runs(target_para, stripped)
                target_para.style = base_style

            # Set consistent font size
            for run in target_para.runs:
                if run.font.size is None:
                    run.font.size = Pt(11)

        break  # Only replace the first occurrence

    return found


def _replace_placeholder_in_tables(
    doc: Document,
    placeholder: str,
    content: str,
) -> None:
    """Replace placeholders found inside table cells with rich content."""
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if placeholder in paragraph.text:
                        paragraph.clear()
                        _add_formatted_runs(paragraph, content)


async def generate_sow_document(
    template_gcs_uri: str,
    placeholders: dict[str, str],
    document_title: str = "Generated Statement of Work",
    output_gcs_bucket: str = "sow-generator-testing-phase",
    output_gcs_folder: str = "sow",
) -> dict[str, Any]:
    """Generate a SOW by replacing placeholders with rich-formatted content.

    Downloads a .docx template from GCS, replaces ``<<PLACEHOLDER>>`` tags
    with professionally formatted content (bullets, bold, italic,
    indentation), and uploads the final document back to GCS.

    Args:
        template_gcs_uri: GCS URI to the .docx template
            (e.g., ``gs://bucket/template.docx``).
        placeholders: Dictionary mapping placeholder tags to expanded
            content strings. Content may use simple markdown:
            ``**bold**``, ``*italic*``, and lines starting with
            ``• `` / ``- `` for bullets.
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
            return {
                "status": "error",
                "error": "Invalid template GCS URI.",
            }

        parts = template_gcs_uri.replace("gs://", "").split("/", 1)
        if len(parts) != 2:  # noqa: PLR2004
            return {
                "status": "error",
                "error": "Invalid template GCS URI format.",
            }

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

        # 2. Open the .docx template
        doc = Document(io.BytesIO(template_bytes))

        # 3. Replace each placeholder with rich-formatted content
        for key, value in placeholders.items():
            # Try body paragraphs first (with rich formatting)
            replaced = _replace_placeholder_with_rich_content(
                doc, key, value
            )
            if not replaced:
                # Fallback: check inside tables
                _replace_placeholder_in_tables(doc, key, value)

        # 4. Save modified document to bytes
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        # 5. Upload to GCS
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        safe_title = _sanitize_filename(document_title)
        output_blob_name = (
            f"{output_gcs_folder}/{safe_title}_{timestamp}.docx"
        )

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
        return {
            "status": "error",
            "error": "Failed to generate SOW document.",
        }
