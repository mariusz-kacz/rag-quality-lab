from __future__ import annotations

from pathlib import Path

import pytest

from rag_quality_lab.schemas import (
    EvaluationMetrics,
    EvaluationRun,
    write_json_artifact,
)


pytestmark = pytest.mark.unit


def test_compare_evaluation_artifacts_builds_metric_and_token_budget_tables(
    tmp_path: Path,
) -> None:
    from rag_quality_lab.eval.reports import compare_evaluation_artifacts

    baseline_path = _write_run(
        tmp_path / "eval-baseline-vector.json",
        mode="baseline-vector",
        metrics=EvaluationMetrics(
            routing_accuracy=None,
            fallback_rate=0.2,
            recall_at_k=0.5,
            mrr=0.4,
            citation_source_match=0.75,
            no_answer_accuracy=1.0,
            average_context_tokens=300.0,
            average_included_chunks=2.0,
        ),
    )
    routed_path = _write_run(
        tmp_path / "eval-routed-vector.json",
        mode="routed-vector",
        metrics=EvaluationMetrics(
            routing_accuracy=0.8,
            fallback_rate=0.1,
            recall_at_k=0.75,
            mrr=0.6,
            citation_source_match=0.75,
            no_answer_accuracy=1.0,
            average_context_tokens=420.0,
            average_included_chunks=3.0,
        ),
    )

    comparison = compare_evaluation_artifacts([baseline_path, routed_path])

    assert comparison["schema_version"] == "1.0"
    assert comparison["artifact_paths"] == [str(baseline_path), str(routed_path)]
    assert comparison["markdown_path"] is None
    assert _row(comparison, "recall_at_k") == {
        "metric": "recall_at_k",
        "values": {
            "baseline-vector": 0.5,
            "routed-vector": 0.75,
        },
        "best_mode": "routed-vector",
    }
    assert _row(comparison, "fallback_rate")["best_mode"] == "routed-vector"
    assert _row(comparison, "citation_source_match")["best_mode"] == "tie"
    assert comparison["token_budget"]["average_context_tokens"] == {
        "metric": "average_context_tokens",
        "values": {
            "baseline-vector": 300.0,
            "routed-vector": 420.0,
        },
        "best_mode": "baseline-vector",
    }


def test_compare_evaluation_artifacts_writes_markdown_report(tmp_path: Path) -> None:
    from rag_quality_lab.eval.reports import compare_evaluation_artifacts

    artifact_path = _write_run(
        tmp_path / "eval-baseline-vector.json",
        mode="baseline-vector",
        metrics=EvaluationMetrics(
            routing_accuracy=1.0,
            fallback_rate=0.0,
            recall_at_k=1.0,
            mrr=1.0,
            citation_source_match=1.0,
            no_answer_accuracy=1.0,
            average_context_tokens=250.0,
            average_included_chunks=2.0,
        ),
    )
    markdown_path = tmp_path / "comparison.md"

    comparison = compare_evaluation_artifacts([artifact_path], markdown=markdown_path)

    assert comparison["markdown_path"] == str(markdown_path)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Evaluation comparison" in markdown
    assert "## Metric comparison" in markdown
    assert "## Token-budget diagnostics" in markdown
    assert "baseline-vector" in markdown
    assert "recall_at_k" in markdown


def test_compare_evaluation_artifacts_rejects_duplicate_modes(tmp_path: Path) -> None:
    from rag_quality_lab.eval.reports import (
        EvaluationRunError,
        compare_evaluation_artifacts,
    )

    first_path = _write_run(
        tmp_path / "eval-baseline-vector-a.json",
        mode="baseline-vector",
        metrics=EvaluationMetrics(recall_at_k=0.5),
    )
    second_path = _write_run(
        tmp_path / "eval-baseline-vector-b.json",
        mode="baseline-vector",
        metrics=EvaluationMetrics(recall_at_k=0.75),
    )

    with pytest.raises(EvaluationRunError, match="Duplicate evaluation artifact"):
        compare_evaluation_artifacts([first_path, second_path])


def _write_run(path: Path, *, mode: str, metrics: EvaluationMetrics) -> Path:
    run = EvaluationRun(
        run_id=f"eval-{mode}",
        retrieval_mode=mode,
        golden_set_path=Path("golden/questions.json"),
        configuration={
            "top_k": 4,
            "max_context_tokens": 700,
            "output_token_limit": 120,
        },
        metrics=metrics,
    )
    return write_json_artifact(path, run)


def _row(comparison: dict[str, object], metric: str) -> dict[str, object]:
    rows = comparison["metrics"]
    assert isinstance(rows, list)
    for row in rows:
        assert isinstance(row, dict)
        if row["metric"] == metric:
            return row
    raise AssertionError(f"Metric row not found: {metric}")
