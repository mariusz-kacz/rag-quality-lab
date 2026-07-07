import json

import pytest

from rag_quality_lab.schemas import (
    ArtifactIOError,
    ArtifactSchemaVersionError,
    CorpusSummaryArtifact,
    read_json_artifact,
    write_json_artifact,
)


def corpus_summary() -> CorpusSummaryArtifact:
    return CorpusSummaryArtifact(
        source_count=0,
        categories={},
        license_summary={},
        pinned_version=None,
        sources=[],
        validation_errors=[],
    )


def test_write_json_artifact_creates_parent_directories_and_schema_version(
    tmp_path,
) -> None:
    artifact_path = tmp_path / "nested" / "corpus-summary.json"

    written_path = write_json_artifact(artifact_path, corpus_summary())

    assert written_path == artifact_path
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["source_count"] == 0


def test_read_json_artifact_validates_model_and_schema_version(tmp_path) -> None:
    artifact_path = tmp_path / "corpus-summary.json"
    write_json_artifact(artifact_path, corpus_summary())

    loaded = read_json_artifact(artifact_path, CorpusSummaryArtifact)

    assert loaded == corpus_summary()


def test_read_json_artifact_rejects_missing_schema_version(tmp_path) -> None:
    artifact_path = tmp_path / "missing-version.json"
    artifact_path.write_text('{"source_count": 0}', encoding="utf-8")

    with pytest.raises(ArtifactSchemaVersionError, match="schema_version"):
        read_json_artifact(artifact_path, CorpusSummaryArtifact)


def test_read_json_artifact_rejects_unexpected_schema_version(tmp_path) -> None:
    artifact_path = tmp_path / "future-version.json"
    payload = corpus_summary().model_dump()
    payload["schema_version"] = "9.0"
    artifact_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ArtifactSchemaVersionError, match="expected '1.0'"):
        read_json_artifact(artifact_path, CorpusSummaryArtifact)


def test_read_json_artifact_rejects_non_object_json(tmp_path) -> None:
    artifact_path = tmp_path / "array.json"
    artifact_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ArtifactIOError, match="JSON object"):
        read_json_artifact(artifact_path, CorpusSummaryArtifact)
