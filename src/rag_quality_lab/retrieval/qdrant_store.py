"""Qdrant vector-store boundary for corpus chunks."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from qdrant_client import QdrantClient, models

from rag_quality_lab.config import QdrantConfig
from rag_quality_lab.schemas import Chunk


class QdrantStoreError(Exception):
    """Raised when Qdrant operations fail or receive invalid input."""


def create_qdrant_client(config: QdrantConfig) -> QdrantClient:
    """Create a Qdrant client from validated runtime configuration."""

    return QdrantClient(
        url=config.url,
        api_key=config.api_key.get_secret_value() if config.api_key is not None else None,
    )


class QdrantStore:
    """Small adapter around Qdrant collection and point operations."""

    def __init__(
        self,
        config: QdrantConfig | None = None,
        *,
        client: QdrantClient | None = None,
    ) -> None:
        if client is None and config is None:
            raise QdrantStoreError("QdrantStore requires a config or client")
        self._client = client or create_qdrant_client(config)  # type: ignore[arg-type]

    def check_available(self) -> None:
        """Verify that Qdrant is reachable before writes begin."""

        self._call("check Qdrant availability", self._client.get_collections)

    def ensure_collection(
        self,
        *,
        collection: str,
        vector_size: int,
        recreate: bool = False,
    ) -> None:
        """Create or recreate the target collection with cosine vectors."""

        clean_collection = _clean_collection(collection)
        if vector_size < 1:
            raise QdrantStoreError(f"vector_size must be >= 1, got {vector_size}")

        vectors_config = models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        if recreate:
            self._call(
                "recreate Qdrant collection",
                self._client.recreate_collection,
                collection_name=clean_collection,
                vectors_config=vectors_config,
            )
            return

        exists = self._call(
            "check Qdrant collection",
            self._client.collection_exists,
            collection_name=clean_collection,
        )
        if not exists:
            self._call(
                "create Qdrant collection",
                self._client.create_collection,
                collection_name=clean_collection,
                vectors_config=vectors_config,
            )

    def upsert_chunks(
        self,
        *,
        collection: str,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        """Upsert chunk vectors and metadata payloads into Qdrant."""

        clean_collection = _clean_collection(collection)
        if len(chunks) != len(vectors):
            raise QdrantStoreError(
                f"chunks and vectors must have the same length; got {len(chunks)} chunks and {len(vectors)} vectors"
            )
        if not chunks:
            return 0

        points = [
            models.PointStruct(
                id=_point_id_for_chunk(chunk),
                vector=[float(value) for value in vector],
                payload=_payload_for_chunk(chunk),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self._call(
            "upsert Qdrant points",
            self._client.upsert,
            collection_name=clean_collection,
            points=points,
            wait=True,
        )
        return len(points)

    def _call(self, operation: str, function: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except QdrantStoreError:
            raise
        except Exception as exc:
            raise QdrantStoreError(f"Failed to {operation}: {exc}") from exc


def _clean_collection(collection: str) -> str:
    clean = collection.strip()
    if not clean:
        raise QdrantStoreError("collection must be non-empty")
    return clean


def _point_id_for_chunk(chunk: Chunk) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-quality-lab:{chunk.chunk_id}"))


def _payload_for_chunk(chunk: Chunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "source_slug": chunk.source_slug,
        "category": str(chunk.category),
        "section_path": list(chunk.section_path),
        "ordinal": chunk.ordinal,
        "content": chunk.content,
        "content_hash": chunk.content_hash,
        "estimated_tokens": chunk.estimated_tokens,
        "provenance": chunk.provenance.model_dump(mode="json"),
    }
