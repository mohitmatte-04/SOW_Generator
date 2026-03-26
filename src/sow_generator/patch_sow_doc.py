import os

file_path = "d:\\AI_ML\\SOW-Generator\\repo\\SOW_Generator\\src\\sow_generator\\tools\\generate_sow_document.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_code = """
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

def markdown_to_docs_requests(markdown_text: str, start_index: int):
    requests = []
    markdown_text = markdown_text.replace('\\r\\n', '\\n')
    lines = markdown_text.split('\\n')
    
    full_text = ""
    paragraph_ranges = []
    bold_ranges = []
    list_ranges = []
    
    current_index = start_index
    in_list = False
    list_start_idx = -1
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            if in_list:
                list_ranges.append((list_start_idx, current_index))
                in_list = False
            full_text += "\\n"
            current_index += 1
            continue
        
        style_type = 'NORMAL_TEXT'
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
            if not in_list:
                in_list = True
                list_start_idx = current_index
        else:
            line_content = line_stripped
            if in_list:
                list_ranges.append((list_start_idx, current_index))
                in_list = False
            
        line_clean, b_ranges = process_inline_markdown(line_content, current_index)
        line_text = line_clean + "\\n"
        full_text += line_text
        
        para_start = current_index
        para_end = current_index + len(line_text)
        
        paragraph_ranges.append((style_type, para_start, para_end))
        bold_ranges.extend(b_ranges)
        
        current_index += len(line_text)

    if in_list:
        list_ranges.append((list_start_idx, current_index))

    if not full_text:
        return []
        
    requests.append({
        'insertText': {
            'location': {'index': start_index},
            'text': full_text
        }
    })
    
    for style_type, start, end in paragraph_ranges:
        if style_type != 'NORMAL_TEXT':
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {'namedStyleType': style_type},
                    'fields': 'namedStyleType'
                }
            })
        
    for start, end in list_ranges:
        requests.append({
            'createParagraphBullets': {
                'range': {'startIndex': start, 'endIndex': end},
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })
        
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

def extract_sections_from_markdown(markdown_content: str, section_names: list = None) -> dict:
    import re
    from markdown_it import MarkdownIt
    
    # Strip markdown code block fences if present
    markdown_content = re.sub(r'^```[a-zA-Z]*\\n', '', markdown_content)
    markdown_content = re.sub(r'\\n```\\s*$', '', markdown_content)
    
    # Pre-process squashed text into proper markdown formatting
    known_sections = [
        "Title", "Customer Name", "Customer Short Name", "Customer Name Bold",
        "Provision Date", "MSA Date", "Opportunity", "Solution Overview",
        "Activities", "Deliverables", "Out of Scope", "Limitations",
        "Success Criteria", "Technical Assumptions", "Payment Schedule",
        "Appendix Details"
    ]
    
    headers_to_format = section_names if section_names else known_sections
    clean_names = [name.replace('<<', '').replace('>>', '').replace('_', ' ').title() if name.startswith('<<') else name for name in headers_to_format]
    clean_names.sort(key=len, reverse=True)
    
    placeholders_map = {}
    for i, clean_name in enumerate(clean_names):
        pattern = re.compile(r'(?:^|\\s+)#+\\s*' + re.escape(clean_name) + r'\\s*[:\\-]*\\s*', re.IGNORECASE)
        token = f"___HEADER_TOKEN_{i}___"
        placeholders_map[token] = f'\\n\\n# {clean_name}\\n'
        markdown_content = pattern.sub(token, markdown_content)
        
    for token, header_text in placeholders_map.items():
        markdown_content = markdown_content.replace(token, header_text)
        
    # Also fix lists and deeper headings
    markdown_content = re.sub(r'(?<=\\S)\\s+([-*]\\s+[A-Za-z0-9])', r'\\n\\1', markdown_content)
    markdown_content = re.sub(r'(?<=\\S)\\s+(#{2,6}\\s+[A-Za-z0-9])', r'\\n\\n\\1\\n', markdown_content)
    markdown_content = re.sub(r'\\n{3,}', '\\n\\n', markdown_content)
    markdown_content = markdown_content.strip()
    
    md = MarkdownIt()
    tokens = md.parse(markdown_content)

    extracted = {}
    current = None

    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            current = tokens[i+1].content.strip().lower()
            extracted[current] = []
        elif token.type == "inline" and current:
            extracted[current].append(token.content)

    extracted_dict = {k: "\\n".join(v).strip() for k, v in extracted.items()}
    
    # Map to placeholder format for compatibility with generate_sow_from_markdown
    sections = {}
    for key, content in extracted_dict.items():
        placeholder = f"<<{key.upper().replace(' ', '_')}>>"
        sections[placeholder] = content
        
    if section_names:
        filtered_sections = {}
        for name in section_names:
            placeholder = name if name.startswith("<<") and name.endswith(">>") else f"<<{name.upper().replace(' ', '_')}>>"
            # Try matching both by the original placeholder and by the normalized key
            if placeholder in sections:
                filtered_sections[placeholder] = sections[placeholder]
            else:
                # Some placeholders might not match exactly due to normalization (removing spaces, etc)
                # But here we assume the keys in `sections` are canonical.
                pass
        return filtered_sections
        
    return sections

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
"""

if "# Markdown to Google Docs logic" not in content:
    content = content.replace(
        "# -------------------------\n# Main test function",
        new_code + "\n# -------------------------\n# Main test function"
    )
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Code successfully injected!")
else:
    print("Code already exists!")
