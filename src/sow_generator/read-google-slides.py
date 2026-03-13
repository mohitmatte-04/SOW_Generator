"""
Production-grade Google Slides content extractor.
Extracts titles, bullet points, tables, speaker notes, and maintains element hierarchy.
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
]

SERVICE_ACCOUNT_FILE = "service_account.json"
FOLDER_ID = "1aAvRRCZ_unwkt38MZfA-_mraBV-RsZXb"
FILE_NAME = "Albertsons Proposal"


class ElementType(Enum):
    """Types of elements in a slide."""
    TITLE = "title"
    SUBTITLE = "subtitle"
    BODY = "body"
    TABLE = "table"
    IMAGE = "image"
    SHAPE = "shape"
    LINE = "line"
    GROUP = "group"
    SPEAKER_NOTES = "speaker_notes"
    UNKNOWN = "unknown"


@dataclass
class TextStyle:
    """Text styling information."""
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    foreground_color: Optional[Dict[str, Any]] = None
    background_color: Optional[Dict[str, Any]] = None
    link: Optional[str] = None


@dataclass
class ParagraphStyle:
    """Paragraph styling and structure."""
    indent_level: int = 0
    alignment: str = "START"
    line_spacing: Optional[float] = None
    direction: str = "LEFT_TO_RIGHT"
    spacing_mode: Optional[str] = None


@dataclass
class BulletInfo:
    """Bullet/list information."""
    list_id: Optional[str] = None
    nesting_level: int = 0
    bullet_style: str = "●"
    list_properties: Optional[Dict[str, Any]] = None


@dataclass
class TextRun:
    """Individual text run with styling."""
    content: str
    text_style: TextStyle
    paragraph_style: ParagraphStyle
    bullet_info: Optional[BulletInfo] = None


@dataclass
class TableCell:
    """Table cell content."""
    row_index: int
    col_index: int
    text_content: str
    row_span: int = 1
    col_span: int = 1
    text_runs: List[TextRun] = None


@dataclass
class Table:
    """Table structure."""
    rows: int
    columns: int
    cells: List[TableCell]

    def to_dict(self):
        return {
            "rows": self.rows,
            "columns": self.columns,
            "cells": [asdict(cell) for cell in self.cells]
        }


@dataclass
class SlideElement:
    """Base slide element."""
    element_id: str
    element_type: ElementType
    transform: Optional[Dict[str, Any]] = None
    size: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = None

    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []


@dataclass
class TextElement(SlideElement):
    """Text-based element (title, body, etc.)."""
    text_runs: List[TextRun] = None
    raw_text: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.text_runs is None:
            self.text_runs = []


@dataclass
class TableElement(SlideElement):
    """Table element."""
    table: Table = None


@dataclass
class ImageElement(SlideElement):
    """Image element."""
    content_url: Optional[str] = None
    source_url: Optional[str] = None
    image_properties: Optional[Dict[str, Any]] = None


@dataclass
class GroupElement(SlideElement):
    """Grouped elements container."""
    pass


@dataclass
class SlideContent:
    """Complete slide content with all elements."""
    slide_number: int
    slide_id: str
    title: Optional[str] = None
    elements: List[SlideElement] = None
    speaker_notes: Optional[str] = None
    layout_type: Optional[str] = None

    def __post_init__(self):
        if self.elements is None:
            self.elements = []


class GoogleSlidesExtractor:
    """Production-grade Google Slides content extractor."""

    def __init__(self, service_account_file: str):
        """Initialize the extractor with service account credentials."""
        self.service_account_file = service_account_file
        self.drive_service = None
        self.slides_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize Google API services."""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=SCOPES
            )
            self.drive_service = build("drive", "v3", credentials=creds)
            self.slides_service = build("slides", "v1", credentials=creds)
            logger.info("Successfully initialized Google API services")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def find_presentation(self, folder_id: str, file_name: str) -> str:
        """Find a presentation by name in a specific folder."""
        try:
            query = (
                f"name='{file_name}' and "
                "mimeType='application/vnd.google-apps.presentation' and "
                f"'{folder_id}' in parents"
            )

            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()

            files = results.get("files", [])

            if not files:
                raise ValueError(f"Presentation '{file_name}' not found in folder")

            logger.info(f"Found presentation: {files[0]['name']} (ID: {files[0]['id']})")
            return files[0]["id"]
        except Exception as e:
            logger.error(f"Error finding presentation: {e}")
            raise

    def _extract_text_style(self, style_dict: Dict[str, Any]) -> TextStyle:
        """Extract text style from API response."""
        return TextStyle(
            bold=style_dict.get("bold", False),
            italic=style_dict.get("italic", False),
            underline=style_dict.get("underline", False),
            strikethrough=style_dict.get("strikethrough", False),
            font_size=style_dict.get("fontSize", {}).get("magnitude"),
            font_family=style_dict.get("fontFamily"),
            foreground_color=style_dict.get("foregroundColor"),
            background_color=style_dict.get("backgroundColor"),
            link=style_dict.get("link", {}).get("url")
        )

    def _extract_paragraph_style(self, para_dict: Dict[str, Any]) -> ParagraphStyle:
        """Extract paragraph style from API response."""
        return ParagraphStyle(
            indent_level=para_dict.get("indentLevel", 0),
            alignment=para_dict.get("alignment", "START"),
            line_spacing=para_dict.get("lineSpacing"),
            direction=para_dict.get("direction", "LEFT_TO_RIGHT"),
            spacing_mode=para_dict.get("spacingMode")
        )

    def _extract_bullet_info(self, bullet_dict: Dict[str, Any]) -> BulletInfo:
        """Extract bullet/list information from API response."""
        return BulletInfo(
            list_id=bullet_dict.get("listId"),
            nesting_level=bullet_dict.get("nestingLevel", 0),
            bullet_style=bullet_dict.get("glyph", "●"),
            list_properties=bullet_dict.get("listProperties")
        )

    def _extract_text_runs(self, text_elements: List[Dict[str, Any]]) -> tuple[List[TextRun], str]:
        """Extract text runs with styling from text elements."""
        text_runs = []
        raw_text = []

        for element in text_elements:
            # Handle text runs
            if "textRun" in element:
                text_run = element["textRun"]
                content = text_run.get("content", "")
                raw_text.append(content)

                text_style = self._extract_text_style(text_run.get("style", {}))

                # Get paragraph style from paragraph marker
                paragraph_marker = element.get("paragraphMarker", {})
                para_style_dict = paragraph_marker.get("style", {})
                paragraph_style = self._extract_paragraph_style(para_style_dict)

                # Extract bullet info if present
                bullet_info = None
                if "bullet" in para_style_dict:
                    bullet_info = self._extract_bullet_info(para_style_dict["bullet"])

                text_runs.append(TextRun(
                    content=content,
                    text_style=text_style,
                    paragraph_style=paragraph_style,
                    bullet_info=bullet_info
                ))

        return text_runs, "".join(raw_text)

    def _determine_element_type(self, element: Dict[str, Any]) -> ElementType:
        """Determine the type of slide element."""
        # Check if it's a placeholder with specific type
        if "shape" in element:
            shape = element["shape"]
            placeholder = shape.get("placeholder", {})
            placeholder_type = placeholder.get("type", "")

            if placeholder_type == "TITLE" or placeholder_type == "CENTERED_TITLE":
                return ElementType.TITLE
            elif placeholder_type == "SUBTITLE":
                return ElementType.SUBTITLE
            elif placeholder_type == "BODY":
                return ElementType.BODY
            else:
                return ElementType.SHAPE

        elif "table" in element:
            return ElementType.TABLE
        elif "image" in element:
            return ElementType.IMAGE
        elif "line" in element:
            return ElementType.LINE
        elif "elementGroup" in element:
            return ElementType.GROUP

        return ElementType.UNKNOWN

    def _extract_table(self, table_dict: Dict[str, Any]) -> Table:
        """Extract table structure and content."""
        rows = table_dict.get("rows", 0)
        columns = table_dict.get("columns", 0)
        table_rows = table_dict.get("tableRows", [])

        cells = []

        for row_idx, row in enumerate(table_rows):
            table_cells = row.get("tableCells", [])
            for col_idx, cell in enumerate(table_cells):
                # Extract text from cell
                text_elements = cell.get("text", {}).get("textElements", [])
                text_runs, raw_text = self._extract_text_runs(text_elements)

                cells.append(TableCell(
                    row_index=row_idx,
                    col_index=col_idx,
                    text_content=raw_text.strip(),
                    row_span=cell.get("rowSpan", 1),
                    col_span=cell.get("columnSpan", 1),
                    text_runs=text_runs
                ))

        return Table(rows=rows, columns=columns, cells=cells)

    def _extract_element(self, element: Dict[str, Any], parent_id: Optional[str] = None) -> Optional[SlideElement]:
        """Extract a single slide element with all its properties."""
        element_id = element.get("objectId")
        element_type = self._determine_element_type(element)
        transform = element.get("transform")
        size = element.get("size")

        # Handle different element types
        if element_type in [ElementType.TITLE, ElementType.SUBTITLE, ElementType.BODY, ElementType.SHAPE]:
            shape = element.get("shape", {})
            text_elements = shape.get("text", {}).get("textElements", [])
            text_runs, raw_text = self._extract_text_runs(text_elements)

            return TextElement(
                element_id=element_id,
                element_type=element_type,
                transform=transform,
                size=size,
                parent_id=parent_id,
                text_runs=text_runs,
                raw_text=raw_text
            )

        elif element_type == ElementType.TABLE:
            table = self._extract_table(element.get("table", {}))
            return TableElement(
                element_id=element_id,
                element_type=element_type,
                transform=transform,
                size=size,
                parent_id=parent_id,
                table=table
            )

        elif element_type == ElementType.IMAGE:
            image_props = element.get("image", {})
            return ImageElement(
                element_id=element_id,
                element_type=element_type,
                transform=transform,
                size=size,
                parent_id=parent_id,
                content_url=image_props.get("contentUrl"),
                source_url=image_props.get("sourceUrl"),
                image_properties=image_props.get("imageProperties")
            )

        elif element_type == ElementType.GROUP:
            group = element.get("elementGroup", {})
            children_ids = [child.get("objectId") for child in group.get("children", [])]

            return GroupElement(
                element_id=element_id,
                element_type=element_type,
                transform=transform,
                size=size,
                parent_id=parent_id,
                children_ids=children_ids
            )

        else:
            # Generic element
            return SlideElement(
                element_id=element_id,
                element_type=element_type,
                transform=transform,
                size=size,
                parent_id=parent_id
            )

    def _extract_speaker_notes(self, slide: Dict[str, Any]) -> Optional[str]:
        """Extract speaker notes from a slide."""
        notes_properties = slide.get("slideProperties", {}).get("notesPage", {})

        if not notes_properties:
            return None

        # Get notes page
        page_elements = notes_properties.get("pageElements", [])
        notes_text = []

        for element in page_elements:
            if "shape" in element:
                shape = element["shape"]
                # Check if this is a notes placeholder
                placeholder = shape.get("placeholder", {})
                if placeholder.get("type") == "BODY":
                    text_elements = shape.get("text", {}).get("textElements", [])
                    _, raw_text = self._extract_text_runs(text_elements)
                    if raw_text.strip():
                        notes_text.append(raw_text.strip())

        return "\n".join(notes_text) if notes_text else None

    def _extract_slide_title(self, elements: List[SlideElement]) -> Optional[str]:
        """Extract the title from slide elements."""
        for element in elements:
            if isinstance(element, TextElement) and element.element_type == ElementType.TITLE:
                return element.raw_text.strip()
        return None

    def extract_slide(self, slide: Dict[str, Any], slide_number: int) -> SlideContent:
        """Extract all content from a single slide."""
        slide_id = slide.get("objectId")
        layout = slide.get("slideProperties", {}).get("layoutObjectId")

        # Extract all page elements
        page_elements = slide.get("pageElements", [])
        elements = []
        element_map = {}

        # First pass: extract all elements
        for page_element in page_elements:
            extracted = self._extract_element(page_element)
            if extracted:
                elements.append(extracted)
                element_map[extracted.element_id] = extracted

        # Second pass: establish parent-child relationships for groups
        for element in elements:
            if isinstance(element, GroupElement):
                for child_id in element.children_ids:
                    if child_id in element_map:
                        element_map[child_id].parent_id = element.element_id

        # Extract speaker notes (requires separate API call in production)
        # For now, we'll try to get from slide properties
        speaker_notes = self._extract_speaker_notes(slide)

        # Extract title
        title = self._extract_slide_title(elements)

        return SlideContent(
            slide_number=slide_number,
            slide_id=slide_id,
            title=title,
            elements=elements,
            speaker_notes=speaker_notes,
            layout_type=layout
        )

    def extract_presentation(self, presentation_id: str) -> List[SlideContent]:
        """Extract all content from a presentation."""
        try:
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()

            slides = presentation.get("slides", [])
            logger.info(f"Extracting {len(slides)} slides")

            extracted_slides = []
            for idx, slide in enumerate(slides, 1):
                try:
                    slide_content = self.extract_slide(slide, idx)
                    extracted_slides.append(slide_content)
                    logger.info(f"Extracted slide {idx}: {slide_content.title or 'Untitled'}")
                except Exception as e:
                    logger.error(f"Error extracting slide {idx}: {e}")
                    continue

            return extracted_slides
        except Exception as e:
            logger.error(f"Error extracting presentation: {e}")
            raise

    def format_slide_content(self, slide: SlideContent) -> str:
        """Format slide content for display."""
        output = []
        output.append("=" * 70)
        output.append(f"Slide {slide.slide_number}: {slide.title or 'Untitled'}")
        output.append("=" * 70)

        # Group elements by type
        for element in slide.elements:
            if isinstance(element, TextElement):
                output.append(f"\n[{element.element_type.value.upper()}]")
                for text_run in element.text_runs:
                    content = text_run.content.strip()
                    if not content:
                        continue

                    # Build prefix with indentation
                    prefix = ""
                    if text_run.bullet_info:
                        indent = "  " * text_run.bullet_info.nesting_level
                        prefix = f"{indent}{text_run.bullet_info.bullet_style} "
                    else:
                        indent = "  " * text_run.paragraph_style.indent_level
                        prefix = indent

                    # Add style markers
                    style_markers = []
                    if text_run.text_style.bold:
                        style_markers.append("BOLD")
                    if text_run.text_style.italic:
                        style_markers.append("ITALIC")
                    if text_run.text_style.font_size and text_run.text_style.font_size > 14:
                        style_markers.append(f"{int(text_run.text_style.font_size)}pt")

                    style_prefix = f"[{', '.join(style_markers)}] " if style_markers else ""
                    output.append(f"{prefix}{style_prefix}{content}")

            elif isinstance(element, TableElement):
                output.append(f"\n[TABLE: {element.table.rows}x{element.table.columns}]")
                for cell in element.table.cells:
                    if cell.text_content:
                        output.append(f"  [{cell.row_index},{cell.col_index}]: {cell.text_content}")

            elif isinstance(element, ImageElement):
                output.append(f"\n[IMAGE: {element.element_id}]")
                if element.source_url:
                    output.append(f"  URL: {element.source_url}")

            elif isinstance(element, GroupElement):
                output.append(f"\n[GROUP: {element.element_id}]")
                output.append(f"  Children: {', '.join(element.children_ids)}")

        # Add speaker notes
        if slide.speaker_notes:
            output.append("\n[SPEAKER NOTES]")
            output.append(slide.speaker_notes)

        output.append("")
        return "\n".join(output)


def main():
    """Main execution function."""
    extractor = GoogleSlidesExtractor(SERVICE_ACCOUNT_FILE)

    # Find presentation
    presentation_id = extractor.find_presentation(FOLDER_ID, FILE_NAME)

    # Extract all slides
    slides = extractor.extract_presentation(presentation_id)

    # Display formatted output
    i = 0
    for slide in slides:
        if i < 10:
            print(extractor.format_slide_content(slide))
        i += 1

    return slides


if __name__ == "__main__":
    main()
