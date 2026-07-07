from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.providers import ChatResponse, TokenUsage
from rag_quality_lab.routing.categories import REQUIRED_CATEGORIES
from rag_quality_lab.schemas import RetrievalResult, RouteDecision


pytestmark = pytest.mark.integration


def test_answerable_query_workflow_persists_valid_trace(tmp_path: Path) -> None:
    run_query, load_trace = _query_workflow_api()
    trace_dir = tmp_path / "traces"
    router = FakeRouter(high_confidence_route())
    retriever = FakeRetriever(
        [
            retrieval_result(
                "chunk-rag-1",
                rank=1,
                estimated_tokens=20,
                content="RAG grounds answers by using selected retrieved context.",
            ),
            retrieval_result(
                "chunk-rag-oversized",
                rank=2,
                estimated_tokens=200,
                content="This chunk is too large for the configured context budget.",
            ),
        ]
    )
    chat_provider = FakeChatProvider(
        "RAG grounds answers by using selected retrieved context. [chunk-rag-1]"
    )

    result = run_query(
        "How does RAG ground answers in context?",
        mode="routed-vector",
        top_k=2,
        max_context_tokens=80,
        output_token_limit=100,
        trace_dir=trace_dir,
        router=router,
        retriever=retriever,
        chat_provider=chat_provider,
    )

    trace = result["trace"]
    trace_path = Path(result["trace_path"])
    loaded_trace = load_trace(trace_path)

    assert trace_path.parent == trace_dir
    assert trace_path.exists()
    assert loaded_trace.trace_id == trace.trace_id
    assert loaded_trace.answer_result == trace.answer_result
    assert loaded_trace.citation_validation == trace.citation_validation

    assert trace.question.text == "How does RAG ground answers in context?"
    assert trace.retrieval_mode == "routed-vector"
    assert trace.route_decision.selected_category == "RAG and context handling"
    assert trace.route_decision.fallback_all_categories is False
    assert [result.chunk_id for result in trace.retrieval_results] == [
        "chunk-rag-1",
        "chunk-rag-oversized",
    ]
    assert [chunk.chunk_id for chunk in trace.context_build.included_chunks] == ["chunk-rag-1"]
    assert [(chunk.chunk_id, chunk.reason) for chunk in trace.context_build.excluded_chunks] == [
        ("chunk-rag-oversized", "budget_exceeded")
    ]
    assert trace.context_build.max_context_tokens == 80
    assert trace.context_build.output_token_limit == 100
    assert trace.answer_result.is_no_answer is False
    assert trace.answer_result.citations == ["chunk-rag-1"]
    assert trace.answer_result.validation_status == "valid"
    assert trace.citation_validation.status == "valid"
    assert trace.citation_validation.cited_chunk_ids == ["chunk-rag-1"]
    assert trace.model_usage is not None
    assert trace.model_usage.total_tokens == 29
    assert trace.model_usage.deployment == "chat-test"

    assert router.questions == ["How does RAG ground answers in context?"]
    assert retriever.calls == [
        {
            "question": "How does RAG ground answers in context?",
            "mode": "routed-vector",
            "top_k": 2,
            "route_decision": high_confidence_route(),
        }
    ]
    assert chat_provider.calls[0]["max_tokens"] == 100


def test_no_answer_query_workflow_persists_not_applicable_citation_trace(
    tmp_path: Path,
) -> None:
    run_query, load_trace = _query_workflow_api()
    trace_dir = tmp_path / "traces"
    router = FakeRouter(fallback_route())
    retriever = FakeRetriever(
        [
            retrieval_result(
                "chunk-scope-1",
                rank=1,
                estimated_tokens=18,
                content="The lab documents local evaluation workflows, not warranties.",
            )
        ]
    )
    chat_provider = FakeChatProvider(
        "I do not have enough evidence in the selected context to answer."
    )

    result = run_query(
        "What warranty does the project provide for enterprise production deployment?",
        mode="routed-vector",
        top_k=3,
        max_context_tokens=100,
        output_token_limit=80,
        trace_dir=trace_dir,
        router=router,
        retriever=retriever,
        chat_provider=chat_provider,
    )

    trace = result["trace"]
    trace_path = Path(result["trace_path"])
    loaded_trace = load_trace(trace_path)

    assert trace_path.exists()
    assert loaded_trace.trace_id == trace.trace_id
    assert loaded_trace.answer_result == trace.answer_result
    assert trace.question.answerability == "answerable"
    assert trace.route_decision.fallback_all_categories is True
    assert trace.route_decision.selected_category is None
    assert [result.chunk_id for result in trace.retrieval_results] == ["chunk-scope-1"]
    assert [chunk.chunk_id for chunk in trace.context_build.included_chunks] == ["chunk-scope-1"]
    assert trace.answer_result.is_no_answer is True
    assert trace.answer_result.citations == []
    assert trace.answer_result.validation_status == "not_applicable"
    assert trace.citation_validation.status == "not_applicable"
    assert trace.citation_validation.cited_chunk_ids == []
    assert trace.citation_validation.invalid_citations == []
    assert trace.model_usage is not None
    assert trace.model_usage.input_tokens == 20
    assert trace.model_usage.output_tokens == 9


class FakeRouter:
    def __init__(self, decision: RouteDecision) -> None:
        self.decision = decision
        self.questions: list[str] = []

    def route(self, question: str) -> RouteDecision:
        self.questions.append(question)
        return self.decision


class FakeRetriever:
    def __init__(self, results: list[RetrievalResult]) -> None:
        self.results = results
        self.calls: list[dict[str, Any]] = []

    def retrieve(
        self,
        *,
        question: str,
        mode: str,
        top_k: int,
        route_decision: RouteDecision,
    ) -> list[RetrievalResult]:
        self.calls.append(
            {
                "question": question,
                "mode": mode,
                "top_k": top_k,
                "route_decision": route_decision,
            }
        )
        return self.results[:top_k]


class FakeChatProvider:
    deployment = "chat-test"

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        self.calls.append(
            {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return ChatResponse(
            content=self.content,
            model="gpt-test",
            usage=TokenUsage(input_tokens=20, output_tokens=9, total_tokens=29),
        )


def high_confidence_route() -> RouteDecision:
    scores = {category.name: 0.02 for category in REQUIRED_CATEGORIES}
    scores["RAG and context handling"] = 0.87
    return RouteDecision(
        selected_category="RAG and context handling",
        fallback_all_categories=False,
        confidence=0.87,
        threshold=0.5,
        category_scores=scores,
    )


def fallback_route() -> RouteDecision:
    return RouteDecision(
        selected_category=None,
        fallback_all_categories=True,
        confidence=0.31,
        threshold=0.5,
        category_scores={category.name: 0.31 for category in REQUIRED_CATEGORIES},
    )


def retrieval_result(
    chunk_id: str,
    *,
    rank: int,
    estimated_tokens: int,
    content: str,
) -> RetrievalResult:
    return RetrievalResult(
        mode="routed-vector",
        rank=rank,
        chunk_id=chunk_id,
        source_slug=f"source-{rank}",
        category="RAG and context handling",
        score=1.0 - (rank / 10),
        estimated_tokens=estimated_tokens,
        content=content,
    )


def _query_workflow_api() -> tuple[Any, Any]:
    from rag_quality_lab.rag.pipeline import run_query
    from rag_quality_lab.rag.traces import load_trace

    return run_query, load_trace
