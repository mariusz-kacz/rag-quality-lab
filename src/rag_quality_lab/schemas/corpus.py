"""Corpus and question schemas shared across the RAG quality workflow."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class KnowledgeCategoryName(StrEnum):
    """Required deterministic routing categories."""

    PROMPTING_TECHNIQUES = "prompting techniques"
    RAG_AND_CONTEXT_HANDLING = "RAG and context handling"
    RAG_EVALUATION_AND_QUALITY = "RAG evaluation and quality"
    LLM_SECURITY_AND_RISKS = "LLM security and risks"
    LLM_SETTINGS_COST_AND_TOKENS = "LLM settings, cost, and tokens"


REQUIRED_KNOWLEDGE_CATEGORIES: tuple[str, ...] = tuple(
    category.value for category in KnowledgeCategoryName
)
Answerability: TypeAlias = Literal["answerable", "no_answer"]
CaseType: TypeAlias = Literal[
    "answerable",
    "no_answer",
    "ambiguous_boundary",
    "fallback_routing",
]


class SchemaModel(BaseModel):
    """Strict immutable base model for public schema records."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


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


class KnowledgeCategory(SchemaModel):
    """A deterministic routing category and its embedding reference."""

    name: KnowledgeCategoryName
    description: str = Field(min_length=1)
    embedding_ref: str | None = None


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


class Question(SchemaModel):
    """An ad hoc query or a golden-set case."""

    text: str = Field(min_length=1)
    question_id: str | None = None
    expected_category: KnowledgeCategoryName | None = None
    expected_relevant_sources: list[str] = Field(default_factory=list)
    answerability: Answerability = "answerable"
    case_type: CaseType = "answerable"

    @model_validator(mode="after")
    def validate_case_alignment(self) -> "Question":
        if self.answerability == "no_answer" and self.case_type == "answerable":
            raise ValueError("no_answer questions cannot use the answerable case type")
        return self
