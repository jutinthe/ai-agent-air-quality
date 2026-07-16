"""Extract title, authors, and DOI from the first pages of a paper."""

from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import median
from typing import Any

import pymupdf


DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
    re.IGNORECASE,
)

ORCID_PATTERN = re.compile(
    r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)

AFFILIATION_PATTERN = re.compile(
    r"\b("
    r"university|college|school|department|division|institute|"
    r"hospital|center|centre|laboratory|faculty|academy|"
    r"research unit|ministry|agency|corporation|inc\.?"
    r")\b",
    re.IGNORECASE,
)

JOURNAL_PATTERN = re.compile(
    r"\b("
    r"journal|volume|vol\.?|issue|received|accepted|published|"
    r"copyright|doi|https?://|www\."
    r")\b",
    re.IGNORECASE,
)

AUTHOR_CONNECTOR_PATTERN = re.compile(
    r"\b(and|&)\b",
    re.IGNORECASE,
)

AUTHOR_MARKER_PATTERN = re.compile(
    r"(?<=\w)[*†‡§¶]|\b\d+[,*†‡§¶]*\b"
)

SUPERSCRIPT_SUFFIX_PATTERN = re.compile(
    r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ])(?:\d+|[*†‡§¶])+(?=\s|,|$)"
)

MULTISPACE_PATTERN = re.compile(r"\s+")

BAD_METADATA_VALUES = {
    "",
    "untitled",
    "unknown",
    "none",
    "null",
    "document",
    "article",
    "manuscript",
    "microsoft word",
    "pdf",
}


@dataclass(frozen=True)
class VisualLine:
    text: str
    y0: float
    y1: float
    x0: float
    x1: float
    max_font_size: float
    average_font_size: float
    bold_fraction: float


@dataclass(frozen=True)
class HeaderExtraction:
    title: str | None
    authors: list[str]
    doi: str | None
    title_source: str
    author_source: str
    doi_source: str
    confidence: float


def clean_text(value: str) -> str:
    return MULTISPACE_PATTERN.sub(" ", value).strip()


def is_usable_metadata(value: str | None) -> bool:
    if not value:
        return False

    normalized = clean_text(value).lower().strip(".-_")

    if normalized in BAD_METADATA_VALUES:
        return False

    if len(normalized) < 4:
        return False

    return True


def _font_is_bold(font_name: str, flags: int) -> bool:
    font = font_name.lower()

    return (
        "bold" in font
        or "black" in font
        or "heavy" in font
        or bool(flags & 16)
    )


def extract_visual_lines(page: pymupdf.Page) -> list[VisualLine]:
    page_dict: dict[str, Any] = page.get_text("dict", sort=True)
    visual_lines: list[VisualLine] = []

    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue

        for line in block.get("lines", []):
            spans = line.get("spans", [])

            if not spans:
                continue

            text_parts: list[str] = []
            weighted_size = 0.0
            total_characters = 0
            max_font_size = 0.0
            bold_characters = 0

            x0_values: list[float] = []
            y0_values: list[float] = []
            x1_values: list[float] = []
            y1_values: list[float] = []

            for span in spans:
                span_text = str(span.get("text", ""))
                cleaned_span = span_text.strip()

                if not cleaned_span:
                    continue

                size = float(span.get("size", 0.0))
                characters = max(len(cleaned_span), 1)
                bbox = span.get("bbox", (0, 0, 0, 0))
                font = str(span.get("font", ""))
                flags = int(span.get("flags", 0))

                text_parts.append(span_text)
                weighted_size += size * characters
                total_characters += characters
                max_font_size = max(max_font_size, size)

                if _font_is_bold(font, flags):
                    bold_characters += characters

                x0_values.append(float(bbox[0]))
                y0_values.append(float(bbox[1]))
                x1_values.append(float(bbox[2]))
                y1_values.append(float(bbox[3]))

            text = clean_text(" ".join(text_parts))

            if not text or not total_characters:
                continue

            visual_lines.append(
                VisualLine(
                    text=text,
                    y0=min(y0_values),
                    y1=max(y1_values),
                    x0=min(x0_values),
                    x1=max(x1_values),
                    max_font_size=max_font_size,
                    average_font_size=weighted_size / total_characters,
                    bold_fraction=bold_characters / total_characters,
                )
            )

    return sorted(visual_lines, key=lambda item: (item.y0, item.x0))


