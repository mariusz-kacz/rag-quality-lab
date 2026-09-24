"""Scores reflect actual context, relevance labels, and missing evidence."""

import asyncio
import importlib.util
import json
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("ir_measures") is None, reason="requires eval extra"
)


@pytest.mark.parametrize(
    "case,faith_status,success_status,hit",
    [
        ("answer", "ok", "ok", 1),
        ("refusal", "not_applicable", "ok", 1),
        ("empty", "not_applicable", "ok", 0),
        ("no_answer", "not_applicable", "ok", None),
        ("failed", "not_run", "not_run", None),
        ("failed_no_answer", "not_applicable", "not_run", None),
        ("nonfinite", "error", "error", 1),
    ],
)
def test_metric_eligibility_and_exact_arguments(
    sample_query_trace, case, faith_status, success_status, hit
):
    from rag_quality_lab.eval.metrics import score_row

    data = sample_query_trace.model_dump()
    data["question"].update(
        question_id="q1",
        grading_notes="Explain the evidence without unsupported claims.",
        expected_relevant_sources=[data["retrieval_results"][0]["source_slug"]],
    )
    relevant = [data["retrieval_results"][0]["chunk_id"]]
    if "no_answer" in case:
        data["question"].update(
            answerability="no_answer",
            case_type="no_answer",
            expected_relevant_sources=[],
        )
        relevant = []
    if case == "refusal":
        data["answer_result"]["is_no_answer"] = True
    if case == "no_answer":
        # Judge eligibility and outcome do not depend on the phrase detector.
        data["answer_result"]["is_no_answer"] = False
        data["answer_result"]["answer_text"] = (
            "The available evidence cannot establish that."
        )
    if case == "empty":
        data["context_build"]["included_chunks"] = []
        data["retrieval_results"] = []
    trace = type(sample_query_trace).model_validate(data)
    failed = case.startswith("failed")
    row = {
        "question_id": "q1",
        "question": trace.question.model_dump(mode="json"),
        "error": "Query failed" if failed else None,
        "mode": "routed-vector",
        "settings": {"top_k": 3},
        "response": trace.answer_result.answer_text,
        "contexts": [c.content for c in trace.context_build.included_chunks],
        "ranked_ids": [r.chunk_id for r in trace.retrieval_results],
        "relevant_ids": relevant,
        "cited_ids": trace.citation_validation.cited_chunk_ids,
        "diagnostics": {}
        if failed
        else {
            "refused": trace.answer_result.is_no_answer,
            "route": trace.route_decision.model_dump(mode="json"),
        },
    }
    calls = []

    async def metric(*args):
        calls.append(args)
        return SimpleNamespace(value=float("nan") if case == "nonfinite" else -0.25)

    success_calls = []

    async def success(**kwargs):
        success_calls.append(kwargs)
        return SimpleNamespace(
            value="invalid"
            if case == "nonfinite"
            else "pass"
            if case == "no_answer"
            else "fail",
            reason="The decisive requirement.",
        )

    class Evaluator:
        llm = object()

        async def call(self, operation, *args, **kwargs):
            return await operation(*args, **kwargs)

    result = asyncio.run(score_row(row, success, metric, Evaluator()))
    scores = result["metrics"]
    assert scores["faithfulness"]["status"] == faith_status
    assert scores["answer_success"]["status"] == success_status
    assert scores["source_hit_at_k"]["value"] == hit
    if faith_status == "ok":
        assert calls[0] == (
            trace.question.text,
            trace.answer_result.answer_text,
            [c.content for c in trace.context_build.included_chunks],
        )
    if success_status == "ok":
        assert scores["answer_success"]["value"] == int(case == "no_answer")
        assert scores["answer_success"]["reason"] == "The decisive requirement."
        assert success_calls[0] == {
            "llm": Evaluator.llm,
            "question": trace.question.text,
            "answerability": trace.question.answerability,
            "grading_notes": trace.question.grading_notes,
            "response": trace.answer_result.answer_text,
            "contexts": json.dumps(row["contexts"], ensure_ascii=False),
        }
    assert "no_answer_accuracy" not in scores
    assert "routing_accuracy" not in scores
    assert "citation_source_match" not in scores
    if failed:
        assert not calls and not success_calls and result["diagnostics"] == {}


def test_retrieval_uses_chunk_ranking_including_unjudged_items():
    from rag_quality_lab.eval.metrics import retrieval_scores

    assert retrieval_scores("q", ["a", "b"], ["unjudged", "b", "a"], 3) == {
        "source_hit_at_k": 1.0,
        "source_mrr_at_k": 0.5,
    }
    assert retrieval_scores("q", ["a"], [], 3) == {
        "source_hit_at_k": 0.0,
        "source_mrr_at_k": 0.0,
    }
