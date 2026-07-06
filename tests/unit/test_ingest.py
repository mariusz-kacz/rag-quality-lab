from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from rag_quality_lab.corpus.ingest import IngestionError, ingest_corpus
from rag_quality_lab.providers import EmbeddingResponse
from rag_quality_lab.schemas import Chunk


pytestmark = pytest.mark.unit


def test_ingest_validates_embeddings_before_qdrant_write(
    temporary_corpus: dict[str, Path],
) -> None:
    store = RecordingStore()

    with pytest.raises(IngestionError, match="Embedding provider returned 1 vector"):
        ingest_corpus(
            project_root=temporary_corpus["root"].parent,
            collection="rag_quality_lab",
            embedding_provider=ShortEmbeddingProvider(),
            qdrant_store=store,
        )

    assert store.operations == []


class ShortEmbeddingProvider:
    @property
    def deployment(self) -> str:
        return "embedding-test"

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse:
        assert texts
        return EmbeddingResponse(vectors=[[1.0, 2.0, 3.0]], model="embedding-test")


class RecordingStore:
    def __init__(self) -> None:
        self.operations: list[str] = []

    def ensure_collection(
        self,
        *,
        collection: str,
        vector_size: int,
        recreate: bool = False,
    ) -> None:
        self.operations.append("ensure_collection")

    def upsert_chunks(
        self,
        *,
        collection: str,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        self.operations.append("upsert_chunks")
        return len(chunks)
