from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import InvalidPDFError, PDFTooLargeError


PDF_SIGNATURE = b"%PDF-"
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class StoredPDF:
    path: Path
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    sha256: str


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    name = name.strip("._")

    if not name:
        return "paper.pdf"

    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"

    return name[:180]


async def store_pdf(
    uploaded_file: UploadFile,
    paper_id: UUID,
    settings: Settings,
) -> StoredPDF:
    original_filename = uploaded_file.filename or "paper.pdf"
    sanitized_filename = sanitize_filename(original_filename)

    if not sanitized_filename.lower().endswith(".pdf"):
        raise InvalidPDFError("Only PDF files are supported.")

    paper_directory = settings.upload_directory / str(paper_id)
    paper_directory.mkdir(parents=True, exist_ok=True)

    stored_filename = "source.pdf"
    destination = paper_directory / stored_filename

    sha256 = hashlib.sha256()
    total_size = 0
    first_chunk = True

    try:
        with destination.open("wb") as output:
            while chunk := await uploaded_file.read(CHUNK_SIZE):
                if first_chunk:
                    first_chunk = False
                    if not chunk.startswith(PDF_SIGNATURE):
                        raise InvalidPDFError(
                            "The uploaded file does not have a valid PDF signature."
                        )

                total_size += len(chunk)

                if total_size > settings.maximum_pdf_size_bytes:
                    raise PDFTooLargeError(
                        "The PDF exceeds the configured "
                        f"{settings.maximum_pdf_size_mb} MB limit."
                    )

                sha256.update(chunk)
                output.write(chunk)

        if total_size == 0:
            raise InvalidPDFError("The uploaded PDF is empty.")

    except Exception:
        destination.unlink(missing_ok=True)

        try:
            paper_directory.rmdir()
        except OSError:
            pass

        raise

    finally:
        await uploaded_file.close()

    return StoredPDF(
        path=destination,
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=uploaded_file.content_type or "application/pdf",
        size_bytes=total_size,
        sha256=sha256.hexdigest(),
    )
