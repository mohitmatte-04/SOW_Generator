"""Tool to generate a SOW document in DOCX format.
Placeholders in the template should use << >> format (e.g., <<PROJECT_NAME>>).
"""

import logging
import os
import json
import copy
import re
from typing import Any, Dict, List, Union, Tuple, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaInMemoryUpload
from google.cloud import storage
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)


# -------------------------
# Helper functions for document processing
# -------------------------

def _parse_value(value):
    """Parse a value that might be a string, list, or dict."""
    if isinstance(value, (list, dict)):
        return value
    # Check if it's a JSON array or object string
    if isinstance(value, str):
        stripped_value = value.strip()
        if stripped_value.startswith('[') or stripped_value.startswith('{'):
            try:
                parsed = json.loads(stripped_value)
                if isinstance(parsed, (list, dict)):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
    return str(value)


def _parse_rich_text(text):
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


def _replace_text_simple(paragraph, key, value, font_name=None, font_size=None, use_custom_fonts=True):
    """
    Text replacement with rich text formatting support.
    Preserves images (logos) in paragraphs while replacing text.
    """
    if key not in paragraph.text:
        return False

    # Get the base run for formatting reference (prefer non-image runs)
    base_run = None
    for run in paragraph.runs:
        # Skip runs that contain images
        if not (run._element.xpath('.//w:drawing') or run._element.xpath('.//w:pict')):
            base_run = run
            break

    # Fallback to first run if all runs contain images
    if not base_run and paragraph.runs:
        base_run = paragraph.runs[0]

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

    # Check if paragraph contains images - if so, use different strategy
    has_images = False
    image_runs = []
    for run in paragraph.runs:
        # Check if run contains an image (inline shape or drawing)
        if run._element.xpath('.//w:drawing') or run._element.xpath('.//w:pict'):
            has_images = True
            image_runs.append(run)

    if has_images:
        # For paragraphs with images, use careful run-by-run replacement
        # This preserves all non-text elements (images, drawings) perfectly

        p_element = paragraph._element

        # Find the run(s) that contain the placeholder
        target_run_index = -1
        for idx, run in enumerate(paragraph.runs):
            # Skip image runs
            if run._element.xpath('.//w:drawing') or run._element.xpath('.//w:pict'):
                continue

            if key in run.text:
                target_run_index = idx
                break

        if target_run_index == -1:
            return False

        target_run = paragraph.runs[target_run_index]
        run_text = target_run.text

        # Check if value has rich formatting
        value_parts = _parse_rich_text(value)
        needs_rich_formatting = any(fmt for _, fmt in value_parts if fmt)

        if not needs_rich_formatting and run_text.strip() == key.strip():
            # Simple case: whole run is the placeholder, no formatting needed
            target_run.text = value

            if use_custom_fonts:
                if font_name:
                    target_run.font.name = font_name
                if font_size:
                    target_run.font.size = Pt(font_size)

            return True

        # Complex case: need to handle rich formatting or mixed text
        # Replace the text in the run, then add new runs after it for rich parts

        # Calculate text parts
        idx_in_run = run_text.find(key)
        text_before_in_run = run_text[:idx_in_run]
        text_after_in_run = run_text[idx_in_run + len(key):]

        # Update the target run with text before placeholder
        target_run.text = text_before_in_run if text_before_in_run else ""

        # Insert new runs after the target run for the value and remaining text
        run_element = target_run._element

        # Add runs for the replacement value (with rich formatting)
        for text, formatting in value_parts:
            if not text:
                continue

            new_run = paragraph.add_run(text)

            # Copy base formatting from target run
            new_run.font.name = target_run.font.name
            new_run.font.size = target_run.font.size
            if target_run.font.color.rgb:
                new_run.font.color.rgb = target_run.font.color.rgb

            # Apply custom fonts if specified
            if use_custom_fonts:
                if font_name:
                    new_run.font.name = font_name
                if font_size:
                    new_run.font.size = Pt(font_size)

            # Apply markdown formatting
            if formatting.get('bold'):
                new_run.font.bold = True
            elif target_run.font.bold is not None:
                new_run.font.bold = target_run.font.bold

            if formatting.get('italic'):
                new_run.font.italic = True
            elif target_run.font.italic is not None:
                new_run.font.italic = target_run.font.italic

            if formatting.get('underline'):
                new_run.font.underline = True
            elif target_run.font.underline is not None:
                new_run.font.underline = target_run.font.underline

            if formatting.get('strike'):
                new_run.font.strike = True

            # Move the new run to come right after the target run
            new_run._element.getparent().remove(new_run._element)
            run_element.addnext(new_run._element)
            run_element = new_run._element

        # Add text after placeholder if any
        if text_after_in_run:
            after_run = paragraph.add_run(text_after_in_run)
            after_run.font.name = target_run.font.name
            after_run.font.size = target_run.font.size
            after_run.font.bold = target_run.font.bold
            after_run.font.italic = target_run.font.italic
            after_run.font.underline = target_run.font.underline
            if target_run.font.color.rgb:
                after_run.font.color.rgb = target_run.font.color.rgb

            # Move it to the right position
            after_run._element.getparent().remove(after_run._element)
            run_element.addnext(after_run._element)

        return True

    # For paragraphs without images, use the original strategy
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
    value_parts = _parse_rich_text(value)
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


