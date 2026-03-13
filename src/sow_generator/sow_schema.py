"""SOW JSON Schema definition.

Defines the canonical Statement of Work template used for extraction
and generation. Each value is a DESCRIPTION of what content belongs there.
During extraction, descriptions get replaced with actual proposal content.
Sections not found in the source are set to "NA".
"""

import copy
from typing import Any

SOW_JSON_SCHEMA: dict[str, Any] = {
  "project_metadata": {
    "title": "DESCRIPTION: The specific project or engagement name (e.g., 'Teradata to GCP Migration')",
    "customer_name": "DESCRIPTION: Full legal name of the client organization",
    "customer_short_name": "DESCRIPTION: Abbreviated customer name or acronym",
    "provision_date": "DESCRIPTION: Date the SOW was generated (format: YYYY-MM-DD)",
    "msa_date": "DESCRIPTION: Effective date of the Master Services Agreement"
  },
  "sow_content": {
    "opportunity": "DESCRIPTION: Business problem, current situation, and project justification",
    "solution_overview": "DESCRIPTION: High-level technical solution and approach summary",
    "activities": "DESCRIPTION: Detailed list of tasks and work steps Onix will perform or simply scope of work for the project",
    "deliverables": "DESCRIPTION: Tangible outputs (reports, code, diagrams, etc.)",
    "out_of_scope": "DESCRIPTION: Tasks explicitly NOT included to prevent scope creep",
    "limitations": "DESCRIPTION: Constraints or restrictions affecting service delivery",
    "success_criteria": "DESCRIPTION: Benchmarks for project success",
    "assumptions": {
      "project_assumptions": "DESCRIPTION: Non-technical assumptions about customer responsibilities, timelines, access",
      "technical_assumptions": "DESCRIPTION: Technical assumptions about software, environment, test scripts"
    },
    "customer_roles_responsibilities": {
      "project_roles": "DESCRIPTION: Customer team members and their project roles",
      "responsibilities": "DESCRIPTION: Customer obligations for successful delivery"
    },
    "project_governance": {
      "location": "DESCRIPTION: Work location (onshore/offshore/hybrid)",
      "raid_management": "DESCRIPTION: Risk, Action, Issue, Decision tracking process",
      "change_control": "DESCRIPTION: Procedures for handling scope changes"
    },
    "project_closure": {
      "knowledge_transfer": "DESCRIPTION: Knowledge transfer plan and documentation handover"
    },
    "contacts": {
      "onix_escalation": "DESCRIPTION: Onix escalation contacts (name, role, email, phone)",
      "customer_primary": "DESCRIPTION: Primary customer contacts (name, role, email, phone)"
    },
    "fees_expenses": {
      "professional_services": "DESCRIPTION: Professional services pricing and breakdown",
      "expenses": "DESCRIPTION: Expense policies and billable items",
      "summary": "DESCRIPTION: Total fees and expense summary",
      "timeline": "DESCRIPTION: Tentative project timeline and phases",
      "payment_schedule": "DESCRIPTION: Milestone-based payment schedule",
      "payment_terms": "DESCRIPTION: Payment terms and conditions"
    },
    "appendices": {
      "prerequisites": "DESCRIPTION: Prerequisites for engagement (Appendix A)",
      "engagement_model": "DESCRIPTION: Proposed engagement model details (Appendix B)",
      "raci": "DESCRIPTION: High-level RACI matrix (Appendix C)",
      "architecture": "DESCRIPTION: GCP reference architecture details (Appendix D)"
    }
  }
}


def get_empty_sow_structure() -> dict[str, Any]:
    """Return a deep copy of the SOW template.

    Returns:
        A fresh dictionary matching the SOW template, safe to mutate.
        During extraction, description values will be replaced with
        actual content from the proposal document.
    """
    return copy.deepcopy(SOW_JSON_SCHEMA)
