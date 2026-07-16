from pathlib import Path

import pymupdf

from app.services.pdf_parser import parse_pdf


def create_academic_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page(width=612, height=792)

    page.insert_text(
        (72, 80),
        "Long-Term Exposure to Fine Particulate Matter",
        fontsize=18,
        fontname="helv",
    )
    page.insert_text(
        (72, 104),
        "and Cardiovascular Mortality",
        fontsize=18,
        fontname="helv",
    )
    page.insert_text(
        (72, 140),
        "Alice Smith, Brian Chen, and Maria Garcia",
        fontsize=11,
        fontname="helv",
    )
    page.insert_text(
        (72, 162),
        "Department of Environmental Health, Example University",
        fontsize=9,
        fontname="helv",
    )
    page.insert_text(
        (72, 185),
        "https://doi.org/10.1234/example.2026.001",
        fontsize=9,
        fontname="helv",
    )
    page.insert_text(
        (72, 230),
        "ABSTRACT",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        (72, 250),
        "We examined PM2.5 exposure and mortality in a cohort.",
        fontsize=10,
        fontname="helv",
    )

    document.set_metadata(
        {
            "title": "Untitled",
            "author": "",
        }
    )

    document.save(path)
    document.close()


def test_infers_title_authors_and_doi(tmp_path: Path) -> None:
    pdf_path = tmp_path / "academic-paper.pdf"
    create_academic_pdf(pdf_path)

    metadata, _, _ = parse_pdf(pdf_path)

    assert metadata.title is not None
    assert "Long-Term Exposure" in metadata.title
    assert "Cardiovascular Mortality" in metadata.title

    assert metadata.authors == [
        "Alice Smith",
        "Brian Chen",
        "Maria Garcia",
    ]

    assert metadata.doi == "10.1234/example.2026.001"
    assert metadata.title_source == "first_page_layout"
    assert metadata.author_source == "first_page_layout"
    assert metadata.doi_source == "first_two_pages"
    assert metadata.header_confidence > 0
