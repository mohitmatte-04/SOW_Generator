"""SOW Generator Sequential Pipeline."""
import logging

from google.adk.agents import SequentialAgent
from google.adk.apps import App
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from google.adk.plugins.logging_plugin import LoggingPlugin
from .input_parser_agent import input_parser_agent
from .extractor_agent import extractor_agent
from .sow_generation_agent import sow_generation_agent

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

sow_pipeline = SequentialAgent(
    name="sow_pipeline",
    description=(
        "Orchestrates the extraction of proposal details "
        "and generation of the Statement of Work."
    ),
    sub_agents=[
        input_parser_agent,
        extractor_agent,
        sow_generation_agent,
    ],
)

# app = App(
#     name="sow-generator",
#     root_agent=sow_pipeline,
#     plugins=[
#         GlobalInstructionPlugin(return_global_instruction),
#         LoggingPlugin()
#     ],
#     events_compaction_config=None,
#     context_cache_config=None,
#     resumability_config=None,

# )
