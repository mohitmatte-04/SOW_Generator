"""SOW JSON Schema definition.

Defines the canonical Statement of Work template used for extraction
and generation. Each value is a DESCRIPTION of what content belongs there.
During extraction, descriptions get replaced with actual proposal content.
Sections not found in the source are set to "NA".
"""

import copy
from typing import Any

SOW_JSON_SCHEMA: dict[str, Any] = {
    "statement_of_work_template": {
        "introductory_provisions": (
            "Standard legal provisions about the SOW relationship to the "
            "Master Services Agreement, conflict resolution between "
            "documents, and project start date agreements."
        ),
        "sections": [
            {
                "section_number": 1,
                "title": "SOW Summary Table",
                "details": (
                    "Supplier and Client full legal names, points of "
                    "contact (name, telephone, email), SOW author, bid "
                    "architect, SOW term (start date, end date, duration), "
                    "and project price."
                ),
            },
            {
                "section_number": 2,
                "title": "Executive Summary",
                "details": (
                    "Business objective, goals, project overview, and "
                    "background context describing why the engagement "
                    "is needed."
                ),
            },
            {
                "section_number": 3,
                "title": "Scope of Work",
                "details": (
                    "Detailed list of activities, tasks, and work items "
                    "that are included in the engagement. Each activity "
                    "should be listed as a separate item."
                ),
            },
            {
                "section_number": 4,
                "title": "Out of Scope",
                "details": (
                    "Activities and work items that are explicitly NOT "
                    "included in this engagement."
                ),
            },
            {
                "section_number": 5,
                "title": "Customer Dependencies",
                "details": (
                    "Requirements and responsibilities that the customer "
                    "must fulfill for successful project delivery, such as "
                    "providing access, approvals, SMEs, sign-offs, and "
                    "internal coordination."
                ),
            },
            {
                "section_number": 6,
                "title": "Assumptions",
                "sub_sections": [
                    {
                        "category": "General Assumptions",
                        "details": (
                            "Non-technical assumptions about customer "
                            "responsibilities, timely access, data reliance, "
                            "RAID management, steering committee response "
                            "times, vendor support levels, and pricing "
                            "scope constraints."
                        ),
                    },
                    {
                        "category": "Technical Assumptions",
                        "details": (
                            "Technical assumptions about software upgrades, "
                            "existing application issues, test scripts, and "
                            "technical environment requirements."
                        ),
                    },
                ],
            },
            {
                "section_number": 7,
                "title": "Deliverables",
                "details": (
                    "Table or list of deliverables with their success "
                    "criteria and format (slides, docs, spreadsheets, "
                    "code, etc.)."
                ),
            },
            {
                "section_number": 8,
                "title": "Change Control Management",
                "details": (
                    "Procedures for handling scope changes including change "
                    "order requirements, review timelines, and reasons for "
                    "initiation such as scope modifications or dependency "
                    "delays."
                ),
            },
            {
                "section_number": 9,
                "title": "Commercials and Timeline",
                "details": (
                    "Pricing model (fixed bid or T&M), work location "
                    "(onshore/offshore), project offering with duration "
                    "and price, invoicing schedule, exclusions (3rd party "
                    "licenses, taxes), and travel expense policies."
                ),
            },
            {
                "section_number": 10,
                "title": "SOW Sign-off",
                "details": (
                    "Termination rights, notice requirements, payment terms "
                    "for fees earned to date, and signature blocks for "
                    "both parties."
                ),
            },
            {
                "section_number": 11,
                "title": "Appendices",
                "sub_sections": [
                    {
                        "name": "Appendix A: In-scope Volumetrics",
                        "details": (
                            "Quantifiable measures and metrics for the "
                            "project scope."
                        ),
                    },
                    {
                        "name": "Appendix B: RACI",
                        "details": (
                            "Responsibility matrix identifying roles for "
                            "Client, Partner, and Provider."
                        ),
                    },
                    {
                        "name": "Appendix C: Accelerators Prerequisite",
                        "details": (
                            "Prerequisites for any accelerators or tools "
                            "to be used in the engagement."
                        ),
                    },
                ],
            },
        ],
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
