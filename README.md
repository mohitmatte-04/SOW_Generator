# Statement of Work (SOW) Generator

An AI-powered multi-agent application built with Google ADK to automate the creation of professional Statements of Work from proposal presentations.

## Features

- **Automated Extraction**: Extracts core business context, proposed solution, and project constraints from Google Slides and PPTX files.
- **AI-Powered Expansion**: Expands high-level points into detailed, professional SOW language.
- **Google Docs Integration**: Merges AI-generated content into a fixed Google Docs template, maintaining professional styling.
- **Multi-Agent Orchestration**: Uses a sequential pipeline of specialized agents for extraction and generation.

## Prerequisites

- Python 3.12+
- Google Cloud Project with the following APIs enabled:
  - Google Slides API
  - Google Drive API
  - Google Docs API
  - Vertex AI API (if using Vertex AI)
- A Google Cloud Service Account or OAuth credentials with appropriate scopes.

## Setup

1.  **Clone the repository and install dependencies**:
    ```bash
    uv install
    ```

2.  **Configure environment variables**:
    Copy `.env.example` to `.env` and fill in the required values:
    ```bash
    cp .env.example .env
    ```

3.  **Authentication**:
    Ensure you have authenticated with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```

## Usage

### Local Development

Run the FastAPI server locally:
```bash
uv run python -m sow_generator.server
```

Open the ADK web interface at `http://localhost:8080/web` (if enabled).

### Agents

- `proposal_extraction_agent`: Analyzes presentations and extracts structured context.
- `sow_generation_agent`: Expands context and generates the final document.
- `sow_pipeline`: The sequential orchestrator.

## Document Template

The generator expects a `.docx` template stored on GCS (defined by `SOW_TEMPLATE_GCS_URI`) containing the following placeholders:

- `{{BUSINESS_PROBLEM}}`
- `{{PROPOSED_SOLUTION}}`
- `{{IN_SCOPE}}`
- `{{OUT_OF_SCOPE}}`

## Deployment

This application is designed for Google Cloud Run. Build and deploy the container using:
```bash
gcloud run deploy sow-generator --source .
```
