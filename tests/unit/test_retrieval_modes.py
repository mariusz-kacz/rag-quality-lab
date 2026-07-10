from __future__ import annotations

from typing import Any

import pytest

from rag_quality_lab.rag.pipeline import QdrantQueryRetriever
from rag_quality_lab.retrieval.qdrant_store import QdrantStore, QdrantStoreError
from rag_quality_lab.schemas import RouteDecision


pytestmark = pytest.mark.unit


def test_supported_retrieval_modes_validate_known_modes() -> None:
    from rag_quality_lab.retrieval.modes import (
        RetrievalModeError,
        supported_retrieval_modes,
        validate_retrieval_mode,
    )

    assert supported_retrieval_modes() == (
        "baseline-vector",
        "routed-vector",
    )
    assert validate_retrieval_mode("baseline-vector") == "baseline-vector"
    assert validate_retrieval_mode("routed-vector") == "routed-vector"

    with pytest.raises(RetrievalModeError, match="keyword-search"):
        validate_retrieval_mode("keyword-search")


def test_baseline_vector_search_normalizes_ranked_results_without_filter() -> None:
    client = FakeSearchClient(
        points=[
            fake_point(
                score=0.91,
                payload={
                    "chunk_id": "chunk-a",
                    "source_slug": "source-a",
                    "category": "RAG and context handling",
                    "section_path": ["Overview"],
                    "estimated_tokens": 42,
                    "content": "RAG uses retrieved context.",
                },
            ),
            fake_point(
                score=0.82,
                payload={
                    "chunk_id": "chunk-b",
                    "source_slug": "source-b",
                    "category": "prompting techniques",
                    "section_path": ["Prompting"],
                    "estimated_tokens": 21,
                    "content": "Prompts shape model behavior.",
                },
            ),
        ]
    )
    store = QdrantStore(client=client)

    results = store.search_chunks(
        collection="rag_quality_lab",
        query_vector=[0.1, 0.2, 0.3],
        mode="baseline-vector",
        top_k=2,
    )

    assert [result.model_dump(mode="json") for result in results] == [
        {
            "mode": "baseline-vector",
            "rank": 1,
            "chunk_id": "chunk-a",
            "source_slug": "source-a",
            "category": "RAG and context handling",
            "section_path": ["Overview"],
            "score": 0.91,
            "estimated_tokens": 42,
            "content": "RAG uses retrieved context.",
        },
        {
            "mode": "baseline-vector",
            "rank": 2,
            "chunk_id": "chunk-b",
            "source_slug": "source-b",
            "category": "prompting techniques",
            "section_path": ["Prompting"],
            "score": 0.82,
            "estimated_tokens": 21,
            "content": "Prompts shape model behavior.",
        },
    ]
    assert client.search_calls == [
        {
            "collection_name": "rag_quality_lab",
            "query": [0.1, 0.2, 0.3],
            "limit": 2,
            "query_filter": None,
            "with_payload": True,
        }
    ]


def test_routed_vector_search_applies_selected_category_filter() -> None:
    client = FakeSearchClient(
        points=[
            fake_point(
                score=0.95,
                payload={
                    "chunk_id": "chunk-rag",
                    "source_slug": "source-rag",
                    "category": "RAG and context handling",
                    "section_path": ["Grounding"],
                    "estimated_tokens": 30,
                    "content": "Retrieved evidence grounds answers.",
                },
            )
        ]
    )
    store = QdrantStore(client=client)

    results = store.search_chunks(
        collection="rag_quality_lab",
        query_vector=[0.1, 0.2, 0.3],
        mode="routed-vector",
        top_k=3,
        selected_category="RAG and context handling",
    )

    assert len(results) == 1
    assert results[0].mode == "routed-vector"
    assert results[0].rank == 1
    assert results[0].category == "RAG and context handling"
    query_filter = client.search_calls[0]["query_filter"]
    assert query_filter is not None
    assert query_filter.must[0].key == "category"
    assert query_filter.must[0].match.value == "RAG and context handling"


def test_routed_vector_search_applies_multi_category_filter() -> None:
    client = FakeSearchClient(points=[])
    store = QdrantStore(client=client)

    store.search_chunks(
        collection="rag_quality_lab",
        query_vector=[0.1, 0.2, 0.3],
        mode="routed-vector",
        top_k=3,
        selected_categories=[
            "RAG evaluation and quality",
            "RAG and context handling",
            "LLM settings, cost, and tokens",
        ],
    )

    query_filter = client.search_calls[0]["query_filter"]
    assert query_filter is not None
    assert query_filter.must[0].key == "category"
    assert query_filter.must[0].match.any == [
        "RAG evaluation and quality",
        "RAG and context handling",
        "LLM settings, cost, and tokens",
    ]


def test_routed_vector_global_fallback_removes_category_filter() -> None:
    client = FakeSearchClient(points=[])
    store = QdrantStore(client=client)

    store.search_chunks(
        collection="rag_quality_lab",
        query_vector=[0.1, 0.2, 0.3],
        mode="routed-vector",
        top_k=3,
        fallback_all_categories=True,
    )

    assert client.search_calls[0]["query_filter"] is None


