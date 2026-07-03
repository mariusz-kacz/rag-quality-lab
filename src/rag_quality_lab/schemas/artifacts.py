"""Top-level artifact schemas written by CLI workflows."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from rag_quality_lab.schemas.corpus import Chunk, SourcePage


class SchemaArtifact(BaseModel):
    """Base model for JSON artifacts with explicit schema versioning."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: str = Field(default="1.0", min_length=1)


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
