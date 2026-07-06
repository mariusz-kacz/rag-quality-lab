"""Corpus ingestion orchestration for validated chunks and Qdrant writes."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from pydantic import SecretStr

from rag_quality_lab.config import (
    MissingSettingError,
    QdrantConfig,
    load_azure_openai_config,
    load_qdrant_config,
)
from rag_quality_lab.corpus.chunking import DEFAULT_MAX_CHUNK_TOKENS, chunk_source_page
from rag_quality_lab.corpus.manifest import (
    DEFAULT_CATEGORIES_PATH,
    DEFAULT_MANIFEST_PATH,
    ManifestValidationError,
    load_categories,
    load_manifest,
)
from rag_quality_lab.providers import AzureOpenAIEmbeddingProvider, EmbeddingResponse
from rag_quality_lab.retrieval.qdrant_store import QdrantStore
from rag_quality_lab.schemas import Chunk, IngestionSummaryArtifact


class IngestionError(Exception):
    """Raised when ingestion cannot produce a validated write batch."""


class EmbeddingProvider(Protocol):
    """Embedding provider behavior required by corpus ingestion."""

    @property
    def deployment(self) -> str: ...

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse: ...


class ChunkVectorStore(Protocol):
    """Vector-store behavior required by corpus ingestion."""

    def ensure_collection(
        self,
        *,
        collection: str,
        vector_size: int,
        recreate: bool = False,
    ) -> None: ...

    def upsert_chunks(
        self,
        *,
        collection: str,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> int: ...


def ingest_corpus(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    categories_path: str | Path = DEFAULT_CATEGORIES_PATH,
    *,
    project_root: str | Path | None = None,
    collection: str | None = None,
    recreate: bool = False,
    embedding_provider: EmbeddingProvider | None = None,
    qdrant_store: ChunkVectorStore | None = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
) -> IngestionSummaryArtifact:
    """Validate, chunk, embed, and write the curated corpus to Qdrant."""

    root = Path(project_root).resolve() if project_root is not None else Path.cwd().resolve()
    target_collection = _resolve_collection(collection)

    manifest = _load_validated_inputs(
        manifest_path,
        categories_path,
        project_root=root,
    )
    chunks = _build_chunks(manifest.sources, project_root=root, max_chunk_tokens=max_chunk_tokens)
    if not chunks:
        raise IngestionError("No corpus chunks were generated; ingestion cannot continue")

    provider = embedding_provider or _create_embedding_provider()
    embedding_response = provider.embed_texts([chunk.content for chunk in chunks])
    vectors = _validate_vectors(embedding_response.vectors, expected_count=len(chunks))

    store = qdrant_store or _create_qdrant_store(collection=target_collection)
    vector_size = len(vectors[0])
    store.ensure_collection(
        collection=target_collection,
        vector_size=vector_size,
        recreate=recreate,
    )
    upserted_count = store.upsert_chunks(
        collection=target_collection,
        chunks=chunks,
        vectors=vectors,
    )
    if upserted_count != len(chunks):
        raise IngestionError(
            f"Qdrant upsert wrote {upserted_count} chunk(s), expected {len(chunks)}"
        )

    return IngestionSummaryArtifact(
        collection=target_collection,
        source_count=manifest.source_count,
        chunk_count=len(chunks),
        category_counts=manifest.category_counts,
        embedding_model=embedding_response.model or provider.deployment,
        ingested_chunks=chunks,
        validation_errors=[],
    )


def _load_validated_inputs(
    manifest_path: str | Path,
    categories_path: str | Path,
    *,
    project_root: Path,
):
    try:
        manifest = load_manifest(manifest_path, project_root=project_root)
        load_categories(categories_path, project_root=project_root)
    except ManifestValidationError as exc:
        raise IngestionError(f"Corpus validation failed before write: {exc}") from exc
    return manifest


def _build_chunks(
    sources,
    *,
    project_root: Path,
    max_chunk_tokens: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for source in sources:
        source_path = (project_root / source.local_ref).resolve()
        try:
            source_path.relative_to(project_root)
        except ValueError as exc:
            raise IngestionError(
                f"Source snapshot for {source.source_slug} escapes project root: {source.local_ref}"
            ) from exc
        try:
            markdown = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise IngestionError(
                f"Source snapshot for {source.source_slug} could not be read: {source.local_ref}"
            ) from exc
        chunks.extend(
            chunk_source_page(
                source,
                markdown,
                max_chunk_tokens=max_chunk_tokens,
            )
        )
    return chunks


def _validate_vectors(vectors: Sequence[Sequence[float]], *, expected_count: int) -> list[list[float]]:
    if len(vectors) != expected_count:
        raise IngestionError(
            f"Embedding provider returned {len(vectors)} vector(s), expected {expected_count}"
        )
    normalized_vectors = [[float(value) for value in vector] for vector in vectors]
    vector_sizes = {len(vector) for vector in normalized_vectors}
    if not vector_sizes or 0 in vector_sizes:
        raise IngestionError("Embedding provider returned an empty vector")
    if len(vector_sizes) != 1:
        raise IngestionError(
            f"Embedding provider returned inconsistent vector dimensions: {sorted(vector_sizes)}"
        )
    return normalized_vectors


def _create_embedding_provider() -> AzureOpenAIEmbeddingProvider:
    config = load_azure_openai_config(require_embedding=True, require_chat=False)
    return AzureOpenAIEmbeddingProvider(config)


def _create_qdrant_store(*, collection: str) -> QdrantStore:
    config = _load_qdrant_config(collection=collection)
    return QdrantStore(config)


def _load_qdrant_config(*, collection: str) -> QdrantConfig:
    if os.environ.get("RAGLAB_QDRANT_COLLECTION", "").strip():
        config = load_qdrant_config()
        return config.model_copy(update={"collection": collection})

    url = os.environ.get("QDRANT_URL", "").strip()
    if not url:
        raise MissingSettingError(["QDRANT_URL"], stage="Qdrant")
    api_key = os.environ.get("QDRANT_API_KEY", "").strip()
    return QdrantConfig(
        url=url,
        api_key=SecretStr(api_key) if api_key else None,
        collection=collection,
    )


def _resolve_collection(collection: str | None) -> str:
    if collection is None:
        env_collection = os.environ.get("RAGLAB_QDRANT_COLLECTION", "").strip()
        if not env_collection:
            raise MissingSettingError(["RAGLAB_QDRANT_COLLECTION"], stage="Qdrant")
        return env_collection
    clean_collection = collection.strip()
    if not clean_collection:
        raise IngestionError("collection must be non-empty")
    return clean_collection
