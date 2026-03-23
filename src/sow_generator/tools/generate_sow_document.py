"""Tool to generate a SOW document in Google Docs format directly via Google Docs API.
Placeholders in the template should use << >> format (e.g., <<PROJECT_NAME>>).
"""

import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
# -------------------------
# Helper functions
# -------------------------

def _flatten_list_to_markdown(items, indent_level=0):
    lines = []
    # 2 spaces per indent level for Markdown nesting
    indent = "  " * indent_level
    
    if not isinstance(items, list):
        return str(items)

    for item in items:
        if isinstance(item, str):
            lines.append(f"{indent}- {item}")
        elif isinstance(item, list):
            if len(item) == 0:
                continue
            elif len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], list):
                # Standard nested format: [parent, [children]]
                lines.append(f"{indent}- **{item[0]}**")
                lines.append(_flatten_list_to_markdown(item[1], indent_level + 1))
            else:
                # Generic list
                lines.append(_flatten_list_to_markdown(item, indent_level))
        elif isinstance(item, dict):
            # LLM Format: {"Section Title": ["item1", "item2"]}
            for k, v in item.items():
                lines.append(f"{indent}- **{k}**")
                if isinstance(v, list):
                    lines.append(_flatten_list_to_markdown(v, indent_level + 1))
                else:
                    lines.append(f"{indent}  - {v}")
        else:
            lines.append(f"{indent}- {str(item)}")
    
    return "\n".join(lines)

def format_list_as_markdown(items):
    return _flatten_list_to_markdown(items, 0)

def _extract_drive_file_id(url_or_id: str) -> str:
    import re
    if not url_or_id:
        return ""
    # Matches typical /d/FILE_ID or id=FILE_ID patterns
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url_or_id)
    if match:
        return match.group(1)
    match = re.search(r'[?&]id=([a-zA-Z0-9-_]+)', url_or_id)
    if match:
        return match.group(1)
    return url_or_id

