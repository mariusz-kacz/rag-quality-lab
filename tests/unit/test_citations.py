from __future__ import annotations

import pytest

from rag_quality_lab.rag.citations import extract_citations, validate_citations
from rag_quality_lab.schemas import ContextChunk


pytestmark = pytest.mark.unit


def test_extract_citations_parses_chunk_ids_in_first_seen_order() -> None:
    answer_text = (
        "Grounded answers cite the chunks they use [chunk-alpha]. "
        "A second claim can cite another chunk [chunk-beta]. "
        "Repeated citations should not duplicate IDs [chunk-alpha]."
    )

    assert extract_citations(answer_text) == ["chunk-alpha", "chunk-beta"]


def test_validate_citations_accepts_citations_from_selected_context() -> None:
    validation = validate_citations(
        "RAG improves answer grounding with retrieved evidence [chunk-alpha] [chunk-beta].",
        selected_context=[
            context_chunk("chunk-alpha", rank=1),
            context_chunk("chunk-beta", rank=2),
        ],
    )

    assert validation.status == "valid"
    assert validation.cited_chunk_ids == ["chunk-alpha", "chunk-beta"]
    assert validation.invalid_citations == []
    assert validation.validation_errors == []


def test_validate_citations_rejects_malformed_citations() -> None:
    validation = validate_citations(
        "This answer has an unfinished citation [chunk-alpha and an empty citation [].",
        selected_context=[context_chunk("chunk-alpha", rank=1)],
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == []
    assert validation.invalid_citations == ["[chunk-alpha", "[]"]
    assert any("malformed" in error for error in validation.validation_errors)


def test_validate_citations_rejects_missing_citations() -> None:
    validation = validate_citations(
        "This answer makes a grounded claim without citing selected evidence.",
        selected_context=[context_chunk("chunk-alpha", rank=1)],
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == []
    assert validation.invalid_citations == []
    assert any("missing" in error for error in validation.validation_errors)


def test_validate_citations_rejects_out_of_context_citations() -> None:
    validation = validate_citations(
        "This answer cites a chunk that was not selected [chunk-gamma].",
        selected_context=[
            context_chunk("chunk-alpha", rank=1),
            context_chunk("chunk-beta", rank=2),
        ],
    )

    assert validation.status == "invalid"
    assert validation.cited_chunk_ids == ["chunk-gamma"]
    assert validation.invalid_citations == ["chunk-gamma"]
    assert any("selected context" in error for error in validation.validation_errors)


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
