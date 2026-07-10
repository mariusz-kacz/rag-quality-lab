from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import rag_quality_lab.cli as cli
from rag_quality_lab.cli import app


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_eval_compare_json_reports_metric_table_token_diagnostics_and_markdown_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    baseline_artifact = tmp_path / "eval" / "baseline-vector.json"
    routed_artifact = tmp_path / "eval" / "routed-vector.json"
    markdown_path = tmp_path / "eval" / "comparison.md"
    comparison = sample_comparison_result(
        artifact_paths=[baseline_artifact, routed_artifact],
        markdown_path=markdown_path,
    )

    def fake_compare_eval(
        *,
        artifact_paths: list[Path],
        markdown: Path | None,
    ) -> dict[str, Any]:
        captured.update(
            {
                "artifact_paths": artifact_paths,
                "markdown": markdown,
            }
        )
        return comparison

    monkeypatch.setattr(cli, "compare_eval", fake_compare_eval, raising=False)

    result = runner.invoke(
        app,
        [
            "eval",
            "compare",
            str(baseline_artifact),
            str(routed_artifact),
            "--markdown",
            str(markdown_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert captured == {
        "artifact_paths": [baseline_artifact, routed_artifact],
        "markdown": markdown_path,
    }

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert payload["artifact_paths"] == [
        str(baseline_artifact),
        str(routed_artifact),
    ]
    assert payload["markdown_path"] == str(markdown_path)
    assert payload["metrics"] == [
        {
            "metric": "hit_rate_at_k",
            "values": {
                "baseline-vector": 0.5,
                "routed-vector": 0.75,
            },
            "counts": {
                "baseline-vector": {"numerator": 2, "denominator": 4},
                "routed-vector": {"numerator": 3, "denominator": 4},
            },
            "included_benchmark_mode": "routed-vector",
        },
        {
            "metric": "mrr",
            "values": {
                "baseline-vector": 0.4,
                "routed-vector": 0.6,
            },
            "included_benchmark_mode": "routed-vector",
        },
        {
            "metric": "no_answer_accuracy",
            "values": {
                "baseline-vector": 1.0,
                "routed-vector": 1.0,
            },
            "included_benchmark_mode": "tie",
        },
    ]
    assert payload["token_budget"] == {
        "average_context_tokens": {
            "values": {
                "baseline-vector": 300.0,
                "routed-vector": 420.0,
            },
            "included_benchmark_mode": "baseline-vector",
        },
        "average_included_chunks": {
            "values": {
                "baseline-vector": 2.0,
                "routed-vector": 3.0,
            },
            "included_benchmark_mode": "baseline-vector",
        },
    }


def test_eval_compare_human_output_reports_metrics_and_markdown_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    baseline_artifact = tmp_path / "eval" / "baseline-vector.json"
    routed_artifact = tmp_path / "eval" / "routed-vector.json"
    markdown_path = tmp_path / "eval" / "comparison.md"

    def fake_compare_eval(
        *,
        artifact_paths: list[Path],
        markdown: Path | None,
    ) -> dict[str, Any]:
        return sample_comparison_result(
            artifact_paths=artifact_paths,
            markdown_path=markdown,
        )

    monkeypatch.setattr(cli, "compare_eval", fake_compare_eval, raising=False)

    result = runner.invoke(
        app,
        [
            "eval",
            "compare",
            str(baseline_artifact),
            str(routed_artifact),
            "--markdown",
            str(markdown_path),
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert "Evaluation comparison" in result.stdout
    assert "Artifacts: 2" in result.stdout
    assert (
        "hit_rate_at_k: baseline-vector=2/4 questions, 50.0%, "
        "routed-vector=3/4 questions, 75.0%, "
        "included-benchmark value=routed-vector"
    ) in result.stdout
    assert (
        "mrr: baseline-vector=0.4, routed-vector=0.6, "
        "included-benchmark value=routed-vector"
    ) in result.stdout
    assert (
        "average_context_tokens: baseline-vector=300.0, routed-vector=420.0, "
        "included-benchmark value=baseline-vector"
    ) in result.stdout
    assert f"Markdown: {markdown_path}" in result.stdout


def sample_comparison_result(
    *,
    artifact_paths: list[Path],
    markdown_path: Path | None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_paths": [str(path) for path in artifact_paths],
        "markdown_path": str(markdown_path) if markdown_path is not None else None,
        "metrics": [
            {
                "metric": "hit_rate_at_k",
                "values": {
                    "baseline-vector": 0.5,
                    "routed-vector": 0.75,
                },
                "counts": {
                    "baseline-vector": {"numerator": 2, "denominator": 4},
                    "routed-vector": {"numerator": 3, "denominator": 4},
                },
                "included_benchmark_mode": "routed-vector",
            },
            {
                "metric": "mrr",
                "values": {
                    "baseline-vector": 0.4,
                    "routed-vector": 0.6,
                },
                "included_benchmark_mode": "routed-vector",
            },
            {
                "metric": "no_answer_accuracy",
                "values": {
                    "baseline-vector": 1.0,
                    "routed-vector": 1.0,
                },
                "included_benchmark_mode": "tie",
            },
        ],
        "token_budget": {
            "average_context_tokens": {
                "values": {
                    "baseline-vector": 300.0,
                    "routed-vector": 420.0,
                },
                "included_benchmark_mode": "baseline-vector",
            },
            "average_included_chunks": {
                "values": {
                    "baseline-vector": 2.0,
                    "routed-vector": 3.0,
                },
                "included_benchmark_mode": "baseline-vector",
            },
        },
    }
