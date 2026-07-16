from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    InvalidPDFError,
    PDFTextExtractionError,
    PDFTooLargeError,
)
from app.schemas.document import ParsedDocument
from app.schemas.paper import (
    PaperUploadResponse,
    ProcessingStatus,
    UploadedFile,
)
from app.services.document_service import (
    load_processed_document,
    process_pdf,
)
from app.services.file_storage import store_pdf


router = APIRouter(prefix="/papers", tags=["Papers"])


@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a research paper",
)
async def upload_paper(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> PaperUploadResponse:
    paper_id = uuid4()

    try:
        stored_pdf = await store_pdf(
            uploaded_file=file,
            paper_id=paper_id,
            settings=settings,
        )

        parsed_document = process_pdf(
            paper_id=paper_id,
            stored_pdf=stored_pdf,
            settings=settings,
        )

    except PDFTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc

    except InvalidPDFError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except PDFTextExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF processing failed: {exc}",
        ) from exc

    return PaperUploadResponse(
        paper_id=paper_id,
        status=ProcessingStatus.PARSED,
        file=UploadedFile(
            filename=stored_pdf.original_filename,
            stored_filename=stored_pdf.stored_filename,
            content_type=stored_pdf.content_type,
            size_bytes=stored_pdf.size_bytes,
            sha256=stored_pdf.sha256,
        ),
        metadata=parsed_document.metadata,
        sections=parsed_document.sections,
        full_text_character_count=len(parsed_document.full_text),
        created_at=datetime.now(UTC),
    )


@router.get(
    "/{paper_id}/parsed",
    response_model=ParsedDocument,
    summary="Retrieve a parsed research paper",
)
async def get_parsed_paper(
    paper_id: UUID,
    settings: Settings = Depends(get_settings),
) -> ParsedDocument:
    document = load_processed_document(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed paper not found.",
        )

    return document
