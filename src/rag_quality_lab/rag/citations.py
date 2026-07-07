from __future__ import annotations
import re
from rag_quality_lab.schemas import ContextChunk, CitationValidation

VALID_CITATION = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9:_-]*)\]")
EMPTY_CITATION = re.compile(r"\[\s*\]")
CITATION_START = re.compile(r"\[[A-Za-z0-9][A-Za-z0-9:_-]*")


def extract_citations(answer_text: str) -> list[str]:
    seen = set()
    citations = []

    for match in VALID_CITATION.finditer(answer_text):
        citation = match.group(1)
        if citation not in seen:
            seen.add(citation)
            citations.append(citation)

    return citations


def find_malformed_citations(answer_text: str) -> list[str]:
    valid_spans = [match.span() for match in VALID_CITATION.finditer(answer_text)]
    malformed: list[tuple[int, str]] = []

    for match in EMPTY_CITATION.finditer(answer_text):
        malformed.append((match.start(), match.group(0)))

    for match in CITATION_START.finditer(answer_text):
        start, end = match.span()

        is_part_of_valid_citation = any(
            valid_start == start and valid_end >= end
            for valid_start, valid_end in valid_spans
        )

        if not is_part_of_valid_citation:
            malformed.append((start, match.group(0)))

    return [text for _, text in sorted(malformed, key=lambda item: item[0])]


def validate_citations(
    answer_text: str, selected_context: list[ContextChunk]
) -> CitationValidation:
    citations = extract_citations(answer_text)
    malformed_citations = find_malformed_citations(answer_text)
    context_chunk_ids = {item.chunk_id for item in selected_context}
    cited_chunk_ids = []
    invalid_citations = []
    validation_errors = []

    for citation in citations:
        cited_chunk_ids.append(citation)

        if citation not in context_chunk_ids:
            invalid_citations.append(citation)
            validation_errors.append(
                f"Citation {citation} from answer text not found in selected context"
            )

    if not cited_chunk_ids and not malformed_citations:
        validation_errors.append("Citations missing in answer text")

    for malformed_citation in malformed_citations:
        invalid_citations.append(malformed_citation)
        validation_errors.append(
            f"Answer text has malformed citation {malformed_citation}"
        )

    return CitationValidation(
        status="invalid" if validation_errors else "valid",
        cited_chunk_ids=cited_chunk_ids,
        invalid_citations=invalid_citations,
        validation_errors=validation_errors,
    )
