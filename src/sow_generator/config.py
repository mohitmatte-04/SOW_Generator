"""Model and agent configuration."""

import os
from google.genai import types as genai_types
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

# Model names
FAST_MODEL = os.getenv("FAST_MODEL", "gemini-3-flash-preview")
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

# Validation configuration
VALIDATION_QUALITY_THRESHOLD = int(
    os.getenv("VALIDATION_QUALITY_THRESHOLD", "75")
)

VALIDATION_WEIGHTS: dict[str, float] = {
    "content_quality": 0.30,
    "grammar": 0.20,
    "sentence_structure": 0.15,
    "clarity": 0.20,
    "coherence": 0.15,
}

# Validation-focused config: analytical, deterministic
VALIDATION_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.1,
    top_p=0.9,
    top_k=40,
    seed=42,
)