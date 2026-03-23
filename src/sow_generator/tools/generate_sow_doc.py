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

def render_content_requests(content, start_index, level=1, bulleted=False):
    """
    Recursively convert nested dict/list into Google Docs API requests
    """
    requests = []
    index = start_index

    for item in content:

        # Case 1: Plain paragraph (or bullet if flag set)
        if isinstance(item, str):
            text = item + "\n"

            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": text
                }
            })

            if bulleted:
                # Apply bullets
                requests.append({
                    "createParagraphBullets": {
                        "range": {
                            "startIndex": index,
                            "endIndex": index + len(text)
                        },
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                })

            index += len(text)

        # Case 2: Nested section
        elif isinstance(item, dict):
            title = item.get("title")
            sub_content = item.get("content")

            # If title is missing, use the first key as the title and its value as content
            if title is None and len(item) == 1:
                title, sub_content = list(item.items())[0]
            
            title = str(title or "")
            sub_content = sub_content if isinstance(sub_content, (list, str, dict)) else []
            if isinstance(sub_content, (str, dict)):
                sub_content = [sub_content]

            # Insert heading
            heading_text = title + "\n"

            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": heading_text
                }
            })

            # Apply heading style based on level
            heading_style = f"HEADING_{min(level + 1, 6)}"

            requests.append({
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(heading_text)
                    },
                    "paragraphStyle": {
                        "namedStyleType": heading_style
                    },
                    "fields": "namedStyleType"
                }
            })

            index += len(heading_text)

            # Recursively render children
            # Default to bulleted if the content is a list of strings
            child_bulleted = any(isinstance(x, str) for x in sub_content) if isinstance(sub_content, list) else False
            child_requests, index = render_content_requests(
                sub_content, index, level + 1, bulleted=child_bulleted
            )

            requests.extend(child_requests)

        # Case 3: List of strings → bullet list
        elif isinstance(item, list):
            # If it's a list of dicts, process each dict as a nested section
            if any(isinstance(x, dict) for x in item):
                for sub_item in item:
                    child_requests, index = render_content_requests([sub_item], index, level)
                    requests.extend(child_requests)
            else:
                # Just a simple list of bullets
                for bullet in item:
                    bullet_text = str(bullet) + "\n"
                    requests.append({
                        "insertText": {
                            "location": {"index": index},
                            "text": bullet_text
                        }
                    })
                    # Apply bullets
                    requests.append({
                        "createParagraphBullets": {
                            "range": {
                                "startIndex": index,
                                "endIndex": index + len(bullet_text)
                            },
                            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                        }
                    })
                    index += len(bullet_text)

    return requests, index


def find_placeholder(doc, placeholder):
    """
    Finds the precise startIndex and endIndex of a placeholder in the document,
    including inside tables.
    """
    def search_content(elements):
        for element in elements:
            if "paragraph" in element:
                for run in element["paragraph"].get("elements", []):
                    text = run.get("textRun", {}).get("content", "")
                    if placeholder in text:
                        start_offset = text.find(placeholder)
                        actual_start = run.get("startIndex") + start_offset
                        actual_end = actual_start + len(placeholder)
                        return actual_start, actual_end
            elif "table" in element:
                for row in element["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        found_start, found_end = search_content(cell.get("content", []))
                        if found_start is not None:
                            return found_start, found_end
        return None, None

    return search_content(doc.get("body").get("content", []))


def replace_placeholder_with_dict(docs_service, doc_id, placeholder, section_data):
    print(f"Replacing placeholder {placeholder} with section data {section_data}")
    doc = docs_service.documents().get(documentId=doc_id).execute()

    start, end = find_placeholder(doc, placeholder)

    if start is None:
        print(f"Placeholder {placeholder} not found")
        return

    requests = []

    # Delete placeholder
    requests.append({
        "deleteContentRange": {
            "range": {
                "startIndex": start,
                "endIndex": end
            }
        }
    })

    if isinstance(section_data, str):
        # Case 1: Simple string replacement
        text = section_data + "\n"
        requests.append({
            "insertText": {
                "location": {"index": start},
                "text": text
            }
        })
    elif isinstance(section_data, list):
        # Case 2: List of items (treat as bulleted content)
        content_requests, _ = render_content_requests(section_data, start, bulleted=True)
        requests.extend(content_requests)
    elif isinstance(section_data, dict):
        # Case 3: Dictionary with title and content
        title = section_data.get("title", "")
        title_text = title + "\n" if title else ""

        if title_text:
            requests.append({
                "insertText": {
                    "location": {"index": start},
                    "text": title_text
                }
            })

            requests.append({
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": start,
                        "endIndex": start + len(title_text)
                    },
                    "paragraphStyle": {
                        "namedStyleType": "HEADING_1"
                    },
                    "fields": "namedStyleType"
                }
            })

        current_index = start + len(title_text)

        # Render nested content
        content = section_data.get("content", [])
        content_requests, _ = render_content_requests(content, current_index)
        requests.extend(content_requests)
    else:
        # Fallback for other types
        text = str(section_data) + "\n"
        requests.append({
            "insertText": {
                "location": {"index": start},
                "text": text
            }
        })

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()


def generate_doc_from_dict(drive_service, docs_service, data, template_id, doc_id):

    # docs_service, drive_service = get_services()

    # Copy template
    # doc_id = copy_template(drive_service, template_id, "Generated Document")

    # Replace each placeholder
    for key, section in data.items():
        # Try finding the placeholder as {{KEY}}, then fallback to <<KEY>> or just KEY
        placeholder_candidates = [f"{{{{{key}}}}}" if not key.startswith("{{") else key, key]
        found_start = None
        found_end = None
        target_placeholder = None
        
        doc = docs_service.documents().get(documentId=doc_id).execute()
        for cand in placeholder_candidates:
            found_start, found_end = find_placeholder(doc, cand)
            if found_start is not None:
                target_placeholder = cand
                break
        
        if target_placeholder:
            replace_placeholder_with_dict(
                docs_service,
                doc_id,
                target_placeholder,
                section
            )
        else:
            print(f"Placeholder {key} not found in document (tried {placeholder_candidates})")

    print(f"Document created: https://docs.google.com/document/d/{doc_id}")


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
        
        generate_doc_from_dict(drive_service, docs_service, placeholders, template_drive_id, new_doc_id)

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