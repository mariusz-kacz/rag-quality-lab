"""Evaluation metric calculations over golden questions and query traces."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from rag_quality_lab.schemas import EvaluationMetrics, QueryTrace, Question, RetrievalMode
from rag_quality_lab.schemas.categories import REQUIRED_KNOWLEDGE_CATEGORIES


class EvaluationResultSetError(ValueError):
    """Raised when traces cannot be matched one-to-one with golden questions."""


def calculate_evaluation_metrics(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
    *,
    retrieval_mode: RetrievalMode = "routed-vector",
    category_margin: float = 0.0,
) -> EvaluationMetrics:
    """Calculate every aggregate metric required for an evaluation artifact."""

    matched_pairs = match_questions_to_traces(questions, traces)
    matched_traces = [trace for _, trace in matched_pairs]
    token_averages = calculate_token_averages(matched_traces)
    return EvaluationMetrics(
        routing_accuracy=calculate_routing_accuracy(questions, traces),
        average_searched_categories=calculate_average_searched_categories(
            matched_traces,
            retrieval_mode=retrieval_mode,
            category_margin=category_margin,
        ),
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
        for question, trace in _matched_questions_and_traces(questions, traces)
        if question.expected_category is not None and trace.route_decision is not None
    ]
    if not scored_pairs:
        return None

    correct = sum(
        1
        for question, trace in scored_pairs
        if trace.route_decision.selected_category == question.expected_category
    )
    return correct / len(scored_pairs)


def calculate_average_searched_categories(
    traces: Sequence[QueryTrace],
    *,
    retrieval_mode: RetrievalMode,
    category_margin: float,
) -> float | None:
    """Return the mean number of categories searched by retrieval."""

    if not traces:
        return None
    counts = [
        len(
            searched_categories(
                trace,
                retrieval_mode=retrieval_mode,
                category_margin=category_margin,
            )
        )
        for trace in traces
    ]
    return sum(counts) / len(counts)


def searched_categories(
    trace: QueryTrace,
    *,
    retrieval_mode: RetrievalMode,
    category_margin: float,
) -> list[str]:
    """Return the effective category scope used for retrieval."""

    if retrieval_mode == "baseline-vector":
        return list(REQUIRED_KNOWLEDGE_CATEGORIES)
    route = trace.route_decision
    if route is None:
        return []
    if route.fallback_all_categories:
        return list(route.category_scores)
    if route.selected_category is None:
        return []
    cutoff = max(0.0, route.confidence - category_margin)
    within_margin = [
        category for category, score in route.category_scores.items() if score >= cutoff
    ]
    return [
        route.selected_category,
        *(category for category in within_margin if category != route.selected_category),
    ]


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

    scored_pairs = _matched_questions_and_traces(questions, traces)
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


def _matched_questions_and_traces(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> list[tuple[Question, QueryTrace]]:
    return match_questions_to_traces(questions, traces)


def match_questions_to_traces(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> list[tuple[Question, QueryTrace]]:
    """Validate and match traces by question ID in golden-question order."""

    golden_ids = [question.question_id for question in questions]
    missing_golden_positions = [
        str(index)
        for index, question_id in enumerate(golden_ids, start=1)
        if question_id is None
    ]
    golden_id_counts = Counter(
        question_id for question_id in golden_ids if question_id is not None
    )
    duplicate_golden_ids = sorted(
        question_id for question_id, count in golden_id_counts.items() if count > 1
    )

    trace_ids = [trace.question.question_id for trace in traces]
    traces_without_ids = [
        trace.trace_id for trace in traces if trace.question.question_id is None
    ]
    result_id_counts = Counter(
        question_id for question_id in trace_ids if question_id is not None
    )
    duplicate_result_ids = sorted(
        question_id for question_id, count in result_id_counts.items() if count > 1
    )

    expected_ids = set(golden_id_counts)
    actual_ids = set(result_id_counts)
    missing_result_ids = sorted(expected_ids - actual_ids)
    unexpected_result_ids = sorted(actual_ids - expected_ids)

    issues: list[str] = []
    if missing_golden_positions:
        issues.append(
            "golden questions without question_id at positions: "
            + ", ".join(missing_golden_positions)
        )
    if duplicate_golden_ids:
        issues.append("duplicate golden question IDs: " + ", ".join(duplicate_golden_ids))
    if traces_without_ids:
        issues.append("traces without question_id: " + ", ".join(traces_without_ids))
    if duplicate_result_ids:
        issues.append(
            "duplicate results for question IDs: " + ", ".join(duplicate_result_ids)
        )
    if unexpected_result_ids:
        issues.append("unexpected question IDs: " + ", ".join(unexpected_result_ids))
    if missing_result_ids:
        issues.append("missing question results: " + ", ".join(missing_result_ids))
    if issues:
        raise EvaluationResultSetError("Invalid evaluation result set: " + "; ".join(issues))

    trace_by_question_id = {
        trace.question.question_id: trace
        for trace in traces
        if trace.question.question_id is not None
    }
    return [
        (question, trace_by_question_id[question.question_id])
        for question in questions
        if question.question_id is not None
    ]


def _retrieval_scored_pairs(
    questions: Sequence[Question],
    traces: Sequence[QueryTrace],
) -> list[tuple[Question, QueryTrace]]:
    return [
        (question, trace)
        for question, trace in _matched_questions_and_traces(questions, traces)
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
