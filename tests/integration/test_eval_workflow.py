from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.schemas import (
    REQUIRED_EVALUATION_METRICS,
    REQUIRED_KNOWLEDGE_CATEGORIES,
    AnswerResult,
    CitationValidation,
    ContextChunk,
    ModelUsage,
    QueryTrace,
    Question,
    RetrievalMode,
    RetrievalResult,
    RouteDecision,
    SelectedContext,
)


pytestmark = pytest.mark.integration


REQUIRED_MARKDOWN_SECTIONS = (
    "Run summary",
    "Retrieval mode and configuration",
    "Aggregate metrics",
    "Per-question table",
    "Request-response pairs",
    "Token-budget diagnostics",
    "No-answer cases",
    "Citation validation failures",
    "Limitations and interpretation notes",
)


def test_baseline_vector_evaluation_writes_json_and_markdown_artifacts(
    tmp_path: Path,
    temporary_golden_file: Path,
) -> None:
    run = _run_evaluation(
        mode="baseline-vector",
        golden_path=temporary_golden_file,
        artifacts_dir=tmp_path / "artifacts" / "eval",
        trace_dir=tmp_path / "artifacts" / "traces" / "baseline-vector",
    )

    _assert_evaluation_artifacts(
        run=run,
        mode="baseline-vector",
        golden_path=temporary_golden_file,
    )


def test_routed_vector_evaluation_writes_json_and_markdown_artifacts(
    tmp_path: Path,
    temporary_golden_file: Path,
) -> None:
    run = _run_evaluation(
        mode="routed-vector",
        golden_path=temporary_golden_file,
        artifacts_dir=tmp_path / "artifacts" / "eval",
        trace_dir=tmp_path / "artifacts" / "traces" / "routed-vector",
    )

    _assert_evaluation_artifacts(
        run=run,
        mode="routed-vector",
        golden_path=temporary_golden_file,
    )


def _run_evaluation(
    *,
    mode: RetrievalMode,
    golden_path: Path,
    artifacts_dir: Path,
    trace_dir: Path,
) -> Any:
    from rag_quality_lab.eval.reports import run_evaluation

    query_runner = FakeEvaluationQueryRunner(trace_dir)
    return run_evaluation(
        mode=mode,
        golden_path=golden_path,
        artifacts_dir=artifacts_dir,
        top_k=3,
        max_context_tokens=500,
        output_token_limit=120,
        query_runner=query_runner,
    )


def _assert_evaluation_artifacts(
    *,
    run: Any,
    mode: RetrievalMode,
    golden_path: Path,
) -> None:
    assert run.retrieval_mode == mode
    assert run.artifact_paths is not None

    json_path = Path(run.artifact_paths.json_path)
    markdown_path = Path(run.artifact_paths.markdown_path)

    assert json_path.exists()
    assert markdown_path.exists()
    assert json_path.parent == markdown_path.parent

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert set(payload) >= {
        "schema_version",
        "run_id",
        "created_at",
        "retrieval_mode",
        "golden_set_path",
        "configuration",
        "metrics",
        "questions",
        "trace_paths",
    }
    assert payload["retrieval_mode"] == mode
    assert Path(payload["golden_set_path"]) == golden_path
    assert payload["configuration"] == {
        "top_k": 3,
        "max_context_tokens": 500,
        "output_token_limit": 120,
        "router_category_margin": 0.15,
    }

    assert set(REQUIRED_EVALUATION_METRICS) <= set(payload["metrics"])
    if mode == "baseline-vector":
        assert payload["metrics"]["routing_accuracy"] is None
        assert all(
            question["metrics"]["routing_accuracy"] is None
            for question in payload["questions"]
        )
    else:
        assert payload["metrics"]["routing_accuracy"] is not None
    assert len(payload["questions"]) == 12
    assert len(payload["trace_paths"]) == 12
    assert {question["case_type"] for question in payload["questions"]} >= {
        "answerable",
        "no_answer",
        "ambiguous_boundary",
        "multi_category_routing",
        "fallback_routing",
    }
    assert all("answer_text" in question for question in payload["questions"])
    assert all("is_no_answer" in question for question in payload["questions"])
    fallback_results = [
        question
        for question in payload["questions"]
        if question["case_type"] == "fallback_routing"
    ]
    assert all(
        question["global_fallback_occurred"] is (mode == "routed-vector")
        for question in fallback_results
    )
    assert all(
        set(question["searched_categories"]) == set(REQUIRED_KNOWLEDGE_CATEGORIES)
        for question in fallback_results
    )

    trace_paths = [Path(path) for path in payload["trace_paths"]]
    assert all(path.exists() for path in trace_paths)
    serialized_traces = [
        json.loads(path.read_text(encoding="utf-8")) for path in trace_paths
    ]
    if mode == "baseline-vector":
        assert all(trace["route_decision"] is None for trace in serialized_traces)
    else:
        assert all(trace["route_decision"] is not None for trace in serialized_traces)
    assert {
        Path(question["trace_path"]) for question in payload["questions"]
    } == set(trace_paths)

    markdown = markdown_path.read_text(encoding="utf-8")
    normalized_markdown = markdown.lower()
    for section in REQUIRED_MARKDOWN_SECTIONS:
        assert section.lower() in normalized_markdown
    assert mode in markdown
    assert str(json_path) in markdown
    assert "The selected context supports the answer." in markdown


