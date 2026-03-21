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

def _flatten_list_to_string_lines(items, indent=0):
    lines = []
    prefix = "    " * indent + "• "
    
    for item in items:
        if isinstance(item, str):
            lines.append(prefix + item)
        elif isinstance(item, list):
            if len(item) == 0:
                continue
            elif len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], list):
                lines.append(prefix + item[0])
                lines.extend(_flatten_list_to_string_lines(item[1], indent + 1))
            else:
                lines.extend(_flatten_list_to_string_lines(item, indent))
        else:
            lines.append(prefix + str(item))
    return lines

def format_list_as_bullets(items):
    return "\n".join(_flatten_list_to_string_lines(items, 0))

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
        logger.info("Preparing replace requests...")
        requests = []
        for key, value in placeholders.items():
            replace_text = ""
            if isinstance(value, list):
                replace_text = format_list_as_bullets(value)
            else:
                # Handle nested dicts or non-string by converting to string
                replace_text = str(value)

            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': key,
                        'matchCase': True
                    },
                    'replaceText': replace_text
                }
            })

        if requests:
            logger.info("Executing batchUpdate...")
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': requests}
            ).execute()
            logger.info("Placeholders replaced successfully.")

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
# Main test function
# -------------------------

async def main():
    """
    Test function to demonstrate usage of generate_sow_document.
    """
    # Configure your Drive IDs
    # Set to a valid Google Docs format FILE ID
    TEMPLATE_DRIVE_ID = os.getenv("sow_template_drive_id")
    
    # Optional folder to put it in
    DRIVE_FOLDER_ID = os.getenv("sow_drive_folder_id") 
    
    # Needs valid credentials in env var 'sow-generator-sa' or absolute path
    CREDENTIALS = os.getenv("sow-generator-sa", "path/to/service_account.json")

    logger.info(f"credentials: {CREDENTIALS}")

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

    print("=" * 70)
    print("SOW Document Generator - Test Execution")
    print("=" * 70)
    print(f"\nTemplate ID: {TEMPLATE_DRIVE_ID}")
    
    result = await generate_sow_document(
        template_drive_id=TEMPLATE_DRIVE_ID,
        placeholders=sample_placeholders,
        document_title="SOW_Acme_Cloud_Migration_2026",
        credentials=CREDENTIALS,
        drive_folder_id=DRIVE_FOLDER_ID,
        share_with_emails=None,
        make_public=False
    )

    # result = await read_google_drive_file(
    #     file_id=TEMPLATE_DRIVE_ID,
    #     credentials=CREDENTIALS
    # )
    
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