def test_qdrant_query_retriever_passes_categories_within_margin() -> None:
    store = RecordingStore()
    retriever = QdrantQueryRetriever(
        collection="rag_quality_lab",
        embedding_provider=FakeEmbeddingProvider(),
        store=store,
        category_score_margin=0.08,
    )
    route_decision = RouteDecision(
        selected_category="RAG evaluation and quality",
        fallback_all_categories=False,
        confidence=0.46,
        threshold=0.18,
        category_scores={
            "prompting techniques": 0.27,
            "RAG and context handling": 0.40,
            "RAG evaluation and quality": 0.46,
            "LLM security and risks": 0.379,
            "LLM settings, cost, and tokens": 0.38,
        },
    )

    retriever.retrieve(
        question="How can limiting retrieved context reduce latency?",
        mode="routed-vector",
        top_k=6,
        route_decision=route_decision,
    )

    assert store.calls == [
        {
            "collection": "rag_quality_lab",
            "query_vector": [0.1, 0.2, 0.3],
            "mode": "routed-vector",
            "top_k": 6,
            "selected_category": "RAG evaluation and quality",
            "selected_categories": [
                "RAG evaluation and quality",
                "RAG and context handling",
                "LLM settings, cost, and tokens",
            ],
            "fallback_all_categories": False,
        }
    ]


def test_qdrant_query_retriever_baseline_searches_globally_without_route() -> None:
    store = RecordingStore()
    embedding_provider = FakeEmbeddingProvider()
    retriever = QdrantQueryRetriever(
        collection="rag_quality_lab",
        embedding_provider=embedding_provider,
        store=store,
        category_score_margin=0.08,
    )

    retriever.retrieve(
        question="How does global retrieval work?",
        mode="baseline-vector",
        top_k=3,
        route_decision=None,
    )

    assert embedding_provider.texts == ["How does global retrieval work?"]
    assert store.calls == [
        {
            "collection": "rag_quality_lab",
            "query_vector": [0.1, 0.2, 0.3],
            "mode": "baseline-vector",
            "top_k": 3,
            "selected_category": None,
            "selected_categories": None,
            "fallback_all_categories": False,
        }
    ]


def test_routed_vector_search_requires_selected_category_without_fallback() -> None:
    store = QdrantStore(client=FakeSearchClient(points=[]))

    with pytest.raises(ValueError, match="selected_category"):
        store.search_chunks(
            collection="rag_quality_lab",
            query_vector=[0.1, 0.2, 0.3],
            mode="routed-vector",
            top_k=3,
        )


def test_search_chunks_reports_missing_payload_field_with_rank() -> None:
    client = FakeSearchClient(
        points=[
            fake_point(
                score=0.91,
                payload={
                    "source_slug": "source-a",
                    "category": "RAG and context handling",
                    "section_path": ["Overview"],
                },
            )
        ]
    )
    store = QdrantStore(client=client)

    with pytest.raises(
        QdrantStoreError,
        match="Invalid Qdrant payload for retrieval result at rank 1: missing chunk_id",
    ):
        store.search_chunks(
            collection="rag_quality_lab",
            query_vector=[0.1, 0.2, 0.3],
            mode="baseline-vector",
            top_k=1,
        )


def test_search_chunks_wraps_invalid_payload_shape_with_rank() -> None:
    client = FakeSearchClient(
        points=[
            fake_point(
                score=0.91,
                payload={
                    "chunk_id": "chunk-a",
                    "source_slug": "source-a",
                    "category": "RAG and context handling",
                    "section_path": [],
                },
            )
        ]
    )
    store = QdrantStore(client=client)

    with pytest.raises(
        QdrantStoreError,
        match="Invalid Qdrant payload for retrieval result at rank 1",
    ):
        store.search_chunks(
            collection="rag_quality_lab",
            query_vector=[0.1, 0.2, 0.3],
            mode="baseline-vector",
            top_k=1,
        )


class FakeSearchClient:
    def __init__(self, *, points: list[Any]) -> None:
        self.points = points
        self.search_calls: list[dict[str, Any]] = []

    def query_points(
        self,
        *,
        collection_name: str,
        query: list[float],
        limit: int,
        query_filter: Any = None,
        with_payload: bool = True,
    ) -> Any:
        self.search_calls.append(
            {
                "collection_name": collection_name,
                "query": query,
                "limit": limit,
                "query_filter": query_filter,
                "with_payload": with_payload,
            }
        )
        return type("FakeQueryResponse", (), {"points": self.points[:limit]})()


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.texts: list[str] = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]


class RecordingStore:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def search_chunks(
        self,
        *,
        collection: str,
        query_vector: list[float],
        mode: str,
        top_k: int,
        selected_category: str | None = None,
        selected_categories: list[str] | None = None,
        fallback_all_categories: bool = False,
    ) -> list[Any]:
        self.calls.append(
            {
                "collection": collection,
                "query_vector": query_vector,
                "mode": mode,
                "top_k": top_k,
                "selected_category": selected_category,
                "selected_categories": selected_categories,
                "fallback_all_categories": fallback_all_categories,
            }
        )
        return []


def fake_point(*, score: float, payload: dict[str, Any]) -> Any:
    return type("FakePoint", (), {"score": score, "payload": payload})()
