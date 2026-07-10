"""Schemas for golden questions, metrics, and evaluation artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, TypeAlias

from pydantic import Field, model_validator

from rag_quality_lab.schemas.base import SchemaModel
from rag_quality_lab.schemas.categories import KnowledgeCategoryName
from rag_quality_lab.schemas.query import CaseType, Question
from rag_quality_lab.schemas.retrieval import RetrievalMode


REQUIRED_CASE_TYPES: tuple[str, ...] = (
    "answerable",
    "no_answer",
    "ambiguous_boundary",
    "fallback_routing",
)
REQUIRED_EVALUATION_METRICS: tuple[str, ...] = (
    "routing_accuracy",
    "fallback_rate",
    "recall_at_k",
    "mrr",
    "citation_source_match",
    "no_answer_accuracy",
    "average_context_tokens",
    "average_included_chunks",
)

MetricName: TypeAlias = Literal[
    "routing_accuracy",
    "fallback_rate",
    "recall_at_k",
    "mrr",
    "citation_source_match",
    "no_answer_accuracy",
    "average_context_tokens",
    "average_included_chunks",
]


class GoldenSet(SchemaModel):
    """Validated golden question set used by evaluation runs."""

    questions: list[Question] = Field(min_length=12, max_length=20)

    @model_validator(mode="after")
    def validate_required_cases(self) -> "GoldenSet":
        case_types = {question.case_type for question in self.questions}
        missing = sorted(set(REQUIRED_CASE_TYPES) - case_types)
        if missing:
            raise ValueError(f"golden set is missing required case types: {missing}")

        for question in self.questions:
            if (
                question.case_type == "answerable"
                and not question.expected_relevant_sources
            ):
                raise ValueError(
                    "answerable golden questions require expected_relevant_sources"
                )
        return self


class EvaluationMetrics(SchemaModel):
    """Aggregate metrics required for every evaluation artifact."""

    routing_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    fallback_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    recall_at_k: float | None = Field(default=None, ge=0.0, le=1.0)
    mrr: float | None = Field(default=None, ge=0.0, le=1.0)
    citation_source_match: float | None = Field(default=None, ge=0.0, le=1.0)
    no_answer_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    average_context_tokens: float | None = Field(default=None, ge=0.0)
    average_included_chunks: float | None = Field(default=None, ge=0.0)


class EvaluationQuestionResult(SchemaModel):
    """Per-question evaluation result and trace reference."""

    question_id: str = Field(min_length=1)
    question_text: str = Field(min_length=1)
    case_type: CaseType
    trace_path: Path
    metrics: dict[MetricName, float | None] = Field(default_factory=dict)
    expected_category: KnowledgeCategoryName | None = None
    selected_category: KnowledgeCategoryName | None = None
    routed_categories: list[KnowledgeCategoryName] = Field(default_factory=list)
    answer_text: str | None = None
    is_no_answer: bool | None = None
    expected_relevant_sources: list[str] = Field(default_factory=list)
    retrieved_sources: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class EvaluationArtifactPaths(SchemaModel):
    """Paths written for one evaluation run."""

    json_path: Path | None = None
    markdown_path: Path | None = None


class EvaluationRun(SchemaModel):
    """Machine-readable evaluation run artifact."""

    schema_version: str = Field(default="1.0", min_length=1)
    run_id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    retrieval_mode: RetrievalMode
    golden_set_path: Path
    configuration: dict[str, Any] = Field(default_factory=dict)
    metrics: EvaluationMetrics
    questions: list[EvaluationQuestionResult] = Field(default_factory=list)
    trace_paths: list[Path] = Field(default_factory=list)
    artifact_paths: EvaluationArtifactPaths | None = None

    @model_validator(mode="after")
    def validate_required_metrics(self) -> "EvaluationRun":
        metric_names = set(self.metrics.model_dump())
        missing = sorted(set(REQUIRED_EVALUATION_METRICS) - metric_names)
        if missing:
            raise ValueError(f"evaluation metrics missing required fields: {missing}")
        return self
