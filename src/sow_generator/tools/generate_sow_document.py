"""Tool to generate a SOW document in DOCX format.
Placeholders in the template should use << >> format (e.g., <<PROJECT_NAME>>).
"""

import logging
import os
import json
import copy
import re
from typing import Any, Dict, List, Union, Tuple
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload
from google.cloud import storage
import google.auth
from google.auth.transport.requests import Request
import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
#         placeholders: Dictionary of placeholders to replace (e.g., {"<<SCOPE>>": "..."}).
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
    output_gcs_uri: str,
    drive_folder_id: str | None = None,
    font_name: str | None = None,
    font_size: int | None = None
) -> Dict[str, Any]:
    """
    Generates a Statement of Work (SOW) by reading a DOCX template from GCS,
    replacing placeholders, and uploading to Google Drive.

    Placeholders in the template should use << >> format (e.g., <<PROJECT_NAME>>).

    Args:
        template_gcs_uri: GCS URI to the DOCX template (gs://bucket/template.docx)
        placeholders: Dictionary mapping placeholder names to replacement values.
                     Keys should include delimiters (e.g., {"<<NAME>>": "Acme Corp"}).
                     Values can be strings or lists (for multiple bullet points).
        document_title: Name of the generated document
        output_gcs_uri: GCS URI where the final document should be saved (for backup)
        drive_folder_id: Google Drive folder ID where document should be uploaded
        font_name: Optional font name to override template font (e.g., 'Calibri', 'Arial')
        font_size: Optional font size in points to override template font size (e.g., 11, 12)

    Returns:
        Status, Google Drive URL, and GCS URI of generated document

    Example:
        placeholders = {
            "<<CLIENT_NAME>>": "**Acme Corp**",
            "<<PROJECT>>": "Cloud Migration",
            "<<DELIVERABLES>>": [
                "Architecture Design",
                "Implementation",
                "Testing"
            ]
        }
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
        for style in document.styles:
            print(f"style: {style.name}")

        # -------------------------
        # 3. Replace placeholders
        # -------------------------

        def parse_value(value):
            """Parse a value that might be a string or list."""
            if isinstance(value, list):
                return value
            # Check if it's a JSON array string
            if isinstance(value, str) and value.strip().startswith('['):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass
            return str(value)

        def parse_rich_text(text):
            """
            Parse markdown-like formatting in text.
            Supports: **bold**, *italic*, __underline__, ~~strikethrough~~
            Returns list of (text, formatting_dict) tuples.
            """
            if not isinstance(text, str):
                return [(str(text), {})]

            # Pattern to match formatting markers
            # Order matters: check longest patterns first
            pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|~~.*?~~)'

            parts = []
            last_end = 0

            for match in re.finditer(pattern, text):
                # Add unformatted text before this match
                if match.start() > last_end:
                    parts.append((text[last_end:match.start()], {}))

                matched_text = match.group(0)
                formatting = {}
                clean_text = matched_text

                # Bold: **text**
                if matched_text.startswith('**') and matched_text.endswith('**') and len(matched_text) > 4:
                    clean_text = matched_text[2:-2]
                    formatting['bold'] = True
                # Italic: *text*
                elif matched_text.startswith('*') and matched_text.endswith('*') and len(matched_text) > 2:
                    clean_text = matched_text[1:-1]
                    formatting['italic'] = True
                # Underline: __text__
                elif matched_text.startswith('__') and matched_text.endswith('__') and len(matched_text) > 4:
                    clean_text = matched_text[2:-2]
                    formatting['underline'] = True
                # Strikethrough: ~~text~~
                elif matched_text.startswith('~~') and matched_text.endswith('~~') and len(matched_text) > 4:
                    clean_text = matched_text[2:-2]
                    formatting['strike'] = True

                parts.append((clean_text, formatting))
                last_end = match.end()

            # Add remaining unformatted text
            if last_end < len(text):
                parts.append((text[last_end:], {}))

            # If no formatting was found, return the whole text
            if not parts:
                parts = [(text, {})]

            return parts

        def replace_text_simple(paragraph, key, value, use_custom_fonts=True):
            """Text replacement with rich text formatting support."""
            if key not in paragraph.text:
                return False

            # Get the base run for formatting reference
            base_run = paragraph.runs[0] if paragraph.runs else None

            # Get full text
            full_text = paragraph.text
            if key not in full_text:
                return False

            # Find the position of the placeholder
            placeholder_start = full_text.find(key)
            placeholder_end = placeholder_start + len(key)

            # Split text into: before placeholder, placeholder value, after placeholder
            text_before = full_text[:placeholder_start]
            text_after = full_text[placeholder_end:]

            # Clear existing runs
            for run in paragraph.runs:
                run._element.getparent().remove(run._element)

            # Add text before placeholder (preserve template formatting)
            if text_before:
                run_before = paragraph.add_run(text_before)
                if base_run:
                    run_before.font.name = base_run.font.name
                    run_before.font.size = base_run.font.size
                    run_before.font.bold = base_run.font.bold
                    run_before.font.italic = base_run.font.italic
                    run_before.font.underline = base_run.font.underline
                    if base_run.font.color.rgb:
                        run_before.font.color.rgb = base_run.font.color.rgb

            # Add replacement value (with custom font if specified)
            value_parts = parse_rich_text(value)
            for text, formatting in value_parts:
                if not text:
                    continue

                run = paragraph.add_run(text)

                # Apply fonts: use custom fonts only if use_custom_fonts=True and fonts are provided
                if base_run:
                    if use_custom_fonts and font_name:
                        run.font.name = font_name
                    else:
                        run.font.name = base_run.font.name
                    
                    if use_custom_fonts and font_size:
                        run.font.size = Pt(font_size)
                    else:
                        run.font.size = base_run.font.size
                    
                    if base_run.font.color.rgb:
                        run.font.color.rgb = base_run.font.color.rgb

                # Apply markdown formatting
                if formatting.get('bold'):
                    run.font.bold = True
                elif base_run and base_run.font.bold is not None:
                    run.font.bold = base_run.font.bold

                if formatting.get('italic'):
                    run.font.italic = True
                elif base_run and base_run.font.italic is not None:
                    run.font.italic = base_run.font.italic

                if formatting.get('underline'):
                    run.font.underline = True
                elif base_run and base_run.font.underline is not None:
                    run.font.underline = base_run.font.underline

                if formatting.get('strike'):
                    run.font.strike = True

            # Add text after placeholder (preserve template formatting)
            if text_after:
                run_after = paragraph.add_run(text_after)
                if base_run:
                    run_after.font.name = base_run.font.name
                    run_after.font.size = base_run.font.size
                    run_after.font.bold = base_run.font.bold
                    run_after.font.italic = base_run.font.italic
                    run_after.font.underline = base_run.font.underline
                    if base_run.font.color.rgb:
                        run_after.font.color.rgb = base_run.font.color.rgb

            return True


        def insert_paragraph_after(reference_para, value, parent_element, prefix="", suffix="", use_custom_fonts=True):
            """Insert a new paragraph after reference, copying its formatting and supporting rich text."""
            # Create new paragraph (empty for now)
            new_para = parent_element.add_paragraph()

            # Copy paragraph-level formatting
            if reference_para.style:
                new_para.style = reference_para.style
            new_para.alignment = reference_para.alignment

            # Copy paragraph format
            pf_src = reference_para.paragraph_format
            pf_dst = new_para.paragraph_format
            pf_dst.left_indent = pf_src.left_indent
            pf_dst.right_indent = pf_src.right_indent
            pf_dst.first_line_indent = pf_src.first_line_indent
            pf_dst.space_before = pf_src.space_before
            pf_dst.space_after = pf_src.space_after
            pf_dst.line_spacing = pf_src.line_spacing

            # Copy or apply bullet/numbering properties (critical for lists)
            # Access the underlying XML element to copy numbering properties
            ref_pPr = reference_para._element.get_or_add_pPr()
            new_pPr = new_para._element.get_or_add_pPr()

            # Check if reference paragraph has numbering
            ref_numPr = ref_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
            
            if ref_numPr is not None:
                # Copy existing numbering properties
                existing_numPr = new_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                if existing_numPr is not None:
                    new_pPr.remove(existing_numPr)
                new_numPr = copy.deepcopy(ref_numPr)
                new_pPr.append(new_numPr)
            else:
                # No bullets in template, apply default bullet style
                # Try to use 'List Bullet' style if available
                try:
                    new_para.style = 'List Bullet'
                except KeyError:
                    # If 'List Bullet' style doesn't exist, create bullet using numbering
                    from docx.oxml import parse_xml
                    from docx.oxml.ns import nsdecls
                    
                    # Create numbering properties for a bullet list
                    numPr_xml = f'''
                    <w:numPr {nsdecls('w')}>
                        <w:ilvl w:val="0"/>
                        <w:numId w:val="1"/>
                    </w:numPr>
                    '''
                    numPr = parse_xml(numPr_xml)
                    
                    # Remove any existing numPr
                    existing_numPr = new_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                    if existing_numPr is not None:
                        new_pPr.remove(existing_numPr)
                    
                    # Add the bullet numbering
                    new_pPr.append(numPr)

            # Get base run for formatting
            base_run = reference_para.runs[0] if reference_para.runs else None

            # Add text before (prefix) - preserve template formatting
            if prefix:
                run_before = new_para.add_run(prefix)
                if base_run:
                    run_before.font.name = base_run.font.name
                    run_before.font.size = base_run.font.size
                    run_before.font.bold = base_run.font.bold
                    run_before.font.italic = base_run.font.italic
                    run_before.font.underline = base_run.font.underline
                    if base_run.font.color.rgb:
                        run_before.font.color.rgb = base_run.font.color.rgb

            # Add replacement value (with custom font if specified)
            value_parts = parse_rich_text(value)
            for text, formatting in value_parts:
                if not text:
                    continue

                run = new_para.add_run(text)

                # Apply fonts: use custom fonts only if use_custom_fonts=True and fonts are provided
                if base_run:
                    if use_custom_fonts and font_name:
                        run.font.name = font_name
                    else:
                        run.font.name = base_run.font.name
                    
                    if use_custom_fonts and font_size:
                        run.font.size = Pt(font_size)
                    else:
                        run.font.size = base_run.font.size
                    
                    if base_run.font.color.rgb:
                        run.font.color.rgb = base_run.font.color.rgb

                # Apply markdown formatting
                if formatting.get('bold'):
                    run.font.bold = True
                elif base_run and base_run.font.bold is not None:
                    run.font.bold = base_run.font.bold

                if formatting.get('italic'):
                    run.font.italic = True
                elif base_run and base_run.font.italic is not None:
                    run.font.italic = base_run.font.italic

                if formatting.get('underline'):
                    run.font.underline = True
                elif base_run and base_run.font.underline is not None:
                    run.font.underline = base_run.font.underline

                if formatting.get('strike'):
                    run.font.strike = True

            # Add text after (suffix) - preserve template formatting
            if suffix:
                run_after = new_para.add_run(suffix)
                if base_run:
                    run_after.font.name = base_run.font.name
                    run_after.font.size = base_run.font.size
                    run_after.font.bold = base_run.font.bold
                    run_after.font.italic = base_run.font.italic
                    run_after.font.underline = base_run.font.underline
                    if base_run.font.color.rgb:
                        run_after.font.color.rgb = base_run.font.color.rgb

            # Move it to the right position in XML
            new_para._element.getparent().remove(new_para._element)
            reference_para._element.addnext(new_para._element)

            return new_para

        def flatten_nested_item(item, level=0):
            """
            Flatten a potentially nested array item into a list of (text, indent_level) tuples.

            Handles nested structure: [main_point, [sub_point_1, sub_point_2]]

            Args:
                item: Either a string or a nested array [main_text, [sub_items...]]
                level: Current indentation level (0 for main bullets, 1 for sub-bullets, etc.)

            Returns:
                List of (text, indent_level) tuples
            """
            if isinstance(item, str):
                # Simple string item
                return [(item.strip(), level)]
            elif isinstance(item, list):
                if len(item) == 0:
                    return []
                elif len(item) == 1:
                    # Single element array - treat as simple item
                    return flatten_nested_item(item[0], level)
                elif len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], list):
                    # Nested structure: [main_point, [sub_points]]
                    result = [(item[0].strip(), level)]
                    # Recursively flatten sub-items at increased indent level
                    for sub_item in item[1]:
                        result.extend(flatten_nested_item(sub_item, level + 1))
                    return result
                else:
                    # Array of items at same level
                    result = []
                    for sub_item in item:
                        result.extend(flatten_nested_item(sub_item, level))
                    return result
            else:
                # Fallback: convert to string
                return [(str(item).strip(), level)]

        def replace_text_with_list(paragraph, key, items, parent_element, use_custom_fonts=True):
            """Replace placeholder with multiple bullet points, supporting nested sub-bullets."""
            if key not in paragraph.text:
                return []

            full_text = paragraph.text
            placeholder_index = full_text.find(key)
            prefix = full_text[:placeholder_index]
            suffix = full_text[placeholder_index + len(key):]

            # Flatten the items list to handle nested arrays
            # This converts nested structures to (text, indent_level) tuples
            flattened_items = []
            for item in items:
                flattened_items.extend(flatten_nested_item(item))

            new_paras = []
            for i, (text, indent_level) in enumerate(flattened_items):
                if i == 0:
                    # Update the original paragraph
                    replace_text_simple(paragraph, key, text, use_custom_fonts)

                    # Ensure the first item has bullets too
                    para_pPr = paragraph._element.get_or_add_pPr()
                    para_numPr = para_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')

                    if para_numPr is None:
                        # No bullets, apply them
                        try:
                            paragraph.style = 'List Bullet'
                        except KeyError:
                            # Create bullet using numbering
                            from docx.oxml import parse_xml
                            from docx.oxml.ns import nsdecls

                            numPr_xml = f'''
                            <w:numPr {nsdecls('w')}>
                                <w:ilvl w:val="{indent_level}"/>
                                <w:numId w:val="1"/>
                            </w:numPr>
                            '''
                            numPr = parse_xml(numPr_xml)
                            existing = para_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                            if existing is not None:
                                para_pPr.remove(existing)
                            para_pPr.append(numPr)
                    else:
                        # Update indent level for existing numbering
                        ilvl_elem = para_numPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                        if ilvl_elem is not None:
                            ilvl_elem.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', str(indent_level))

                    new_paras.append(paragraph)
                else:
                    # Insert new paragraph with appropriate indent level
                    new_para = insert_paragraph_after(new_paras[-1], text, parent_element, prefix, suffix, use_custom_fonts)

                    # Set the indent level for sub-bullets
                    new_pPr = new_para._element.get_or_add_pPr()
                    new_numPr = new_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')

                    if new_numPr is not None:
                        # Update indent level
                        ilvl_elem = new_numPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                        if ilvl_elem is not None:
                            ilvl_elem.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', str(indent_level))

                    new_paras.append(new_para)

            return new_paras

        def replace_placeholders_in_paragraphs(paragraphs, parent_element, use_custom_fonts=True):
            """Replace all placeholders in paragraphs."""
            processed_ids = set()
            i = 0

            while i < len(paragraphs):
                para = paragraphs[i]
                para_id = id(para)

                if para_id not in processed_ids:
                    processed_ids.add(para_id)

                    # Check if this paragraph is the document title - preserve its fonts
                    para_is_title = False
                    if hasattr(para, 'style') and para.style and hasattr(para.style, 'name'):
                        # Only preserve fonts for the main Title style
                        if para.style.name == 'Title':
                            para_is_title = True
                    
                    # Determine whether to use custom fonts for this paragraph
                    use_fonts_for_para = use_custom_fonts and not para_is_title

                    for key, value in placeholders.items():
                        parsed_value = parse_value(value)

                        if isinstance(parsed_value, list) and len(parsed_value) > 0:
                            # Handle list values
                            new_paras = replace_text_with_list(para, key, parsed_value, parent_element, use_fonts_for_para)
                            for p in new_paras:
                                processed_ids.add(id(p))
                        else:
                            # Handle simple string replacement
                            replace_text_simple(para, key, str(parsed_value), use_fonts_for_para)

                i += 1

        # Replace in main document
        replace_placeholders_in_paragraphs(document.paragraphs, document)

        # Replace in tables
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_placeholders_in_paragraphs(cell.paragraphs, cell)

        # Replace in headers and footers
        for section in document.sections:
            # Replace in header (default/primary header)
            header = section.header
            replace_placeholders_in_paragraphs(header.paragraphs, header, use_custom_fonts=False)

            # Replace in header tables
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

            # Replace in footer (default/primary footer)
            footer = section.footer
            replace_placeholders_in_paragraphs(footer.paragraphs, footer, use_custom_fonts=False)

            # Replace in footer tables
            for table in footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

            # Replace in first page header (if different)
            if section.first_page_header:
                first_header = section.first_page_header
                replace_placeholders_in_paragraphs(first_header.paragraphs, first_header, use_custom_fonts=False)
                for table in first_header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

            # Replace in first page footer (if different)
            if section.first_page_footer:
                first_footer = section.first_page_footer
                replace_placeholders_in_paragraphs(first_footer.paragraphs, first_footer, use_custom_fonts=False)
                for table in first_footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

            # Replace in even page header (if different)
            if section.even_page_header:
                even_header = section.even_page_header
                replace_placeholders_in_paragraphs(even_header.paragraphs, even_header, use_custom_fonts=False)
                for table in even_header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

            # Replace in even page footer (if different)
            if section.even_page_footer:
                even_footer = section.even_page_footer
                replace_placeholders_in_paragraphs(even_footer.paragraphs, even_footer, use_custom_fonts=False)
                for table in even_footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            replace_placeholders_in_paragraphs(cell.paragraphs, cell, use_custom_fonts=False)

        # -------------------------
        # 4. Save modified doc
        # -------------------------

        output_stream = io.BytesIO()
        document.save(output_stream)
        output_stream.seek(0)

        # -------------------------
        # 5. Upload to Google Drive (if folder ID provided)
        # -------------------------

        drive_url = None
        if drive_folder_id:
            try:
                # Authenticate with Google Drive
                credentials, _ = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/drive.file"]
                )
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())

                drive_service = build("drive", "v3", credentials=credentials)

                # Reset stream position
                output_stream.seek(0)

                # Upload file to Google Drive
                file_metadata = {
                    "name": f"{document_title}.docx",
                    "parents": [drive_folder_id],
                    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }

                media = MediaIoBaseUpload(
                    output_stream,
                    mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    resumable=True
                )

                uploaded_file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, webViewLink"
                ).execute()

                drive_url = uploaded_file.get("webViewLink")
                logger.info(f"Uploaded to Google Drive: {drive_url}")

            except Exception as e:
                logger.error(f"Failed to upload to Google Drive: {e}", exc_info=True)
                # Continue even if Drive upload fails

        # -------------------------
        # 6. Upload to GCS (backup)
        # -------------------------

        output_bucket = output_gcs_uri.split("/")[2]
        output_path_prefix = "/".join(output_gcs_uri.split("/")[3:])

        output_bucket_obj = storage_client.bucket(output_bucket)

        final_blob_path = f"{output_path_prefix}{document_title}.docx"

        output_blob = output_bucket_obj.blob(final_blob_path)

        # Reset stream position for GCS upload
        output_stream.seek(0)

        output_blob.upload_from_file(
            output_stream,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        final_gcs_uri = f"gs://{output_bucket}/{final_blob_path}"
        logger.info(f"Uploaded to GCS: {final_gcs_uri}")

        return {
            "status": "success",
            "data": {
                "document_title": document_title,
                "gcs_uri": final_gcs_uri,
                "drive_url": drive_url
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate SOW document: {e}", exc_info=True)

        return {
            "status": "error",
            "error": str(e)
        }


# -------------------------
# Main test function
# -------------------------

async def main():
    """
    Test function to demonstrate usage of generate_sow_document.

    Before running:
    1. Set up a GCS bucket with a DOCX template containing placeholders
    2. Update the GCS URIs below with your actual bucket/paths
    3. Ensure you have GCS credentials configured
    """

    # Configure your GCS paths
    TEMPLATE_GCS_URI = "gs://agent_engine_depoly/sow-generator/sow-template/SOW Template.docx"
    OUTPUT_GCS_URI = "gs://agent_engine_depoly/sow-generator/generated-sows/test.docx"

    # Sample placeholders matching your template
    # Template should have placeholders like <<CLIENT_NAME>>, <<PROJECT_NAME>>, etc.
    sample_placeholders = {
        # Simple text replacements
        "<<CUSTOMER_NAME>>": "Acme Corporation",
        "<<CUSTOMER_SHORT_NAME>>": "Acme",
        "<<CUSTOMER_NAME_BOLD>>": "**Acme**",
        "<<TITLE>>": "Cloud Migration Initiative",
        "<<PROVISION_DATE>>": "13 March 2026",

        # Rich text examples
        "<<OPPORTUNITY>>": "This project aims to **migrate** critical workloads to the cloud, enabling *greater scalability* and __improved performance__.",

        "<<SOLUTION_OVERVIEW>>": "This is the solution overview.",

        "<<ACTIVITIES>>": ["This is activity 1", "This is activity 2", "This is activity 3"],

        # List replacements (will create bullet points)
        "<<DELIVERABLES>>": [
            "**Architecture Design Document** - Comprehensive cloud architecture blueprint",
            "Implementation Plan - Detailed migration roadmap",
            "Testing & Validation Report",
            "*Training Materials* for IT staff",
            "Post-Migration Support (90 days)"
        ],
        
        "<<IN_SCOPE>>": "In Scope",

        "<<IN_SCOPE_ACTIVITIES>>": [
            "Migration of production databases to Cloud SQL",
            "Implementation of Kubernetes clusters",
            "Setup of CI/CD pipelines",
            "Security hardening and compliance validation",
            "Performance testing and optimization"
        ],

        "<<OUT_OF_SCOPE>>": [
            "Legacy system decommissioning",
            "Third-party software licensing",
            "Hardware procurement",
            "~~On-premises infrastructure maintenance~~"
        ],
        
        "<<LIMITATIONS>>": "This is limitation",

        "<<SUCCESS_CRITERIA>>": ["This is success criteria 1", "This is success criteria 2", "This is success criteria 3"],
        

        "<<MILESTONES>>": [
            "**Phase 1**: Discovery & Assessment - Weeks 1-4",
            "**Phase 2**: Architecture Design - Weeks 5-8",
            "**Phase 3**: Implementation - Weeks 9-16",
            "**Phase 4**: Testing & Validation - Weeks 17-20",
            "**Phase 5**: Go-Live & Handover - Weeks 21-24"
        ],

        "<<ASSUMPTIONS>>": [
            "Client will provide timely access to all systems",
            "Necessary cloud credits are available",
            "Key stakeholders are available for weekly reviews",
            "Existing documentation is accurate and up-to-date"
        ],

        "<<RISKS>>": [
            "**High**: Data migration complexity - *Mitigation: Phased approach with rollback plan*",
            "**Medium**: Resource availability constraints",
            "**Low**: Third-party API compatibility issues"
        ]
    }

    print("=" * 70)
    print("SOW Document Generator - Test Execution")
    print("=" * 70)
    print(f"\nTemplate: {TEMPLATE_GCS_URI}")
    print(f"Output Location: {OUTPUT_GCS_URI}")
    print(f"Number of placeholders: {len(sample_placeholders)}")
    print("\nGenerating document...\n")

    # Generate the document
    result = await generate_sow_document(
        template_gcs_uri=TEMPLATE_GCS_URI,
        placeholders=sample_placeholders,
        document_title="SOW_Acme_Cloud_Migration_2026",
        output_gcs_uri=OUTPUT_GCS_URI,
        font_name="Plus Jakarta Sans",  # Optional: override template font
        font_size=10          # Optional: override template font size
    )

    # Display results
    print("=" * 70)
    print("Generation Result")
    print("=" * 70)

    if result["status"] == "success":
        print("✅ SUCCESS!")
        print(f"\nDocument Title: {result['data']['document_title']}")
        print(f"GCS URI: {result['data']['gcs_uri']}")
        print("\nYou can download the document using:")
        print(f"  gsutil cp {result['data']['gcs_uri']} ./")
    else:
        print("❌ FAILED!")
        print(f"Error: {result['error']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import asyncio

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run the async main function
    asyncio.run(main())