class FakeEvaluationQueryRunner:
    def __init__(self, trace_dir: Path) -> None:
        self.trace_dir = trace_dir
        self.calls: list[dict[str, Any]] = []

    def __call__(
        self,
        question: Question | str,
        *,
        mode: RetrievalMode,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
        trace_dir: Path | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        golden_question = question if isinstance(question, Question) else Question(text=question)
        trace_directory = trace_dir or self.trace_dir
        trace_directory.mkdir(parents=True, exist_ok=True)

        self.calls.append(
            {
                "question": golden_question.text,
                "mode": mode,
                "top_k": top_k,
                "max_context_tokens": max_context_tokens,
                "output_token_limit": output_token_limit,
            }
        )

        trace = _trace_for_question(
            golden_question,
            mode=mode,
            ordinal=len(self.calls),
            top_k=top_k,
            max_context_tokens=max_context_tokens,
            output_token_limit=output_token_limit,
        )
        trace_path = trace_directory / f"{trace.trace_id}.json"
        trace_path.write_text(trace.model_dump_json(indent=2) + "\n", encoding="utf-8")

        return {"trace": trace, "trace_path": trace_path}


def _trace_for_question(
    question: Question,
    *,
    mode: RetrievalMode,
    ordinal: int,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
) -> QueryTrace:
    source_slug = (
        question.expected_relevant_sources[0]
        if question.expected_relevant_sources
        else f"unmatched-source-{ordinal:02d}"
    )
    chunk_id = f"{source_slug}:overview:0001"
    category = question.expected_category or "RAG and context handling"
    is_no_answer = question.answerability == "no_answer"
    route_decision = None if mode == "baseline-vector" else _route_decision(question)
    retrieval_results = [
        RetrievalResult(
            mode=mode,
            rank=rank,
            chunk_id=chunk_id if rank == 1 else f"distractor-{ordinal:02d}-{rank}",
            source_slug=source_slug if rank == 1 else f"distractor-source-{rank}",
            category=category,
            section_path=["Overview"],
            score=1.0 - (rank / 10),
            estimated_tokens=24 + rank,
            content=f"Retrieved context for {question.text}",
        )
        for rank in range(1, top_k + 1)
    ]
    included_chunks = [
        ContextChunk(
            chunk_id=result.chunk_id,
            source_slug=result.source_slug,
            category=result.category,
            section_path=result.section_path,
            retrieval_rank=result.rank,
            content=result.content or "Retrieved context.",
            estimated_tokens=result.estimated_tokens or 1,
        )
        for result in retrieval_results[:2]
    ]

    return QueryTrace(
        trace_id=f"trace-{mode}-{ordinal:02d}",
        question=question,
        retrieval_mode=mode,
        route_decision=route_decision,
        retrieval_results=retrieval_results,
        context_build=SelectedContext(
            max_context_tokens=max_context_tokens,
            output_token_limit=output_token_limit,
            included_chunks=included_chunks,
            excluded_chunks=[],
            final_estimated_context_tokens=sum(
                chunk.estimated_tokens for chunk in included_chunks
            ),
        ),
        answer_result=AnswerResult(
            answer_text=(
                "I do not have enough evidence in the selected context to answer."
                if is_no_answer
                else f"The selected context supports the answer. [{chunk_id}]"
            ),
            is_no_answer=is_no_answer,
            citations=[] if is_no_answer else [chunk_id],
            validation_status="not_applicable" if is_no_answer else "valid",
        ),
        citation_validation=CitationValidation(
            status="not_applicable" if is_no_answer else "valid",
            cited_chunk_ids=[] if is_no_answer else [chunk_id],
        ),
        model_usage=ModelUsage(
            input_tokens=100 + ordinal,
            output_tokens=20,
            total_tokens=120 + ordinal,
            model="gpt-test",
            deployment="chat-test",
        ),
    )


def _route_decision(question: Question) -> RouteDecision:
    scores = {category: 0.05 for category in REQUIRED_KNOWLEDGE_CATEGORIES}
    if question.case_type == "fallback_routing":
        return RouteDecision(
            selected_category=None,
            fallback_all_categories=True,
            confidence=0.24,
            threshold=0.5,
            category_scores={category: 0.24 for category in REQUIRED_KNOWLEDGE_CATEGORIES},
        )

    if question.case_type == "multi_category_routing":
        selected_category = question.expected_searched_categories[0]
        for category in question.expected_searched_categories:
            scores[category] = 0.75
        scores[selected_category] = 0.86
        return RouteDecision(
            selected_category=selected_category,
            fallback_all_categories=False,
            confidence=0.86,
            threshold=0.5,
            category_scores=scores,
        )

    selected_category = question.expected_category or "RAG and context handling"
    scores[selected_category] = 0.86
    return RouteDecision(
        selected_category=selected_category,
        fallback_all_categories=False,
        confidence=0.86,
        threshold=0.5,
        category_scores=scores,
    )
