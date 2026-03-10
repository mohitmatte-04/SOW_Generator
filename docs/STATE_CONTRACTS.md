# State Contracts for SOW Generator

This document defines the keys and structure of the state shared between agents.

| State Key | Type | Set By | Read By | Description |
|-----------|------|--------|---------|-------------|
| `presentation_source` | String | User | `proposal_extraction_agent` | URL to Google Slides or local path to PPTX. |
| `proposal_extraction_agent_context` | Dict | `proposal_extraction_agent` | `sow_generation_agent` | Structured data containing extraction results. |
| `sow_generation_agent_result` | Dict | `sow_generation_agent` | User | Contains the generated document URL and status. |

## Detailed Schemas

### `proposal_extraction_agent_context`

```json
{
  "status": "success",
  "data": {
    "business_problem": "...",
    "proposed_solution": "...",
    "in_scope": ["...", "..."],
    "out_of_scope": ["...", "..."]
  }
}
```

### `sow_generation_agent_result`

```json
{
  "status": "success",
  "data": {
    "final_sow_url": "https://docs.google.com/document/d/...",
    "document_id": "..."
  }
}
```
