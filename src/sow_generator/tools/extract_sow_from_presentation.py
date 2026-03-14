"""Tool to extract SOW-relevant data from a PPTX presentation in GCS.

Orchestrates the full extraction pipeline: download from GCS, convert to
PDF using Google Slides API, save PDF as artifact using ADK artifact service,
send to Gemini multimodal for structured extraction against the SOW JSON schema,
save results back to GCS.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from google import genai
from google.adk.agents import ToolContext
from google.genai import types as genai_types

from ..sow_schema import SOW_JSON_SCHEMA
from ..utils.gcs_utils import (
    download_blob_to_tempfile,
    parse_gcs_uri,
    upload_json_to_gcs,
)
from ..utils.google_slides_to_pdf_converter import (
    ConversionError,
    GoogleSlidesConverter,
)
from ..utils.pptx_converter import extract_text_from_pptx

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
                    msg = (
                        f"Failed to parse LLM response as JSON: {exc}"
                    )
                    raise ValueError(msg) from exc

    msg = "Failed to parse LLM response as JSON: incomplete JSON object"
    raise ValueError(msg)


def _validate_extracted_output(
    extracted: dict[str, Any],
) -> dict[str, Any]:
    """Validate and normalize LLM output.

    Ensures the output has the expected ``statement_of_work_template``
    top-level key. If the LLM returned inner content directly, wraps it.
    """
    if "statement_of_work_template" in extracted:
        return extracted
    return {"statement_of_work_template": extracted}


async def extract_sow_from_presentation(
    context: ToolContext, gcs_uri: str
) -> dict[str, Any]:
    """Extract SOW-relevant data from a PPTX file stored in GCS.

    This tool orchestrates a multi-step pipeline:
    1. Downloads the PPTX from GCS.
    2. Converts PPTX → PDF using Google Slides API.
    3. Saves the PDF as an artifact using ADK artifact service.
    4. Sends the PDF artifact to Gemini for structured extraction.
    5. Merges the LLM output into the canonical SOW JSON schema.
    6. Saves the result as JSON to ``/processed_metadata/`` in the same bucket.
    7. Cleans up temporary local files (PDF artifact persists via artifact service).

    Args:
        context: ADK ToolContext for accessing artifact service and session.
        gcs_uri: GCS URI to the PPTX file
            (e.g. ``gs://bucket-name/path/to/file.pptx``).

    Returns:
        A dictionary containing:
        - ``status``: "success" or "error"
        - ``data``: The populated SOW structure (on success)
        - ``metadata_uri``: GCS URI of the saved JSON file (on success)
        - ``pdf_artifact_filename``: Artifact filename of the PDF (on success)
        - ``pdf_artifact_version``: Version number of the PDF artifact (on success)
        - ``error``: Error message (on failure)
    """
    pptx_local: Path | None = None
    pdf_local: Path | None = None
    pdf_artifact_filename: str | None = None
    pdf_artifact_version: int | None = None

    try:
        # ── Step 1: Download PPTX from GCS ──────────────────────────────
        logger.info("Starting extraction for: %s", gcs_uri)
        pptx_local = download_blob_to_tempfile(gcs_uri, suffix=".pptx")

        # ── Step 2: Convert PPTX → PDF using Google Slides API ──────────
        use_pdf = True
        try:
            # Get credentials file path from environment or use default
            credentials_file = os.getenv(
                "GOOGLE_APPLICATION_CREDENTIALS",
                str(Path(__file__).parent.parent / "prj-sandbox-presales-portal-b9a1ce61abb0.json")
            )

            logger.info("Initializing Google Slides converter")
            converter = GoogleSlidesConverter(credentials_file)

            logger.info("Converting PPTX to PDF using Google Slides API")
            pdf_local = converter.convert_pptx_to_pdf(
                pptx_local,
                cleanup=True  # Cleanup temporary Google Drive files
            )
            logger.info("PDF conversion successful: %s", pdf_local)

        except (ConversionError, FileNotFoundError) as conv_err:
            logger.warning(
                "PDF conversion failed, falling back to text extraction: %s",
                conv_err,
            )
            use_pdf = False

        # ── Step 3: Prepare content for Gemini ───────────────────────────
        model_name = os.getenv("REASONING_MODEL", "gemini-3-pro-preview")
        client = genai.Client(
            vertexai=bool(os.getenv("GOOGLE_GENAI_USE_VERTEXAI")),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

        extraction_prompt = _build_extraction_prompt()

        if use_pdf and pdf_local is not None:
            # Save PDF as an artifact using ADK artifact service
            bucket_name, blob_path = parse_gcs_uri(gcs_uri)
            source_stem = Path(blob_path).stem
            pdf_artifact_filename = f"{source_stem}_converted.pdf"

            # Read PDF bytes and create artifact Part
            with open(pdf_local, "rb") as f:
                pdf_bytes = f.read()

            pdf_artifact = genai_types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf"
            )

            # Save using ADK artifact service
            logger.info("Saving PDF as artifact: %s", pdf_artifact_filename)
            pdf_artifact_version = await context.save_artifact(
                filename=pdf_artifact_filename,
                artifact=pdf_artifact
            )
            logger.info(
                "PDF artifact saved: %s (version %d)",
                pdf_artifact_filename,
                pdf_artifact_version
            )

            # Load the artifact back to get the GCS URI for Gemini
            # Note: ADK artifacts in GCS follow pattern: gs://bucket/artifacts/{app_name}/{user_id}/{session_id}/{filename}
            # We'll use the artifact service's GCS URI if available
            artifact_service_uri = os.getenv("ARTIFACT_SERVICE_URI", "")
            if artifact_service_uri.startswith("gs://"):
                # Construct the GCS path for the artifact
                app_name = context.app_name or "sow_generator"
                user_id = context.user_id or "default_user"
                session_id = context.session_id or "default_session"
                pdf_gcs_uri = f"{artifact_service_uri.rstrip('/')}/artifacts/{app_name}/{user_id}/{session_id}/{pdf_artifact_filename}"
            else:
                # Fallback: Load artifact and upload to temp GCS location
                logger.warning("ARTIFACT_SERVICE_URI not set or not a GCS URI, using fallback")
                pdf_gcs_uri = f"gs://{bucket_name}/_tmp_artifacts/{pdf_artifact_filename}"
                # Re-upload for Gemini (this is a workaround)
                from ..utils.gcs_utils import upload_file_to_gcs
                upload_file_to_gcs(pdf_local, pdf_gcs_uri)

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
                    temperature=0.1,  # Fully deterministic
                    top_p=1.0,
                    top_k=1,
                    max_output_tokens=8192,
                    seed=42,
                ),
            )

        # ── Step 4: Parse and validate extracted data ────────────────────
        raw_text = response.text or ""
        extracted_data = _parse_llm_json(raw_text)
        sow_output = _validate_extracted_output(extracted_data)

        # ── Step 5: Save result JSON to GCS ──────────────────────────────
        bucket_name, blob_path = parse_gcs_uri(gcs_uri)
        source_stem = Path(blob_path).stem
        metadata_blob = f"processed_metadata/{source_stem}_sow_extracted.json"
        metadata_uri = f"gs://{bucket_name}/{metadata_blob}"

        upload_json_to_gcs(sow_output, metadata_uri)
        logger.info("Extraction results saved to: %s", metadata_uri)

        # Prepare result with artifact information
        result = {
            "status": "success",
            "metadata_uri": metadata_uri,
        }

        # Include PDF artifact information if PDF conversion was used
        if pdf_artifact_filename:
            result["pdf_artifact_filename"] = pdf_artifact_filename
            result["pdf_artifact_version"] = pdf_artifact_version

        return result

    except Exception as exc:
        logger.error("Extraction failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}

    finally:
        # ── Step 6: Cleanup temporary local files ────────────────────────
        # Note: We keep the PDF artifact in GCS (in artifacts/pdfs/) for reference
        if pptx_local is not None and pptx_local.exists():
            pptx_local.unlink(missing_ok=True)
        if pdf_local is not None and pdf_local.exists():
            pdf_local.unlink(missing_ok=True)
            # Also remove the temp directory created for PDF
            try:
                pdf_local.parent.rmdir()
            except OSError:
                # Directory may not be empty or may not exist
                pass