def _looks_like_noise(line: VisualLine) -> bool:
    text = line.text

    if len(text) < 3:
        return True

    if EMAIL_PATTERN.search(text):
        return True

    if text.lower().startswith(
        (
            "http://",
            "https://",
            "www.",
            "doi:",
            "downloaded from",
        )
    ):
        return True

    if JOURNAL_PATTERN.search(text):
        return True

    return False


def _title_line_score(
    line: VisualLine,
    page_height: float,
    body_font_size: float,
) -> float:
    score = 0.0
    text = line.text
    word_count = len(text.split())

    font_ratio = (
        line.max_font_size / body_font_size
        if body_font_size > 0
        else 1.0
    )

    score += min(font_ratio, 3.0) * 2.0
    score += line.bold_fraction * 1.5

    if line.y0 < page_height * 0.45:
        score += 1.5

    if line.y0 < page_height * 0.25:
        score += 0.75

    if 4 <= word_count <= 30:
        score += 1.0

    if len(text) >= 25:
        score += 0.5

    if text.endswith((".", ";")):
        score -= 1.0

    if AFFILIATION_PATTERN.search(text):
        score -= 3.0

    if JOURNAL_PATTERN.search(text):
        score -= 3.0

    if EMAIL_PATTERN.search(text):
        score -= 4.0

    if word_count > 40:
        score -= 2.0

    return score


def infer_title(
    lines: list[VisualLine],
    page_height: float,
) -> tuple[str | None, int | None, int | None, float]:
    candidates = [
        line
        for line in lines
        if line.y0 <= page_height * 0.55
        and not _looks_like_noise(line)
    ]

    if not candidates:
        return None, None, None, 0.0

    font_sizes = [
        line.average_font_size
        for line in candidates
        if line.average_font_size > 0
    ]

    body_font_size = median(font_sizes) if font_sizes else 10.0

    scored = [
        (
            _title_line_score(line, page_height, body_font_size),
            index,
            line,
        )
        for index, line in enumerate(lines)
        if line in candidates
    ]

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_index, best_line = scored[0]

    if best_score < 4.0:
        return None, None, None, 0.0

    selected_indexes = [best_index]

    # Join wrapped title lines when their font sizes and positions match.
    for direction in (-1, 1):
        index = best_index + direction

        while 0 <= index < len(lines):
            candidate = lines[index]

            if candidate.y0 > page_height * 0.55:
                break

            font_difference = abs(
                candidate.max_font_size - best_line.max_font_size
            )

            vertical_gap = (
                best_line.y0 - candidate.y1
                if direction == -1
                else candidate.y0 - best_line.y1
            )

            if (
                font_difference <= 1.5
                and vertical_gap <= best_line.max_font_size * 1.8
                and not _looks_like_noise(candidate)
                and not AFFILIATION_PATTERN.search(candidate.text)
                and len(candidate.text.split()) <= 25
            ):
                selected_indexes.append(index)
                index += direction
            else:
                break

    selected_indexes.sort()
    title = clean_text(
        " ".join(lines[index].text for index in selected_indexes)
    )

    confidence = min(0.98, max(0.5, best_score / 10.0))

    return (
        title,
        selected_indexes[0],
        selected_indexes[-1],
        confidence,
    )


def _looks_like_author_line(text: str) -> bool:
    if not text or len(text) > 500:
        return False

    if EMAIL_PATTERN.search(text):
        return False

    if AFFILIATION_PATTERN.search(text):
        return False

    if JOURNAL_PATTERN.search(text):
        return False

    words = text.split()

    if len(words) < 2 or len(words) > 60:
        return False

    comma_count = text.count(",")
    has_connector = bool(AUTHOR_CONNECTOR_PATTERN.search(text))
    capitalized_words = sum(
        1
        for word in words
        if word.strip(",;*†‡§¶0123456789")
        and word.strip(",;*†‡§¶0123456789")[0].isupper()
    )

    capitalized_ratio = capitalized_words / max(len(words), 1)

    return (
        comma_count >= 1
        or has_connector
        or capitalized_ratio >= 0.55
    )


def _remove_author_markers(text: str) -> str:
    text = SUPERSCRIPT_SUFFIX_PATTERN.sub("", text)
    text = ORCID_PATTERN.sub("", text)
    text = re.sub(r"\([^)]*(?:ORCID|corresponding)[^)]*\)", "", text, flags=re.I)
    return clean_text(text.strip(" ,;"))


