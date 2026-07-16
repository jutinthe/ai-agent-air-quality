"""Structured OpenAI extraction service."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI
from pydantic import ValidationError

from app.core.config import Settings
from app.prompts.extraction_prompt import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_TEMPLATE,
)
from app.schemas.document import ParsedDocument
from app.schemas.extraction import PaperExtraction
from app.schemas.llm_extraction import (
    ExtractionRunMetadata,
    StoredExtraction,
)
from app.services.extraction_context import build_extraction_context


PROMPT_VERSION = "3.0.0"


class ExtractionServiceError(Exception):
    """Raised when structured extraction cannot be completed."""


def _metadata_value(value: str | None) -> str:
    return value if value else "Not available"


def _build_user_prompt(
    document: ParsedDocument,
    paper_context: str,
) -> str:
    metadata = document.metadata

    return EXTRACTION_USER_TEMPLATE.format(
        title=_metadata_value(metadata.title),
        authors=(
            ", ".join(metadata.authors)
            if metadata.authors
            else _metadata_value(metadata.author)
        ),
        doi=_metadata_value(metadata.doi),
        page_count=metadata.page_count,
        paper_context=paper_context,
    )


def _validate_extraction(
    extraction: PaperExtraction,
    document: ParsedDocument,
    model: str,
) -> PaperExtraction:
    extraction.extraction_model = model
    extraction.extraction_prompt_version = PROMPT_VERSION

    if (
        extraction.paper_metadata.title.lower()
        == "not clearly reported"
        and document.metadata.title
    ):
        extraction.paper_metadata.title = document.metadata.title

    if (
        not extraction.paper_metadata.authors
        and document.metadata.authors
    ):
        extraction.paper_metadata.authors = document.metadata.authors

    if not extraction.paper_metadata.doi and document.metadata.doi:
        extraction.paper_metadata.doi = document.metadata.doi

    return extraction


def save_extraction(
    paper_id: UUID,
    stored_extraction: StoredExtraction,
    processed_directory: Path,
) -> Path:
    paper_directory = processed_directory / str(paper_id)
    paper_directory.mkdir(parents=True, exist_ok=True)

    output_path = paper_directory / "extraction.json"
    output_path.write_text(
        json.dumps(
            stored_extraction.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def load_extraction(
    paper_id: UUID,
    processed_directory: Path,
) -> StoredExtraction | None:
    path = (
        processed_directory
        / str(paper_id)
        / "extraction.json"
    )

    if not path.exists():
        return None

    return StoredExtraction.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def extract_paper(
    paper_id: UUID,
    document: ParsedDocument,
    settings: Settings,
    force: bool = False,
) -> StoredExtraction:
    if not force:
        existing = load_extraction(
            paper_id=paper_id,
            processed_directory=settings.processed_directory,
        )

        if existing is not None:
            return existing

    if not settings.openai_api_key:
        raise ExtractionServiceError(
            "OPENAI_API_KEY is not configured."
        )

    context = build_extraction_context(
        document=document,
        maximum_characters=settings.extraction_maximum_characters,
    )

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=0,
    )

    user_prompt = _build_user_prompt(
        document=document,
        paper_context=context.text,
    )

    last_error: Exception | None = None
    attempts = 0

    for attempt in range(1, settings.extraction_maximum_attempts + 1):
        attempts = attempt

        try:
            response = client.responses.parse(
                model=settings.openai_extraction_model,
                input=[
                    {
                        "role": "system",
                        "content": EXTRACTION_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                text_format=PaperExtraction,
            )

            extraction = response.output_parsed

            if extraction is None:
                raise ExtractionServiceError(
                    "The model returned no parsed extraction."
                )

            extraction = _validate_extraction(
                extraction=extraction,
                document=document,
                model=settings.openai_extraction_model,
            )

            warnings: list[str] = []

            if context.sections_omitted:
                warnings.append(
                    "Some sections were omitted or truncated: "
                    + ", ".join(context.sections_omitted)
                )

            stored = StoredExtraction(
                extraction=extraction,
                run_metadata=ExtractionRunMetadata(
                    paper_id=paper_id,
                    model=settings.openai_extraction_model,
                    prompt_version=PROMPT_VERSION,
                    input_character_count=context.character_count,
                    sections_used=context.sections_used,
                    sections_omitted=context.sections_omitted,
                    attempts=attempts,
                    created_at=datetime.now(UTC),
                ),
                warnings=warnings,
            )

            save_extraction(
                paper_id=paper_id,
                stored_extraction=stored,
                processed_directory=settings.processed_directory,
            )

            return stored

        except (
            APIConnectionError,
            APITimeoutError,
            APIError,
            ValidationError,
            ExtractionServiceError,
        ) as exc:
            last_error = exc

            if attempt < settings.extraction_maximum_attempts:
                time.sleep(min(2 ** (attempt - 1), 8))

    raise ExtractionServiceError(
        f"Structured extraction failed after {attempts} attempts: "
        f"{last_error}"
    )
