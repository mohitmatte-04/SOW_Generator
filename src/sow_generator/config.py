"""Model and agent configuration."""

import os

from dotenv import load_dotenv

from dotenv import load_dotenv
from google.genai import types as genai_types

load_dotenv()

# Model names
FAST_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3-flash-preview")
REASONING_MODEL = os.getenv("REASONING_MODEL", "gemini-3.1-pro-preview")

# Production configuration: deterministic
PRODUCTION_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.1,
    top_p=0.9,
    top_k=40,
    # max_output_tokens=2048,
    seed=42,
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
    temperature=0.4,
    top_p=0.9,
    top_k=40,
    seed=42,
)
