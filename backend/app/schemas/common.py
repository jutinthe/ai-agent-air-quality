from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_ASSESSED = "not_assessed"


class EvidenceLocation(StrictBaseModel):
    section: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    table_or_figure: str | None = None
    quoted_text: str | None = Field(default=None, max_length=2000)


class ExtractionEvidence(StrictBaseModel):
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_ASSESSED
    locations: list[EvidenceLocation] = Field(default_factory=list)
    extraction_notes: str | None = None
