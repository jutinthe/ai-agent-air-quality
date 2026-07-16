from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.document import (
    DetectedSection,
    ParsedPage,
    SectionType,
)


@dataclass(frozen=True)
class HeadingCandidate:
    section_type: SectionType
    heading: str
    normalized_heading: str
    page_number: int
    page_index: int
    line_index: int
    confidence: float


HEADING_PATTERNS: list[tuple[SectionType, tuple[str, ...]]] = [
    (
        SectionType.ABSTRACT,
        (
            r"abstract",
            r"summary",
        ),
    ),
    (
        SectionType.KEYWORDS,
        (
            r"key\s*words?",
            r"index\s+terms?",
        ),
    ),
    (
        SectionType.INTRODUCTION,
        (
            r"introduction",
            r"general\s+introduction",
        ),
    ),
    (
        SectionType.BACKGROUND,
        (
            r"background",
            r"study\s+background",
        ),
    ),
    (
        SectionType.LITERATURE_REVIEW,
        (
            r"literature\s+review",
            r"related\s+work",
        ),
    ),
    (
        SectionType.METHODS,
        (
            r"methods?",
            r"materials?\s+and\s+methods?",
            r"methodology",
            r"study\s+methods?",
            r"experimental\s+procedures?",
            r"patients?\s+and\s+methods?",
            r"data\s+and\s+methods?",
        ),
    ),
    (
        SectionType.RESULTS,
        (
            r"results?",
            r"findings",
            r"study\s+results?",
        ),
    ),
    (
        SectionType.DISCUSSION,
        (
            r"discussion",
            r"results?\s+and\s+discussion",
        ),
    ),
    (
        SectionType.CONCLUSION,
        (
            r"conclusions?",
            r"concluding\s+remarks?",
            r"summary\s+and\s+conclusions?",
        ),
    ),
    (
        SectionType.LIMITATIONS,
        (
            r"limitations?",
            r"strengths?\s+and\s+limitations?",
        ),
    ),
    (
        SectionType.ACKNOWLEDGMENTS,
        (
            r"acknowledg(?:e)?ments?",
            r"funding",
            r"author\s+contributions?",
        ),
    ),
    (
        SectionType.REFERENCES,
        (
            r"references?",
            r"bibliography",
            r"literature\s+cited",
        ),
    ),
    (
        SectionType.SUPPLEMENTARY,
        (
            r"supplementary\s+(?:materials?|information|methods?)",
            r"supporting\s+information",
            r"appendix",
        ),
    ),
]


NUMBERING_PREFIX = re.compile(
    r"^\s*(?:"
    r"(?:section\s+)?"
    r"(?:\d+(?:\.\d+)*|[ivxlcdm]+)"
    r"[.)\s:-]*"
    r")?",
    re.IGNORECASE,
)

WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_heading(line: str) -> str:
    heading = line.strip()
    heading = NUMBERING_PREFIX.sub("", heading)
    heading = heading.strip(" .:;-–—")
    heading = WHITESPACE_PATTERN.sub(" ", heading)
    return heading.lower()


def _match_heading(line: str) -> tuple[SectionType, str] | None:
    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section_type, patterns in HEADING_PATTERNS:
        for pattern in patterns:
            if re.fullmatch(pattern, normalized, flags=re.IGNORECASE):
                return section_type, normalized

    return None


def _heading_confidence(line: str) -> float:
    stripped = line.strip()
    confidence = 0.72

    if stripped.isupper() and len(stripped) > 2:
        confidence += 0.10

    if len(stripped.split()) <= 5:
        confidence += 0.08

    if re.match(
        r"^(?:\d+(?:\.\d+)*|[IVXLCDM]+)[.)\s:-]+",
        stripped,
        flags=re.IGNORECASE,
    ):
        confidence += 0.05

    if stripped.endswith((".", ",", ";")):
        confidence -= 0.12

    return max(0.0, min(confidence, 1.0))


