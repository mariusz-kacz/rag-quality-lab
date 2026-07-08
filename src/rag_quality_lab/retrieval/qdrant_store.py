"""Qdrant vector-store boundary for corpus chunks."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from qdrant_client import QdrantClient, models

from rag_quality_lab.config import QdrantConfig
from rag_quality_lab.retrieval.modes import validate_retrieval_mode
from rag_quality_lab.schemas import Chunk, RetrievalMode, RetrievalResult


class QdrantStoreError(Exception):
    """Raised when Qdrant operations fail or receive invalid input."""


def create_qdrant_client(config: QdrantConfig) -> QdrantClient:
    """Create a Qdrant client from validated runtime configuration."""

    return QdrantClient(
        url=config.url,
        api_key=config.api_key.get_secret_value()
        if config.api_key is not None
        else None,
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

        vectors_config = models.VectorParams(
            size=vector_size, distance=models.Distance.COSINE
        )
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

    def search_chunks(
        self,
        *,
        collection: str,
        query_vector: list[float],
        mode: str,
        top_k: int,
        selected_category: str | None = None,
        fallback_all_categories: bool = False,
    ) -> list[RetrievalResult]:
        result: list[RetrievalResult] = []
        clean_collection = _clean_collection(collection)
        validated_mode = validate_retrieval_mode(mode)

        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        query_filter = None
        if validated_mode == "routed-vector":
            if not fallback_all_categories:
                if selected_category is None:
                    raise ValueError(
                        "selected_category is required for routed-vector when fallback_all_categories is false"
                    )

                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="category",
                            match=models.MatchValue(value=selected_category),
                        )
                    ]
                )

        response = self._call(
            "query Qdrant points",
            self._client.query_points,
            collection_name=clean_collection,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        for index, point in enumerate(response.points, start=1):
            result.append(
                _retrieval_result_from_point(
                    point=point,
                    mode=validated_mode,
                    rank=index,
                )
            )

        return result

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


def _retrieval_result_from_point(
    *,
    point: Any,
    mode: RetrievalMode,
    rank: int,
) -> RetrievalResult:
    payload = point.payload or {}

    try:
        return RetrievalResult(
            mode=mode,
            rank=rank,
            chunk_id=payload["chunk_id"],
            source_slug=payload["source_slug"],
            category=payload["category"],
            section_path=payload["section_path"],
            score=point.score,
            estimated_tokens=payload.get("estimated_tokens"),
            content=payload.get("content"),
        )
    except KeyError as exc:
        missing_field = exc.args[0]
        raise QdrantStoreError(
            "Invalid Qdrant payload for retrieval result "
            f"at rank {rank}: missing {missing_field}"
        ) from exc
    except Exception as exc:
        raise QdrantStoreError(
            f"Invalid Qdrant payload for retrieval result at rank {rank}: {exc}"
        ) from exc


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
