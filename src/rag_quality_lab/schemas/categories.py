"""Schemas for the shared knowledge-category taxonomy."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from rag_quality_lab.schemas.base import SchemaModel


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


class KnowledgeCategory(SchemaModel):
    """A deterministic routing category and its embedding reference."""

    name: KnowledgeCategoryName
    description: str = Field(min_length=1)
    embedding_ref: str | None = None