async def read_google_drive_file(
    file_id: str,
    credentials: Union[str, Path, Dict]
) -> Dict[str, Any]:
    """
    Reads the text content of a Google Drive file.
    
    Args:
        file_id: Google Drive File ID
        credentials: Path to service account JSON, JSON string, or parsed dict
        
    Returns:
        Dictionary containing status and text content.
    """
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    file_id = _extract_drive_file_id(file_id)
    logger.info(f"Reading file from Google Drive: {file_id}")
    try:
        scopes = ['https://www.googleapis.com/auth/drive.readonly']

        # Handle different credential formats
        if isinstance(credentials, dict):
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=scopes
            )
        elif isinstance(credentials, (str, Path)):
            credentials_path = Path(credentials) if isinstance(credentials, str) else credentials
            if credentials_path.exists() and credentials_path.is_file():
                creds = service_account.Credentials.from_service_account_file(
                    str(credentials), scopes=scopes
                )
            else:
                try:
                    credentials_dict = json.loads(str(credentials))
                    creds = service_account.Credentials.from_service_account_info(
                        credentials_dict, scopes=scopes
                    )
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid credentials: {e}") from e
        else:
            raise TypeError(f"credentials must be str, Path, or dict, got {type(credentials)}")

        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = drive_service.files().get(fileId=file_id, fields='mimeType', supportsAllDrives=True).execute()
        mime_type = file_metadata.get('mimeType', '')
        
        # Google Workspace documents must be exported, others can be downloaded
        if mime_type.startswith('application/vnd.google-apps.'):
            # Export Google Docs as plain text
            request = drive_service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            # Download regular files directly
            request = drive_service.files().get_media(fileId=file_id)
            
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        text_content = fh.getvalue().decode('utf-8')
        
        return {
            "status": "success",
            "text": text_content
        }
        
    except Exception as e:
        logger.error(f"Failed to read file from Google Drive: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

# -------------------------
# Main functions
# -------------------------

async def generate_sow_document(
    template_drive_id: str,
    placeholders: Dict[str, Any],
    document_title: str,
    credentials: Union[str, Path, Dict],
    drive_folder_id: Optional[str] = None,
    share_with_emails: Optional[List[str]] = None,
    make_public: bool = False
) -> Dict[str, Any]:
    """
    Generates a Statement of Work (SOW) by copying a Google Docs template
    and replacing placeholders using the Google Docs API.

    Args:
        template_drive_id: Google Drive File ID of the Google Docs template
        placeholders: Dictionary mapping placeholder names to replacement values.
                     Keys should include delimiters (e.g., {"<<NAME>>": "Acme Corp"}).
                     Values can be strings or lists (for multiple bullet points).
        document_title: Name of the generated document
        credentials: Path to service account JSON, JSON string, or parsed dict
        drive_folder_id: Optional Google Drive folder ID to place the new doc
        share_with_emails: Optional list of emails to share with (as editors)
        make_public: If True, makes the document publicly readable

    Returns:
        Dictionary containing status and Google Drive file info.
    """
    logger.info("=" * 80)
    template_drive_id = _extract_drive_file_id(template_drive_id)
    logger.info("generate_sow_document called (Docs API version)")
    logger.info(f"template_drive_id: {template_drive_id}")
    logger.info(f"document_title: {document_title}")
    logger.info(f"Number of placeholders: {len(placeholders)}")
    logger.info("=" * 80)

    try:
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents'
        ]

        # Handle different credential formats
        if isinstance(credentials, dict):
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=scopes
            )
        elif isinstance(credentials, (str, Path)):
            credentials_path = Path(credentials) if isinstance(credentials, str) else credentials
            if credentials_path.exists() and credentials_path.is_file():
                creds = service_account.Credentials.from_service_account_file(
                    str(credentials), scopes=scopes
                )
            else:
                try:
                    credentials_dict = json.loads(str(credentials))
                    creds = service_account.Credentials.from_service_account_info(
                        credentials_dict, scopes=scopes
                    )
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid credentials: not a valid file path or JSON string: {e}"
                    ) from e
        else:
            raise TypeError(f"credentials must be str, Path, or dict, got {type(credentials)}")

        # Build APIs
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # -------------------------
        # 1. Copy the template document
        # -------------------------
        logger.info(f"Copying template document {template_drive_id}...")
        body = {'name': document_title}
        if drive_folder_id:
            body['parents'] = [drive_folder_id]

        copied_file = drive_service.files().copy(
            fileId=template_drive_id,
            body=body,
            fields='id, name, webViewLink, webContentLink',
            supportsAllDrives=True
        ).execute()
        
        new_doc_id = copied_file.get('id')
        logger.info(f"Document copied successfully. New File ID: {new_doc_id}")

        # -------------------------
        # 2. Batch replace placeholders
        # -------------------------
        # -------------------------
        # 2. Batch replace placeholders (Two-Pass Strategy)
        # -------------------------
        logger.info("Preparing replacement requests...")
        
        # Get latest doc structure to find placeholder positions
        doc = docs_service.documents().get(documentId=new_doc_id).execute()
        placeholders_in_doc = find_placeholders_in_doc(doc.get('body').get('content', []))
        
        # Pass 1: Transformations (Insert/Delete) - Process in REVERSE order
        transform_requests = []
        # Store metadata for Pass 2
        formatting_metadata = [] # list of (original_start, md_text or val)
        
        # find_placeholders_in_doc returns them sorted by startIndex DESC
        for p in placeholders_in_doc:
            key = p['text']
            val = placeholders.get(key)
            if val is None:
                continue
            
            is_formatted = isinstance(val, list) or (isinstance(val, str) and ('\n' in val or val.startswith('- ') or val.startswith('# ')))
            
            if is_formatted:
                md_text = format_list_as_markdown(val) if isinstance(val, list) else val
                
                # Use markdown_to_docs_requests in trans-mode to get the exact inserted length
                snip_trans = markdown_to_docs_requests(md_text, p['startIndex'], only_styles=False)
                inserted_len = len(snip_trans[0]['insertText']['text'])
                deleted_len = p['endIndex'] - p['startIndex']
                
                transform_requests.extend(snip_trans)
                # Delete the placeholder itself
                transform_requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': p['startIndex'] + inserted_len,
                            'endIndex': p['endIndex'] + inserted_len
                        }
                    }
                })
                
                formatting_metadata.append({
                    'original_start': p['startIndex'],
                    'md_text': md_text,
                    'shift_delta': inserted_len - deleted_len
                })
            else:
                # Simple text replacement - doesn't shift indices for subsequent (earlier) placeholders
                # since it's a replaceAllText, but we want to track it for Pass 2 styling if needed.
                # For simplicity, we'll just use replaceAllText for plain strings.
                transform_requests.append({
                    'replaceAllText': {
                        'containsText': {'text': key, 'matchCase': True},
                        'replaceText': str(val)
                    }
                })

        if transform_requests:
            logger.info(f"Executing Pass 1 (Transformations) with {len(transform_requests)} requests...")
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': transform_requests}
            ).execute()
            logger.info("Pass 1 completed.")

        # Pass 2: Styling - Process in FORWARD order to account for shifts correctly
        # Actually, if we use the final document indices, we need to know the shift.
        style_requests = []
        # Sort metadata by original start index ASC
        formatting_metadata.sort(key=lambda x: x['original_start'])
        
        running_shift = 0
        for meta in formatting_metadata:
            effective_start = meta['original_start'] + running_shift
            # Generate style requests for this block
            # markdown_to_docs_requests now should NOT include insertText
            snip_styles = markdown_to_docs_requests(meta['md_text'], effective_start, only_styles=True)
            style_requests.extend(snip_styles)
            running_shift += meta['shift_delta']

        if style_requests:
            logger.info(f"Executing Pass 2 (Styling) with {len(style_requests)} requests...")
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': style_requests}
            ).execute()
            logger.info("Pass 2 completed.")

        # -------------------------
        # 3. Handle sharing permissions
        # -------------------------
        if share_with_emails:
            for email in share_with_emails:
                try:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    drive_service.permissions().create(
                        fileId=new_doc_id,
                        body=permission,
                        sendNotificationEmail=True
                    ).execute()
                    logger.info(f"Shared document with {email}")
                except Exception as e:
                    logger.warning(f"Failed to share with {email}: {e}")

        if make_public:
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                drive_service.permissions().create(
                    fileId=new_doc_id,
                    body=permission
                ).execute()
                logger.info("Document made publicly accessible")
            except Exception as e:
                logger.warning(f"Failed to make document public: {e}")

        return {
            "status": "success",
            "data": {
                "document_title": copied_file.get('name'),
                "file_id": new_doc_id,
                "web_view_link": copied_file.get('webViewLink')
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate SOW document: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


# -------------------------
# Markdown to Google Docs logic
# -------------------------

def process_inline_markdown(text: str, start_index: int):
    # returns clean_text, list of bold ranges (start, end)
    import re
    clean_text = ""
    bold_ranges = []
    parts = re.split(r'(\*\*.*?\*\*)', text)
    current_idx = start_index
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            inner = part[2:-2]
            clean_text += inner
            bold_ranges.append((current_idx, current_idx + len(inner)))
            current_idx += len(inner)
        else:
            clean_text += part
            current_idx += len(part)
    return clean_text, bold_ranges

def markdown_to_docs_requests(markdown_text: str, start_index: int, only_styles: bool = False):
    requests = []
    markdown_text = markdown_text.replace('\r\n', '\n')
    lines = markdown_text.split('\n')
    
    full_text = ""
    paragraph_ranges = []
    bold_ranges = []
    list_items = [] # stores (start, end)
    
    current_index = start_index
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            full_text += "\n"
            current_index += 1
            continue
        
        # Calculate nesting level based on leading spaces (2 spaces = 1 level)
        leading_spaces = len(line) - len(line.lstrip())
        nesting_level = leading_spaces // 2
        
        # Add tabs for nesting
        tabs = "\t" * nesting_level
        full_text += tabs
        current_index += len(tabs)
        
        style_type = 'NORMAL_TEXT'
        line_content = line_stripped
        is_bullet = False
        
        if line_stripped.startswith('### '):
            style_type = 'HEADING_3'
            line_content = line_stripped[4:]
        elif line_stripped.startswith('## '):
            style_type = 'HEADING_2'
            line_content = line_stripped[3:]
        elif line_stripped.startswith('# '):
            style_type = 'HEADING_1'
            line_content = line_stripped[2:]
        elif line_stripped.startswith('- '):
            style_type = 'NORMAL_TEXT'
            line_content = line_stripped[2:]
            is_bullet = True
        
        line_clean, b_ranges = process_inline_markdown(line_content, current_index)
        line_text = line_clean + "\n"
        full_text += line_text
        
        para_start = current_index - len(tabs)
        para_end = current_index + len(line_text)
        
        paragraph_ranges.append((style_type, para_start, para_end))
        bold_ranges.extend(b_ranges)
        
        if is_bullet:
            list_items.append((para_start, para_end))
        
        current_index += len(line_text)

    if not full_text:
        return []
        
    # Pass 1: Transformation (Only if not in style-only mode)
    if not only_styles:
        requests.append({
            'insertText': {
                'location': {'index': start_index},
                'text': full_text
            }
        })
        return requests # Return early for transformation batch
    
    # Pass 2: Styling
    # Apply paragraph styles (Headings)
    for style_type, start, end in paragraph_ranges:
        if style_type != 'NORMAL_TEXT':
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {'namedStyleType': style_type},
                    'fields': 'namedStyleType'
                }
            })
    
    # Create bullets
    for start, end in list_items:
        requests.append({
            'createParagraphBullets': {
                'range': {'startIndex': start, 'endIndex': end},
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })
        
    # Apply bolding
    for start, end in bold_ranges:
        if start < end:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })
            
    return requests

