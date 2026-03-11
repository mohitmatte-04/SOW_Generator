"""Tests for sow_schema module."""

from sow_generator.sow_schema import SOW_JSON_SCHEMA, get_empty_sow_structure


class TestSOWJSONSchema:
    """Tests for the SOW JSON schema constant."""

    def test_schema_has_template_key(self) -> None:
        assert "statement_of_work_template" in SOW_JSON_SCHEMA

    def test_template_has_introductory_provisions(self) -> None:
        template = SOW_JSON_SCHEMA["statement_of_work_template"]
        assert "introductory_provisions" in template
        assert isinstance(template["introductory_provisions"], str)

    def test_template_has_sections_list(self) -> None:
        template = SOW_JSON_SCHEMA["statement_of_work_template"]
        assert "sections" in template
        assert isinstance(template["sections"], list)

    def test_sections_have_correct_count(self) -> None:
        sections = SOW_JSON_SCHEMA["statement_of_work_template"]["sections"]
        assert len(sections) == 11

    def test_sections_have_sequential_numbers(self) -> None:
        sections = SOW_JSON_SCHEMA["statement_of_work_template"]["sections"]
        for i, section in enumerate(sections, start=1):
            assert section["section_number"] == i

    def test_all_sections_have_title(self) -> None:
        sections = SOW_JSON_SCHEMA["statement_of_work_template"]["sections"]
        for section in sections:
            assert "title" in section
            assert isinstance(section["title"], str)

    def test_sections_with_sub_sections(self) -> None:
        sections = SOW_JSON_SCHEMA["statement_of_work_template"]["sections"]
        # Section 6 (Assumptions) and 11 (Appendices) have sub_sections
        section_6 = sections[5]  # index 5 = section_number 6
        assert "sub_sections" in section_6
        assert len(section_6["sub_sections"]) == 2

        section_11 = sections[10]  # index 10 = section_number 11
        assert "sub_sections" in section_11
        assert len(section_11["sub_sections"]) == 3

    def test_expected_section_titles(self) -> None:
        sections = SOW_JSON_SCHEMA["statement_of_work_template"]["sections"]
        titles = [s["title"] for s in sections]
        assert "SOW Summary Table" in titles
        assert "Executive Summary" in titles
        assert "Scope of Work" in titles
        assert "Out of Scope" in titles
        assert "Deliverables" in titles
        assert "Commercials and Timeline" in titles
        assert "Appendices" in titles


class TestGetEmptySOWStructure:
    """Tests for the get_empty_sow_structure helper."""

    def test_returns_deep_copy(self) -> None:
        copy1 = get_empty_sow_structure()
        copy2 = get_empty_sow_structure()
        assert copy1 == copy2
        assert copy1 is not copy2

    def test_mutation_does_not_affect_original(self) -> None:
        copy = get_empty_sow_structure()
        copy["statement_of_work_template"]["introductory_provisions"] = "Modified"
        assert isinstance(
            SOW_JSON_SCHEMA["statement_of_work_template"]["introductory_provisions"],
            str,
        )
        assert (
            SOW_JSON_SCHEMA["statement_of_work_template"]["introductory_provisions"]
            != "Modified"
        )

    def test_nested_list_mutation_does_not_affect_original(self) -> None:
        copy = get_empty_sow_structure()
        copy["statement_of_work_template"]["sections"][0]["title"] = "Changed"
        assert (
            SOW_JSON_SCHEMA["statement_of_work_template"]["sections"][0]["title"]
            == "SOW Summary Table"
        )
