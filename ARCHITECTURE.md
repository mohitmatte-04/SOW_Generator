# SOW Generator Application - Architecture Design

## 1. System Overview

### Problem Statement
The goal is to automate the creation of highly accurate (90%+) Statements of Work (SOW) by extracting high-level business problem details from proposal documents (Google Slides or PPTX) and expanding them into detailed SOW sections. The final output must be a properly formatted Google Doc that merges fixed template text with the AI-generated dynamic content.

### High-Level Architecture
```text
User Input (PPTX path or Google Slides URL)
  ↓
[Sequential Pipeline]
  ├─ 1. proposal_extraction_agent (Reads slides, extracts business context & solution)
  └─ 2. sow_generation_agent (Expands context into SOW sections, populates Google Doc)
  ↓
Final Output (Google Doc URL)
```

### Key Design Decisions
1. **Multi-agent Sequential Pipeline:** A sequential architecture is chosen because the workflow has strictly linear dependencies (Extraction -> Generation -> Document Assembly).
2. **Clear Separation of Concerns:** 
   - `proposal_extraction_agent` specializes in parsing unstructured presentation data and distilling it into structured requirements.
   - `sow_generation_agent` specializes in professional business/legal writing and API interactions to generate the final document.
3. **Template-based Document Assembly:** To guarantee 100% adherence to the fixed formatting and style, the system uses a Google Docs template. The agent generates the dynamic content, and a deterministic tool handles duplicating the template and performing text-replacement on designated placeholders.

## 2. Agent Specifications

### Agent: proposal_extraction_agent

**Single Core Responsibility:**
Analyzes proposal presentations (Google Slides or local PPTX) to extract the core business problem, proposed solution, and project constraints into a structured format.

**Naming:**
- Agent name: `proposal_extraction_agent`
- Output key: `proposal_extraction_agent_context`

**Model Selection:**
- Model: `gemini-2.5-pro` (or latest reasoning model available in ADK)
- Rationale: High reasoning capability is required to synthesize and distill unstructured presentation slides into coherent business requirements.
- Temperature: `0.1` (We want deterministic, highly accurate factual extraction).

**Input State Keys:**
- `presentation_source`: String - URL to Google Slides or local path to `.pptx` - Set by: User/Orchestrator

**Output State Key:**
- `proposal_extraction_agent_context`: Dict - Structured extraction containing `business_problem`, `proposed_solution`, `in_scope`, `out_of_scope`.

**Tools Required:**
- `read_presentation_content()`: Parses text and structure from a Google Slides URL or local `.pptx` file.

**Dependencies:**
- Depends on: None (First in sequence)
- Depended on by: `sow_generation_agent`

**Error Handling:**
- Retry strategy: Retry tool calls on network failure.
- Fallback behavior: If presentation is unreadable, gracefully halt and ask the user for a valid file/link.

### Agent: sow_generation_agent

**Single Core Responsibility:**
Expands the extracted proposal context into detailed, professional SOW sections and generates the final Google Doc using the predefined template.

**Naming:**
- Agent name: `sow_generation_agent`
- Output key: `sow_generation_agent_result`

**Model Selection:**
- Model: `gemini-2.5-pro` (or equivalent Pro model)
- Rationale: Needs strong professional writing capabilities to expand brief points into comprehensive SOW language.
- Temperature: `0.4` (Slightly higher to allow for natural language expansion while maintaining professional tone).

**Input State Keys:**
- `proposal_extraction_agent_context`: Dict - Extracted context - Set by: `proposal_extraction_agent`

**Output State Key:**
- `sow_generation_agent_result`: Dict - Contains the `final_sow_url` and a `status` message.

**Tools Required:**
- `generate_sow_document()`: Duplicates the SOW template from Google Drive/GCS, performs text replacement for specific placeholders (e.g., `{{SCOPE_OF_WORK}}`, `{{OUT_OF_SCOPE}}`), and returns the new Google Doc URL.

**Dependencies:**
- Depends on: `proposal_extraction_agent`
- Depended on by: None (Final step)

## 3. Orchestration Design

### Pattern: Sequential Pipeline
The process is a straight line: Information is extracted, then expanded, then inserted into the document.

### Data Flow
```text
State: { presentation_source: "..." }
  ↓
proposal_extraction_agent (Uses read_presentation_content)
  ↓
State: { ..., proposal_extraction_agent_context: { business_problem: "...", ... } }
  ↓
sow_generation_agent (Generates expanded text, uses generate_sow_document)
  ↓
State: { ..., sow_generation_agent_result: { final_sow_url: "https://docs.google.com/..." } }
```

## 4. Tool Inventory

| Tool Name | Purpose | Agent(s) Using | External API/Service | Error Handling |
|-----------|---------|----------------|---------------------|----------------|
| `read_presentation_content` | Extracts text from Google Slides or PPTX | `proposal_extraction_agent` | Google Slides API, `python-pptx` | Catch OAuth errors, file not found. Return structured error. |
| `generate_sow_document` | Duplicates template and replaces placeholder tags | `sow_generation_agent` | Google Drive API, Google Docs API | Retry on rate limits (429). Validate template exists. |

## 5. State Contracts

| State Key | Type | Set By | Read By | Description |
|-----------|------|--------|---------|-------------|
| `presentation_source` | String | User | `proposal_extraction_agent` | Input path or URL to the presentation |
| `proposal_extraction_agent_context` | Dict | `proposal_extraction_agent` | `sow_generation_agent` | Structured data containing the core proposal details |
| `sow_generation_agent_result` | Dict | `sow_generation_agent` | User | Contains the generated document URL and success status |

## 6. Deployment Architecture

### Target Environment
- **Platform:** Google Cloud Run (Containerized FastAPI service)
- **Authentication:** Google Cloud Service Account with domain-wide delegation or specific OAuth tokens for accessing Google Drive/Docs/Slides APIs.

### Infrastructure/Storage
- **Template Storage:** Google Cloud Storage (GCS) or a designated Google Drive folder accessible by the Service Account.
- **Output Storage:** Final SOW Google Docs created in a designated Drive folder.

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Google API Rate Limits | Medium | High | Implement exponential backoff in tool logic. |
| Formatting lost during text replacement | Low | High | Use precise placeholder replacement (e.g., `{{TAG}}`) in the Docs API rather than replacing entire sections, preserving the template's paragraph styling. |
| Poor extraction from image-heavy slides | Medium | Medium | Prompt `proposal_extraction_agent` to warn if insufficient text is found. |
