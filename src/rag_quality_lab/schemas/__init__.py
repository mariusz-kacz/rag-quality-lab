"""Shared Pydantic schemas for artifacts and domain records."""

from rag_quality_lab.schemas.artifacts import (
    DEFAULT_SCHEMA_VERSION,
    ArtifactIOError,
    ArtifactSchemaVersionError,
    CorpusSummaryArtifact,
    IngestionSummaryArtifact,
    read_json_artifact,
    write_json_artifact,
)
from rag_quality_lab.schemas.categories import (
    REQUIRED_KNOWLEDGE_CATEGORIES,
    KnowledgeCategory,
    KnowledgeCategoryName,
)
from rag_quality_lab.schemas.corpus import (
    Chunk,
    Provenance,
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
from rag_quality_lab.schemas.query import (
    AnswerResult,
    Answerability,
    CaseType,
    CitationValidation,
    SelectedContext,
    ContextChunk,
    ExcludedContextChunk,
    GenerationResult,
    ModelUsage,
    QueryTrace,
    Question,
    RouteDecision,
    ValidationStatus,
)
from rag_quality_lab.schemas.retrieval import RetrievalMode, RetrievalResult

__all__ = [
    "REQUIRED_EVALUATION_METRICS",
    "REQUIRED_KNOWLEDGE_CATEGORIES",
    "AnswerResult",
    "Answerability",
    "ArtifactIOError",
    "ArtifactSchemaVersionError",
    "CaseType",
    "Chunk",
    "CitationValidation",
    "SelectedContext",
    "ContextChunk",
    "CorpusSummaryArtifact",
    "DEFAULT_SCHEMA_VERSION",
    "EvaluationArtifactPaths",
    "EvaluationMetrics",
    "EvaluationQuestionResult",
    "EvaluationRun",
    "ExcludedContextChunk",
    "GenerationResult",
    "GoldenSet",
    "IngestionSummaryArtifact",
    "KnowledgeCategory",
    "KnowledgeCategoryName",
    "ModelUsage",
    "Provenance",
    "QueryTrace",
    "Question",
    "RetrievalMode",
    "RetrievalResult",
    "RouteDecision",
    "SourcePage",
    "SourceSection",
    "ValidationStatus",
    "read_json_artifact",
    "write_json_artifact",
]
