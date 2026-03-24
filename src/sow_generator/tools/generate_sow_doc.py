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

def render_content_to_text_and_styles(content, level=1, bulleted=False):
    """
    Recursively convert nested dict/list into a single string and a list of style requests.
    Styles are relative to the start of the returned string (offset 0).
    """
    full_text = ""
    styles = []

    for item in content:
        # Case 1: Plain paragraph (or bullet if flag set)
        if isinstance(item, str):
            curr_offset = len(full_text)
            line_text = item + "\n"
            full_text += line_text

            if bulleted:
                styles.append({
                    "type": "bullet",
                    "offset": curr_offset,
                    "length": len(line_text)
                })

        # Case 2: Nested section
        elif isinstance(item, dict):
            # If it has an explicit title/content pattern
            if "title" in item or "content" in item:
                title = str(item.get("title") or "")
                sub_content = item.get("content")
                
                # Render this single section
                content_to_process = [(title, sub_content)]
            else:
                # Multi-key dictionary: treat each key as a title
                content_to_process = list(item.items())

            for title, sub_content in content_to_process:
                # Heading
                curr_offset = len(full_text)
                heading_text = str(title) + "\n"
                full_text += heading_text

                styles.append({
                    "type": "section_title",
                    "offset": curr_offset,
                    "length": len(heading_text),
                    "level": min(level + 1, 6)
                })

                # Recursively render children
                sub_content = sub_content if isinstance(sub_content, (list, str, dict)) else []
                if isinstance(sub_content, (str, dict)):
                    sub_content = [sub_content]
                
                child_bulleted = any(isinstance(x, str) for x in sub_content) if isinstance(sub_content, list) else False
                child_text, child_styles = render_content_to_text_and_styles(
                    sub_content, level + 1, bulleted=child_bulleted
                )

                # Shift child styles by current full_text length and add
                content_start_offset = len(full_text)
                full_text += child_text
                for s in child_styles:
                    s["offset"] += content_start_offset
                    styles.append(s)

        # Case 3: List (rarely happens at this level but handle for safety)
        elif isinstance(item, list):
            child_text, child_styles = render_content_to_text_and_styles(item, level, bulleted=True)
            content_start_offset = len(full_text)
            full_text += child_text
            for s in child_styles:
                s["offset"] += content_start_offset
                styles.append(s)

    return full_text, styles


def search_elements(elements, placeholder):
    """
    Recursively search for ALL occurrences of placeholder within structural elements.
    Returns a list of (start, end) tuples.
    """
    matches = []
    for element in elements:
        if "paragraph" in element:
            para = element["paragraph"]
            for run in para.get("elements", []):
                if "textRun" in run:
                    text = run.get("textRun", {}).get("content", "")
                    
                    # Fuzzy match: case-insensitive
                    u_text = text.upper()
                    u_placeholder = placeholder.upper()

                    curr_pos = 0
                    while True:
                        pos = u_text.find(u_placeholder, curr_pos)
                        if pos == -1:
                            break
                        
                        # We found a match. Calculate exact indices.
                        # Note: We use the length of the actual placeholder string passed in
                        actual_start = (run.get("startIndex") or 0) + pos
                        actual_end = actual_start + len(placeholder)
                        matches.append((actual_start, actual_end))
                        curr_pos = pos + len(placeholder)
        elif "table" in element:
            table = element["table"]
            for row in table.get("tableRows", []):
                for cell in row.get("tableCells", []):
                    matches.extend(search_elements(cell.get("content", []), placeholder))
    return matches

def find_placeholder(doc, placeholder):
    """
    Find ALL occurrences of a placeholder in the doc body, headers, or footers.
    Returns a list of (start, end, segment_id) tuples.
    """
    all_matches = []
    
    # 1. Search Body
    body_matches = search_elements(doc.get("body", {}).get("content", []), placeholder)
    for start, end in body_matches:
        all_matches.append((start, end, None))
    
    # 2. Search Headers
    headers = doc.get("headers", {})
    for header_id in headers:
        header_matches = search_elements(headers[header_id].get("content", []), placeholder)
        for start, end in header_matches:
            all_matches.append((start, end, header_id))
            
    # 3. Search Footers
    footers = doc.get("footers", {})
    for footer_id in footers:
        footer_matches = search_elements(footers[footer_id].get("content", []), placeholder)
        for start, end in footer_matches:
            all_matches.append((start, end, footer_id))
            
    return all_matches


