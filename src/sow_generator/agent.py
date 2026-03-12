"""Main agent entry point for SOW Generator.

Root agent architecture
-----------------------
The root agent is ``sow_pipeline``, a ``SequentialAgent`` that orchestrates
two LLM sub-agents in order:

1. **extractor_agent** — Accepts a GCS URI to a PPTX/PPT proposal deck from
   the user, converts it, sends it to Gemini for multimodal analysis, and
   saves the extracted SOW JSON to GCS. Stores the result (including
   ``metadata_uri``) in session state under ``extractor_agent_context``.

2. **sow_generation_agent** — Automatically reads ``metadata_uri`` from the
   ``extractor_agent_context`` state (no additional user input needed),
   downloads the extracted JSON, maps the content to DOCX template
   placeholders, and generates the final SOW document in GCS.

Usage
-----
Send the agent a single message containing the GCS URI of the proposal deck:

    "Generate an SOW from gs://my-bucket/proposals/client_deck.pptx"

The pipeline runs automatically end-to-end and returns the GCS URI of the
generated SOW document.
"""

from google.adk.agents import Agent

from .sow_pipeline import sow_pipeline

# Export the root agent
root_agent: Agent = sow_pipeline

__all__ = ["root_agent"]
