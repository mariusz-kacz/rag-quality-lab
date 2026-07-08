"""Corpus schemas shared across the RAG quality workflow."""

from __future__ import annotations

from pydantic import Field, field_validator

from rag_quality_lab.schemas.base import SchemaModel
from rag_quality_lab.schemas.categories import KnowledgeCategoryName


class SourceSection(SchemaModel):
    """One section available in a pinned source page."""

    heading: str = Field(min_length=1)
    level: int = Field(default=1, ge=1)
    ordinal: int = Field(default=0, ge=0)
    anchor: str | None = None


class Provenance(SchemaModel):
    """Source provenance persisted with retrievable chunks and artifacts."""

    url: str = Field(min_length=1)
    license: str = Field(min_length=1)
    pinned_version: str = Field(min_length=1)
    local_ref: str = Field(min_length=1)


class SourcePage(SchemaModel):
    """One selected page from the pinned corpus source."""

    source_slug: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str = Field(min_length=1)
    category: KnowledgeCategoryName
    url: str = Field(min_length=1)
    license: str = Field(min_length=1)
    pinned_version: str = Field(min_length=1)
    local_ref: str = Field(min_length=1)
    sections: list[SourceSection] = Field(default_factory=list)

    @property
    def provenance(self) -> Provenance:
        """Return the provenance shape used by chunks."""

        return Provenance(
            url=self.url,
            license=self.license,
            pinned_version=self.pinned_version,
            local_ref=self.local_ref,
        )


class Chunk(SchemaModel):
    """Stable retrievable text unit produced from a source page."""

    chunk_id: str = Field(min_length=1)
    source_slug: str = Field(min_length=1)
    category: KnowledgeCategoryName
    section_path: list[str] = Field(min_length=1)
    ordinal: int = Field(ge=0)
    content: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    estimated_tokens: int = Field(gt=0)
    provenance: Provenance

    @field_validator("section_path")
    @classmethod
    def validate_section_path(cls, value: list[str]) -> list[str]:
        if any(not section.strip() for section in value):
            raise ValueError("section_path entries must be non-empty")
        return value
