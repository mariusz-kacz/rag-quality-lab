"""Evaluation metric calculations over golden questions and query traces."""

from __future__ import annotations

from collections.abc import Sequence

from rag_quality_lab.schemas import EvaluationMetrics, QueryTrace, Question


def calculate_evaluation_metrics(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> EvaluationMetrics:
    """Calculate every aggregate metric required for an evaluation artifact."""

    token_averages = calculate_token_averages(traces)
    return EvaluationMetrics(
        routing_accuracy=calculate_routing_accuracy(questions, traces),
        fallback_rate=calculate_fallback_rate(traces),
        hit_rate_at_k=calculate_hit_rate_at_k(questions, traces),
        mrr=calculate_mrr(questions, traces),
        citation_source_match=calculate_citation_source_match(questions, traces),
        no_answer_accuracy=calculate_no_answer_accuracy(questions, traces),
        average_context_tokens=token_averages.average_context_tokens,
        average_included_chunks=token_averages.average_included_chunks,
    )


def calculate_routing_accuracy(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> float | None:
    """Score category routing against questions with expected categories."""

    scored_pairs = [
        (question, trace)
        for question, trace in _paired_questions_and_traces(questions, traces)
        if question.expected_category is not None
    ]
    if not scored_pairs:
        return None

    correct = sum(
        1
        for question, trace in scored_pairs
        if trace.route_decision.selected_category == question.expected_category
    )
    return correct / len(scored_pairs)


def calculate_fallback_rate(traces: Sequence[QueryTrace]) -> float | None:
    """Return the share of traces that fell back to all-category retrieval."""

    if not traces:
        return None
    fallback_count = sum(1 for trace in traces if trace.route_decision.fallback_all_categories)
    return fallback_count / len(traces)


def calculate_hit_rate_at_k(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> float | None:
    """Calculate the share of answerable questions that are retrieval hits.

    A question counts as a hit when at least one expected source or expected chunk
    appears in the top-k retrieved results.
    """

    scored_pairs = _retrieval_scored_pairs(questions, traces)
    if not scored_pairs:
        return None

    hits = sum(
        1
        for question, trace in scored_pairs
        if _first_relevant_rank(question, trace) is not None
    )
    return hits / len(scored_pairs)


def calculate_mrr(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> float | None:
    """Calculate mean reciprocal rank using the first relevant retrieval."""

    scored_pairs = _retrieval_scored_pairs(questions, traces)
    if not scored_pairs:
        return None

    reciprocal_ranks = [
        0.0 if rank is None else 1.0 / rank
        for rank in (
            _first_relevant_rank(question, trace) for question, trace in scored_pairs
        )
    ]
    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def calculate_citation_source_match(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> float | None:
    """Score cited included chunks against expected source slugs or chunk IDs."""

    scored_pairs = _retrieval_scored_pairs(questions, traces)
    if not scored_pairs:
        return None

    matches = sum(
        1
        for question, trace in scored_pairs
        if _citation_matches_expected_source(question, trace)
    )
    return matches / len(scored_pairs)


def calculate_no_answer_accuracy(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> float | None:
    """Score whether answer/no-answer behavior matches the golden label."""

    scored_pairs = _paired_questions_and_traces(questions, traces)
    if not scored_pairs:
        return None

    correct = sum(
        1
        for question, trace in scored_pairs
        if (question.answerability == "no_answer") == trace.answer_result.is_no_answer
    )
    return correct / len(scored_pairs)


def calculate_token_averages(traces: Sequence[QueryTrace]) -> EvaluationMetrics:
    """Return average context-token and included-chunk diagnostics."""

    if not traces:
        return EvaluationMetrics(
            average_context_tokens=None,
            average_included_chunks=None,
        )

    return EvaluationMetrics(
        average_context_tokens=sum(
            trace.context_build.final_estimated_context_tokens for trace in traces
        )
        / len(traces),
        average_included_chunks=sum(
            len(trace.context_build.included_chunks) for trace in traces
        )
        / len(traces),
    )


def _paired_questions_and_traces(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> list[tuple[Question, QueryTrace]]:
    return list(zip(questions, traces, strict=False))


def _retrieval_scored_pairs(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> list[tuple[Question, QueryTrace]]:
    return [
        (question, trace)
        for question, trace in _paired_questions_and_traces(questions, traces)
        if question.answerability == "answerable" and question.expected_relevant_sources
    ]


def _first_relevant_rank(question: Question, trace: QueryTrace) -> int | None:
    expected = set(question.expected_relevant_sources)
    for result in trace.retrieval_results:
        if result.source_slug in expected or result.chunk_id in expected:
            return result.rank
    return None


def _citation_matches_expected_source(question: Question, trace: QueryTrace) -> bool:
    expected = set(question.expected_relevant_sources)
    cited_chunk_ids = set(trace.citation_validation.cited_chunk_ids)
    if not cited_chunk_ids:
        return False

    for chunk in trace.context_build.included_chunks:
        if chunk.chunk_id not in cited_chunk_ids:
            continue
        if chunk.source_slug in expected or chunk.chunk_id in expected:
            return True
    return False
