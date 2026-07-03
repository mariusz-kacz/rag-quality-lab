from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rag_quality_lab.cli import app
from rag_quality_lab.routing.categories import category_names
from rag_quality_lab.schemas.artifacts import DEFAULT_SCHEMA_VERSION


pytestmark = pytest.mark.contract

runner = CliRunner()


def test_corpus_inspect_json_reports_valid_manifest_summary(
    monkeypatch: pytest.MonkeyPatch,
    temporary_corpus: dict[str, Path],
) -> None:
    monkeypatch.chdir(temporary_corpus["root"].parent)

    result = runner.invoke(app, ["corpus", "inspect", "--json"])

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == DEFAULT_SCHEMA_VERSION
    assert payload["source_count"] == 15
    assert payload["validation_errors"] == []
    assert payload["license_summary"] == {"MIT": 15}
    assert payload["pinned_version"] == "dair-ai-prompt-guide@abc123"
    assert set(payload["categories"]) == set(category_names())
    assert all(count == 3 for count in payload["categories"].values())

    first_source = payload["sources"][0]
    assert first_source["source_slug"] == "source-01"
    assert first_source["category"] in category_names()
    assert first_source["url"].startswith("https://example.test/prompt-guide/")
    assert first_source["license"] == "MIT"
    assert first_source["pinned_version"] == "dair-ai-prompt-guide@abc123"
    assert first_source["local_ref"] == "corpus/sources/source-01.md"


def test_corpus_inspect_failure_identifies_missing_local_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    temporary_corpus: dict[str, Path],
) -> None:
    monkeypatch.chdir(temporary_corpus["root"].parent)
    missing_snapshot = temporary_corpus["root"] / "sources" / "source-01.md"
    missing_snapshot.unlink()

    result = runner.invoke(app, ["corpus", "inspect"])

    assert result.exit_code != 0
    assert "corpus inspect" in result.stderr
    assert "missing local source snapshot" in result.stderr
    assert "corpus/sources/source-01.md" in result.stderr
