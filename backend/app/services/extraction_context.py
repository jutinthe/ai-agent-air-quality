"""Build a focused context from parsed paper sections."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.document import ParsedDocument, SectionType


SECTION_PRIORITY: dict[SectionType, int] = {
    SectionType.ABSTRACT: 1,
    SectionType.METHODS: 2,
    SectionType.RESULTS: 3,
    SectionType.DISCUSSION: 4,
    SectionType.LIMITATIONS: 5,
    SectionType.CONCLUSION: 6,
    SectionType.INTRODUCTION: 7,
    SectionType.BACKGROUND: 8,
    SectionType.TITLE: 9,
    SectionType.SUPPLEMENTARY: 10,
    SectionType.OTHER: 11,
    SectionType.KEYWORDS: 12,
    SectionType.LITERATURE_REVIEW: 13,
    SectionType.ACKNOWLEDGMENTS: 14,
    SectionType.REFERENCES: 99,
}


@dataclass(frozen=True)
class ExtractionContext:
    text: str
    sections_used: list[str]
    sections_omitted: list[str]
    character_count: int


def _format_section(
    section_type: str,
    heading: str,
    start_page: int,
    end_page: int,
    text: str,
) -> str:
    page_label = (
        f"PAGE {start_page}"
        if start_page == end_page
        else f"PAGES {start_page}-{end_page}"
    )

    return (
        f"\n\n=== {section_type.upper()}: {heading} "
        f"[{page_label}] ===\n{text.strip()}"
    )


def build_extraction_context(
    document: ParsedDocument,
    maximum_characters: int = 120_000,
) -> ExtractionContext:
    selected_parts: list[str] = []
    sections_used: list[str] = []
    sections_omitted: list[str] = []
    current_length = 0

    candidate_sections = sorted(
        document.sections,
        key=lambda section: (
            SECTION_PRIORITY.get(section.section_type, 50),
            section.start_page,
        ),
    )

    for section in candidate_sections:
        section_name = section.section_type.value

        if section.section_type == SectionType.REFERENCES:
            sections_omitted.append(section_name)
            continue

        if not section.text.strip():
            sections_omitted.append(section_name)
            continue

        formatted = _format_section(
            section_type=section_name,
            heading=section.heading,
            start_page=section.start_page,
            end_page=section.end_page,
            text=section.text,
        )

        remaining = maximum_characters - current_length

        if remaining <= 0:
            sections_omitted.append(section_name)
            continue

        if len(formatted) > remaining:
            if remaining >= 2_000:
                formatted = formatted[:remaining]
                formatted += "\n[SECTION TRUNCATED]"
                selected_parts.append(formatted)
                sections_used.append(section_name)
                current_length += len(formatted)
            else:
                sections_omitted.append(section_name)

            continue

        selected_parts.append(formatted)
        sections_used.append(section_name)
        current_length += len(formatted)

    if not selected_parts:
        fallback = document.full_text[:maximum_characters]

        return ExtractionContext(
            text=fallback,
            sections_used=["full_text_fallback"],
            sections_omitted=[],
            character_count=len(fallback),
        )

    context_text = "".join(selected_parts).strip()

    return ExtractionContext(
        text=context_text,
        sections_used=sections_used,
        sections_omitted=sections_omitted,
        character_count=len(context_text),
    )
