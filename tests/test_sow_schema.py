"""Tests for sow_schema module."""

from sow_generator.sow_schema import SOW_JSON_SCHEMA, get_empty_sow_structure


class TestSOWJSONSchema:
    """Tests for the SOW JSON schema constant."""

    def test_schema_has_sow_structure_key(self) -> None:
        assert "sow_structure" in SOW_JSON_SCHEMA

    def test_schema_has_all_top_level_sections(self) -> None:
        structure = SOW_JSON_SCHEMA["sow_structure"]
        expected_keys = {
            "1.0_executive_summary",
            "2.0_scope",
            "3.0_success_criteria",
            "4.0_assumptions_and_customer_dependencies",
            "5.0_customer_roles_and_responsibilities",
            "7.0_project_governance",
            "8.0_project_closure",
            "9.0_primary_project_contacts",
            "10.0_fees_and_expenses",
            "11.0_signatures",
            "appendices",
        }
        assert expected_keys == set(structure.keys())

    def test_scalar_values_are_na(self) -> None:
        structure = SOW_JSON_SCHEMA["sow_structure"]
        assert structure["3.0_success_criteria"] == "NA"
        assert structure["11.0_signatures"] == "NA"

    def test_nested_values_are_na(self) -> None:
        executive = SOW_JSON_SCHEMA["sow_structure"]["1.0_executive_summary"]
        assert executive["1.1_opportunity"] == "NA"
        assert executive["1.2_solution_overview"] == "NA"

    def test_fees_section_has_all_subsections(self) -> None:
        fees = SOW_JSON_SCHEMA["sow_structure"]["10.0_fees_and_expenses"]
        expected = {
            "10.1_professional_services",
            "10.2_expenses",
            "10.3_fees_and_expense_summary",
            "10.4_tentative_project_timeline",
            "10.5_milestone_payment_schedule",
            "10.6_payment",
        }
        assert expected == set(fees.keys())


class TestGetEmptySOWStructure:
    """Tests for the get_empty_sow_structure helper."""

    def test_returns_deep_copy(self) -> None:
        copy1 = get_empty_sow_structure()
        copy2 = get_empty_sow_structure()
        assert copy1 == copy2
        assert copy1 is not copy2

    def test_mutation_does_not_affect_original(self) -> None:
        copy = get_empty_sow_structure()
        copy["sow_structure"]["3.0_success_criteria"] = "Modified"
        assert SOW_JSON_SCHEMA["sow_structure"]["3.0_success_criteria"] == "NA"

    def test_nested_mutation_does_not_affect_original(self) -> None:
        copy = get_empty_sow_structure()
        copy["sow_structure"]["1.0_executive_summary"]["1.1_opportunity"] = "Changed"
        assert (
            SOW_JSON_SCHEMA["sow_structure"]["1.0_executive_summary"]["1.1_opportunity"]
            == "NA"
        )
