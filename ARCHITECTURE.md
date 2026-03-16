# SOW Generator Application - Architecture Design

## 1. System Overview

### Problem Statement
The goal is to automate the creation of highly accurate (90%+) Statements of Work (SOW) by extracting high-level business problem details from proposal documents (PPTX) and expanding them into detailed SOW sections. The final output is a properly formatted DOCX document that merges fixed template text with dynamic, validated content.

### High-Level Architecture (4-Stage Pipeline)
```text
User Input (GCS PPTX URI)
  ↓
[Sequential Pipeline]
  ├─ 1. proposal_extraction_agent (Reads slides, extracts business context & solution)
  ├─ 2. sow_generation_agent (Expands context into professional SOW sections)
  ├─ 3. content_validation_agent (Evaluates content quality against 5 dimensions)
  └─ 4. annotate_document_agent (Conditional: Annotates low-quality sections in DOCX)
  ↓
Final Output (Annotated GCS DOCX URI)
```

## 2. Agent Specifications

### Agent: proposal_extraction_agent
- **Responsibility**: Analyzes PPTX content on GCS to extract core business details.
- **Tools**: `read_presentation_content()`
- **Output**: `proposal_extraction_agent_context`

### Agent: sow_generation_agent
- **Responsibility**: Professional writing and DOCX assembly from a GCS template.
- **Tools**: `generate_sow_document()`
- **Output**: `sow_generation_agent_result`

### Agent: content_validation_agent
- **Responsibility**: Quality gatekeeper. Scores sections based on accuracy, grammar, and clarity.
- **Tools**: `validate_content()`
- **Output**: `content_validation_result` (Scores & Feedback)

### Agent: annotate_document_agent
- **Responsibility**: Post-processing. Injects "Needs Manual Review" notices for sections under threshold (75).
- **Tools**: `annotate_sow_document()`
- **Output**: `annotate_document_result`

## 3. Tool Inventory

| Tool Name | Purpose | Service |
|-----------|---------|---------|
| `read_presentation_content` | Extracts structured text from local/GCS PPTX | python-pptx |
| `generate_sow_document` | Replace placeholders in DOCX while maintaining style | python-docx |
| `validate_content` | Computes weighted quality scores | Python |
| `annotate_sow_document` | Directly manipulates DOCX XML for inline notices | python-docx |

## 4. Deployment Architecture
- **Platform**: Google Cloud Run
- **Storage**: Google Cloud Storage for templates and generated outputs.
- **Persistence**: ADK Session Service for state management and memory.
