from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from app.core.config import Settings, get_settings
from app.schemas.llm_extraction import ExtractionResponse
from app.services.document_service import load_processed_document
from app.services.llm_extraction_service import (
    ExtractionServiceError,
    extract_paper,
    load_extraction,
)


router = APIRouter(
    prefix="/papers",
    tags=["Structured Extraction"],
)


@router.post(
    "/{paper_id}/extract",
    response_model=ExtractionResponse,
    summary="Extract the 12-field structured research record",
)
async def run_structured_extraction(
    paper_id: UUID,
    force: bool = Query(
        default=False,
        description="Rerun extraction even if a saved result exists.",
    ),
    settings: Settings = Depends(get_settings),
) -> ExtractionResponse:
    document = load_processed_document(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Parsed paper not found. Upload and parse the PDF first."
            ),
        )

    try:
        stored = await run_in_threadpool(
            extract_paper,
            paper_id,
            document,
            settings,
            force,
        )
    except ExtractionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ExtractionResponse(
        paper_id=paper_id,
        status="completed",
        extraction=stored.extraction,
        run_metadata=stored.run_metadata,
        warnings=stored.warnings,
    )


@router.get(
    "/{paper_id}/extraction",
    response_model=ExtractionResponse,
    summary="Retrieve a saved structured extraction",
)
async def get_structured_extraction(
    paper_id: UUID,
    settings: Settings = Depends(get_settings),
) -> ExtractionResponse:
    stored = load_extraction(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Extraction not found. Run the extraction endpoint first."
            ),
        )

    return ExtractionResponse(
        paper_id=paper_id,
        status="completed",
        extraction=stored.extraction,
        run_metadata=stored.run_metadata,
        warnings=stored.warnings,
    )
