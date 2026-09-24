from __future__ import annotations

import pytest

from rag_quality_lab.rag.context import build_context
from rag_quality_lab.schemas import ContextChunk
from rag_quality_lab.schemas.categories import KnowledgeCategoryName

pytestmark = pytest.mark.unit


def test_context_builder_includes_ranked_chunks_until_budget_is_reached() -> None:
    candidates = [
        context_chunk("chunk-1", rank=1, estimated_tokens=30),
        context_chunk("chunk-2", rank=2, estimated_tokens=40),
        context_chunk("chunk-3", rank=3, estimated_tokens=50),
    ]

    context = build_context(
        candidates,
        max_context_tokens=100,
        output_token_limit=200,
        prompt_overhead_tokens=10,
    )

    assert [chunk.chunk_id for chunk in context.included_chunks] == [
        "chunk-1",
        "chunk-2",
    ]
    assert [chunk.retrieval_rank for chunk in context.included_chunks] == [1, 2]
    assert context.final_estimated_context_tokens == 80
    assert context.max_context_tokens == 100
    assert context.output_token_limit == 200
    assert [(chunk.chunk_id, chunk.reason) for chunk in context.excluded_chunks] == [
        ("chunk-3", "budget_exceeded")
    ]


def test_context_builder_records_all_excluded_chunk_reasons() -> None:
    candidates = [
        context_chunk("chunk-1", rank=1, estimated_tokens=60),
        context_chunk("chunk-2", rank=2, estimated_tokens=35),
        context_chunk("chunk-3", rank=3, estimated_tokens=25),
    ]

    context = build_context(
        candidates,
        max_context_tokens=90,
        output_token_limit=150,
        prompt_overhead_tokens=10,
    )

    assert [chunk.chunk_id for chunk in context.included_chunks] == ["chunk-1"]
    assert [(chunk.chunk_id, chunk.reason) for chunk in context.excluded_chunks] == [
        ("chunk-2", "budget_exceeded"),
        ("chunk-3", "budget_exceeded"),
    ]
    assert context.final_estimated_context_tokens == 70


def test_context_builder_handles_single_oversized_chunk_without_exceeding_budget() -> (
    None
):
    candidates = [
        context_chunk("oversized", rank=1, estimated_tokens=250),
    ]

    context = build_context(
        candidates,
        max_context_tokens=100,
        output_token_limit=50,
        prompt_overhead_tokens=10,
    )

    assert context.included_chunks == []
    assert context.final_estimated_context_tokens == 10
    assert [(chunk.chunk_id, chunk.reason) for chunk in context.excluded_chunks] == [
        ("oversized", "budget_exceeded")
    ]


def test_context_builder_sorts_candidates_by_retrieval_rank_before_budgeting() -> None:
    candidates = [
        context_chunk("chunk-3", rank=3, estimated_tokens=10),
        context_chunk("chunk-1", rank=1, estimated_tokens=10),
        context_chunk("chunk-2", rank=2, estimated_tokens=10),
    ]

    context = build_context(
        candidates,
        max_context_tokens=100,
        output_token_limit=100,
        prompt_overhead_tokens=0,
    )

    assert [chunk.chunk_id for chunk in context.included_chunks] == [
        "chunk-1",
        "chunk-2",
        "chunk-3",
    ]


def test_context_builder_rejects_prompt_overhead_that_exceeds_budget() -> None:
    with pytest.raises(ValueError, match="prompt_overhead_tokens"):
        build_context(
            [context_chunk("chunk-1", rank=1, estimated_tokens=10)],
            max_context_tokens=50,
            output_token_limit=100,
            prompt_overhead_tokens=60,
        )


def test_reranked_context_preserves_both_ranks_and_enforces_count_and_tokens():
    candidates = [
        context_chunk("c1", rank=1, estimated_tokens=10).model_copy(
            update={"rerank_rank": 4}
        ),
        context_chunk("c2", rank=2, estimated_tokens=200).model_copy(
            update={"rerank_rank": 2}
        ),
        context_chunk("c3", rank=3, estimated_tokens=30).model_copy(
            update={"rerank_rank": 3}
        ),
        context_chunk("c4", rank=4, estimated_tokens=40).model_copy(
            update={"rerank_rank": 1}
        ),
    ]
    context = build_context(
        candidates,
        max_context_tokens=100,
        output_token_limit=100,
        prompt_overhead_tokens=0,
        max_chunks=2,
    )
    assert [c.chunk_id for c in context.included_chunks] == ["c4", "c3"]
    assert [c.retrieval_rank for c in context.included_chunks] == [4, 3]
    assert [c.rerank_rank for c in context.included_chunks] == [1, 3]
    assert [(c.chunk_id, c.reason) for c in context.excluded_chunks] == [
        ("c2", "budget_exceeded"),
        ("c1", "chunk_limit_exceeded"),
    ]
    assert context.final_estimated_context_tokens == 70


def context_chunk(chunk_id: str, *, rank: int, estimated_tokens: int) -> ContextChunk:
    return ContextChunk(
        chunk_id=chunk_id,
        source_slug=f"source-{rank}",
        category=KnowledgeCategoryName.RAG_AND_CONTEXT_HANDLING,
        section_path=["Overview"],
        retrieval_rank=rank,
        content=f"Content for {chunk_id}.",
        estimated_tokens=estimated_tokens,
    )
