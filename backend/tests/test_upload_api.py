from pathlib import Path

import pymupdf
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def create_test_pdf(path: Path) -> None:
    document = pymupdf.open()

    first_page = document.new_page()
    first_page.insert_text(
        (72, 72),
        (
            "Air Pollution and Health\n\n"
            "ABSTRACT\n"
            "This study examined PM2.5 exposure and health outcomes.\n\n"
            "INTRODUCTION\n"
            "Air pollution affects human health."
        ),
    )

    second_page = document.new_page()
    second_page.insert_text(
        (72, 72),
        (
            "METHODS\n"
            "We conducted a cohort study using air monitoring data.\n\n"
            "RESULTS\n"
            "Higher PM2.5 was associated with increased risk.\n\n"
            "DISCUSSION\n"
            "The association was robust in sensitivity analyses."
        ),
    )

    document.save(path)
    document.close()


def test_upload_pdf(tmp_path: Path) -> None:
    settings = get_settings()
    original_upload_directory = settings.upload_directory
    original_processed_directory = settings.processed_directory

    settings.upload_directory = tmp_path / "uploads"
    settings.processed_directory = tmp_path / "processed"
    settings.create_storage_directories()

    pdf_path = tmp_path / "test-paper.pdf"
    create_test_pdf(pdf_path)

    try:
        with TestClient(app) as client:
            with pdf_path.open("rb") as pdf_file:
                response = client.post(
                    "/api/papers/upload",
                    files={
                        "file": (
                            "test-paper.pdf",
                            pdf_file,
                            "application/pdf",
                        )
                    },
                )

        assert response.status_code == 201

        body = response.json()

        assert body["status"] == "parsed"
        assert body["metadata"]["page_count"] == 2
        assert body["full_text_character_count"] > 100
        assert len(body["sections"]) >= 3

        paper_id = body["paper_id"]

        processed_file = (
            settings.processed_directory
            / paper_id
            / "parsed_document.json"
        )

        assert processed_file.exists()

    finally:
        settings.upload_directory = original_upload_directory
        settings.processed_directory = original_processed_directory


def test_rejects_non_pdf() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/papers/upload",
            files={
                "file": (
                    "notes.txt",
                    b"This is not a PDF.",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 400