def _insert_paragraph_after(reference_para, value, parent_element, prefix="", suffix="", font_name=None, font_size=None, use_custom_fonts=True):
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
    value_parts = _parse_rich_text(value)
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


def _flatten_nested_item(item, level=0):
    """
    Flatten a potentially nested array or dictionary item into a list of (text, indent_level) tuples.

    Handles nested structure:
    - Lists: [main_point, [sub_point_1, sub_point_2]]
    - Dicts: {"Section 1": ["Point 1", {"Sub-section": ["Sub-point"]}]}

    Args:
        item: Either a string, a dictionary, or a nested array
        level: Current indentation level (0 for main bullets, 1 for sub-bullets, etc.)

    Returns:
        List of (text, indent_level) tuples
    """
    if isinstance(item, str):
        # Simple string item
        return [(item.strip(), level)]
    elif isinstance(item, dict):
        result = []
        for key, value in item.items():
            # Add the key as a point at current level
            result.append((str(key).strip(), level))
            # Process the values at the next indent level
            result.extend(_flatten_nested_item(value, level + 1))
        return result
    elif isinstance(item, list):
        if len(item) == 0:
            return []
        elif len(item) == 1:
            # Single element array - treat as simple item
            return _flatten_nested_item(item[0], level)
        elif len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], (list, dict)):
            # Nested structure: [main_point, [sub_points]] or [main_point, {sub_points}]
            result = [(item[0].strip(), level)]
            # Recursively flatten sub-items at increased indent level
            if isinstance(item[1], list):
                for sub_item in item[1]:
                    result.extend(_flatten_nested_item(sub_item, level + 1))
            else:
                result.extend(_flatten_nested_item(item[1], level + 1))
            return result
        else:
            # Array of items at same level
            result = []
            for sub_item in item:
                result.extend(_flatten_nested_item(sub_item, level))
            return result
    else:
        # Fallback: convert to string
        return [(str(item).strip(), level)]


