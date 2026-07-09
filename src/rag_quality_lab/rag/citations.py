from __future__ import annotations
import re
from collections.abc import Mapping, Sequence

from rag_quality_lab.schemas.query import CitationValidation, ContextChunk

VALID_CITATION = re.compile(r"\[(C[1-9][0-9]*)\]")
EMPTY_CITATION = re.compile(r"\[\s*\]")
CITATION_START = re.compile(r"\[C[0-9]*")

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
    answer_text: str,
    selected_context: Sequence[ContextChunk],
    citation_aliases: Mapping[str, str],
) -> CitationValidation:
    citations = extract_citations(answer_text)
    malformed_citations = find_malformed_citations(answer_text)
    context_chunk_ids = {item.chunk_id for item in selected_context}
    aliases = dict(citation_aliases)
    cited_chunk_ids = []
    invalid_citations = []
    validation_errors = []

    for citation in citations:
        resolved_citation = aliases.get(citation)
        if resolved_citation is None:
            cited_chunk_ids.append(citation)
            invalid_citations.append(citation)
            validation_errors.append(
                f"Citation {citation} from answer text not found in selected context"
            )
            continue

        cited_chunk_ids.append(resolved_citation)

        if resolved_citation not in context_chunk_ids:
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


def citation_aliases_for_context(
    selected_context: Sequence[ContextChunk],
) -> dict[str, str]:
    return {
        f"C{index}": chunk.chunk_id
        for index, chunk in enumerate(selected_context, start=1)
    }
