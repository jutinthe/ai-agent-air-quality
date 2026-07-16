from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.core.config import Settings
from app.schemas.document import ParsedDocument
from app.services.file_storage import StoredPDF
from app.services.pdf_parser import parse_pdf
from app.services.section_detector import detect_sections


def process_pdf(
    paper_id: UUID,
    stored_pdf: StoredPDF,
    settings: Settings,
) -> ParsedDocument:
    metadata, pages, full_text = parse_pdf(stored_pdf.path)
    sections = detect_sections(pages)

    parsed_document = ParsedDocument(
        paper_id=paper_id,
        original_filename=stored_pdf.original_filename,
        stored_filename=stored_pdf.stored_filename,
        sha256=stored_pdf.sha256,
        file_size_bytes=stored_pdf.size_bytes,
        metadata=metadata,
        pages=pages,
        sections=sections,
        full_text=full_text,
        extracted_at=datetime.now(UTC),
    )

    save_processed_document(
        document=parsed_document,
        processed_directory=settings.processed_directory,
    )

    return parsed_document


def save_processed_document(
    document: ParsedDocument,
    processed_directory: Path,
) -> Path:
    paper_directory = processed_directory / str(document.paper_id)
    paper_directory.mkdir(parents=True, exist_ok=True)

    output_path = paper_directory / "parsed_document.json"

    output_path.write_text(
        json.dumps(
            document.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def load_processed_document(
    paper_id: UUID,
    processed_directory: Path,
) -> ParsedDocument | None:
    input_path = (
        processed_directory
        / str(paper_id)
        / "parsed_document.json"
    )

    if not input_path.exists():
        return None

    return ParsedDocument.model_validate_json(
        input_path.read_text(encoding="utf-8")
    )
