"""Schemas for retrieval modes and ranked retrieval results."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import Field, field_validator

from rag_quality_lab.schemas.base import SchemaModel
from rag_quality_lab.schemas.categories import KnowledgeCategoryName


RetrievalMode: TypeAlias = Literal["baseline-vector", "routed-vector"]


class RetrievalResult(SchemaModel):
    """One ranked retrieved chunk."""

    mode: RetrievalMode
    rank: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    source_slug: str = Field(min_length=1)
    category: KnowledgeCategoryName
    section_path: list[str] = Field(min_length=1)
    score: float
    estimated_tokens: int | None = Field(default=None, gt=0)
    content: str | None = None

    @field_validator("section_path")
    @classmethod
    def validate_section_path(cls, value: list[str]) -> list[str]:
        if any(not section.strip() for section in value):
            raise ValueError("section_path entries must be non-empty")
        return value
