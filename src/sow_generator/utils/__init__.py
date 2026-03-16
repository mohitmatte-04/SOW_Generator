"""Utils module for sow_generator."""

import json
import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerEnv(BaseSettings):
    """Server environment configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    google_cloud_project: str = Field(..., alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field("us-central1", alias="GOOGLE_CLOUD_LOCATION")
    agent_name: str = Field("sow_generator", alias="AGENT_NAME")

    agent_engine_uri: str | None = Field(None, alias="AGENT_ENGINE")
    artifact_service_uri: str | None = Field(None, alias="ARTIFACT_SERVICE_URI")

    host: str = Field("127.0.0.1", alias="HOST")
    port: int = Field(8000, alias="PORT")

    allow_origins: str = Field('["*"]', alias="ALLOW_ORIGINS")
    serve_web_interface: bool = Field(True, alias="SERVE_WEB_INTERFACE")
    reload_agents: bool = Field(True, alias="RELOAD_AGENTS")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    @property
    def allow_origins_list(self) -> list[str]:
        return json.loads(self.allow_origins)


def initialize_environment(settings_class: type[BaseSettings]) -> BaseSettings:
    """Initializes and validates environment settings."""
    return settings_class()


def configure_otel_resource(agent_name: str, project_id: str) -> None:
    """Configures OpenTelemetry resource attributes."""
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = (
        f"service.name={agent_name},gcp.project_id={project_id}"
    )


def setup_opentelemetry(
    project_id: str, agent_name: str, log_level: str = "INFO"
) -> None:
    """Configures OpenTelemetry for tracing and logging to Google Cloud."""
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    logger.info("OpenTelemetry setup for %s in project %s", agent_name, project_id)
