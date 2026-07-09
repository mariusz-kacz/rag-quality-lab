from __future__ import annotations

import pytest

from rag_quality_lab.rag.citations import (
    citation_aliases_for_context,
    extract_citations,
    validate_citations,
)
from rag_quality_lab.schemas import ContextChunk


pytestmark = pytest.mark.unit


def test_extract_citations_parses_chunk_ids_in_first_seen_order() -> None:
    answer_text = (
        "Grounded answers cite the chunks they use [C1]. "
        "A second claim can cite another chunk [C2]. "
        "Repeated citations should not duplicate IDs [C1]."
    )

    assert extract_citations(answer_text) == ["C1", "C2"]


def test_validate_citations_accepts_aliases_from_selected_context() -> None:
    selected_context = [
        context_chunk("chunk-alpha", rank=1),
        context_chunk("chunk-beta", rank=2),
    ]
    validation = validate_citations(
        "RAG improves answer grounding with retrieved evidence [C1] [C2].",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "valid"
    assert validation.cited_chunk_ids == ["chunk-alpha", "chunk-beta"]
    assert validation.invalid_citations == []
    assert validation.validation_errors == []


def test_validate_citations_resolves_short_aliases_to_chunk_ids() -> None:
    selected_context = [
        context_chunk("source-alpha:section:0001:long-hash", rank=1),
        context_chunk("source-beta:section:0002:long-hash", rank=2),
    ]

    validation = validate_citations(
        "RAG improves answer grounding with retrieved evidence [C1] [C2].",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "valid"
    assert validation.cited_chunk_ids == [
        "source-alpha:section:0001:long-hash",
        "source-beta:section:0002:long-hash",
    ]
    assert validation.invalid_citations == []
    assert validation.validation_errors == []


def test_validate_citations_rejects_malformed_citations() -> None:
    selected_context = [context_chunk("chunk-alpha", rank=1)]
    validation = validate_citations(
        "This answer has an unfinished citation [C1 and an empty citation [].",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == []
    assert validation.invalid_citations == ["[C1", "[]"]
    assert any("malformed" in error for error in validation.validation_errors)


def test_validate_citations_rejects_missing_citations() -> None:
    selected_context = [context_chunk("chunk-alpha", rank=1)]
    validation = validate_citations(
        "This answer makes a grounded claim without citing selected evidence.",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == []
    assert validation.invalid_citations == []
    assert any("missing" in error for error in validation.validation_errors)


def test_validate_citations_rejects_out_of_context_citations() -> None:
    selected_context = [
        context_chunk("chunk-alpha", rank=1),
        context_chunk("chunk-beta", rank=2),
    ]
    validation = validate_citations(
        "This answer cites a chunk that was not selected [C3].",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == ["C3"]
    assert validation.invalid_citations == ["C3"]
    assert any("selected context" in error for error in validation.validation_errors)


def test_validate_citations_rejects_legacy_chunk_id_citations() -> None:
    selected_context = [context_chunk("chunk-alpha", rank=1)]

    validation = validate_citations(
        "This answer cites a raw chunk id [chunk-alpha].",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == []
    assert validation.invalid_citations == ["[chunk-alpha]"]
    assert any("malformed" in error for error in validation.validation_errors)


def test_validate_citations_ignores_editorial_brackets() -> None:
    selected_context = [context_chunk("chunk-alpha", rank=1)]

    validation = validate_citations(
        "The source says trimming keep[s] citations clear. [C1]",
        selected_context=selected_context,
        citation_aliases=citation_aliases_for_context(selected_context),
    )

    assert validation.status == "valid"
    assert validation.cited_chunk_ids == ["chunk-alpha"]
    assert validation.invalid_citations == []
    assert validation.validation_errors == []


def context_chunk(chunk_id: str, *, rank: int) -> ContextChunk:
    return ContextChunk(
        chunk_id=chunk_id,
        source_slug=f"source-{rank}",
        category="RAG and context handling",
        section_path=["Overview"],
        retrieval_rank=rank,
        content=f"Evidence for {chunk_id}.",
        estimated_tokens=20,
    )
