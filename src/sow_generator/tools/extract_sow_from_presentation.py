# """Tool to extract SOW-relevant data from a PPTX presentation in GCS.

# Orchestrates the full extraction pipeline: download from GCS, convert to
# PDF using Google Slides API, save PDF as artifact using ADK artifact service,
# send to Gemini multimodal for structured extraction against the SOW JSON schema,
# save results back to GCS.
# """

# import json
# import logging
# import os
# import re
# from pathlib import Path
# from typing import Any

# from google import genai
# from google.adk.agents.tool_context import ToolContext
# from google.genai import types as genai_types

# from ..sow_schema import SOW_JSON_SCHEMA
# from ..utils.gcs_utils import (
#     download_blob_to_tempfile,
#     parse_gcs_uri,
#     upload_json_to_gcs,
# )
# from ..utils.google_slides_to_pdf_converter import (
#     ConversionError,
#     GoogleSlidesConverter,
# )
# from ..utils.pptx_converter import extract_text_from_pptx

# logger = logging.getLogger(__name__)

# _EXTRACTION_SYSTEM_PROMPT = """\
# You are a document analysis expert. You receive a proposal presentation and \
# must extract information into a structured SOW (Statement of Work) template.

CRITICAL RULES - NO HALLUCINATION:
1. Extract ONLY information EXPLICITLY present in the proposal document.
2. ABSOLUTELY FORBIDDEN: Adding, inferring, fabricating, paraphrasing, or \
embellishing ANY information.
3. Copy relevant text EXACTLY AS-IS from the source — character-for-character \
where possible. Do NOT rephrase, reword, or expand.
4. If you cannot find specific information for a field, use "NA" — NEVER guess \
or create placeholder content.
5. DO NOT copy the same content to multiple fields. Each piece of information \
should appear in ONLY ONE field (the most semantically appropriate one).
6. Filter out irrelevant content (logos, decorative text, page numbers, slide \
numbers, footer text, "Thank You" slides).
7. Each key in the template has a DESCRIPTION of what to look for. Replace \
the description with the ACTUAL content found in the proposal.
8. Match proposal headings/titles to the closest SOW template section by \
semantic meaning. If uncertain, choose ONE field (don't duplicate).
9. Return ONLY valid JSON matching the template structure — no markdown \
fences, no commentary.

DEDUPLICATION RULE (CRITICAL):
Before finalizing your JSON, scan through ALL fields and ensure no content \
is duplicated across multiple fields. If you find the same text in multiple \
places, keep it ONLY in the most appropriate field and set others to "NA".

STRUCTURE PRESERVATION RULES (CRITICAL):
10. Analyze how content is structured in the source document and preserve that \
structure in your JSON output:
   - BULLET POINTS or NUMBERED LISTS → extract as JSON array
   - CONTINUOUS PARAGRAPH(S) → extract as single string
   - NESTED SUB-POINTS (indented or sub-numbered) → preserve hierarchy using nested arrays
   - TABLE ROWS → extract as JSON array (each row becomes an array item)

11. When extracting list-structured content (bullets/numbered items):
   - Each bullet point or list item becomes a separate string in a JSON array
   - DO NOT merge multiple distinct points into a single paragraph string
   - DO NOT include bullet symbols (•, -, *, >) or numbers (1., 2., 3., a., b.) — extract only text
   - For items WITH sub-points, use a nested array structure (see examples below)
   - For items WITHOUT sub-points, use simple strings in the array

12. DETECTING SUB-POINTS (multiple methods):
   - Visual indentation (text indented further right than parent)
   - Different bullet style (e.g., • for main, - or ◦ for sub)
   - Sub-numbering (1.1, 1.2 or a., b. under 1.)
   - Hierarchical structure in tables (parent-child relationships)
   - ALL of these indicate sub-points and should use nested array format

13. When extracting paragraph-structured content:
   - Keep as a single string with the full narrative text
   - Preserve paragraph breaks using \\n if multiple paragraphs exist

14. Mixed content handling:
   - If BULLETS are the primary content: return as JSON array
   - If PARAGRAPH is primary with minor bullets: convert each bullet to a \
     separate paragraph and combine all using \\n separators into a single string

TABLE PARSING RULES (CRITICAL):

Tables are common in presentations (especially for deliverables, scope, phases, etc.).

15. When encountering a TABLE structure:
   - Identify the table headers/column names in the first row or first column
   - Determine if it's a 2-column format (label | content) or multi-column
   - Extract data based on semantic meaning, not just position

16. TWO-COLUMN TABLE FORMAT (most common):
   - First column contains: section names, deliverable names, phase names, etc.
   - Second column contains: descriptions, details, content
   - Extract each row as a separate item
   - If rows have hierarchical relationship (parent-child), use nested arrays

17. MULTI-COLUMN TABLE FORMAT:
   - Analyze headers to understand what each column represents
   - Combine column data logically for each row
   - Format: "Column1: value1, Column2: value2" OR use nested structure

TABLE PARSING EXAMPLES:

Example 1 - Two-column deliverables table:

| Deliverable           | Description                           |
|-----------------------|---------------------------------------|
| Architecture Document | Detailed design of cloud architecture |
| Migration Plan        | Step-by-step migration procedures     |
| Testing Report        | Validation and test results           |

Extract as:
"deliverables": [
  "Architecture Document - Detailed design of cloud architecture",
  "Migration Plan - Step-by-step migration procedures",
  "Testing Report - Validation and test results"
]

Example 2 - Hierarchical table with parent-child rows:

| Phase               | Activities                       |
|---------------------|----------------------------------|
| Phase 1: Discovery  |                                  |
|   ↳ Activity 1.1    | Requirements gathering           |
|   ↳ Activity 1.2    | Stakeholder interviews           |
| Phase 2: Design     | Architecture design              |

Extract as:
"activities": [
  ["Phase 1: Discovery", [
    "Requirements gathering",
    "Stakeholder interviews"
  ]],
  "Phase 2: Design - Architecture design"
]

Example 3 - Table in shapes/text boxes:

If table-like content appears in shapes, text boxes, or SmartArt:
- Look for visual alignment, indentation, and spacing
- Treat aligned items at same indent level as siblings
- Treat indented items as children (use nested arrays)

SHAPE AND TEXT BOX PARSING:

18. Content in SHAPES, TEXT BOXES, or SMARTART:
   - Extract text content from all shapes (don't ignore them!)
   - Analyze spatial positioning:
     * Items at same horizontal level = same hierarchy (siblings)
     * Items indented/positioned to the right = sub-items (children)
   - Preserve this hierarchy using nested arrays

19. VISUAL INDENTATION DETECTION:
   - If text has LEADING SPACES or TAB characters → sub-item
   - If text is VISUALLY POSITIONED to the right → sub-item
   - If text uses smaller font or different color AND is indented → sub-item

HANDLING NESTED SUB-POINTS:

When a bullet point has sub-points (detected by ANY method below):
- Different bullet symbols (•, -, ◦, ▪)
- Numbering (1.1, 1.2, a., b.)
- Visual indentation
- Table hierarchy
- Spatial positioning in shapes

Represent as nested array: [main_point_text, [sub_point_1, sub_point_2, ...]]

Source example with indentation:
  • Phase 1: Planning
      Requirements gathering
      Stakeholder interviews
  • Phase 2: Implementation
  • Phase 3: Testing
      Unit testing
      Integration testing

Extract as:
"activities": [
  ["Phase 1: Planning", [
    "Requirements gathering",
    "Stakeholder interviews"
  ]],
  "Phase 2: Implementation",
  ["Phase 3: Testing", [
    "Unit testing",
    "Integration testing"
  ]]
]

EXAMPLES:

Simple bullet list (no nesting):
Source:
  • Design cloud architecture
  • Migrate databases to GCP
  • Implement security controls

Extract as:
"activities": [
  "Design cloud architecture",
  "Migrate databases to GCP",
  "Implement security controls"
]

Paragraph content:
Source:
  "The client faces challenges with legacy infrastructure. Performance issues \
  have impacted operations."

Extract as (COPY EXACTLY, no rephrasing):
"opportunity": "The client faces challenges with legacy infrastructure. Performance issues have impacted operations."

Mixed content (paragraph primary, minor bullets):
Source:
  "The engagement includes the following key activities:
  • Database migration
  • Security implementation
  Additional optimization work will be performed."

Extract as:
"activities": "The engagement includes the following key activities:\\nDatabase migration\\nSecurity implementation\\nAdditional optimization work will be performed."

If ANY field has no matching content, use "NA" (string, not array).

FINAL VALIDATION BEFORE RETURNING JSON:
1. Scan all fields - is any content duplicated? If yes, keep in ONE field only.
2. Did you add/rephrase ANY text? If yes, revert to exact source text.
3. Are table contents properly parsed into arrays?
4. Are nested structures properly represented with nested arrays?
5. Is the JSON valid and parseable?

# SOW TEMPLATE (replace descriptions with extracted content):
# """


# def _build_extraction_prompt() -> str:
#     """Build the full extraction prompt including the SOW schema."""
#     schema_str = json.dumps(SOW_JSON_SCHEMA, indent=2)
#     return _EXTRACTION_SYSTEM_PROMPT + schema_str


# def _parse_llm_json(raw_text: str) -> dict[str, Any]:
#     """Parse LLM output into a JSON dict, handling markdown fences and extra data.

#     Gemini may return trailing commentary, multiple JSON objects, or prose
#     after the JSON block. This function extracts the *first* complete JSON
#     object by scanning brace depth.

#     Args:
#         raw_text: Raw text response from the LLM.

#     Returns:
#         Parsed dictionary.

#     Raises:
#         ValueError: If no valid JSON object can be found in the response.
#     """
#     text = raw_text.strip()

#     # 1. Strip markdown code fences if present
#     fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
#     match = re.search(fence_pattern, text, re.DOTALL)
#     if match:
#         text = match.group(1).strip()

#     # 2. Try direct parse first (fast path)
#     try:
#         return json.loads(text)  # type: ignore[no-any-return]
#     except json.JSONDecodeError:
#         pass

#     # 3. Fallback: extract the first complete JSON object by brace scanning
#     start = text.find("{")
#     if start == -1:
#         msg = "Failed to parse LLM response as JSON: no JSON object found"
#         raise ValueError(msg)

#     depth = 0
#     in_string = False
#     escape_next = False
#     for i, ch in enumerate(text[start:], start):
#         if escape_next:
#             escape_next = False
#             continue
#         if ch == "\\" and in_string:
#             escape_next = True
#             continue
#         if ch == '"':
#             in_string = not in_string
#             continue
#         if in_string:
#             continue
#         if ch == "{":
#             depth += 1
#         elif ch == "}":
#             depth -= 1
#             if depth == 0:
#                 candidate = text[start : i + 1]
#                 try:
#                     return json.loads(candidate)  # type: ignore[no-any-return]
#                 except json.JSONDecodeError as exc:
#                     msg = (
#                         f"Failed to parse LLM response as JSON: {exc}"
#                     )
#                     raise ValueError(msg) from exc

#     msg = "Failed to parse LLM response as JSON: incomplete JSON object"
#     raise ValueError(msg)


# def _validate_extracted_output(
#     extracted: dict[str, Any],
# ) -> dict[str, Any]:
#     """Validate and normalize LLM output.

#     Ensures the output has the expected ``statement_of_work_template``
#     top-level key. If the LLM returned inner content directly, wraps it.
#     """
#     if "statement_of_work_template" in extracted:
#         return extracted
#     return {"statement_of_work_template": extracted}


# async def extract_sow_from_presentation(
#     context: ToolContext, gcs_uri: str
# ) -> dict[str, Any]:
#     """Extract SOW-relevant data from a PPTX file stored in GCS.

#     This tool orchestrates a multi-step pipeline:
#     1. Downloads the PPTX from GCS.
#     2. Converts PPTX → PDF using Google Slides API.
#     3. Saves the PDF as an artifact using ADK artifact service.
#     4. Sends the PDF artifact to Gemini for structured extraction.
#     5. Merges the LLM output into the canonical SOW JSON schema.
#     6. Saves the result as JSON to ``/processed_metadata/`` in the same bucket.
#     7. Cleans up temporary local files (PDF artifact persists via artifact service).

#     Args:
#         context: ADK ToolContext for accessing artifact service and session.
#         gcs_uri: GCS URI to the PPTX file
#             (e.g. ``gs://bucket-name/path/to/file.pptx``).

    Returns:
        A dictionary containing:
        - ``status``: "success" or "error"
        - ``data``: The populated SOW structure (on success)
        - ``metadata_uri``: GCS URI of the saved JSON file (on success)
        - ``error``: Error message (on failure)
    """
    # ═══════════════════════════════════════════════════════════════════
    # TESTING-1: PPTX conversion commented out for faster PDF testing
    # To revert: ask "revert testing-1"
    # ═══════════════════════════════════════════════════════════════════
    # pptx_local: Path | None = None
    # pdf_local: Path | None = None
    pdf_gcs_uri: str | None = None

    try:
        # ── Step 1: Check if PDF or PPTX ──────────────────────────────
        logger.info("Starting extraction for: %s", gcs_uri)

        # Check if input is already a PDF
        if gcs_uri.lower().endswith('.pdf'):
            # Input is PDF - use directly from GCS
            logger.info("Input is PDF, using directly from GCS")
            pdf_gcs_uri = gcs_uri
        else:
            # Input is PPTX - COMMENTED OUT for testing
            logger.error("PPTX conversion is COMMENTED OUT for testing (testing-1)")
            raise ValueError("PPTX conversion is currently disabled for faster testing. Please provide a PDF file instead (e.g., gs://bucket/path/file.pdf)")

        # ═══════════════════════════════════════════════════════════════════
        # COMMENTED OUT (testing-1): PPTX download and conversion
        # ═══════════════════════════════════════════════════════════════════
        # pptx_local = download_blob_to_tempfile(gcs_uri, suffix=".pptx")
        #
        # # ── Step 2: Convert PPTX → PDF or extract text ──────────────────
        # use_pdf = True
        # try:
        #     pdf_local = convert_pptx_to_pdf(pptx_local)
        #     # Upload PDF to a temp GCS location for cloud-native processing
        #     bucket_name, _ = parse_gcs_uri(gcs_uri)
        #     pdf_blob_name = f"_tmp_extraction/{pdf_local.name}"
        #     pdf_gcs_uri = f"gs://{bucket_name}/{pdf_blob_name}"
        #     upload_file_to_gcs(pdf_local, pdf_gcs_uri)
        # except (ConversionError, FileNotFoundError) as conv_err:
        #     logger.warning(
        #         "PDF conversion failed, falling back to text extraction: %s",
        #         conv_err,
        #     )
        #     use_pdf = False
        # ═══════════════════════════════════════════════════════════════════

        # ── Step 2: Prepare content for Gemini ───────────────────────────
        model_name = os.getenv("REASONING_MODEL", "gemini-2.0-flash-exp")
        client = genai.Client(
            vertexai=bool(os.getenv("GOOGLE_GENAI_USE_VERTEXAI")),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

#         extraction_prompt = _build_extraction_prompt()

        # Send PDF to Gemini (directly from GCS)
        logger.info("Sending PDF to Gemini via GCS: %s", pdf_gcs_uri)
        response = client.models.generate_content(
            model=model_name,
            contents=[
                genai_types.Content(
                    role="user",
                    parts=[
                        genai_types.Part.from_uri(
                            file_uri=pdf_gcs_uri,
                            mime_type="application/pdf",
                        ),
                        genai_types.Part.from_text(text=extraction_prompt),
                    ],
                ),
            ],
            config=genai_types.GenerateContentConfig(
                temperature=0.0,  # Fully deterministic
                top_p=1.0,
                top_k=1,
                max_output_tokens=16384,  # Large enough for full JSON schema output
                seed=42,
            ),
        )

        # ═══════════════════════════════════════════════════════════════════
        # COMMENTED OUT (testing-1): Fallback text extraction
        # ═══════════════════════════════════════════════════════════════════
        # else:
        #     # Fallback: send extracted text to Gemini
        #     slide_text = extract_text_from_pptx(pptx_local)
        #     logger.info("Sending extracted text to Gemini (%d chars)", len(slide_text))
        #     response = client.models.generate_content(
        #         model=model_name,
        #         contents=[
        #             genai_types.Content(
        #                 role="user",
        #                 parts=[
        #                     genai_types.Part.from_text(
        #                         text=(
        #                             f"Presentation content:\n\n{slide_text}\n\n"
        #                             f"{extraction_prompt}"
        #                         ),
        #                     ),
        #                 ],
        #             ),
        #         ],
        #         config=genai_types.GenerateContentConfig(
        #             temperature=0.1,  # Fully deterministic
        #             top_p=1.0,
        #             top_k=1,
        #             max_output_tokens=8192,
        #             seed=42,
        #         ),
        #     )
        # ═══════════════════════════════════════════════════════════════════

        # ── Step 4: Parse and validate extracted data ────────────────────
        raw_text = response.text or ""
        extracted_data = _parse_llm_json(raw_text)
        sow_output = _validate_extracted_output(extracted_data)

#         # ── Step 5: Save result JSON to GCS ──────────────────────────────
#         bucket_name, blob_path = parse_gcs_uri(gcs_uri)
#         source_stem = Path(blob_path).stem
#         metadata_blob = f"processed_metadata/{source_stem}_sow_extracted.json"
#         metadata_uri = f"gs://{bucket_name}/{metadata_blob}"

#         upload_json_to_gcs(sow_output, metadata_uri)
#         logger.info("Extraction results saved to: %s", metadata_uri)

#         # Prepare result with artifact information
#         result = {
#             "status": "success",
#             "metadata_uri": metadata_uri,
#         }

#         # Include PDF artifact information if PDF conversion was used
#         if pdf_artifact_filename:
#             result["pdf_artifact_filename"] = pdf_artifact_filename
#             result["pdf_artifact_version"] = pdf_artifact_version

#         return result

#     except Exception as exc:
#         logger.error("Extraction failed: %s", exc, exc_info=True)
#         return {"status": "error", "error": str(exc)}

    finally:
        # ── Step 6: Cleanup temporary files ──────────────────────────────
        # ═══════════════════════════════════════════════════════════════════
        # COMMENTED OUT (testing-1): Cleanup for PPTX/PDF local files
        # ═══════════════════════════════════════════════════════════════════
        # if pptx_local is not None and pptx_local.exists():
        #     pptx_local.unlink(missing_ok=True)
        # if pdf_local is not None and pdf_local.exists():
        #     pdf_local.unlink(missing_ok=True)
        #     # Also remove the temp directory created for PDF
        #     pdf_local.parent.rmdir()
        # if pdf_gcs_uri is not None and pdf_gcs_uri.startswith("gs://") and "_tmp_extraction/" in pdf_gcs_uri:
        #     # Only delete if it's a temp file we created, not the original input PDF
        #     try:
        #         delete_gcs_blob(pdf_gcs_uri)
        #     except Exception:  # noqa: BLE001
        #         logger.warning("Failed to clean up temp PDF: %s", pdf_gcs_uri)
        # ═══════════════════════════════════════════════════════════════════

        # No cleanup needed when using PDF directly from GCS
        pass
