from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
import pytest

from rag_quality_lab.rag.pipeline import QueryRetrievalResult
from rag_quality_lab.routing.categories import REQUIRED_CATEGORIES
from rag_quality_lab.schemas import Question, RetrievalResult, RouteDecision


pytestmark = pytest.mark.integration


def test_reranking_requests_twenty_candidates_and_generates_from_three(tmp_path: Path):
    from rag_quality_lab.schemas.retrieval import RerankingResult, RerankedChunk

    run_query, load_trace = _query_workflow_api()
    candidates = [
        retrieval_result(
            f"c{i}",
            rank=i,
            estimated_tokens=200,
            content=f"Evidence {i}",
            mode="baseline-vector",
        )
        for i in range(1, 21)
    ]
    retriever = FakeRetriever(candidates)

    class ReverseReranker:
        def rerank(self, question, candidates):
            assert question == "Which evidence?"
            return RerankingResult(
                model="test-cross-encoder",
                elapsed_ms=5,
                results=[
                    RerankedChunk(
                        chunk_id=c.chunk_id,
                        retrieval_rank=c.rank,
                        rank=i,
                        score=float(21 - i),
                    )
                    for i, c in enumerate(reversed(candidates), 1)
                ],
            )

    result = run_query(
        "Which evidence?",
        mode="baseline-vector",
        top_k=3,
        max_context_tokens=1000,
        output_token_limit=500,
        trace_dir=tmp_path,
        retriever=retriever,
        chat_model=FakeChatModel("Evidence 20. [C1]"),
        rerank_enabled=True,
        candidate_k=20,
        reranker=ReverseReranker(),
    )
    trace = load_trace(result["trace_path"])
    assert retriever.calls[0]["top_k"] == 20
    assert [r.chunk_id for r in trace.retrieval_results] == [
        f"c{i}" for i in range(1, 21)
    ]
    assert trace.reranking.model == "test-cross-encoder"
    assert [c.chunk_id for c in trace.context_build.included_chunks] == [
        "c20",
        "c19",
        "c18",
    ]
    assert [c.retrieval_rank for c in trace.context_build.included_chunks] == [
        20,
        19,
        18,
    ]
    assert len(trace.context_build.excluded_chunks) == 17
    assert trace.context_build.final_estimated_context_tokens == 600
    assert trace.answer_result.citations == ["c20"]
    assert trace.citation_validation.status == "valid"