def find_heading_candidates(
    pages: list[ParsedPage],
) -> list[HeadingCandidate]:
    candidates: list[HeadingCandidate] = []

    for page_index, page in enumerate(pages):
        lines = page.text.splitlines()

        for line_index, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                continue

            if len(stripped) > 100:
                continue

            if len(stripped.split()) > 10:
                continue

            match = _match_heading(stripped)

            if match is None:
                continue

            section_type, normalized = match

            candidates.append(
                HeadingCandidate(
                    section_type=section_type,
                    heading=stripped,
                    normalized_heading=normalized,
                    page_number=page.page_number,
                    page_index=page_index,
                    line_index=line_index,
                    confidence=_heading_confidence(stripped),
                )
            )

    return _deduplicate_candidates(candidates)


def _deduplicate_candidates(
    candidates: list[HeadingCandidate],
) -> list[HeadingCandidate]:
    if not candidates:
        return []

    result: list[HeadingCandidate] = []

    for candidate in candidates:
        if result:
            previous = result[-1]

            same_location = (
                previous.page_index == candidate.page_index
                and abs(previous.line_index - candidate.line_index) <= 1
            )

            if (
                same_location
                and previous.section_type == candidate.section_type
            ):
                if candidate.confidence > previous.confidence:
                    result[-1] = candidate
                continue

        result.append(candidate)

    return result


def _extract_section_text(
    pages: list[ParsedPage],
    start: HeadingCandidate,
    end: HeadingCandidate | None,
) -> tuple[str, int]:
    text_parts: list[str] = []

    end_page_index = end.page_index if end else len(pages) - 1

    for page_index in range(start.page_index, end_page_index + 1):
        lines = pages[page_index].text.splitlines()

        start_line = start.line_index + 1 if page_index == start.page_index else 0

        if end is not None and page_index == end.page_index:
            end_line = end.line_index
        else:
            end_line = len(lines)

        page_text = "\n".join(lines[start_line:end_line]).strip()

        if page_text:
            text_parts.append(page_text)

    text = "\n\n".join(text_parts).strip()
    end_page = end.page_number if end is not None else pages[-1].page_number

    if end is not None and end.line_index == 0 and end.page_number > 1:
        end_page = max(start.page_number, end.page_number - 1)

    return text, end_page


def detect_sections(
    pages: list[ParsedPage],
) -> list[DetectedSection]:
    if not pages:
        return []

    candidates = find_heading_candidates(pages)

    if not candidates:
        complete_text = "\n\n".join(
            page.text for page in pages if page.text
        )

        return [
            DetectedSection(
                section_type=SectionType.OTHER,
                heading="Full document",
                normalized_heading="full document",
                start_page=1,
                end_page=pages[-1].page_number,
                text=complete_text,
                character_count=len(complete_text),
                heading_confidence=0.0,
            )
        ]

    sections: list[DetectedSection] = []

    first_candidate = candidates[0]

    preamble_parts: list[str] = []

    for page_index in range(0, first_candidate.page_index + 1):
        lines = pages[page_index].text.splitlines()

        end_line = (
            first_candidate.line_index
            if page_index == first_candidate.page_index
            else len(lines)
        )

        text = "\n".join(lines[:end_line]).strip()

        if text:
            preamble_parts.append(text)

    preamble = "\n\n".join(preamble_parts).strip()

    if preamble:
        sections.append(
            DetectedSection(
                section_type=SectionType.TITLE,
                heading="Document preamble",
                normalized_heading="document preamble",
                start_page=1,
                end_page=first_candidate.page_number,
                text=preamble,
                character_count=len(preamble),
                heading_confidence=0.5,
            )
        )

    for index, candidate in enumerate(candidates):
        next_candidate = (
            candidates[index + 1]
            if index + 1 < len(candidates)
            else None
        )

        text, end_page = _extract_section_text(
            pages,
            candidate,
            next_candidate,
        )

        sections.append(
            DetectedSection(
                section_type=candidate.section_type,
                heading=candidate.heading,
                normalized_heading=candidate.normalized_heading,
                start_page=candidate.page_number,
                end_page=end_page,
                text=text,
                character_count=len(text),
                heading_confidence=candidate.confidence,
            )
        )

    return sections
