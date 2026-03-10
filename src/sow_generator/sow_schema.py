"""SOW JSON Schema definition.

Defines the canonical Statement of Work structure used for extraction
and generation. All sections default to "NA" when not found in source material.
"""

import copy
from typing import Any

SOW_JSON_SCHEMA: dict[str, Any] = {
    "sow_structure": {
        "1.0_executive_summary": {
            "1.1_opportunity": "NA",
            "1.2_solution_overview": "NA",
        },
        "2.0_scope": {
            "2.1_scope_and_deliverables": "NA",
            "2.2_out_of_scope_and_limitations": "NA",
        },
        "3.0_success_criteria": "NA",
        "4.0_assumptions_and_customer_dependencies": {
            "4.1_project_assumptions": "NA",
            "4.2_technical_assumptions": "NA",
        },
        "5.0_customer_roles_and_responsibilities": {
            "5.1_customer_project_roles": "NA",
            "5.2_customer_responsibilities": "NA",
        },
        "7.0_project_governance": {
            "7.1_location": "NA",
            "7.2_risk_action_issue_and_decision_management": "NA",
            "7.3_change_control_management": "NA",
        },
        "8.0_project_closure": {
            "8.1_knowledge_transfer": "NA",
        },
        "9.0_primary_project_contacts": {
            "9.1_onix_escalation_contacts": "NA",
            "9.2_primary_customer_contacts": "NA",
        },
        "10.0_fees_and_expenses": {
            "10.1_professional_services": "NA",
            "10.2_expenses": "NA",
            "10.3_fees_and_expense_summary": "NA",
            "10.4_tentative_project_timeline": "NA",
            "10.5_milestone_payment_schedule": "NA",
            "10.6_payment": "NA",
        },
        "11.0_signatures": "NA",
        "appendices": {
            "appendix_a_prerequisites": "NA",
            "appendix_b_proposed_engagement_model": "NA",
            "appendix_c_high_level_raci": "NA",
            "appendix_d_gcp_reference_architecture": "NA",
        },
    }
}


def get_empty_sow_structure() -> dict[str, Any]:
    """Return a deep copy of the SOW schema with all values set to 'NA'.

    Returns:
        A fresh dictionary matching the SOW JSON schema, safe to mutate.
    """
    return copy.deepcopy(SOW_JSON_SCHEMA)
