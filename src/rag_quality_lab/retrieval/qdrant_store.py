"""Qdrant vector-store boundary for corpus chunks."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient, models

from rag_quality_lab.config import QdrantConfig
from rag_quality_lab.retrieval.modes import validate_retrieval_mode
from rag_quality_lab.schemas import Chunk, RetrievalMode, RetrievalResult


class QdrantStoreError(Exception):
    """Raised when Qdrant operations fail or receive invalid input."""


class IndexInventoryError(QdrantStoreError):
    """Index validation failure with a safe, actionable message for the user."""


@dataclass(frozen=True)
class IndexInventory:
    """Identity and complete chunk/source mapping read from the active index."""

    index_fingerprint: str
    chunk_sources: dict[str, str]


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
        self._owns_client = client is None
        if client is None:
            assert config is not None
            client = create_qdrant_client(config)
        self._client = client

    def close(self) -> None:
        """Close a factory-created client once; injected clients remain caller-owned."""
        if self._owns_client:
            self._client.close()
            self._owns_client = False

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
        index_fingerprint: str,
    ) -> int:
        """Upsert a complete corpus only into an empty or compatible index."""

        clean_collection = _clean_collection(collection)
        if len(chunks) != len(vectors):
            raise QdrantStoreError(
                f"chunks and vectors must have the same length; got {len(chunks)} chunks and {len(vectors)} vectors"
            )
        if not chunks:
            return 0

        if not index_fingerprint.strip():
            raise QdrantStoreError("index_fingerprint must be non-empty")
        incompatible = self._call(
            "check Qdrant index fingerprint",
            self._client.count,
            collection_name=clean_collection,
            count_filter=models.Filter(
                must_not=[
                    models.FieldCondition(
                        key="index_fingerprint",
                        match=models.MatchValue(value=index_fingerprint),
                    )
                ]
            ),
            exact=True,
        )
        if incompatible.count:
            raise QdrantStoreError(
                f"Collection {clean_collection!r} contains an incompatible or missing "
                "index fingerprint. Run corpus ingest --recreate to rebuild it."
            )

        points = [
            models.PointStruct(
                id=_point_id_for_chunk(chunk),
                vector=[float(value) for value in vector],
                payload={
                    **_payload_for_chunk(chunk),
                    "index_fingerprint": index_fingerprint,
                },
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

    def inventory(self, *, collection: str, page_size: int = 256) -> IndexInventory:
        """Read payloads without vectors or writes; require a homogeneous index."""
        clean_collection = _clean_collection(collection)
        if page_size < 1:
            raise QdrantStoreError("page_size must be >= 1")
        offset = None
        chunk_sources: dict[str, str] = {}
        fingerprints: set[str] = set()
        while True:
            points, offset = self._call(
                "read Qdrant inventory",
                self._client.scroll,
                collection_name=clean_collection,
                limit=page_size,
                offset=offset,
                with_payload=["chunk_id", "source_slug", "index_fingerprint"],
                with_vectors=False,
            )
            for point in points:
                payload = point.payload or {}
                missing = [
                    key
                    for key in ("chunk_id", "source_slug", "index_fingerprint")
                    if not isinstance(payload.get(key), str) or not payload[key].strip()
                ]
                if missing:
                    raise IndexInventoryError(
                        f"Qdrant index has chunks missing {', '.join(missing)}. "
                        "Re-ingest into a new collection, or run corpus ingest --recreate "
                        "to replace the current collection before evaluation."
                    )
                chunk_id = payload["chunk_id"]
                source_slug = payload["source_slug"]
                fingerprint = payload["index_fingerprint"]
                if chunk_id in chunk_sources:
                    raise IndexInventoryError(
                        "Qdrant index contains duplicate chunk IDs. "
                        "Rebuild it with corpus ingest --recreate before evaluation."
                    )
                chunk_sources[chunk_id] = source_slug
                fingerprints.add(fingerprint)
            if offset is None:
                break
        if not chunk_sources:
            raise IndexInventoryError(
                "Qdrant collection is empty. Run corpus ingest before evaluation."
            )
        if len(fingerprints) != 1:
            raise IndexInventoryError(
                "Qdrant collection contains mixed index fingerprints. "
                "Rebuild it with corpus ingest --recreate before evaluation."
            )
        return IndexInventory(fingerprints.pop(), chunk_sources)

    def search_chunks(
        self,
        *,
        collection: str,
        query_vector: list[float],
        mode: str,
        top_k: int,
        selected_category: str | None = None,
        selected_categories: Sequence[str] | None = None,
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
                categories = _selected_categories(
                    selected_category=selected_category,
                    selected_categories=selected_categories,
                )
                if not categories:
                    raise ValueError(
                        "selected_category is required for routed-vector when fallback_all_categories is false"
                    )

                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="category",
                            match=_category_match(categories),
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


def _selected_categories(
    *,
    selected_category: str | None,
    selected_categories: Sequence[str] | None,
) -> list[str]:
    raw_categories = (
        list(selected_categories)
        if selected_categories is not None
        else ([selected_category] if selected_category is not None else [])
    )
    categories: list[str] = []
    for category in raw_categories:
        clean = category.strip()
        if clean and clean not in categories:
            categories.append(clean)
    return categories


def _category_match(categories: Sequence[str]) -> Any:
    if len(categories) == 1:
        return models.MatchValue(value=categories[0])
    return models.MatchAny(any=list(categories))


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
