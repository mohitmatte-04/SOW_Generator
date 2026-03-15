"""Model and agent configuration."""

import os

from dotenv import load_dotenv
from google.genai import types as genai_types

load_dotenv()

# Model names
FAST_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3-flash-preview")
REASONING_MODEL = os.getenv("REASONING_MODEL", "gemini-3.1-pro-preview")

# SOW Template Configuration
SOW_TEMPLATE_GCS_URI = os.getenv(
    "SOW_TEMPLATE_GCS_URI",
    "gs://sow-generator-testing-phase/templates/sow_template.docx"
)

# SOW Output Configuration
SOW_OUTPUT_DRIVE_FOLDER_ID = os.getenv(
    "SOW_OUTPUT_DRIVE_FOLDER_ID",
    None  # Must be configured in .env
)
SOW_OUTPUT_FOLDER_URL = os.getenv(
    "SOW_OUTPUT_FOLDER_URL",
    "https://drive.google.com/drive/folders/YOUR_FOLDER_ID_HERE"
)
SOW_OUTPUT_GCS_URI = os.getenv(
    "SOW_OUTPUT_GCS_URI",
    "gs://sow-generator-testing-phase/generated-sows"
)

# Production configuration: fully deterministic, no hallucination
PRODUCTION_CONFIG = genai_types.GenerateContentConfig(
    # temperature=0.0,  # Fully deterministic — critical for extraction fidelity
    # top_p=1.0,        # No nucleus sampling truncation at temp=0
    # top_k=1,          # Always pick the single most likely token
    # max_output_tokens=2048,
    seed=42,  # Seed not supported by all models
)

# Creative configuration
CREATIVE_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.8,
    top_p=0.95,
    top_k=50,
    # max_output_tokens=4096,
    seed=42,
)

# SOW generation configuration: warm enough for professional writing expansion
SOW_GENERATION_CONFIG = genai_types.GenerateContentConfig(
    # temperature=0.4,
    # top_p=0.9,
    # top_k=40,
    seed=42,
)
