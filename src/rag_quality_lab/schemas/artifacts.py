"""Top-level artifact schemas written by CLI workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from rag_quality_lab.schemas.corpus import Chunk, SourcePage


DEFAULT_SCHEMA_VERSION = "1.0"
ArtifactModel = TypeVar("ArtifactModel", bound=BaseModel)


class ArtifactIOError(Exception):
    """Base exception for artifact read/write failures."""


class ArtifactSchemaVersionError(ArtifactIOError):
    """Raised when an artifact has a missing or unsupported schema version."""


class SchemaArtifact(BaseModel):
    """Base model for JSON artifacts with explicit schema versioning."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, min_length=1)


class CorpusSummaryArtifact(SchemaArtifact):
    """Machine-readable corpus inspection summary."""

    source_count: int = Field(ge=0)
    categories: dict[str, int] = Field(default_factory=dict)
    license_summary: dict[str, int] = Field(default_factory=dict)
    pinned_version: str | None = None
    sources: list[SourcePage] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)


class IngestionSummaryArtifact(SchemaArtifact):
    """Machine-readable corpus ingestion summary."""

    collection: str = Field(min_length=1)
    source_count: int = Field(ge=0)
    chunk_count: int = Field(ge=0)
    category_counts: dict[str, int] = Field(default_factory=dict)
    embedding_model: str = Field(min_length=1)
    ingested_chunks: list[Chunk] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)


def write_json_artifact(path: str | Path, artifact: BaseModel) -> Path:
    """Write a Pydantic artifact as stable UTF-8 JSON and return the path."""

    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        artifact.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def read_json_artifact(
    path: str | Path,
    model_type: type[ArtifactModel],
    *,
    expected_schema_version: str = DEFAULT_SCHEMA_VERSION,
) -> ArtifactModel:
    """Read and validate a JSON artifact against a Pydantic model."""

    artifact_path = Path(path)
    try:
        raw_data: Any = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactIOError(f"Invalid JSON artifact at {artifact_path}: {exc.msg}") from exc

    if not isinstance(raw_data, dict):
        raise ArtifactIOError(f"Artifact at {artifact_path} must contain a JSON object")

    _validate_schema_version(raw_data, artifact_path, expected_schema_version)
    return model_type.model_validate(raw_data)


def _validate_schema_version(
    raw_data: dict[str, Any],
    artifact_path: Path,
    expected_schema_version: str,
) -> None:
    schema_version = raw_data.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version:
        raise ArtifactSchemaVersionError(
            f"Artifact at {artifact_path} is missing required schema_version"
        )
    if schema_version != expected_schema_version:
        raise ArtifactSchemaVersionError(
            f"Artifact at {artifact_path} uses schema_version {schema_version!r}; "
            f"expected {expected_schema_version!r}"
        )
