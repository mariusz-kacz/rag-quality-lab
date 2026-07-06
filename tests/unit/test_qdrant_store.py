from __future__ import annotations

import uuid
from typing import Any

import pytest
from qdrant_client import models

from rag_quality_lab.retrieval.qdrant_store import QdrantStore, QdrantStoreError
from rag_quality_lab.schemas import Chunk, Provenance


pytestmark = pytest.mark.unit


def test_check_available_calls_qdrant_collections_endpoint() -> None:
    client = FakeQdrantClient()
    store = QdrantStore(client=client)

    store.check_available()

    assert client.calls == [("get_collections", {})]


def test_check_available_wraps_client_errors() -> None:
    client = FakeQdrantClient(fail_operation="get_collections")
    store = QdrantStore(client=client)

    with pytest.raises(QdrantStoreError, match="availability"):
        store.check_available()


def test_ensure_collection_recreates_collection_with_cosine_vector_config() -> None:
    client = FakeQdrantClient()
    store = QdrantStore(client=client)

    store.ensure_collection(collection=" rag_quality_lab ", vector_size=3, recreate=True)

    assert client.calls[0][0] == "recreate_collection"
    call = client.calls[0][1]
    assert call["collection_name"] == "rag_quality_lab"
    assert isinstance(call["vectors_config"], models.VectorParams)
    assert call["vectors_config"].size == 3
    assert call["vectors_config"].distance == models.Distance.COSINE


def test_ensure_collection_creates_collection_when_missing() -> None:
    client = FakeQdrantClient(collection_exists=False)
    store = QdrantStore(client=client)

    store.ensure_collection(collection="rag_quality_lab", vector_size=4)

    assert [name for name, _ in client.calls] == [
        "collection_exists",
        "create_collection",
    ]
    assert client.calls[1][1]["vectors_config"].size == 4


def test_ensure_collection_does_not_create_existing_collection() -> None:
    client = FakeQdrantClient(collection_exists=True)
    store = QdrantStore(client=client)

    store.ensure_collection(collection="rag_quality_lab", vector_size=4)

    assert [name for name, _ in client.calls] == ["collection_exists"]


def test_upsert_chunks_maps_chunk_payload_and_stable_point_ids() -> None:
    client = FakeQdrantClient()
    store = QdrantStore(client=client)
    chunk = _chunk()

    count = store.upsert_chunks(
        collection="rag_quality_lab",
        chunks=[chunk],
        vectors=[[0, 1, 2]],
    )

    assert count == 1
    assert client.calls[0][0] == "upsert"
    call = client.calls[0][1]
    assert call["collection_name"] == "rag_quality_lab"
    assert call["wait"] is True
    point = call["points"][0]
    assert uuid.UUID(point.id)
    assert point.id == str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-quality-lab:{chunk.chunk_id}"))
    assert point.vector == [0.0, 1.0, 2.0]
    assert point.payload == {
        "chunk_id": "rag-overview:0000:overview:abcdef123456",
        "source_slug": "rag-overview",
        "category": "RAG and context handling",
        "section_path": ["Overview"],
        "ordinal": 0,
        "content": "RAG grounds answers in retrieved context.",
        "content_hash": "abcdef1234567890",
        "estimated_tokens": 8,
        "provenance": {
            "url": "https://example.test/rag",
            "license": "MIT",
            "pinned_version": "abc123",
            "local_ref": "corpus/sources/rag-overview.md",
        },
    }


def test_upsert_chunks_rejects_vector_count_mismatch() -> None:
    store = QdrantStore(client=FakeQdrantClient())

    with pytest.raises(QdrantStoreError, match="same length"):
        store.upsert_chunks(
            collection="rag_quality_lab",
            chunks=[_chunk()],
            vectors=[],
        )


class FakeQdrantClient:
    def __init__(
        self,
        *,
        collection_exists: bool = False,
        fail_operation: str | None = None,
    ) -> None:
        self._collection_exists = collection_exists
        self._fail_operation = fail_operation
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_collections(self) -> object:
        self._record("get_collections")
        return object()

    def collection_exists(self, *, collection_name: str) -> bool:
        self._record("collection_exists", collection_name=collection_name)
        return self._collection_exists

    def create_collection(
        self,
        *,
        collection_name: str,
        vectors_config: models.VectorParams,
    ) -> bool:
        self._record(
            "create_collection",
            collection_name=collection_name,
            vectors_config=vectors_config,
        )
        return True

    def recreate_collection(
        self,
        *,
        collection_name: str,
        vectors_config: models.VectorParams,
    ) -> bool:
        self._record(
            "recreate_collection",
            collection_name=collection_name,
            vectors_config=vectors_config,
        )
        return True

    def upsert(
        self,
        *,
        collection_name: str,
        points: list[models.PointStruct],
        wait: bool,
    ) -> object:
        self._record(
            "upsert",
            collection_name=collection_name,
            points=points,
            wait=wait,
        )
        return object()

    def _record(self, operation: str, **kwargs: Any) -> None:
        if operation == self._fail_operation:
            raise RuntimeError("boom")
        self.calls.append((operation, kwargs))


def _chunk() -> Chunk:
    return Chunk(
        chunk_id="rag-overview:0000:overview:abcdef123456",
        source_slug="rag-overview",
        category="RAG and context handling",
        section_path=["Overview"],
        ordinal=0,
        content="RAG grounds answers in retrieved context.",
        content_hash="abcdef1234567890",
        estimated_tokens=8,
        provenance=Provenance(
            url="https://example.test/rag",
            license="MIT",
            pinned_version="abc123",
            local_ref="corpus/sources/rag-overview.md",
        ),
    )
