from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import rag_quality_lab.cli as cli
from rag_quality_lab.cli import app
from rag_quality_lab.schemas import (
    EvaluationArtifactPaths,
    EvaluationMetricCount,
    EvaluationMetrics,
    EvaluationQuestionResult,
    EvaluationRun,
)


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_eval_run_json_reports_metrics_and_artifact_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    golden_path = tmp_path / "golden" / "questions.json"
    artifacts_dir = tmp_path / "eval"
    json_path = artifacts_dir / "eval-routed-vector.json"
    markdown_path = artifacts_dir / "eval-routed-vector.md"
    evaluation = sample_evaluation_run(
        mode="routed-vector",
        golden_path=golden_path,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    def fake_run_eval(
        *,
        mode: str,
        golden: Path,
        artifacts_dir: Path,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
    ) -> EvaluationRun:
        captured.update(
            {
                "mode": mode,
                "golden": golden,
                "artifacts_dir": artifacts_dir,
                "top_k": top_k,
                "max_context_tokens": max_context_tokens,
                "output_token_limit": output_token_limit,
            }
        )
        return evaluation

    monkeypatch.setattr(cli, "run_eval", fake_run_eval, raising=False)

    result = runner.invoke(
        app,
        [
            "eval",
            "run",
            "--mode",
            "routed-vector",
            "--golden",
            str(golden_path),
            "--artifacts-dir",
            str(artifacts_dir),
            "--top-k",
            "4",
            "--max-context-tokens",
            "700",
            "--output-token-limit",
            "120",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert captured == {
        "mode": "routed-vector",
        "golden": golden_path,
        "artifacts_dir": artifacts_dir,
        "top_k": 4,
        "max_context_tokens": 700,
        "output_token_limit": 120,
    }

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert payload["run_id"] == "eval-routed-vector"
    assert payload["retrieval_mode"] == "routed-vector"
    assert payload["golden_set_path"] == str(golden_path)
    assert payload["question_count"] == 2
    assert set(payload["metrics"]) == {
        "routing_accuracy",
        "average_searched_categories",
        "hit_rate_at_k",
        "mrr",
        "citation_source_match",
        "no_answer_accuracy",
        "average_context_tokens",
        "average_included_chunks",
    }
    assert payload["metrics"]["routing_accuracy"] == 0.5
    assert payload["metrics"]["hit_rate_at_k"] == 0.75
    assert payload["metrics"]["mrr"] == 0.625
    assert payload["metrics"]["citation_source_match"] == 1.0
    assert payload["metrics"]["no_answer_accuracy"] == 1.0
    assert payload["metrics"]["average_context_tokens"] == 420.0
    assert payload["metrics"]["average_included_chunks"] == 3.0
    assert payload["json_path"] == str(json_path)
    assert payload["markdown_path"] == str(markdown_path)
    assert payload["trace_paths"] == [
        str(artifacts_dir / "traces" / "trace-001.json"),
        str(artifacts_dir / "traces" / "trace-002.json"),
    ]


def test_eval_run_human_output_reports_summary_and_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    artifacts_dir = tmp_path / "eval"
    evaluation = sample_evaluation_run(
        mode="baseline-vector",
        golden_path=tmp_path / "golden" / "questions.json",
        json_path=artifacts_dir / "eval-baseline-vector.json",
        markdown_path=artifacts_dir / "eval-baseline-vector.md",
    )

    def fake_run_eval(
        *,
        mode: str,
        golden: Path,
        artifacts_dir: Path,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
    ) -> EvaluationRun:
        captured.update(
            {
                "top_k": top_k,
                "max_context_tokens": max_context_tokens,
                "output_token_limit": output_token_limit,
            }
        )
        return evaluation

    monkeypatch.setattr(cli, "run_eval", fake_run_eval, raising=False)

    result = runner.invoke(
        app,
        [
            "eval",
            "run",
            "--mode",
            "baseline-vector",
            "--artifacts-dir",
            str(artifacts_dir),
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert captured == {
        "top_k": 3,
        "max_context_tokens": 1000,
        "output_token_limit": 800,
    }
    assert "Evaluation: eval-baseline-vector" in result.stdout
    assert "Mode: baseline-vector" in result.stdout
    assert "Questions: 2" in result.stdout
    assert "routing_accuracy: 1/2 questions, 50.0%" in result.stdout
    assert "hit_rate_at_k: 3/4 questions, 75.0%" in result.stdout
    assert "Scope: These results are evidence from a small, manually curated benchmark" in result.stdout
    assert f"JSON: {artifacts_dir / 'eval-baseline-vector.json'}" in result.stdout
    assert f"Markdown: {artifacts_dir / 'eval-baseline-vector.md'}" in result.stdout


def test_eval_run_unsupported_optional_mode_reports_error() -> None:
    result = runner.invoke(
        app,
        [
            "eval",
            "run",
            "--mode",
            "hybrid-vector",
            "--json",
        ],
    )

    assert result.exit_code != 0
    assert "unsupported" in result.stderr.lower()
    assert "hybrid-vector" in result.stderr


def sample_evaluation_run(
    *,
    mode: str,
    golden_path: Path,
    json_path: Path,
    markdown_path: Path,
) -> EvaluationRun:
    artifacts_dir = json_path.parent
    trace_paths = [
        artifacts_dir / "traces" / "trace-001.json",
        artifacts_dir / "traces" / "trace-002.json",
    ]
    return EvaluationRun(
        run_id=f"eval-{mode}",
        retrieval_mode=mode,
        golden_set_path=golden_path,
        configuration={
            "top_k": 4,
            "max_context_tokens": 700,
            "output_token_limit": 120,
        },
        metrics=EvaluationMetrics(
            routing_accuracy=0.5,
            hit_rate_at_k=0.75,
            mrr=0.625,
            citation_source_match=1.0,
            no_answer_accuracy=1.0,
            average_context_tokens=420.0,
            average_included_chunks=3.0,
        ),
        metric_counts={
            "routing_accuracy": EvaluationMetricCount(numerator=1, denominator=2),
            "hit_rate_at_k": EvaluationMetricCount(numerator=3, denominator=4),
            "citation_source_match": EvaluationMetricCount(numerator=4, denominator=4),
            "no_answer_accuracy": EvaluationMetricCount(numerator=2, denominator=2),
        },
        questions=[
            EvaluationQuestionResult(
                question_id="q-001",
                question_text="How does RAG ground answers?",
                case_type="answerable",
                trace_path=trace_paths[0],
                metrics={"hit_rate_at_k": 1.0, "mrr": 1.0},
                expected_relevant_sources=["source-02"],
                retrieved_sources=["source-02"],
            ),
            EvaluationQuestionResult(
                question_id="q-002",
                question_text="What warranty is provided?",
                case_type="no_answer",
                trace_path=trace_paths[1],
                metrics={"no_answer_accuracy": 1.0},
            ),
        ],
        trace_paths=trace_paths,
        artifact_paths=EvaluationArtifactPaths(
            json_path=json_path,
            markdown_path=markdown_path,
        ),
    )
