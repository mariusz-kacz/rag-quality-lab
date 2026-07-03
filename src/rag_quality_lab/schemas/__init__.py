"""Shared Pydantic schemas for artifacts and domain records."""

from rag_quality_lab.schemas.artifacts import CorpusSummaryArtifact, IngestionSummaryArtifact
from rag_quality_lab.schemas.corpus import (
    REQUIRED_KNOWLEDGE_CATEGORIES,
    Chunk,
    KnowledgeCategory,
    Provenance,
    Question,
    SourcePage,
    SourceSection,
)
from rag_quality_lab.schemas.eval import (
    REQUIRED_EVALUATION_METRICS,
    EvaluationArtifactPaths,
    EvaluationMetrics,
    EvaluationQuestionResult,
    EvaluationRun,
    GoldenSet,
)
from rag_quality_lab.schemas.trace import (
    AnswerResult,
    CitationValidation,
    ContextBuild,
    ContextChunk,
    ExcludedContextChunk,
    ModelUsage,
    QueryTrace,
    RetrievalResult,
    RouteDecision,
)

__all__ = [
    "REQUIRED_EVALUATION_METRICS",
    "REQUIRED_KNOWLEDGE_CATEGORIES",
    "AnswerResult",
    "Chunk",
    "CitationValidation",
    "ContextBuild",
    "ContextChunk",
    "CorpusSummaryArtifact",
    "EvaluationArtifactPaths",
    "EvaluationMetrics",
    "EvaluationQuestionResult",
    "EvaluationRun",
    "ExcludedContextChunk",
    "GoldenSet",
    "IngestionSummaryArtifact",
    "KnowledgeCategory",
    "ModelUsage",
    "Provenance",
    "QueryTrace",
    "Question",
    "RetrievalResult",
    "RouteDecision",
    "SourcePage",
    "SourceSection",
]
