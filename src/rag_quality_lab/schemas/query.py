"""Schemas for one traced RAG query workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, TypeAlias

from pydantic import Field, field_validator, model_validator

from rag_quality_lab.schemas.base import SchemaModel
from rag_quality_lab.schemas.categories import (
    REQUIRED_KNOWLEDGE_CATEGORIES,
    KnowledgeCategoryName,
)
from rag_quality_lab.schemas.retrieval import RetrievalMode, RetrievalResult


Answerability: TypeAlias = Literal["answerable", "no_answer"]
CaseType: TypeAlias = Literal[
    "answerable",
    "no_answer",
    "ambiguous_boundary",
    "multi_category_routing",
    "fallback_routing",
]
ValidationStatus: TypeAlias = Literal["valid", "invalid", "not_applicable"]


class Question(SchemaModel):
    """An ad hoc query or a golden-set case."""

    text: str = Field(min_length=1)
    question_id: str | None = None
    expected_category: KnowledgeCategoryName | None = None
    expected_relevant_sources: list[str] = Field(default_factory=list)
    answerability: Answerability = "answerable"
    case_type: CaseType = "answerable"
    expected_fallback_all_categories: bool | None = None
    expected_searched_categories: list[KnowledgeCategoryName] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_case_alignment(self) -> "Question":
        if self.answerability == "no_answer" and self.case_type == "answerable":
            raise ValueError("no_answer questions cannot use the answerable case type")
        if self.case_type == "multi_category_routing":
            if self.expected_fallback_all_categories is not False:
                raise ValueError(
                    "multi_category_routing questions require fallback to be disabled"
                )
            if len(self.expected_searched_categories) < 2:
                raise ValueError(
                    "multi_category_routing questions require at least two searched categories"
                )
        if self.case_type == "fallback_routing":
            if self.expected_fallback_all_categories is not True:
                raise ValueError(
                    "fallback_routing questions require all-category fallback"
                )
            if set(self.expected_searched_categories) != set(
                REQUIRED_KNOWLEDGE_CATEGORIES
            ):
                raise ValueError(
                    "fallback_routing questions must expect all categories to be searched"
                )
        return self


class RouteDecision(SchemaModel):
    """Deterministic category routing output for one query."""

    selected_category: KnowledgeCategoryName | None = None
    fallback_all_categories: bool
    confidence: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0)
    category_scores: dict[KnowledgeCategoryName, float]

    @model_validator(mode="after")
    def validate_route_consistency(self) -> "RouteDecision":
        expected = set(REQUIRED_KNOWLEDGE_CATEGORIES)
        actual = set(self.category_scores)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(
                f"category_scores must include exactly five categories; missing={missing}, extra={extra}"
            )
        if self.fallback_all_categories and self.selected_category is not None:
            raise ValueError(
                "selected_category must be empty when routing falls back to all categories"
            )
        if not self.fallback_all_categories and self.selected_category is None:
            raise ValueError(
                "selected_category is required when routing does not fall back"
            )
        return self


class ContextChunk(SchemaModel):
    """A retrieved chunk selected for answer context."""

    chunk_id: str = Field(min_length=1)
    source_slug: str = Field(min_length=1)
    category: KnowledgeCategoryName
    section_path: list[str] = Field(min_length=1)
    retrieval_rank: int = Field(ge=1)
    content: str = Field(min_length=1)
    estimated_tokens: int = Field(gt=0)

    @field_validator("section_path")
    @classmethod
    def validate_section_path(cls, value: list[str]) -> list[str]:
        if any(not section.strip() for section in value):
            raise ValueError("section_path entries must be non-empty")
        return value


class ExcludedContextChunk(ContextChunk):
    """A retrieved chunk excluded from answer context."""

    reason: str = Field(min_length=1)


class SelectedContext(SchemaModel):
    """Bounded context selected for answer generation."""

    max_context_tokens: int = Field(gt=0)
    output_token_limit: int = Field(gt=0)
    included_chunks: list[ContextChunk] = Field(default_factory=list)
    excluded_chunks: list[ExcludedContextChunk] = Field(default_factory=list)
    final_estimated_context_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_budget_and_order(self) -> "SelectedContext":
        if self.final_estimated_context_tokens > self.max_context_tokens:
            raise ValueError(
                "final_estimated_context_tokens cannot exceed max_context_tokens"
            )
        included_ranks = [chunk.retrieval_rank for chunk in self.included_chunks]
        if included_ranks != sorted(included_ranks):
            raise ValueError("included_chunks must preserve retrieval rank order")
        return self


class AnswerResult(SchemaModel):
    """Generated answer or explicit no-answer result."""

    answer_text: str = Field(min_length=1)
    is_no_answer: bool
    citations: list[str] = Field(default_factory=list)
    validation_status: ValidationStatus
    validation_errors: list[str] = Field(default_factory=list)


class GenerationResult(SchemaModel):
    answer: AnswerResult
    model_usage: ModelUsage | None = None


class CitationValidation(SchemaModel):
    """Citation validation outcome against the selected context."""

    status: ValidationStatus
    cited_chunk_ids: list[str] = Field(default_factory=list)
    invalid_citations: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)


class ModelUsage(SchemaModel):
    """Token usage returned by a model provider when available."""

    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    model: str | None = None
    deployment: str | None = None


class QueryTrace(SchemaModel):
    """Persisted record of one full query workflow."""

    schema_version: str = Field(default="1.0", min_length=1)
    trace_id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    question: Question
    retrieval_mode: RetrievalMode
    route_decision: RouteDecision | None = None
    retrieval_results: list[RetrievalResult] = Field(default_factory=list)
    context_build: SelectedContext
    answer_result: AnswerResult
    citation_validation: CitationValidation
    model_usage: ModelUsage | None = None

    @field_validator("retrieval_results")
    @classmethod
    def validate_retrieval_ranks(
        cls, value: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        ranks = [result.rank for result in value]
        if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
            raise ValueError("retrieval_results ranks must be unique and ordered")
        return value
