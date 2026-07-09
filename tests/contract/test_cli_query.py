from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import rag_quality_lab.cli as cli
from rag_quality_lab.cli import app
from rag_quality_lab.schemas import QueryTrace


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_query_json_reports_answer_route_context_and_trace_path(
    monkeypatch: pytest.MonkeyPatch,
    sample_query_trace: QueryTrace,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    trace_path = tmp_path / "traces" / f"{sample_query_trace.trace_id}.json"

    def fake_run_query(
        question: str,
        *,
        mode: str,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
        trace_dir: Path,
    ) -> dict[str, Any]:
        captured.update(
            {
                "question": question,
                "mode": mode,
                "top_k": top_k,
                "max_context_tokens": max_context_tokens,
                "output_token_limit": output_token_limit,
                "trace_dir": trace_dir,
            }
        )
        return {
            "trace": sample_query_trace,
            "trace_path": trace_path,
        }

    monkeypatch.setattr(cli, "run_query", fake_run_query, raising=False)

    result = runner.invoke(
        app,
        [
            "query",
            "How does RAG ground answers?",
            "--mode",
            "routed-vector",
            "--top-k",
            "6",
            "--max-context-tokens",
            "500",
            "--output-token-limit",
            "100",
            "--trace-dir",
            str(tmp_path / "traces"),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert captured == {
        "question": "How does RAG ground answers?",
        "mode": "routed-vector",
        "top_k": 6,
        "max_context_tokens": 500,
        "output_token_limit": 100,
        "trace_dir": tmp_path / "traces",
    }

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert payload["question"] == "How does RAG ground answers?"
    assert payload["retrieval_mode"] == "routed-vector"
    assert (
        payload["answer_text"]
        == "RAG grounds answers in selected context. [source-02:overview:0001]"
    )
    assert payload["is_no_answer"] is False
    assert payload["citations"] == ["source-02:overview:0001"]
    assert payload["validation_status"] == "valid"
    assert payload["route_decision"] == {
        "selected_category": "RAG and context handling",
        "fallback_all_categories": False,
        "confidence": 0.82,
        "threshold": 0.2,
        "category_scores": sample_query_trace.route_decision.category_scores,
    }
    assert payload["retrieval_result_count"] == 1
    assert payload["included_chunk_count"] == 1
    assert payload["excluded_chunk_count"] == 0
    assert payload["final_estimated_context_tokens"] == 10
    assert payload["output_token_limit"] == 100
    assert payload["trace_id"] == "trace-test-001"
    assert payload["trace_path"] == str(trace_path)


def test_query_human_output_reports_trace_path(
    monkeypatch: pytest.MonkeyPatch,
    sample_query_trace: QueryTrace,
    tmp_path: Path,
) -> None:
    trace_path = tmp_path / "traces" / f"{sample_query_trace.trace_id}.json"

    def fake_run_query(
        question: str,
        *,
        mode: str,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
        trace_dir: Path,
    ) -> dict[str, Any]:
        return {
            "trace": sample_query_trace,
            "trace_path": trace_path,
        }

    monkeypatch.setattr(cli, "run_query", fake_run_query, raising=False)

    result = runner.invoke(
        app,
        [
            "query",
            "How does RAG ground answers?",
            "--mode",
            "routed-vector",
            "--trace-dir",
            str(tmp_path / "traces"),
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert "RAG grounds answers in selected context." in result.stdout
    assert "Citations: source-02:overview:0001" in result.stdout
    assert "Mode: routed-vector" in result.stdout
    assert "Route: RAG and context handling" in result.stdout
    assert "Retrieved chunks: 1" in result.stdout
    assert "Included chunks: 1" in result.stdout
    assert "Excluded chunks: 0" in result.stdout
    assert f"Trace: {trace_path}" in result.stdout


def test_query_unsupported_mode_reports_error() -> None:
    result = runner.invoke(
        app,
        [
            "query",
            "How does RAG ground answers?",
            "--mode",
            "keyword-search",
            "--json",
        ],
    )

    assert result.exit_code != 0
    assert "unsupported" in result.stderr.lower()
    assert "keyword-search" in result.stderr
