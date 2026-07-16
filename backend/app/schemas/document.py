from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.schemas.common import StrictBaseModel


class SectionType(StrEnum):
    TITLE = "title"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    INTRODUCTION = "introduction"
    BACKGROUND = "background"
    LITERATURE_REVIEW = "literature_review"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    LIMITATIONS = "limitations"
    REFERENCES = "references"
    ACKNOWLEDGMENTS = "acknowledgments"
    SUPPLEMENTARY = "supplementary"
    OTHER = "other"


class PDFMetadata(StrictBaseModel):
    title: str | None = None

    # Keep the original string for backward compatibility.
    author: str | None = None

    # Preferred structured author representation.
    authors: list[str] = Field(default_factory=list)

    doi: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: str | None = None
    modification_date: str | None = None
    page_count: int = Field(ge=1)

    title_source: str = "not_found"
    author_source: str = "not_found"
    doi_source: str = "not_found"
    header_confidence: float = Field(default=0.0, ge=0, le=1)


class TextBlock(StrictBaseModel):
    page_number: int = Field(ge=1)
    block_number: int = Field(ge=0)
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    character_count: int = Field(ge=0)


class ParsedPage(StrictBaseModel):
    page_number: int = Field(ge=1)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    text: str
    character_count: int = Field(ge=0)
    blocks: list[TextBlock] = Field(default_factory=list)


class DetectedSection(StrictBaseModel):
    section_type: SectionType
    heading: str
    normalized_heading: str
    start_page: int = Field(ge=1)
    end_page: int = Field(ge=1)
    text: str
    character_count: int = Field(ge=0)
    heading_confidence: float = Field(ge=0, le=1)


class ParsedDocument(StrictBaseModel):
    paper_id: UUID
    original_filename: str
    stored_filename: str
    sha256: str
    file_size_bytes: int = Field(ge=1)
    metadata: PDFMetadata
    pages: list[ParsedPage]
    sections: list[DetectedSection]
    full_text: str
    extracted_at: datetime
