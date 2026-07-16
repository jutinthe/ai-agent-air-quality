from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import StrictBaseModel
from app.schemas.extraction import PaperExtraction


class ExtractionRunMetadata(StrictBaseModel):
    paper_id: UUID
    model: str
    prompt_version: str
    input_character_count: int = Field(ge=0)
    sections_used: list[str] = Field(default_factory=list)
    sections_omitted: list[str] = Field(default_factory=list)
    attempts: int = Field(ge=1)
    created_at: datetime


class StoredExtraction(StrictBaseModel):
    extraction: PaperExtraction
    run_metadata: ExtractionRunMetadata
    warnings: list[str] = Field(default_factory=list)


class ExtractionResponse(StrictBaseModel):
    paper_id: UUID
    status: str
    extraction: PaperExtraction
    run_metadata: ExtractionRunMetadata
    warnings: list[str] = Field(default_factory=list)
