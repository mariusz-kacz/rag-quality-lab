from __future__ import annotations

from collections.abc import Sequence

import pytest

from rag_quality_lab.providers import EmbeddingResponse
from rag_quality_lab.routing.categories import category_descriptions
from rag_quality_lab.routing.embedding_router import (
    EmbeddingCategoryRouter,
    EmbeddingRouterError,
)
from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES


pytestmark = pytest.mark.unit


def test_embedding_router_selects_high_confidence_category() -> None:
    provider = FakeEmbeddingProvider(
        query_vectors={
            "How does RAG use retrieved context to ground answers?": [
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
            ],
        }
    )
    router = EmbeddingCategoryRouter(
        embedding_provider=provider,
        threshold=0.5,
    )

    decision = router.route("How does RAG use retrieved context to ground answers?")

    assert decision.selected_category == "RAG and context handling"
    assert decision.fallback_all_categories is False
    assert decision.confidence == pytest.approx(1.0)
    assert decision.threshold == 0.5
    assert decision.category_scores == {
        "prompting techniques": pytest.approx(0.0),
        "RAG and context handling": pytest.approx(1.0),
        "RAG evaluation and quality": pytest.approx(0.0),
        "LLM security and risks": pytest.approx(0.0),
        "LLM settings, cost, and tokens": pytest.approx(0.0),
    }
    assert provider.calls[0] == list(category_descriptions().values())
    assert provider.calls[1] == [
        "How does RAG use retrieved context to ground answers?"
    ]


def test_embedding_router_falls_back_when_confidence_below_threshold() -> None:
    provider = FakeEmbeddingProvider(
        query_vectors={
            "How do risk, tokens, retrieval, and quality interact?": [
                0.2,
                0.2,
                0.2,
                0.2,
                0.2,
            ],
        }
    )
    router = EmbeddingCategoryRouter(
        embedding_provider=provider,
        threshold=0.9,
    )

    decision = router.route("How do risk, tokens, retrieval, and quality interact?")

    assert decision.selected_category is None
    assert decision.fallback_all_categories is True
    assert decision.confidence == pytest.approx(0.4472135955)
    assert decision.threshold == 0.9
    assert set(decision.category_scores) == set(REQUIRED_KNOWLEDGE_CATEGORIES)
    assert all(
        score == pytest.approx(0.4472135955)
        for score in decision.category_scores.values()
    )


def test_embedding_router_reports_all_category_scores_in_required_order() -> None:
    provider = FakeEmbeddingProvider(
        query_vectors={
            "Which settings affect token cost and latency?": [0.0, 0.0, 0.0, 0.0, 1.0],
        }
    )
    router = EmbeddingCategoryRouter(
        embedding_provider=provider,
        threshold=0.1,
    )

    decision = router.route("Which settings affect token cost and latency?")

    assert tuple(decision.category_scores) == REQUIRED_KNOWLEDGE_CATEGORIES
    assert decision.selected_category == "LLM settings, cost, and tokens"
    assert decision.category_scores["LLM settings, cost, and tokens"] == pytest.approx(
        1.0
    )


def test_embedding_router_rejects_empty_questions() -> None:
    router = EmbeddingCategoryRouter(
        embedding_provider=FakeEmbeddingProvider(query_vectors={}),
        threshold=0.5,
    )

    with pytest.raises(EmbeddingRouterError, match="question cannot be empty"):
        router.route("  ")


def test_embedding_router_clamps_negative_similarity_to_zero_confidence() -> None:
    provider = FakeEmbeddingProvider(
        query_vectors={
            "What is unrelated to these categories?": [-1.0, -1.0, -1.0, -1.0, -1.0],
        }
    )
    router = EmbeddingCategoryRouter(
        embedding_provider=provider,
        threshold=0.5,
    )

    decision = router.route("What is unrelated to these categories?")

    assert decision.selected_category is None
    assert decision.fallback_all_categories is True
    assert decision.confidence == 0.0
    assert all(score == 0.0 for score in decision.category_scores.values())


def test_embedding_router_rejects_invalid_threshold() -> None:
    with pytest.raises(EmbeddingRouterError, match="threshold"):
        EmbeddingCategoryRouter(
            embedding_provider=FakeEmbeddingProvider(query_vectors={}),
            threshold=1.1,
        )


def test_embedding_router_rejects_wrong_category_embedding_count() -> None:
    router = EmbeddingCategoryRouter(
        embedding_provider=WrongCountEmbeddingProvider(vector_count=1),
        threshold=0.5,
    )

    with pytest.raises(EmbeddingRouterError, match="category vector"):
        router.route("How does RAG work?")


def test_embedding_router_rejects_wrong_query_embedding_count() -> None:
    router = EmbeddingCategoryRouter(
        embedding_provider=WrongCountEmbeddingProvider(vector_count=5, query_count=0),
        threshold=0.5,
    )

    with pytest.raises(EmbeddingRouterError, match="query vector"):
        router.route("How does RAG work?")


class FakeEmbeddingProvider:
    deployment = "embedding-test"

    def __init__(self, *, query_vectors: dict[str, list[float]]) -> None:
        self.query_vectors = query_vectors
        self.calls: list[list[str]] = []
        descriptions = category_descriptions()
        self.category_vectors = {
            descriptions["prompting techniques"]: [1.0, 0.0, 0.0, 0.0, 0.0],
            descriptions["RAG and context handling"]: [0.0, 1.0, 0.0, 0.0, 0.0],
            descriptions["RAG evaluation and quality"]: [0.0, 0.0, 1.0, 0.0, 0.0],
            descriptions["LLM security and risks"]: [0.0, 0.0, 0.0, 1.0, 0.0],
            descriptions["LLM settings, cost, and tokens"]: [0.0, 0.0, 0.0, 0.0, 1.0],
        }

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse:
        clean_texts = list(texts)
        self.calls.append(clean_texts)
        return EmbeddingResponse(
            vectors=[
                self.category_vectors.get(text) or self.query_vectors[text]
                for text in clean_texts
            ],
            model="embedding-test",
        )


class WrongCountEmbeddingProvider:
    deployment = "embedding-test"

    def __init__(self, *, vector_count: int, query_count: int | None = None) -> None:
        self.vector_count = vector_count
        self.query_count = query_count if query_count is not None else vector_count
        self.calls = 0

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse:
        self.calls += 1
        vector_count = self.vector_count if self.calls == 1 else self.query_count
        return EmbeddingResponse(
            vectors=[[1.0, 0.0, 0.0, 0.0, 0.0] for _ in range(vector_count)],
            model="embedding-test",
        )
