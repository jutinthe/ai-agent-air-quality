from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.document import (
    DetectedSection,
    ParsedDocument,
    PDFMetadata,
    SectionType,
)
from app.services.extraction_context import build_extraction_context


def make_document() -> ParsedDocument:
    return ParsedDocument(
        paper_id=uuid4(),
        original_filename="paper.pdf",
        stored_filename="source.pdf",
        sha256="abc123",
        file_size_bytes=1000,
        metadata=PDFMetadata(
            title="Example Study",
            authors=["Example Author"],
            page_count=5,
        ),
        pages=[],
        sections=[
            DetectedSection(
                section_type=SectionType.METHODS,
                heading="Methods",
                normalized_heading="methods",
                start_page=2,
                end_page=3,
                text="We conducted a cohort study.",
                character_count=28,
                heading_confidence=0.9,
            ),
            DetectedSection(
                section_type=SectionType.RESULTS,
                heading="Results",
                normalized_heading="results",
                start_page=4,
                end_page=4,
                text="PM2.5 was associated with mortality.",
                character_count=36,
                heading_confidence=0.9,
            ),
            DetectedSection(
                section_type=SectionType.REFERENCES,
                heading="References",
                normalized_heading="references",
                start_page=5,
                end_page=5,
                text="A long reference list.",
                character_count=22,
                heading_confidence=0.9,
            ),
        ],
        full_text="Complete paper text",
        extracted_at=datetime.now(UTC),
    )


def test_context_prioritizes_scientific_sections() -> None:
    context = build_extraction_context(make_document())

    assert "METHODS" in context.text
    assert "RESULTS" in context.text
    assert "A long reference list" not in context.text
    assert "references" in context.sections_omitted


def test_context_respects_character_limit() -> None:
    context = build_extraction_context(
        make_document(),
        maximum_characters=50,
    )

    assert context.character_count <= 50
