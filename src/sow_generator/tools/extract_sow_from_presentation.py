"""Tool to extract SOW-relevant data from a PPTX presentation in GCS.

Orchestrates the full extraction pipeline: download from GCS, convert to
PDF, send to Gemini multimodal for structured extraction against the SOW
JSON schema, save results back to GCS.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types as genai_types

from ..sow_schema import SOW_JSON_SCHEMA, get_empty_sow_structure
from ..utils.gcs_utils import (
    delete_gcs_blob,
    download_blob_to_tempfile,
    parse_gcs_uri,
    upload_file_to_gcs,
    upload_json_to_gcs,
)
from ..utils.pptx_converter import (
    ConversionError,
    convert_pptx_to_pdf,
    extract_text_from_pptx,
)

logger = logging.getLogger(__name__)

_EXTRACTION_SYSTEM_PROMPT = """\
You are a document analysis expert. You receive presentation content and must \
extract information relevant to a Statement of Work (SOW).

RULES:
1. Extract ONLY information present in the source material.
2. Maintain the hierarchical structure of the SOW schema exactly.
3. If a section's information is NOT found, keep its value as "NA".
4. Filter out irrelevant content (logos, decorative text, page numbers, etc.).
5. Preserve the logical ordering and hierarchy of the slides.
6. For sections that contain lists or multiple items, use bullet-point format.
7. Return ONLY valid JSON matching the schema — no markdown fences, no commentary.

SOW JSON SCHEMA (populate each field):
"""


def _build_extraction_prompt() -> str:
    """Build the full extraction prompt including the SOW schema."""
    schema_str = json.dumps(SOW_JSON_SCHEMA, indent=2)
    return _EXTRACTION_SYSTEM_PROMPT + schema_str


def _parse_llm_json(raw_text: str) -> dict[str, Any]:
    """Parse LLM output into a JSON dict, handling markdown fences.

    Args:
        raw_text: Raw text response from the LLM.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(fence_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    try:
        return json.loads(text)  # type: ignore[no-any-return]
    except json.JSONDecodeError as exc:
        msg = f"Failed to parse LLM response as JSON: {exc}"
        raise ValueError(msg) from exc


def _merge_into_schema(
    extracted: dict[str, Any],
    template: dict[str, Any],
) -> dict[str, Any]:
    """Recursively merge extracted data into the SOW template.

    Any keys in the template not present in ``extracted`` remain "NA".
    """
    for key, default_val in template.items():
        if key in extracted:
            if isinstance(default_val, dict) and isinstance(extracted[key], dict):
                _merge_into_schema(extracted[key], default_val)
                template[key] = default_val
            else:
                template[key] = extracted[key]
    return template


async def extract_sow_from_presentation(gcs_uri: str) -> dict[str, Any]:
    """Extract SOW-relevant data from a PPTX file stored in GCS.

    This tool orchestrates a multi-step pipeline:
    1. Downloads the PPTX from GCS.
    2. Converts PPTX → PDF (or extracts text as fallback).
    3. Sends the content to Gemini for structured extraction.
    4. Merges the LLM output into the canonical SOW JSON schema.
    5. Saves the result as JSON to ``/processed_metadata/`` in the same bucket.
    6. Cleans up temporary files.

    Args:
        gcs_uri: GCS URI to the PPTX file
            (e.g. ``gs://bucket-name/path/to/file.pptx``).

    Returns:
        A dictionary containing:
        - ``status``: "success" or "error"
        - ``data``: The populated SOW structure (on success)
        - ``metadata_uri``: GCS URI of the saved JSON file (on success)
        - ``error``: Error message (on failure)
    """
    pptx_local: Path | None = None
    pdf_local: Path | None = None
    pdf_gcs_uri: str | None = None

    try:
        # ── Step 1: Download PPTX from GCS ──────────────────────────────
        logger.info("Starting extraction for: %s", gcs_uri)
        pptx_local = download_blob_to_tempfile(gcs_uri, suffix=".pptx")

        # ── Step 2: Convert PPTX → PDF or extract text ──────────────────
        use_pdf = True
        try:
            pdf_local = convert_pptx_to_pdf(pptx_local)
        except (ConversionError, FileNotFoundError) as conv_err:
            logger.warning(
                "PDF conversion failed, falling back to text extraction: %s",
                conv_err,
            )
            use_pdf = False

        # ── Step 3: Prepare content for Gemini ───────────────────────────
        model_name = os.getenv("REASONING_MODEL", "gemini-2.5-pro-preview-05-06")
        client = genai.Client(
            vertexai=bool(os.getenv("GOOGLE_GENAI_USE_VERTEXAI")),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

        extraction_prompt = _build_extraction_prompt()

        if use_pdf and pdf_local is not None:
            # Upload PDF to a temp GCS location for cloud-native processing
            bucket_name, _ = parse_gcs_uri(gcs_uri)
            pdf_blob_name = f"_tmp_extraction/{pdf_local.name}"
            pdf_gcs_uri = f"gs://{bucket_name}/{pdf_blob_name}"
            upload_file_to_gcs(pdf_local, pdf_gcs_uri)

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
                    temperature=0.1,
                    top_p=0.9,
                    seed=42,
                ),
            )
        else:
            # Fallback: send extracted text to Gemini
            slide_text = extract_text_from_pptx(pptx_local)
            logger.info("Sending extracted text to Gemini (%d chars)", len(slide_text))
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    genai_types.Content(
                        role="user",
                        parts=[
                            genai_types.Part.from_text(
                                text=(
                                    f"Presentation content:\n\n{slide_text}\n\n"
                                    f"{extraction_prompt}"
                                ),
                            ),
                        ],
                    ),
                ],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.9,
                    seed=42,
                ),
            )

        # ── Step 4: Parse and merge into SOW schema ──────────────────────
        raw_text = response.text or ""
        extracted_data = _parse_llm_json(raw_text)

        sow_structure = get_empty_sow_structure()
        if "sow_structure" in extracted_data:
            _merge_into_schema(
                extracted_data["sow_structure"],
                sow_structure["sow_structure"],
            )
        else:
            _merge_into_schema(extracted_data, sow_structure["sow_structure"])

        # ── Step 5: Save result JSON to GCS ──────────────────────────────
        bucket_name, blob_path = parse_gcs_uri(gcs_uri)
        source_stem = Path(blob_path).stem
        metadata_blob = f"processed_metadata/{source_stem}_sow_extracted.json"
        metadata_uri = f"gs://{bucket_name}/{metadata_blob}"

        upload_json_to_gcs(sow_structure, metadata_uri)
        logger.info("Extraction results saved to: %s", metadata_uri)

        return {
            "status": "success",
            "data": sow_structure,
            "metadata_uri": metadata_uri,
        }

    except Exception as exc:
        logger.error("Extraction failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}

    finally:
        # ── Step 6: Cleanup temporary files ──────────────────────────────
        if pptx_local is not None and pptx_local.exists():
            pptx_local.unlink(missing_ok=True)
        if pdf_local is not None and pdf_local.exists():
            pdf_local.unlink(missing_ok=True)
            # Also remove the temp directory created for PDF
            pdf_local.parent.rmdir()
        if pdf_gcs_uri is not None:
            try:
                delete_gcs_blob(pdf_gcs_uri)
            except Exception:  # noqa: BLE001
                logger.warning("Failed to clean up temp PDF: %s", pdf_gcs_uri)
