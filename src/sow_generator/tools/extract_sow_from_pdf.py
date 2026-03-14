"""Tool to extract SOW data from a PDF file.

Sends a PDF to Gemini for structured extraction against the SOW JSON schema
and saves results to GCS.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types as genai_types

from ..sow_schema import SOW_JSON_SCHEMA
from ..utils.gcs_utils import parse_gcs_uri, upload_json_to_gcs

logger = logging.getLogger(__name__)

_EXTRACTION_SYSTEM_PROMPT = """\
You are a document analysis expert. You receive a proposal presentation and \
must extract information into a structured SOW (Statement of Work) template.

CRITICAL RULES:
1. Extract ONLY information explicitly present in the proposal document.
2. DO NOT add, infer, fabricate, or embellish ANY information.
3. Copy relevant text as-is from the source — do not rephrase or expand.
4. Each key in the template has a DESCRIPTION of what to look for. \
Replace the description with the ACTUAL content found in the proposal.
5. If a section has no matching content in the proposal, set its value to "NA".
6. Match proposal headings/titles to the closest SOW template section by \
semantic meaning. Map content under each proposal heading into the \
corresponding template key.
7. If a proposal heading covers multiple template sections, split the content.
8. If multiple proposal headings map to one template section, combine them.
9. Filter out irrelevant content (logos, decorative text, page numbers).
10. Return ONLY valid JSON matching the template structure — no markdown \
fences, no commentary.

SOW TEMPLATE (replace descriptions with extracted content):
"""


def _build_extraction_prompt() -> str:
    """Build the full extraction prompt including the SOW schema."""
    schema_str = json.dumps(SOW_JSON_SCHEMA, indent=2)
    return _EXTRACTION_SYSTEM_PROMPT + schema_str


def _parse_llm_json(raw_text: str) -> dict[str, Any]:
    """Parse LLM output into a JSON dict, handling markdown fences and extra data.

    Gemini may return trailing commentary, multiple JSON objects, or prose
    after the JSON block. This function extracts the *first* complete JSON
    object by scanning brace depth.

    Args:
        raw_text: Raw text response from the LLM.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If no valid JSON object can be found in the response.
    """
    text = raw_text.strip()

    # 1. Strip markdown code fences if present
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(fence_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    # 2. Try direct parse first (fast path)
    try:
        return json.loads(text)  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        pass

    # 3. Fallback: extract the first complete JSON object by brace scanning
    start = text.find("{")
    if start == -1:
        msg = "Failed to parse LLM response as JSON: no JSON object found"
        raise ValueError(msg)

    depth = 0
    in_string = False
    escape_next = False
    for i, ch in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)  # type: ignore[no-any-return]
                except json.JSONDecodeError as exc:
                    msg = f"Failed to parse LLM response as JSON: {exc}"
                    raise ValueError(msg) from exc

    msg = "Failed to parse LLM response as JSON: incomplete JSON object"
    raise ValueError(msg)


def _validate_extracted_output(extracted: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize LLM output.

    Ensures the output has the expected ``statement_of_work_template``
    top-level key. If the LLM returned inner content directly, wraps it.
    """
    if "statement_of_work_template" in extracted:
        return extracted
    return {"statement_of_work_template": extracted}


async def extract_sow_from_pdf(
    pdf_gcs_uri: str, original_gcs_uri: str
) -> dict[str, Any]:
    """Extract SOW-relevant data from a PDF file.

    This tool sends the PDF to Gemini for structured extraction, merges the
    output into the canonical SOW JSON schema, and saves the result to GCS.

    The PDF file path will be provided by a before-tool callback that loads
    the artifact saved by the convert_slides_to_pdf tool.

    Args:
        pdf_gcs_uri: GCS URI to the PDF file (loaded from artifact).
        original_gcs_uri: Original GCS URI of the source PPTX (for naming).

    Returns:
        A dictionary containing:
        - ``status``: "success" or "error"
        - ``metadata_uri``: GCS URI of the saved JSON file (on success)
        - ``error``: Error message (on failure)
    """
    try:
        # Step 1: Prepare Gemini client
        model_name = os.getenv("REASONING_MODEL", "gemini-2.0-flash-exp")
        client = genai.Client(
            vertexai=bool(os.getenv("GOOGLE_GENAI_USE_VERTEXAI")),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

        extraction_prompt = _build_extraction_prompt()

        # Step 2: Send PDF to Gemini for extraction
        logger.info("Sending PDF to Gemini for extraction: %s", pdf_gcs_uri)
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
                max_output_tokens=8192,  # Large enough for full JSON schema output
                seed=42,
            ),
        )

        # Step 3: Parse and validate extracted data
        raw_text = response.text or ""
        extracted_data = _parse_llm_json(raw_text)
        sow_output = _validate_extracted_output(extracted_data)

        # Step 4: Save result JSON to GCS
        bucket_name, blob_path = parse_gcs_uri(original_gcs_uri)
        source_stem = Path(blob_path).stem
        metadata_blob = f"processed_metadata/{source_stem}_sow_extracted.json"
        metadata_uri = f"gs://{bucket_name}/{metadata_blob}"

        upload_json_to_gcs(sow_output, metadata_uri)
        logger.info("Extraction results saved to: %s", metadata_uri)

        return {"status": "success", "metadata_uri": metadata_uri}

    except Exception as exc:
        logger.error("Extraction failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
