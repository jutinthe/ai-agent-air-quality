from app.schemas.document import ParsedPage, SectionType
from app.services.section_detector import detect_sections


def create_page(page_number: int, text: str) -> ParsedPage:
    return ParsedPage(
        page_number=page_number,
        width=612,
        height=792,
        text=text,
        character_count=len(text),
        blocks=[],
    )


def test_detects_standard_research_sections() -> None:
    pages = [
        create_page(
            1,
            """Air Pollution and Health
Example Author

ABSTRACT
This study evaluated long-term PM2.5 exposure and mortality.

1. Introduction
Air pollution is an important public health concern.
""",
        ),
        create_page(
            2,
            """2. Methods
We created a retrospective cohort and estimated exposure.

3. Results
Higher exposure was associated with greater mortality.
""",
        ),
        create_page(
            3,
            """4. Discussion
The findings were consistent with previous studies.

5. Conclusions
Lower air pollution may improve population health.

References
Example citation.
""",
        ),
    ]

    sections = detect_sections(pages)
    section_types = [section.section_type for section in sections]

    assert SectionType.ABSTRACT in section_types
    assert SectionType.INTRODUCTION in section_types
    assert SectionType.METHODS in section_types
    assert SectionType.RESULTS in section_types
    assert SectionType.DISCUSSION in section_types
    assert SectionType.CONCLUSION in section_types
    assert SectionType.REFERENCES in section_types


def test_returns_full_document_when_no_headings_exist() -> None:
    pages = [
        create_page(
            1,
            "This document contains continuous text without section headings.",
        )
    ]

    sections = detect_sections(pages)

    assert len(sections) == 1
    assert sections[0].section_type == SectionType.OTHER
