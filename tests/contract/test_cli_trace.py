from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rag_quality_lab.cli import app


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_trace_inspect_json_outputs_trace_schema_fields(
    temporary_trace_file: Path,
) -> None:
    result = runner.invoke(
        app, ["trace", "inspect", str(temporary_trace_file), "--json"]
    )

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["schema_version"] == "1.0"
    assert payload["trace_id"] == "trace-test-001"
    assert payload["created_at"]
    assert payload["question"] == {
        "text": "How does RAG ground answers?",
        "question_id": None,
        "expected_category": None,
        "expected_relevant_sources": [],
        "answerability": "answerable",
        "case_type": "answerable",
    }
    assert payload["retrieval_mode"] == "routed-vector"
    assert payload["route_decision"]["selected_category"] == "RAG and context handling"
    assert payload["route_decision"]["fallback_all_categories"] is False
    assert set(payload["route_decision"]["category_scores"]) == {
        "prompting techniques",
        "RAG and context handling",
        "RAG evaluation and quality",
        "LLM security and risks",
        "LLM settings, cost, and tokens",
    }
    assert payload["retrieval_results"] == [
        {
            "mode": "routed-vector",
            "rank": 1,
            "chunk_id": "source-02:overview:0001",
            "source_slug": "source-02",
            "category": "RAG and context handling",
            "score": 0.91,
            "fusion_score": None,
            "estimated_tokens": 10,
            "content": "Retrieval augmented generation grounds answers in selected context.",
        }
    ]
    assert payload["context_build"]["max_context_tokens"] == 500
    assert payload["context_build"]["output_token_limit"] == 100
    assert payload["context_build"]["final_estimated_context_tokens"] == 10
    assert (
        payload["context_build"]["included_chunks"][0]["chunk_id"]
        == "source-02:overview:0001"
    )
    assert payload["context_build"]["excluded_chunks"] == []
    assert payload["answer_result"] == {
        "answer_text": "RAG grounds answers in selected context. [source-02:overview:0001]",
        "is_no_answer": False,
        "citations": ["source-02:overview:0001"],
        "validation_status": "valid",
        "validation_errors": [],
    }
    assert payload["citation_validation"] == {
        "status": "valid",
        "cited_chunk_ids": ["source-02:overview:0001"],
        "invalid_citations": [],
        "validation_errors": [],
    }
    assert payload["model_usage"] == {
        "input_tokens": 42,
        "output_tokens": 12,
        "total_tokens": 54,
        "model": "gpt-test",
        "deployment": "chat-test",
    }


def test_trace_inspect_human_output_reports_key_diagnostics(
    temporary_trace_file: Path,
) -> None:
    result = runner.invoke(app, ["trace", "inspect", str(temporary_trace_file)])

    assert result.exit_code == 0, result.stderr
    assert "Trace: trace-test-001" in result.stdout
    assert "Question: How does RAG ground answers?" in result.stdout
    assert "Mode: routed-vector" in result.stdout
    assert "Route: RAG and context handling" in result.stdout
    assert "Retrieved chunks: 1" in result.stdout
    assert "Included chunks: 1" in result.stdout
    assert "Excluded chunks: 0" in result.stdout
    assert "Citation validation: valid" in result.stdout
    assert "Model usage: 54 tokens" in result.stdout


def test_trace_inspect_missing_file_reports_artifact_error(tmp_path: Path) -> None:
    missing_trace = tmp_path / "missing-trace.json"

    result = runner.invoke(app, ["trace", "inspect", str(missing_trace), "--json"])

    assert result.exit_code != 0
    assert "artifact" in result.stderr.lower()
    assert str(missing_trace) in result.stderr
