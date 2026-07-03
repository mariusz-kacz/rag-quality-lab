from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import rag_quality_lab.cli as cli
from rag_quality_lab.cli import app
from rag_quality_lab.config import MissingSettingError
from rag_quality_lab.schemas.artifacts import DEFAULT_SCHEMA_VERSION, IngestionSummaryArtifact
from rag_quality_lab.schemas.corpus import Chunk


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_corpus_ingest_json_reports_qdrant_ingestion_summary(
    monkeypatch: pytest.MonkeyPatch,
    temporary_corpus: dict[str, Path],
) -> None:
    monkeypatch.chdir(temporary_corpus["root"].parent)
    captured: dict[str, Any] = {}

    def fake_ingest_corpus(*, collection: str, recreate: bool) -> IngestionSummaryArtifact:
        captured["collection"] = collection
        captured["recreate"] = recreate
        chunk = Chunk(
            chunk_id="source-01:overview:0000:abc123",
            source_slug="source-01",
            category="prompting techniques",
            section_path=["Overview"],
            ordinal=0,
            content="Prompt engineering uses instructions and examples to shape model output.",
            content_hash="abc123",
            estimated_tokens=11,
            provenance={
                "url": "https://example.test/prompt-guide/source-01",
                "license": "MIT",
                "pinned_version": "dair-ai-prompt-guide@abc123",
                "local_ref": "corpus/sources/source-01.md",
            },
        )
        return IngestionSummaryArtifact(
            collection=collection,
            source_count=15,
            chunk_count=30,
            category_counts={
                "prompting techniques": 6,
                "RAG and context handling": 6,
                "RAG evaluation and quality": 6,
                "LLM security and risks": 6,
                "LLM settings, cost, and tokens": 6,
            },
            embedding_model="embedding-test",
            ingested_chunks=[chunk],
            validation_errors=[],
        )

    monkeypatch.setattr(cli, "ingest_corpus", fake_ingest_corpus, raising=False)

    result = runner.invoke(
        app,
        ["corpus", "ingest", "--collection", "rag_quality_lab", "--recreate", "--json"],
    )

    assert result.exit_code == 0, result.stderr
    assert captured == {"collection": "rag_quality_lab", "recreate": True}

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == DEFAULT_SCHEMA_VERSION
    assert payload["collection"] == "rag_quality_lab"
    assert payload["source_count"] == 15
    assert payload["chunk_count"] == 30
    assert payload["embedding_model"] == "embedding-test"
    assert payload["validation_errors"] == []
    assert payload["category_counts"] == {
        "prompting techniques": 6,
        "RAG and context handling": 6,
        "RAG evaluation and quality": 6,
        "LLM security and risks": 6,
        "LLM settings, cost, and tokens": 6,
    }

    first_chunk = payload["ingested_chunks"][0]
    assert first_chunk["chunk_id"] == "source-01:overview:0000:abc123"
    assert first_chunk["source_slug"] == "source-01"
    assert first_chunk["category"] == "prompting techniques"
    assert first_chunk["section_path"] == ["Overview"]
    assert first_chunk["content_hash"] == "abc123"
    assert first_chunk["estimated_tokens"] == 11
    assert first_chunk["provenance"] == {
        "url": "https://example.test/prompt-guide/source-01",
        "license": "MIT",
        "pinned_version": "dair-ai-prompt-guide@abc123",
        "local_ref": "corpus/sources/source-01.md",
    }


def test_corpus_ingest_failure_reports_missing_embedding_configuration(
    monkeypatch: pytest.MonkeyPatch,
    temporary_corpus: dict[str, Path],
) -> None:
    monkeypatch.chdir(temporary_corpus["root"].parent)

    def fake_ingest_corpus(*, collection: str, recreate: bool) -> IngestionSummaryArtifact:
        raise MissingSettingError(
            ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
            stage="Azure OpenAI embeddings",
        )

    monkeypatch.setattr(cli, "ingest_corpus", fake_ingest_corpus, raising=False)

    result = runner.invoke(app, ["corpus", "ingest", "--collection", "rag_quality_lab"])

    assert result.exit_code != 0
    assert "Error [Azure OpenAI embeddings]" in result.stderr
    assert "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" in result.stderr
