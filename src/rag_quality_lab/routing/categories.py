"""Required knowledge categories used for deterministic routing."""

from __future__ import annotations

from rag_quality_lab.schemas.corpus import KnowledgeCategory, KnowledgeCategoryName


PROMPTING_TECHNIQUES_DESCRIPTION = (
    "Prompt design, instruction patterns, few-shot examples, chain-of-thought style reasoning, "
    "prompt templates, and practical methods for improving model responses through input design."
)
RAG_AND_CONTEXT_HANDLING_DESCRIPTION = (
    "Retrieval augmented generation concepts, document retrieval, chunk selection, grounding, "
    "context-window management, and using external evidence to answer questions."
)
RAG_EVALUATION_AND_QUALITY_DESCRIPTION = (
    "RAG quality measurement, retrieval metrics, answer evaluation, golden datasets, diagnostics, "
    "and methods for comparing retrieval or generation strategies."
)
LLM_SECURITY_AND_RISKS_DESCRIPTION = (
    "Prompt injection, jailbreaks, data leakage, unsafe model behavior, adversarial inputs, "
    "and security controls or risk mitigations for LLM applications."
)
LLM_SETTINGS_COST_AND_TOKENS_DESCRIPTION = (
    "Model parameters, tokenization, context limits, latency, pricing, cost tradeoffs, "
    "temperature, sampling settings, and operational budget considerations."
)


REQUIRED_CATEGORIES: tuple[KnowledgeCategory, ...] = (
    KnowledgeCategory(
        name=KnowledgeCategoryName.PROMPTING_TECHNIQUES,
        description=PROMPTING_TECHNIQUES_DESCRIPTION,
        embedding_ref="category:prompting-techniques",
    ),
    KnowledgeCategory(
        name=KnowledgeCategoryName.RAG_AND_CONTEXT_HANDLING,
        description=RAG_AND_CONTEXT_HANDLING_DESCRIPTION,
        embedding_ref="category:rag-and-context-handling",
    ),
    KnowledgeCategory(
        name=KnowledgeCategoryName.RAG_EVALUATION_AND_QUALITY,
        description=RAG_EVALUATION_AND_QUALITY_DESCRIPTION,
        embedding_ref="category:rag-evaluation-and-quality",
    ),
    KnowledgeCategory(
        name=KnowledgeCategoryName.LLM_SECURITY_AND_RISKS,
        description=LLM_SECURITY_AND_RISKS_DESCRIPTION,
        embedding_ref="category:llm-security-and-risks",
    ),
    KnowledgeCategory(
        name=KnowledgeCategoryName.LLM_SETTINGS_COST_AND_TOKENS,
        description=LLM_SETTINGS_COST_AND_TOKENS_DESCRIPTION,
        embedding_ref="category:llm-settings-cost-and-tokens",
    ),
)

CATEGORY_BY_NAME: dict[str, KnowledgeCategory] = {
    category.name: category for category in REQUIRED_CATEGORIES
}


def category_names() -> tuple[str, ...]:
    """Return category names in deterministic routing order."""

    return tuple(category.name for category in REQUIRED_CATEGORIES)


def category_descriptions() -> dict[KnowledgeCategoryName, str]:
    """Return category descriptions keyed by category name."""

    return {category.name: category.description for category in REQUIRED_CATEGORIES}


def get_category(name: KnowledgeCategoryName | str) -> KnowledgeCategory:
    """Return a required category by name."""

    return CATEGORY_BY_NAME[str(name)]