def _replace_text_with_list(paragraph, key, items, parent_element, font_name=None, font_size=None, use_custom_fonts=True):
    """Replace placeholder with multiple bullet points, supporting nested sub-bullets."""
    from docx.shared import Inches, Pt
    
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
        flattened_items.extend(_flatten_nested_item(item))

    new_paras = []
    from docx.shared import Inches

    for i, (text, indent_level) in enumerate(flattened_items):
        if i == 0:
            # Update the original paragraph
            _replace_text_simple(paragraph, key, text, font_name, font_size, use_custom_fonts)

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
                        <w:ilvl w:val="0"/>
                        <w:numId w:val="1"/>
                    </w:numPr>
                    '''
                    numPr = parse_xml(numPr_xml)
                    existing = para_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                    if existing is not None:
                        para_pPr.remove(existing)
                    para_pPr.append(numPr)
            else:
                # Force ilvl to 0 so the bullet style is identical for all items
                ilvl_elem = para_numPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                if ilvl_elem is not None:
                    ilvl_elem.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', str(indent_level))

            # Reset paragraph indentation to ensure consistency across all sections
            # The template may have different indents for different placeholders
            paragraph.paragraph_format.left_indent = None
            paragraph.paragraph_format.first_line_indent = None


            # The ilvl (indent level) now handles all bullet positioning automatically

            new_paras.append(paragraph)
        else:
            # Insert new paragraph with formatting copied from prior paragraph
            new_para = _insert_paragraph_after(new_paras[-1], text, parent_element, prefix, suffix, font_name, font_size, use_custom_fonts)

            # Enforce same bullet type by keeping level 0
            new_pPr = new_para._element.get_or_add_pPr()
            new_numPr = new_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')

            if new_numPr is not None:
                ilvl_elem = new_numPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                if ilvl_elem is not None:
                    ilvl_elem.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val',  str(indent_level))

            # Reset paragraph indentation to ensure consistency across all sections
            # The template may have different indents for different placeholders
            new_para.paragraph_format.left_indent = None
            new_para.paragraph_format.first_line_indent = None

            # The ilvl (indent level) now handles all bullet positioning automatically

            new_paras.append(new_para)

    return new_paras


def _replace_placeholders_in_paragraphs(paragraphs, parent_element, placeholders, font_name=None, font_size=None, use_custom_fonts=True):
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
                parsed_value = _parse_value(value)

                # Check if placeholder exists in this paragraph
                if key in para.text:
                    logger.info(f"Found placeholder {repr(key)} in paragraph: {para.text[:100]}...")

                if isinstance(parsed_value, (list, dict)) and len(parsed_value) > 0:
                    # Handle list and dict values
                    items_to_process = parsed_value if isinstance(parsed_value, list) else [parsed_value]
                    new_paras = _replace_text_with_list(para, key, items_to_process, parent_element, font_name, font_size, use_fonts_for_para)
                    if len(new_paras) > 0:
                        logger.info(f"Replaced {repr(key)} with structured items")
                    for p in new_paras:
                        processed_ids.add(id(p))
                else:
                    # Handle simple string replacement
                    replaced = _replace_text_simple(para, key, str(parsed_value), font_name, font_size, use_fonts_for_para)
                    if replaced:
                        logger.info(f"Replaced {repr(key)} with string value")

        i += 1


def _process_document_placeholders(document, placeholders, font_name=None, font_size=None):
    """
    Process all placeholders in a Document object (main content, tables, headers, footers).

    Images (such as logos in headers) are automatically preserved during text replacement.

    Args:
        document: python-docx Document object
        placeholders: Dictionary mapping placeholder names to values
        font_name: Optional font name override
        font_size: Optional font size override
    """
    # Replace in main document
    _replace_placeholders_in_paragraphs(document.paragraphs, document, placeholders, font_name, font_size)

    # Replace in tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size)

    # Replace in headers and footers
    for section in document.sections:
        # Replace in header (default/primary header)
        header = section.header
        _replace_placeholders_in_paragraphs(header.paragraphs, header, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in header tables
        for table in header.tables:
            for row in table.rows:
                for cell in row.cells:
                    _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in footer (default/primary footer)
        footer = section.footer
        _replace_placeholders_in_paragraphs(footer.paragraphs, footer, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in footer tables
        for table in footer.tables:
            for row in table.rows:
                for cell in row.cells:
                    _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in first page header (if different)
        if section.first_page_header:
            first_header = section.first_page_header
            _replace_placeholders_in_paragraphs(first_header.paragraphs, first_header, placeholders, font_name, font_size, use_custom_fonts=False)
            for table in first_header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in first page footer (if different)
        if section.first_page_footer:
            first_footer = section.first_page_footer
            _replace_placeholders_in_paragraphs(first_footer.paragraphs, first_footer, placeholders, font_name, font_size, use_custom_fonts=False)
            for table in first_footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in even page header (if different)
        if section.even_page_header:
            even_header = section.even_page_header
            _replace_placeholders_in_paragraphs(even_header.paragraphs, even_header, placeholders, font_name, font_size, use_custom_fonts=False)
            for table in even_header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)

        # Replace in even page footer (if different)
        if section.even_page_footer:
            even_footer = section.even_page_footer
            _replace_placeholders_in_paragraphs(even_footer.paragraphs, even_footer, placeholders, font_name, font_size, use_custom_fonts=False)
            for table in even_footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        _replace_placeholders_in_paragraphs(cell.paragraphs, cell, placeholders, font_name, font_size, use_custom_fonts=False)


# -------------------------
# Main functions
# -------------------------

async def upload_to_google_drive(
    document_stream: io.BytesIO,
    document_title: str,
    service_account_key_path: str,
    drive_folder_id: Optional[str] = None,
    share_with_emails: Optional[List[str]] = None,
    make_public: bool = False
) -> Dict[str, Any]:
    """
    Uploads a document to Google Drive using service account credentials.

    Args:
        document_stream: BytesIO stream containing the document data
        document_title: Name of the document (should include .docx extension)
        service_account_key_path: Path to the service account JSON key file
        drive_folder_id: Optional Google Drive folder ID to upload to. If None, uploads to root.
        share_with_emails: Optional list of email addresses to share the document with (as editors)
        make_public: If True, makes the document publicly readable (anyone with link can view)

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - data: Dict with file_id, web_view_link, web_content_link (if success)
            - error: Error message (if error)

    Example:
        result = await upload_to_google_drive(
            document_stream=output_stream,
            document_title="SOW_Acme_2026.docx",
            credentials="/path/to/service-account-key.json or key json",
            drive_folder_id="1abc123def456",
            share_with_emails=["user@example.com"],
            make_public=False
        )
    """
    try:
        scopes=['https://www.googleapis.com/auth/drive']
        # Reset stream position
        document_stream.seek(0)
        # Handle different credential formats
        if isinstance(credentials, dict):
            # Already a parsed JSON dict
            creds = service_account.Credentials.from_service_account_info(
                credentials,
                scopes=scopes
            )
        elif isinstance(credentials, (str, Path)):
            # Check if it's a file path or JSON string
            credentials_path = Path(credentials) if isinstance(credentials, str) else credentials

            if credentials_path.exists() and credentials_path.is_file():
                # It's a file path
                creds = service_account.Credentials.from_service_account_file(
                    str(credentials),
                    scopes=scopes
                )
            else:
                # Assume it's a JSON string
                try:
                    credentials_dict = json.loads(str(credentials))
                    creds = service_account.Credentials.from_service_account_info(
                        credentials_dict,
                        scopes=scopes
                    )
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid credentials: not a valid file path or JSON string: {e}"
                    ) from e
        else:
            raise TypeError(
                f"credentials must be str, Path, or dict, got {type(credentials)}"
            )

        # Build Drive API service
        drive_service = build('drive', 'v3', credentials=creds)

        # Prepare file metadata
        file_metadata = {
            'name': document_title,
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        # Add parent folder if specified
        if drive_folder_id:
            file_metadata['parents'] = [drive_folder_id]

        # Create media upload from stream
        media = MediaInMemoryUpload(
            document_stream.read(),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )

        # Upload file
        logger.info(f"Uploading document '{document_title}' to Google Drive...")
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, webContentLink'
        ).execute()

        file_id = file.get('id')
        logger.info(f"Document uploaded successfully. File ID: {file_id}")

        # Handle sharing permissions
        if share_with_emails:
            for email in share_with_emails:
                try:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    drive_service.permissions().create(
                        fileId=file_id,
                        body=permission,
                        sendNotificationEmail=True
                    ).execute()
                    logger.info(f"Shared document with {email}")
                except Exception as e:
                    logger.warning(f"Failed to share with {email}: {e}")

        # Make public if requested
        if make_public:
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                drive_service.permissions().create(
                    fileId=file_id,
                    body=permission
                ).execute()
                logger.info("Document made publicly accessible")
            except Exception as e:
                logger.warning(f"Failed to make document public: {e}")

        return {
            "status": "success",
            "data": {
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "web_view_link": file.get('webViewLink'),
                "web_content_link": file.get('webContentLink')
            }
        }

    except Exception as e:
        logger.error(f"Failed to upload document to Google Drive: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


async def generate_sow_document(
    template_gcs_uri: str,
    placeholders: Dict[str, str],
    document_title: str,
    output_gcs_uri: str,
    font_name: str | None = None,
    font_size: int | None = None
) -> Dict[str, Any]:
    """
    Generates a Statement of Work (SOW) by reading a DOCX template from GCS,
    replacing placeholders, and writing the final document back to GCS.

    Placeholders in the template should use << >> format (e.g., <<PROJECT_NAME>>).

    Args:
        template_gcs_uri: GCS URI to the DOCX template (gs://bucket/template.docx)
        placeholders: Dictionary mapping placeholder names to replacement values.
                     Keys should include delimiters (e.g., {"<<NAME>>": "Acme Corp"}).
                     Values can be strings or lists (for multiple bullet points).
        document_title: Name of the generated document
        output_gcs_uri: GCS URI where the final document should be saved
        font_name: Optional font name to override template font (e.g., 'Calibri', 'Arial')
        font_size: Optional font size in points to override template font size (e.g., 11, 12)

    Returns:
        Status and GCS URI of generated document

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
    logger.info("=" * 80)
    logger.info("generate_sow_document called")
    logger.info(f"template_gcs_uri: {template_gcs_uri}")
    logger.info(f"document_title: {document_title}")
    logger.info(f"output_gcs_uri: {output_gcs_uri}")
    logger.info(f"font_name: {font_name}, font_size: {font_size}")
    logger.info(f"Number of placeholders: {len(placeholders)}")
    logger.info("Placeholders keys:")
    for key in placeholders.keys():
        logger.info(f"  - {repr(key)}")
    logger.info("=" * 80)

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
        # 3. Replace placeholders using helper functions
        # -------------------------

        _process_document_placeholders(document, placeholders, font_name, font_size)

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


async def generate_and_upload_sow_to_drive(
    template_gcs_uri: str,
    placeholders: Dict[str, str],
    document_title: str,
    service_account_key_path: str,
    drive_folder_id: Optional[str] = None,
    share_with_emails: Optional[List[str]] = None,
    make_public: bool = False,
    font_name: str | None = None,
    font_size: int | None = None
) -> Dict[str, Any]:
    """
    Generates a SOW document from a GCS template and uploads it directly to Google Drive.
    This is a convenience function that combines document generation and Drive upload.

    Args:
        template_gcs_uri: GCS URI to the DOCX template (gs://bucket/template.docx)
        placeholders: Dictionary mapping placeholder names to replacement values
        document_title: Name of the generated document (without .docx extension)
        service_account_key_path: Path to the service account JSON key file
        drive_folder_id: Optional Google Drive folder ID to upload to
        share_with_emails: Optional list of email addresses to share with (as editors)
        make_public: If True, makes the document publicly readable
        font_name: Optional font name to override template font
        font_size: Optional font size in points to override template font size

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - data: Dict with Google Drive file info (if success)
            - error: Error message (if error)

    Example:
        result = await generate_and_upload_sow_to_drive(
            template_gcs_uri="gs://bucket/template.docx",
            placeholders={"<<CLIENT_NAME>>": "Acme Corp"},
            document_title="SOW_Acme_2026",
            service_account_key_path="/path/to/key.json",
            drive_folder_id="1abc123",
            share_with_emails=["client@example.com"]
        )
    """
    try:
        # First, generate the document to GCS (temporary location)
        temp_gcs_output = "gs://temp-bucket/temp-output"  # This won't actually be used

        # Generate document in memory
        storage_client = storage.Client()

        template_bucket = template_gcs_uri.split("/")[2]
        template_blob_path = "/".join(template_gcs_uri.split("/")[3:])

        bucket = storage_client.bucket(template_bucket)
        blob = bucket.blob(template_blob_path)

        template_stream = io.BytesIO()
        blob.download_to_file(template_stream)
        template_stream.seek(0)

        document = Document(template_stream)

        # -------------------------
        # 2. Replace placeholders using shared helper functions
        # -------------------------
        logger.info("Processing placeholders...")
        _process_document_placeholders(document, placeholders, font_name, font_size)

        # -------------------------
        # 3. Save document to stream
        # -------------------------
        logger.info("Saving document to stream...")
        output_stream = io.BytesIO()
        document.save(output_stream)
        output_stream.seek(0)

        # -------------------------
        # 4. Upload to Google Drive
        # -------------------------
        document_title_with_ext = f"{document_title}.docx" if not document_title.endswith('.docx') else document_title

        logger.info("Uploading to Google Drive...")
        drive_result = await upload_to_google_drive(
            document_stream=output_stream,
            document_title=document_title_with_ext,
            credentials=os.getenv("sow-generator-sa"),
            drive_folder_id=os.getenv("sow_drive_folder_id"),
            share_with_emails=share_with_emails,
            make_public=False
        )

        if drive_result["status"] == "error":
            return drive_result

        return {
            "status": "success",
            "data": {
                "document_title": document_title_with_ext,
                "google_drive": drive_result["data"]
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate and upload SOW: {e}", exc_info=True)
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