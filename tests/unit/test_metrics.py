from __future__ import annotations

import pytest

from rag_quality_lab.schemas import (
    AnswerResult,
    CitationValidation,
    ContextChunk,
    ModelUsage,
    QueryTrace,
    Question,
    RetrievalResult,
    RouteDecision,
    SelectedContext,
)


pytestmark = pytest.mark.unit


def test_calculate_routing_accuracy_scores_expected_category_matches() -> None:
    from rag_quality_lab.eval.metrics import calculate_routing_accuracy

    questions = [
        question("q-1", expected_category="RAG and context handling"),
        question("q-2", expected_category="RAG evaluation and quality"),
        question("q-3", expected_category="LLM security and risks"),
        question("q-4", expected_category=None),
    ]
    traces = [
        trace("q-1", selected_category="RAG and context handling"),
        trace("q-2", selected_category="RAG and context handling"),
        trace("q-3", fallback_all_categories=True),
        trace("q-4", selected_category="prompting techniques"),
    ]

    assert calculate_routing_accuracy(questions, traces) == pytest.approx(1 / 3)


def test_calculate_fallback_rate_counts_all_category_routes() -> None:
    from rag_quality_lab.eval.metrics import calculate_fallback_rate

    traces = [
        trace("q-1", selected_category="RAG and context handling"),
        trace("q-2", fallback_all_categories=True),
        trace("q-3", selected_category="LLM security and risks"),
        trace("q-4", fallback_all_categories=True),
    ]

    assert calculate_fallback_rate(traces) == pytest.approx(0.5)


def test_fallback_count_and_average_searched_categories_are_distinct() -> None:
    from rag_quality_lab.eval.metrics import (
        calculate_average_searched_categories,
        calculate_fallback_count,
    )

    traces = [
        trace("q-1", selected_category="RAG and context handling"),
        trace("q-2", fallback_all_categories=True),
    ]

    assert calculate_fallback_count(traces) == 1
    assert calculate_average_searched_categories(
        traces,
        retrieval_mode="routed-vector",
        category_margin=0.0,
    ) == pytest.approx(3.0)


def test_calculate_hit_rate_at_k_returns_zero_when_no_expected_result_is_retrieved() -> None:
    from rag_quality_lab.eval.metrics import calculate_hit_rate_at_k

    questions = [question("q-1", expected_relevant_sources=["source-missing"])]
    traces = [
        trace("q-1", retrievals=[retrieval("chunk-a-1", "source-a", rank=1)])
    ]

    assert calculate_hit_rate_at_k(questions, traces) == 0.0


def test_calculate_hit_rate_at_k_returns_one_when_an_expected_chunk_is_retrieved() -> None:
    from rag_quality_lab.eval.metrics import calculate_hit_rate_at_k

    questions = [question("q-1", expected_relevant_sources=["chunk-b-1"])]
    traces = [
        trace(
            "q-1",
            retrievals=[
                retrieval("chunk-x-1", "source-x", rank=1),
                retrieval("chunk-b-1", "source-b", rank=2),
            ],
        )
    ]

    assert calculate_hit_rate_at_k(questions, traces) == 1.0


def test_calculate_hit_rate_at_k_returns_one_for_one_of_several_expected_sources() -> None:
    from rag_quality_lab.eval.metrics import calculate_hit_rate_at_k

    questions = [
        question(
            "q-1",
            expected_relevant_sources=["source-missing", "source-b", "source-other"],
        )
    ]
    traces = [
        trace("q-1", retrievals=[retrieval("chunk-b-1", "source-b", rank=1)])
    ]

    assert calculate_hit_rate_at_k(questions, traces) == 1.0


def test_calculate_mrr_uses_first_relevant_retrieval_rank() -> None:
    from rag_quality_lab.eval.metrics import calculate_mrr

    questions = [
        question("q-1", expected_relevant_sources=["source-a"]),
        question("q-2", expected_relevant_sources=["chunk-b-1"]),
        question("q-3", expected_relevant_sources=["source-missing"]),
    ]
    traces = [
        trace("q-1", retrievals=[retrieval("chunk-a-1", "source-a", rank=1)]),
        trace(
            "q-2",
            retrievals=[
                retrieval("chunk-x-1", "source-x", rank=1),
                retrieval("chunk-b-1", "source-b", rank=2),
            ],
        ),
        trace("q-3", retrievals=[retrieval("chunk-c-1", "source-c", rank=1)]),
    ]

    assert calculate_mrr(questions, traces) == pytest.approx(0.5)


def test_calculate_citation_source_match_scores_cited_context_sources() -> None:
    from rag_quality_lab.eval.metrics import calculate_citation_source_match

    questions = [
        question("q-1", expected_relevant_sources=["source-a"]),
        question("q-2", expected_relevant_sources=["source-b"]),
        no_answer_question("q-3"),
    ]
    traces = [
        trace(
            "q-1",
            included_chunks=[context_chunk("chunk-a-1", "source-a")],
            cited_chunk_ids=["chunk-a-1"],
        ),
        trace(
            "q-2",
            included_chunks=[context_chunk("chunk-x-1", "source-x")],
            cited_chunk_ids=["chunk-x-1"],
        ),
        trace(
            "q-3",
            included_chunks=[context_chunk("chunk-c-1", "source-c")],
            is_no_answer=True,
            cited_chunk_ids=[],
        ),
    ]

    assert calculate_citation_source_match(questions, traces) == pytest.approx(0.5)


