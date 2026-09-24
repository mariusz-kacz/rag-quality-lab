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
    max_chunks: int | None = None,
) -> SelectedContext:
    if max_context_tokens < prompt_overhead_tokens:
        raise ValueError("prompt_overhead_tokens cannot exceed max_context_tokens")
    if max_chunks is not None and max_chunks < 1:
        raise ValueError("max_chunks must be >= 1")

    estimated_context_tokens = prompt_overhead_tokens
    included_chunks = []
    excluded_chunks = []
    sorted_candidates = sorted(
        candidates, key=lambda c: c.rerank_rank or c.retrieval_rank
    )
    for candidate in sorted_candidates:
        if max_chunks is not None and len(included_chunks) >= max_chunks:
            reason = "chunk_limit_exceeded"
        elif estimated_context_tokens + candidate.estimated_tokens > max_context_tokens:
            reason = "budget_exceeded"
        else:
            included_chunks.append(candidate)
            estimated_context_tokens += candidate.estimated_tokens
            continue

        excluded_chunks.append(
            ExcludedContextChunk(
                **candidate.model_dump(),
                reason=reason,
            )
        )

    return SelectedContext(
        included_chunks=included_chunks,
        excluded_chunks=excluded_chunks,
        final_estimated_context_tokens=estimated_context_tokens,
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
    )
