from __future__ import annotations

from typing import Any

import pytest

from rag_quality_lab.retrieval.qdrant_store import QdrantStore


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
        "routed-hybrid",
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
            "score": 0.91,
            "fusion_score": None,
            "estimated_tokens": 42,
            "content": "RAG uses retrieved context.",
        },
        {
            "mode": "baseline-vector",
            "rank": 2,
            "chunk_id": "chunk-b",
            "source_slug": "source-b",
            "category": "prompting techniques",
            "score": 0.82,
            "fusion_score": None,
            "estimated_tokens": 21,
            "content": "Prompts shape model behavior.",
        },
    ]
    assert client.search_calls == [
        {
            "collection_name": "rag_quality_lab",
            "query_vector": [0.1, 0.2, 0.3],
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
    assert client.search_calls[0]["query_filter"] == {
        "must": [
            {
                "key": "category",
                "match": {"value": "RAG and context handling"},
            }
        ]
    }


def test_routed_vector_search_requires_selected_category_without_fallback() -> None:
    store = QdrantStore(client=FakeSearchClient(points=[]))

    with pytest.raises(ValueError, match="selected_category"):
        store.search_chunks(
            collection="rag_quality_lab",
            query_vector=[0.1, 0.2, 0.3],
            mode="routed-vector",
            top_k=3,
        )


class FakeSearchClient:
    def __init__(self, *, points: list[Any]) -> None:
        self.points = points
        self.search_calls: list[dict[str, Any]] = []

    def search(
        self,
        *,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        query_filter: Any = None,
        with_payload: bool = True,
    ) -> list[Any]:
        self.search_calls.append(
            {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "query_filter": query_filter,
                "with_payload": with_payload,
            }
        )
        return self.points[:limit]


def fake_point(*, score: float, payload: dict[str, Any]) -> Any:
    return type("FakePoint", (), {"score": score, "payload": payload})()