def extract_sections_from_markdown(markdown_content: str) -> dict:
    import re
    sections = {}
    
    meta_title = re.search(r'- Title:\s*(.*)', markdown_content)
    if meta_title: sections['<<TITLE>>'] = meta_title.group(1).strip()
    
    meta_cust = re.search(r'- Customer Name:\s*(.*)', markdown_content)
    if meta_cust: sections['<<CUSTOMER_NAME>>'] = meta_cust.group(1).strip()
    
    meta_msa = re.search(r'- MSA Date:\s*(.*)', markdown_content)
    if meta_msa: sections['<<MSA_DATE>>'] = meta_msa.group(1).strip()
    
    content_match = re.search(r'# SOW Content\n(.*)', markdown_content, re.DOTALL | re.IGNORECASE)
    if content_match:
        sow_text = content_match.group(1)
        lines = sow_text.split('\n')
        current_section = None
        current_content = []
        for line in lines:
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                title = line[3:].strip().upper().replace(' ', '_')
                current_section = f"<<{title}>>"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
            
    return {k: v for k, v in sections.items() if v}

def find_placeholders_in_doc(doc_content):
    found = []
    
    def process_elements(elements):
        for element in elements:
            if 'paragraph' in element:
                for pe in element['paragraph'].get('elements', []):
                    if 'textRun' in pe:
                        content = pe['textRun'].get('content', '')
                        start_idx = pe['startIndex']
                        import re
                        for match in re.finditer(r'<<[^>]+>>', content):
                            found.append({
                                'text': match.group(),
                                'startIndex': start_idx + match.start(),
                                'endIndex': start_idx + match.end()
                            })
            elif 'table' in element:
                for row in element['table'].get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        process_elements(cell.get('content', []))

    process_elements(doc_content)
    found.sort(key=lambda x: x['startIndex'], reverse=True)
    return found