def test_baseline_query_bypasses_router_and_serializes_routing_as_not_applicable(
    tmp_path: Path,
) -> None:
    run_query, load_trace = _query_workflow_api()
    router = FakeRouter(high_confidence_route())
    retriever = FakeRetriever(
        [
            retrieval_result(
                "chunk-global-1",
                rank=1,
                estimated_tokens=20,
                content="Global retrieval returns this context.",
                mode="baseline-vector",
            )
        ]
    )

    result = run_query(
        "Which context is found globally?",
        mode="baseline-vector",
        top_k=1,
        max_context_tokens=80,
        output_token_limit=100,
        trace_dir=tmp_path / "traces",
        router=router,
        retriever=retriever,
        chat_model=FakeChatModel("Global retrieval found the context. [C1]"),
    )

    trace = result["trace"]
    trace_path = Path(result["trace_path"])
    loaded_trace = load_trace(trace_path)
    serialized_trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert router.questions == []
    assert trace.route_decision is None
    assert loaded_trace.route_decision is None
    assert serialized_trace["route_decision"] is None
    assert retriever.calls == [
        {
            "question": "Which context is found globally?",
            "mode": "baseline-vector",
            "top_k": 1,
            "route_decision": None,
        }
    ]
    assert trace.retrieval_results[0].mode == "baseline-vector"


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
    chat_model = FakeChatModel(
        "RAG grounds answers by using selected retrieved context. [C1]"
    )

    result = run_query(
        Question(
            question_id="q-rag-grounding",
            text="How does RAG ground answers in context?",
        ),
        mode="routed-vector",
        top_k=2,
        max_context_tokens=80,
        output_token_limit=100,
        trace_dir=trace_dir,
        router=router,
        retriever=retriever,
        chat_model=chat_model,
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
    assert trace.question.question_id == "q-rag-grounding"
    assert trace.retrieval_mode == "routed-vector"
    assert trace.route_decision.selected_category == "RAG and context handling"
    assert trace.route_decision.fallback_all_categories is False
    assert [result.chunk_id for result in trace.retrieval_results] == [
        "chunk-rag-1",
        "chunk-rag-oversized",
    ]
    assert [chunk.chunk_id for chunk in trace.context_build.included_chunks] == [
        "chunk-rag-1"
    ]
    assert [
        (chunk.chunk_id, chunk.reason) for chunk in trace.context_build.excluded_chunks
    ] == [("chunk-rag-oversized", "budget_exceeded")]
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
    assert chat_model.calls[0]["max_tokens"] == 100


@pytest.mark.parametrize("refusal_only", [True, False])
def test_no_answer_query_workflow_persists_validation(
    tmp_path: Path,
    refusal_only: bool,
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
    response = "There is not enough evidence in the selected context to answer."
    if not refusal_only:
        response += " However, the warranty is ten years. [C999]"
    chat_model = FakeChatModel(response)
    question = Question(
        question_id="q-warranty",
        text="What warranty does the project provide for enterprise production deployment?",
        answerability="no_answer",
        case_type="no_answer",
    )

    result = run_query(
        question,
        mode="routed-vector",
        top_k=3,
        max_context_tokens=100,
        output_token_limit=80,
        trace_dir=trace_dir,
        router=router,
        retriever=retriever,
        chat_model=chat_model,
    )

    trace = result["trace"]
    trace_path = Path(result["trace_path"])
    loaded_trace = load_trace(trace_path)

    assert trace_path.exists()
    assert loaded_trace.trace_id == trace.trace_id
    assert loaded_trace.answer_result == trace.answer_result
    assert trace.question == question
    assert trace.route_decision.fallback_all_categories is True
    assert trace.route_decision.selected_category is None
    assert [result.chunk_id for result in trace.retrieval_results] == ["chunk-scope-1"]
    assert [chunk.chunk_id for chunk in trace.context_build.included_chunks] == [
        "chunk-scope-1"
    ]
    assert loaded_trace.answer_result.answer_text == response
    assert loaded_trace.answer_result.is_no_answer is refusal_only
    citations = [] if refusal_only else ["C999"]
    assert loaded_trace.answer_result.citations == citations
    status = "not_applicable" if refusal_only else "invalid"
    assert loaded_trace.answer_result.validation_status == status
    assert loaded_trace.citation_validation.status == status
    assert loaded_trace.citation_validation.cited_chunk_ids == citations
    assert loaded_trace.citation_validation.invalid_citations == citations
    errors = (
        []
        if refusal_only
        else ["Citation C999 from answer text not found in selected context"]
    )
    assert loaded_trace.answer_result.validation_errors == errors
    assert loaded_trace.citation_validation.validation_errors == errors
    assert trace.model_usage is not None
    assert trace.model_usage.input_tokens == 20
    assert trace.model_usage.output_tokens == 9


class FakeRouter:
    def close(self) -> None:
        pytest.fail("The query must not close an injected router")

    def __init__(self, decision: RouteDecision) -> None:
        self.decision = decision
        self.questions: list[str] = []

    def route(self, question: str) -> RouteDecision:
        self.questions.append(question)
        return self.decision


class FakeRetriever:
    def close(self) -> None:
        pytest.fail("The query must not close an injected retriever")

    def __init__(self, results: list[RetrievalResult]) -> None:
        self.results = results
        self.calls: list[dict[str, Any]] = []

    def retrieve(
        self,
        *,
        question: str,
        mode: str,
        top_k: int,
        route_decision: RouteDecision | None,
    ) -> QueryRetrievalResult:
        self.calls.append(
            {
                "question": question,
                "mode": mode,
                "top_k": top_k,
                "route_decision": route_decision,
            }
        )
        categories = (
            [route_decision.selected_category]
            if route_decision is not None and not route_decision.fallback_all_categories
            else [category.name for category in REQUIRED_CATEGORIES]
        )
        return QueryRetrievalResult(self.results[:top_k], categories)


class FakeChatModel:
    deployment_name = "chat-test"

    def close(self) -> None:
        pytest.fail("The query must not close an injected chat model")

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict[str, Any]] = []

    def invoke(
        self,
        input: list[BaseMessage],
        config: Any | None = None,
        *,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        self.calls.append(
            {
                "messages": input,
                "config": config,
                "max_tokens": max_tokens,
                "kwargs": kwargs,
            }
        )
        return AIMessage(
            content=self.content,
            response_metadata={"model_name": "gpt-test"},
            usage_metadata={
                "input_tokens": 20,
                "output_tokens": 9,
                "total_tokens": 29,
            },
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
    mode: str = "routed-vector",
) -> RetrievalResult:
    return RetrievalResult(
        mode=mode,
        rank=rank,
        chunk_id=chunk_id,
        source_slug=f"source-{rank}",
        category="RAG and context handling",
        section_path=["Overview"],
        score=1.0 - (rank / 10),
        estimated_tokens=estimated_tokens,
        content=content,
    )


def _query_workflow_api() -> tuple[Any, Any]:
    from rag_quality_lab.rag.pipeline import run_query
    from rag_quality_lab.rag.traces import load_trace

    return run_query, load_trace
