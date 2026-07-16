from __future__ import annotations

from pathlib import Path

import pymupdf

from app.core.exceptions import InvalidPDFError, PDFTextExtractionError
from app.schemas.document import PDFMetadata, ParsedPage, TextBlock
from app.services.header_extractor import extract_header_information


MINIMUM_DOCUMENT_CHARACTERS = 100


def _clean_metadata_value(value: object) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip()
    return cleaned or None


def _normalize_text(text: str) -> str:
    lines = [
        line.rstrip()
        for line in text.replace("\x00", "").splitlines()
    ]

    normalized_lines: list[str] = []
    previous_blank = False

    for line in lines:
        is_blank = not line.strip()

        if is_blank and previous_blank:
            continue

        normalized_lines.append(line)
        previous_blank = is_blank

    return "\n".join(normalized_lines).strip()


def _extract_blocks(
    page: pymupdf.Page,
    page_number: int,
) -> list[TextBlock]:
    raw_blocks = page.get_text("blocks", sort=True)
    blocks: list[TextBlock] = []

    for block_number, raw_block in enumerate(raw_blocks):
        x0, y0, x1, y1, text, *_ = raw_block
        cleaned_text = _normalize_text(str(text))

        if not cleaned_text:
            continue

        blocks.append(
            TextBlock(
                page_number=page_number,
                block_number=block_number,
                x0=float(x0),
                y0=float(y0),
                x1=float(x1),
                y1=float(y1),
                text=cleaned_text,
                character_count=len(cleaned_text),
            )
        )

    return blocks


def parse_pdf(
    pdf_path: Path,
) -> tuple[PDFMetadata, list[ParsedPage], str]:
    try:
        document = pymupdf.open(pdf_path)
    except Exception as exc:
        raise InvalidPDFError(
            f"PyMuPDF could not open the uploaded file: {exc}"
        ) from exc

    try:
        if not document.is_pdf:
            raise InvalidPDFError("The uploaded document is not a PDF.")

        if document.page_count < 1:
            raise InvalidPDFError(
                "The PDF does not contain any pages."
            )

        raw_metadata = document.metadata or {}

        header = extract_header_information(
            document=document,
            raw_metadata=raw_metadata,
        )

        metadata_author = _clean_metadata_value(
            raw_metadata.get("author")
        )

        metadata = PDFMetadata(
            title=header.title,
            author=(
                ", ".join(header.authors)
                if header.authors
                else metadata_author
            ),
            authors=header.authors,
            doi=header.doi,
            subject=_clean_metadata_value(
                raw_metadata.get("subject")
            ),
            keywords=_clean_metadata_value(
                raw_metadata.get("keywords")
            ),
            creator=_clean_metadata_value(
                raw_metadata.get("creator")
            ),
            producer=_clean_metadata_value(
                raw_metadata.get("producer")
            ),
            creation_date=_clean_metadata_value(
                raw_metadata.get("creationDate")
            ),
            modification_date=_clean_metadata_value(
                raw_metadata.get("modDate")
            ),
            page_count=document.page_count,
            title_source=header.title_source,
            author_source=header.author_source,
            doi_source=header.doi_source,
            header_confidence=header.confidence,
        )

        pages: list[ParsedPage] = []
        full_text_parts: list[str] = []

        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            page_number = page_index + 1

            text = _normalize_text(
                page.get_text("text", sort=True)
            )
            blocks = _extract_blocks(page, page_number)

            pages.append(
                ParsedPage(
                    page_number=page_number,
                    width=float(page.rect.width),
                    height=float(page.rect.height),
                    text=text,
                    character_count=len(text),
                    blocks=blocks,
                )
            )

            if text:
                full_text_parts.append(
                    f"--- PAGE {page_number} ---\n{text}"
                )

        full_text = "\n\n".join(full_text_parts).strip()

        if len(full_text) < MINIMUM_DOCUMENT_CHARACTERS:
            raise PDFTextExtractionError(
                "Very little machine-readable text was found. "
                "The PDF may be scanned and require OCR."
            )

        return metadata, pages, full_text

    finally:
        document.close()
