import re
from typing import List, Dict


def split_into_sections(text: str, section_names: List[str]) -> Dict[str, str]:
    """
    Split text into sections based on provided section names.
    Returns a dictionary: {section_name: content}
    """

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    # Build regex pattern for section names
    # Example: (Opportunity|Solution Overview|Activities)
    pattern = r'(?=(' + '|'.join(map(re.escape, section_names)) + r'))'

    matches = list(re.finditer(pattern, text))

    sections = {}

    for i, match in enumerate(matches):
        section_name = match.group(1)
        start = match.start()

        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        # Remove section name from content
        content = re.sub(r'^' + re.escape(section_name), '', content).strip()

        sections[section_name] = content

    return sections


def format_section_content(content: str) -> str:
    """
    Apply formatting rules inside each section.
    """

    # Add line breaks for bullet points
    content = re.sub(r'\s(\* )', r'\n\1', content)
    content = re.sub(r'\s(- )', r'\n\1', content)

    # Add line breaks after sentences
    content = re.sub(r'(?<=[.])\s+', '\n', content)

    # Clean extra newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


def build_markdown(sections: Dict[str, str]) -> str:
    """
    Convert sections dictionary into clean markdown
    """

    md_output = []

    for section, content in sections.items():
        md_output.append(f"# {section}\n")

        formatted_content = format_section_content(content)
        md_output.append(formatted_content + "\n")

    return "\n".join(md_output)


def convert_to_markdown(text: str, section_names: List[str]) -> str:
    """
    Full pipeline: split → format → rebuild markdown
    """
    sections = split_into_sections(text, section_names)
    markdown = build_markdown(sections)
    return markdown


# ------------------ USAGE ------------------

if __name__ == "__main__":

    section_names = [
        "Opportunity",
        "Solution Overview",
        "Activities",
        "Deliverables",
        "Out of Scope",
        "Limitations",
        "Success Criteria",
        "Technical Assumptions",
        "Payment Schedule",
        "Appendix Details"
    ]

    with open("D:\\AI_ML\\SOW-Generator\\repo\\SOW_Generator\\src\\sow_generator\\enriched-content.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    formatted_md = convert_to_markdown(raw_text, section_names)

    with open("structured_output.md", "w", encoding="utf-8") as f:
        f.write(formatted_md)

    print("Structured markdown generated: structured_output.md")