def split_authors(author_text: str) -> list[str]:
    cleaned = _remove_author_markers(author_text)

    cleaned = re.sub(
        r"\s+(?:and|&)\s+",
        ", ",
        cleaned,
        flags=re.IGNORECASE,
    )

    possible_authors = [
        _remove_author_markers(part)
        for part in re.split(r"\s*[,;]\s*", cleaned)
    ]

    authors: list[str] = []

    for author in possible_authors:
        if not author:
            continue

        if AFFILIATION_PATTERN.search(author):
            continue

        if EMAIL_PATTERN.search(author):
            continue

        author = AUTHOR_MARKER_PATTERN.sub("", author)
        author = clean_text(author.strip(" ,;"))

        if len(author.split()) < 1:
            continue

        if author.lower() in {"and", "et al", "et al."}:
            continue

        authors.append(author)

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(authors))


def infer_authors(
    lines: list[VisualLine],
    title_end_index: int | None,
    page_height: float,
) -> tuple[list[str], float]:
    if title_end_index is None:
        return [], 0.0

    candidate_lines: list[str] = []

    for line in lines[title_end_index + 1 : title_end_index + 10]:
        if line.y0 > page_height * 0.65:
            break

        if AFFILIATION_PATTERN.search(line.text):
            break

        if EMAIL_PATTERN.search(line.text):
            break

        normalized = line.text.strip().lower()

        if normalized in {
            "abstract",
            "summary",
            "introduction",
            "keywords",
        }:
            break

        if _looks_like_author_line(line.text):
            candidate_lines.append(line.text)
        elif candidate_lines:
            break

    if not candidate_lines:
        return [], 0.0

    authors = split_authors(" ".join(candidate_lines))

    if not authors:
        return [], 0.0

    confidence = 0.72

    if len(authors) >= 2:
        confidence += 0.08

    if any("," in line for line in candidate_lines):
        confidence += 0.05

    return authors, min(confidence, 0.92)


def find_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text)

    if not match:
        return None

    return match.group(0).rstrip(".,;)]}")


def normalize_metadata_authors(author_value: str | None) -> list[str]:
    if not is_usable_metadata(author_value):
        return []

    assert author_value is not None

    if ";" in author_value:
        candidates = author_value.split(";")
    elif AUTHOR_CONNECTOR_PATTERN.search(author_value):
        candidates = re.split(
            r"\s+(?:and|&)\s+",
            author_value,
            flags=re.IGNORECASE,
        )
    else:
        # Avoid splitting "Last, First" into two authors.
        candidates = [author_value]

    return [
        clean_text(candidate)
        for candidate in candidates
        if clean_text(candidate)
    ]


def extract_header_information(
    document: pymupdf.Document,
    raw_metadata: dict[str, Any],
) -> HeaderExtraction:
    first_page = document.load_page(0)
    lines = extract_visual_lines(first_page)

    inferred_title, _, title_end_index, title_confidence = infer_title(
        lines=lines,
        page_height=float(first_page.rect.height),
    )

    inferred_authors, author_confidence = infer_authors(
        lines=lines,
        title_end_index=title_end_index,
        page_height=float(first_page.rect.height),
    )

    metadata_title = str(raw_metadata.get("title") or "").strip()
    metadata_author = str(raw_metadata.get("author") or "").strip()

    if inferred_title:
        title = inferred_title
        title_source = "first_page_layout"
    elif is_usable_metadata(metadata_title):
        title = metadata_title
        title_source = "pdf_metadata"
        title_confidence = 0.65
    else:
        title = None
        title_source = "not_found"
        title_confidence = 0.0

    if inferred_authors:
        authors = inferred_authors
        author_source = "first_page_layout"
    else:
        authors = normalize_metadata_authors(metadata_author)
        author_source = "pdf_metadata" if authors else "not_found"
        author_confidence = 0.6 if authors else 0.0

    first_two_pages_text = "\n".join(
        document.load_page(page_index).get_text("text", sort=True)
        for page_index in range(min(2, document.page_count))
    )

    doi = find_doi(first_two_pages_text)
    doi_source = "first_two_pages" if doi else "not_found"

    confidence_values = [
        value
        for value in (title_confidence, author_confidence)
        if value > 0
    ]

    overall_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values
        else 0.0
    )

    return HeaderExtraction(
        title=title,
        authors=authors,
        doi=doi,
        title_source=title_source,
        author_source=author_source,
        doi_source=doi_source,
        confidence=round(overall_confidence, 3),
    )
