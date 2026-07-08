from __future__ import annotations

from rag_quality_lab.schemas.query import (
    SelectedContext,
    ContextChunk,
    ExcludedContextChunk,
)


def build_context(
    candidates: list[ContextChunk],
    max_context_tokens: int,
    output_token_limit: int,
    prompt_overhead_tokens: int,
) -> SelectedContext:
    if max_context_tokens < prompt_overhead_tokens:
        raise ValueError("prompt_overhead_tokens cannot exceed max_context_tokens")

    estimated_context_tokens = prompt_overhead_tokens
    included_chunks = []
    excluded_chunks = []
    sorted_candidates = sorted(candidates, key=lambda c: c.retrieval_rank)
    for candidate in sorted_candidates:
        if estimated_context_tokens + candidate.estimated_tokens <= max_context_tokens:
            included_chunks.append(candidate)
            estimated_context_tokens += candidate.estimated_tokens
            continue

        excluded_chunks.append(
            ExcludedContextChunk(
                category=candidate.category,
                content=candidate.content,
                chunk_id=candidate.chunk_id,
                estimated_tokens=candidate.estimated_tokens,
                source_slug=candidate.source_slug,
                section_path=candidate.section_path,
                reason="budget_exceeded",
                retrieval_rank=candidate.retrieval_rank,
            )
        )

    return SelectedContext(
        included_chunks=included_chunks,
        excluded_chunks=excluded_chunks,
        final_estimated_context_tokens=estimated_context_tokens,
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
    )
