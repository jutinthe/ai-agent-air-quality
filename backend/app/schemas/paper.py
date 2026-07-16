from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.schemas.common import StrictBaseModel
from app.schemas.document import DetectedSection, PDFMetadata
from app.schemas.extraction import PaperExtraction


class ProcessingStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    EXTRACTING = "extracting"
    GENERATING_OUTPUTS = "generating_outputs"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadedFile(StrictBaseModel):
    filename: str
    stored_filename: str
    content_type: str
    size_bytes: int = Field(ge=1)
    sha256: str


class PaperUploadResponse(StrictBaseModel):
    paper_id: UUID
    status: ProcessingStatus
    file: UploadedFile
    metadata: PDFMetadata
    sections: list[DetectedSection]
    full_text_character_count: int = Field(ge=0)
    created_at: datetime


class PaperProcessingStatus(StrictBaseModel):
    paper_id: UUID
    status: ProcessingStatus
    progress_percent: int = Field(ge=0, le=100)
    current_stage: str | None = None
    error_message: str | None = None
    updated_at: datetime


class PaperExtractionResponse(StrictBaseModel):
    paper_id: UUID
    status: ProcessingStatus
    extraction: PaperExtraction | None = None