def replace_placeholder_with_dict(docs_service, doc_id, placeholder, section_data):
    """
    Replace ALL occurrences of a placeholder with hierarchical section data.
    """
    # Get document to find location
    doc = docs_service.documents().get(documentId=doc_id).execute()
    matches = find_placeholder(doc, placeholder)

    if not matches:
        print(f"Placeholder {placeholder} not found in document content.")
        return

    # To handle multiple replacements correctly, we must process them in REVERSE order
    # so that index shifts from earlier replacements don't affect later ones.
    # Group by segment_id then sort by startIndex descending.
    matches_by_segment = {}
    for start, end, sid in matches:
        if sid not in matches_by_segment:
            matches_by_segment[sid] = []
        matches_by_segment[sid].append((start, end))

    requests = []

    # Prepare ALL content first
    all_text, styles = "", []
    if isinstance(section_data, str):
        all_text = section_data + "\n"
    elif isinstance(section_data, list):
        all_text, styles = render_content_to_text_and_styles(section_data, level=1, bulleted=True)
    elif isinstance(section_data, dict):
        if "title" in section_data or "content" in section_data:
            title = str(section_data.get("title") or "")
            content = section_data.get("content")
            content_to_process = [(title, content)]
        else:
            content_to_process = list(section_data.items())

        for title, content in content_to_process:
            title_text = str(title) + "\n" if title else ""
            curr_title_offset = len(all_text)
            if title_text:
                all_text += title_text
                styles.append({"type": "section_title", "offset": curr_title_offset, "length": len(title_text), "level": 1})
            content = content if isinstance(content, (list, str, dict)) else []
            if isinstance(content, (str, dict)): content = [content]
            child_text, child_styles = render_content_to_text_and_styles(content, level=1)
            content_start_offset = len(all_text)
            all_text += child_text
            for s in child_styles:
                s["offset"] += content_start_offset
                styles.append(s)
    else:
        all_text = str(section_data) + "\n"

    # Create insertion and styling requests for EACH match
    # Crucially, we must sort by startIndex DESCENDING to avoid indexing issues
    if all_text:
        for sid, seg_matches in matches_by_segment.items():
            # Sort matches in this segment by start index descending
            seg_matches.sort(key=lambda x: x[0], reverse=True)
            
            for start, end in seg_matches:
                # 1. Delete placeholder
                drange = {"startIndex": start, "endIndex": end}
                if sid: drange["segmentId"] = sid
                requests.append({"deleteContentRange": {"range": drange}})

                # 2. Insert text
                loc = {"index": start}
                if sid: loc["segmentId"] = sid
                requests.append({"insertText": {"location": loc, "text": all_text}})

                # 3. Apply styles relative to this 'start'
                for s in styles:
                    s_start = start + s["offset"]
                    s_end = s_start + s["length"]
                    srange = {"startIndex": s_start, "endIndex": s_end}
                    if sid: srange["segmentId"] = sid

                    if s["type"] == "section_title":
                        # Set to normal text style but make it bold
                        requests.append({
                            "updateParagraphStyle": {
                                "range": srange,
                                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                "fields": "namedStyleType"
                            }
                        })
                        requests.append({
                            "updateTextStyle": {
                                "range": srange,
                                "textStyle": {"bold": True},
                                "fields": "bold"
                            }
                        })
                    elif s["type"] == "bullet":
                        requests.append({"createParagraphBullets": {"range": srange, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})

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
        # Generate candidates for this key
        raw_key = key.replace("<<", "").replace(">>", "").replace("{{", "").replace("}}", "")
        
        placeholder_candidates = [
            key,                         # Exact key from JSON (e.g. "<<TITLE>>")
            f"<<{raw_key}>>",            # <<TITLE>>
            f"{{{{{raw_key}}}}}"         # {{TITLE}}
        ]
        
        # Specific fallbacks for poorly named placeholders in the template
        if "PROVISION_DATE" in raw_key.upper():
            placeholder_candidates.append("xxxxxxxxxx")
        if "ENTER_MSA_DATE" in raw_key.upper():
            placeholder_candidates.append("<<Enter MSA Date>>")

        # Deduplicate candidates
        placeholder_candidates = list(dict.fromkeys(placeholder_candidates))
        
        target_placeholder = None
        
        doc = docs_service.documents().get(documentId=doc_id).execute()
        for cand in placeholder_candidates:
            matches = find_placeholder(doc, cand)
            if matches:
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
        agent_result = json.load(f)
    
    logger.info(f"agent result {agent_result}")
    logger.info(f"type of agent result {type(agent_result)}")
    placeholders = {
            "<<TITLE>>": agent_result.get("title", "Not specified."),
            "<<CUSTOMER_NAME>>": agent_result.get("customer_name", "Not specified."),
            "<<CUSTOMER_SHORT_NAME>>": agent_result.get("customer_short_name", "Not specified."),
            "<<CUSTOMER_NAME_BOLD>>": agent_result.get("customer_name_bold", "Not specified."),
            "<<PROVISION_DATE>>": agent_result.get("provision_date", "Not specified."),
            "<<Enter MSA Date>>": agent_result.get("enter_msa_date", "Not specified."),
            "<<OPPORTUNITY>>": agent_result.get("opportunity", "Not specified."),
            "<<SOLUTION_OVERVIEW>>": agent_result.get("solution_overview", "Not specified."),
            "<<ACTIVITIES>>": agent_result.get("activities", "Not specified."),
            "<<DELIVERABLES>>": agent_result.get("deliverables", "Not specified."),
            "<<OUT_OF_SCOPE>>": agent_result.get("out_of_scope", "Not specified."),
            "<<LIMITATIONS>>": agent_result.get("limitations", "Not specified."),
            "<<SUCCESS_CRITERIA>>": agent_result.get("success_criteria", "Not specified."),
            "<<TECHNICAL_ASSUMPTIONS>>": agent_result.get("technical_assumptions", "Not specified."),
            "<<PAYMENT_SCHEDULE>>": agent_result.get("payment_schedule", "Not specified."),
            "<<ADD_APPENDIX_DETAILS>>": agent_result.get("add_appendix_details", "Not specified."),
        }

    result = await generate_sow_document(
        template_drive_id=TEMPLATE_DRIVE_ID,
        placeholders=agent_result,
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