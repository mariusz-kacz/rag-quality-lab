import math
from dataclasses import dataclass

from rag_quality_lab.corpus.ingest import EmbeddingProvider
from rag_quality_lab.routing import category_descriptions
from rag_quality_lab.schemas import RouteDecision
from rag_quality_lab.schemas.corpus import KnowledgeCategoryName


class EmbeddingRouterError(Exception):
    """Raised when embedding-based category routing cannot produce a decision."""


@dataclass(frozen=True)
class CategoryEmbedding:
    category: KnowledgeCategoryName
    embedding: list[float]


class EmbeddingCategoryRouter:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        threshold: float,
    ) -> None:
        if threshold < 0.0 or threshold > 1.0:
            raise EmbeddingRouterError("threshold must be between 0.0 and 1.0")
        self.embedding_provider = embedding_provider
        self.threshold = threshold
        self.category_embeddings: list[CategoryEmbedding] = []

    def _embed_category_descriptions(
        self,
    ) -> None:
        descriptions = category_descriptions()
        category_embedding_vectors = self.embedding_provider.embed_texts(
            list(descriptions.values())
        )
        if len(category_embedding_vectors.vectors) != len(descriptions):
            raise EmbeddingRouterError(
                "embedding provider returned "
                f"{len(category_embedding_vectors.vectors)} category vector(s), "
                f"expected {len(descriptions)}"
            )

        self.category_embeddings = [
            CategoryEmbedding(
                category=category,
                embedding=embedding,
            )
            for category, embedding in zip(
                descriptions, category_embedding_vectors.vectors
            )
        ]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def route(
        self,
        input_text: str,
    ) -> RouteDecision:
        question = input_text.strip()
        if not question:
            raise EmbeddingRouterError("question cannot be empty")

        if not self.category_embeddings:
            self._embed_category_descriptions()

        query_embedding_vectors = self.embedding_provider.embed_texts(
            [question]
        ).vectors
        if len(query_embedding_vectors) != 1:
            raise EmbeddingRouterError(
                "embedding provider returned "
                f"{len(query_embedding_vectors)} query vector(s), expected 1"
            )
        query_embedding = query_embedding_vectors[0]
        category_scores = {
            item.category: max(
                0.0,
                self._cosine_similarity(query_embedding, item.embedding),
            )
            for item in self.category_embeddings
        }
        selected_category, confidence = max(
            category_scores.items(),
            key=lambda item: item[1],
        )

        fallback_all_categories = confidence < self.threshold
        return RouteDecision(
            selected_category=None if fallback_all_categories else selected_category,
            fallback_all_categories=fallback_all_categories,
            confidence=confidence,
            threshold=self.threshold,
            category_scores=category_scores,
        )