def test_calculate_no_answer_accuracy_scores_answerability_matches() -> None:
    from rag_quality_lab.eval.metrics import calculate_no_answer_accuracy

    questions = [
        question("q-1", answerability="answerable"),
        no_answer_question("q-2"),
        no_answer_question("q-3"),
        question("q-4", answerability="answerable"),
    ]
    traces = [
        trace("q-1", is_no_answer=False),
        trace("q-2", is_no_answer=True),
        trace("q-3", is_no_answer=False),
        trace("q-4", is_no_answer=True),
    ]

    assert calculate_no_answer_accuracy(questions, traces) == pytest.approx(0.5)


def test_calculate_token_averages_reports_context_and_included_chunk_means() -> None:
    from rag_quality_lab.eval.metrics import calculate_token_averages

    traces = [
        trace(
            "q-1",
            included_chunks=[
                context_chunk("chunk-a-1", "source-a", estimated_tokens=40),
                context_chunk("chunk-a-2", "source-a", estimated_tokens=60),
            ],
            final_estimated_context_tokens=100,
        ),
        trace(
            "q-2",
            included_chunks=[
                context_chunk("chunk-b-1", "source-b", estimated_tokens=100),
                context_chunk("chunk-b-2", "source-b", estimated_tokens=100),
                context_chunk("chunk-b-3", "source-b", estimated_tokens=50),
                context_chunk("chunk-b-4", "source-b", estimated_tokens=50),
            ],
            final_estimated_context_tokens=300,
        ),
    ]

    averages = calculate_token_averages(traces)

    assert averages.average_context_tokens == pytest.approx(200.0)
    assert averages.average_included_chunks == pytest.approx(3.0)


def question(
    question_id: str,
    *,
    expected_category: str | None = "RAG and context handling",
    expected_relevant_sources: list[str] | None = None,
    answerability: str = "answerable",
) -> Question:
    return Question(
        question_id=question_id,
        text=f"Question {question_id}?",
        expected_category=expected_category,
        expected_relevant_sources=expected_relevant_sources or ["source-a"],
        answerability=answerability,
        case_type="answerable",
    )


def no_answer_question(question_id: str) -> Question:
    return Question(
        question_id=question_id,
        text=f"Question {question_id}?",
        expected_category="RAG evaluation and quality",
        expected_relevant_sources=[],
        answerability="no_answer",
        case_type="no_answer",
    )


def trace(
    trace_id: str,
    *,
    selected_category: str | None = "RAG and context handling",
    fallback_all_categories: bool = False,
    retrievals: list[RetrievalResult] | None = None,
    included_chunks: list[ContextChunk] | None = None,
    cited_chunk_ids: list[str] | None = None,
    is_no_answer: bool = False,
    final_estimated_context_tokens: int | None = None,
) -> QueryTrace:
    chunks = included_chunks or [context_chunk("chunk-a-1", "source-a")]
    citations = [] if is_no_answer else (cited_chunk_ids or [chunks[0].chunk_id])
    return QueryTrace(
        trace_id=f"trace-{trace_id}",
        question=Question(text=f"Question {trace_id}?"),
        retrieval_mode="routed-vector",
        route_decision=RouteDecision(
            selected_category=None if fallback_all_categories else selected_category,
            fallback_all_categories=fallback_all_categories,
            confidence=0.1 if fallback_all_categories else 0.9,
            threshold=0.2,
            category_scores={
                "prompting techniques": 0.1,
                "RAG and context handling": 0.9,
                "RAG evaluation and quality": 0.2,
                "LLM security and risks": 0.1,
                "LLM settings, cost, and tokens": 0.1,
            },
        ),
        retrieval_results=retrievals
        or [retrieval(chunks[0].chunk_id, chunks[0].source_slug, rank=1)],
        context_build=SelectedContext(
            max_context_tokens=1000,
            output_token_limit=500,
            included_chunks=chunks,
            excluded_chunks=[],
            final_estimated_context_tokens=(
                final_estimated_context_tokens
                if final_estimated_context_tokens is not None
                else sum(chunk.estimated_tokens for chunk in chunks)
            ),
        ),
        answer_result=AnswerResult(
            answer_text=(
                "There is not enough evidence in the selected context to answer."
                if is_no_answer
                else f"Answer. [{citations[0]}]"
            ),
            is_no_answer=is_no_answer,
            citations=citations,
            validation_status="not_applicable" if is_no_answer else "valid",
        ),
        citation_validation=CitationValidation(
            status="not_applicable" if is_no_answer else "valid",
            cited_chunk_ids=citations,
        ),
        model_usage=ModelUsage(input_tokens=20, output_tokens=10, total_tokens=30),
    )


def retrieval(chunk_id: str, source_slug: str, *, rank: int) -> RetrievalResult:
    return RetrievalResult(
        mode="routed-vector",
        rank=rank,
        chunk_id=chunk_id,
        source_slug=source_slug,
        category="RAG and context handling",
        section_path=["Overview"],
        score=1.0 - (rank / 10),
        estimated_tokens=25,
        content=f"Content for {chunk_id}.",
    )


def context_chunk(
    chunk_id: str,
    source_slug: str,
    *,
    estimated_tokens: int = 50,
) -> ContextChunk:
    return ContextChunk(
        chunk_id=chunk_id,
        source_slug=source_slug,
        category="RAG and context handling",
        section_path=["Overview"],
        retrieval_rank=1,
        content=f"Content for {chunk_id}.",
        estimated_tokens=estimated_tokens,
    )