async def generate_sow_from_markdown(
    template_drive_id: str,
    drive_folder_id: str,
    markdown_content: str,
    credentials,
    document_title: str = "Generated SOW",
    share_with_emails = None,
    make_public: bool = False
) -> dict:
    logger.info("=" * 80)
    template_drive_id = _extract_drive_file_id(template_drive_id)
    drive_folder_id = _extract_drive_file_id(drive_folder_id) if drive_folder_id else None
    logger.info("generate_sow_from_markdown called")
    logger.info(f"template_drive_id: {template_drive_id}")
    logger.info(f"drive_folder_id: {drive_folder_id}")
    logger.info("=" * 80)
    logger.info(f"markdown content \n{markdown_content}")
    try:
        sections = extract_sections_from_markdown(markdown_content)
        logger.info(f"Extracted placeholders from markdown: {list(sections.keys())}")
        
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents'
        ]

        if isinstance(credentials, dict):
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=scopes
            )
        elif isinstance(credentials, (str, Path)):
            credentials_path = Path(credentials) if isinstance(credentials, str) else credentials
            if credentials_path.exists() and credentials_path.is_file():
                creds = service_account.Credentials.from_service_account_file(
                    str(credentials), scopes=scopes
                )
            else:
                try:
                    credentials_dict = json.loads(str(credentials))
                    creds = service_account.Credentials.from_service_account_info(
                        credentials_dict, scopes=scopes
                    )
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid credentials: {e}") from e
        else:
            raise TypeError(f"credentials must be str, Path, or dict")

        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        logger.info(f"Copying template document {template_drive_id}...")
        body = {'name': document_title}
        if drive_folder_id:
            body['parents'] = [drive_folder_id]

        copied_file = drive_service.files().copy(
            fileId=template_drive_id,
            body=body,
            fields='id, name, webViewLink',
            supportsAllDrives=True
        ).execute()
        
        new_doc_id = copied_file.get('id')
        logger.info(f"Document copied successfully. New File ID: {new_doc_id}")

        doc = docs_service.documents().get(documentId=new_doc_id).execute()
        doc_content = doc.get('body').get('content')
        
        placeholders_in_doc = find_placeholders_in_doc(doc_content)
        logger.info(f"Found placeholders in doc: {[p['text'] for p in placeholders_in_doc]}")
        
        requests = []
        for p in placeholders_in_doc:
            p_text = p['text']
            md_text = sections.get(p_text)
            if md_text is not None:
                reqs = markdown_to_docs_requests(md_text, p['startIndex'])
                inserted_len = 0
                if reqs and 'insertText' in reqs[0]:
                    inserted_len = len(reqs[0]['insertText']['text'])
                requests.extend(reqs)
                
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': p['startIndex'] + inserted_len,
                            'endIndex': p['endIndex'] + inserted_len
                        }
                    }
                })

        if requests:
            logger.info("Executing batchUpdate...")
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': requests}
            ).execute()
            logger.info("Placeholders replaced successfully.")

        if share_with_emails:
            for email in share_with_emails:
                try:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    drive_service.permissions().create(
                        fileId=new_doc_id,
                        body=permission,
                        sendNotificationEmail=True
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to share with {email}: {e}")

        if make_public:
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                drive_service.permissions().create(
                    fileId=new_doc_id,
                    body=permission
                ).execute()
            except Exception as e:
                logger.warning(f"Failed to make document public: {e}")

        return {
            "status": "success",
            "data": {
                "document_title": copied_file.get('name'),
                "file_id": new_doc_id,
                "web_view_link": copied_file.get('webViewLink')
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate SOW document from markdown: {e}", exc_info=True)
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
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate SOW Document")
    parser.add_argument('--input-format', type=str, choices=['json', 'markdown'], default='json',
                        help='Input format: json (default) or markdown')
    parser.add_argument('--markdown-file', type=str, help='Path to markdown file if input-format is markdown')
    parser.add_argument('--json-file', type=str, help='Path to json file if input-format is json')
    args = parser.parse_args()

    # Configure your Drive IDs
    # Set to a valid Google Docs format FILE ID
    TEMPLATE_DRIVE_ID = os.getenv("sow_template_drive_id")
    
    # Optional folder to put it in
    DRIVE_FOLDER_ID = os.getenv("sow_drive_folder_id") 
    
    # Needs valid credentials in env var 'sow-generator-sa' or absolute path
    CREDENTIALS = os.getenv("sow-generator-sa", "path/to/service_account.json")

    logger.info(f"credentials: {CREDENTIALS}")

    print("=" * 70)
    print("SOW Document Generator - Test Execution")
    print("=" * 70)
    print(f"\nTemplate ID: {TEMPLATE_DRIVE_ID}")
    
    if args.input_format == 'markdown':
        markdown_content = ""
        if args.markdown_file and Path(args.markdown_file).exists():
            with open(args.markdown_file, "r", encoding="utf-8") as f:
                markdown_content = f.read()
        else:
            markdown_content = """# Project Metadata
- Title: Cloud Migration Initiative
- Customer Name: Acme Corporation
- MSA Date: 13 March 2026

# Category
migration

# SOW Content
## Opportunity
This project aims to migrate critical workloads.

## Activities
- This is activity 1
- This is activity 2
- This is activity 3"""

        result = await generate_sow_from_markdown(
            template_drive_id=TEMPLATE_DRIVE_ID,
            drive_folder_id=DRIVE_FOLDER_ID,
            markdown_content=markdown_content,
            credentials=CREDENTIALS,
            document_title="SOW_Acme_Cloud_Migration_2026_MD",
            share_with_emails=None,
            make_public=False
        )
    else:
        sample_placeholders = {
            "<<CUSTOMER_NAME>>": "Acme Corporation",
            "<<TITLE>>": "Cloud Migration Initiative",
            "<<PROVISION_DATE>>": "13 March 2026",
            "<<OPPORTUNITY>>": "This project aims to migrate critical workloads.",
            "<<ACTIVITIES>>": ["This is activity 1", "This is activity 2", "This is activity 3"],
            "<<DELIVERABLES>>": [
                "Architecture Design Document",
                "Implementation Plan",
                "Testing & Validation Report"
            ]
        }

        with open(args.json_file, "r", encoding="utf-8") as f:
            json_content = json.load(f)
        result = await generate_sow_document(
            template_drive_id=TEMPLATE_DRIVE_ID,
            placeholders=json_content,
            document_title="SOW_Acme_Cloud_Migration_2026",
            credentials=CREDENTIALS,
            drive_folder_id=DRIVE_FOLDER_ID,
            share_with_emails=None,
            make_public=False
        )
    
    print("=" * 70)
    print("Generation Result\n")
    print(result)
    print("=" * 70)

    if result["status"] == "success":
        print("✅ SUCCESS!")
        print(f"\nDocument Title: {result['data']['document_title']}")
        print(f"File ID: {result['data']['file_id']}")
        print(f"Web View Link: {result['data']['web_view_link']}")
    else:
        print("❌ FAILED!")
        print(f"Error: {result['error']}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())