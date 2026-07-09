from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES, Chunk


pytestmark = pytest.mark.integration


def test_clean_corpus_inspection_and_fake_qdrant_ingestion_workflow(
    temporary_corpus: dict[str, Path],
    fake_embedding_provider: Any,
    fake_foundry_client: Any,
) -> None:
    inspect_corpus, ingest_corpus = _corpus_workflow_api()
    project_root = temporary_corpus["root"].parent
    qdrant_store = FakeQdrantStore()

    inspection = inspect_corpus(project_root=project_root)

    assert inspection.source_count == 15
    assert inspection.validation_errors == []
    assert inspection.license_summary == {"MIT": 15}
    assert inspection.pinned_version == "dair-ai-prompt-guide@abc123"
    assert inspection.categories == {
        category: 3 for category in REQUIRED_KNOWLEDGE_CATEGORIES
    }
    assert all(
        source.local_ref.startswith("corpus/sources/") for source in inspection.sources
    )

    ingestion = ingest_corpus(
        project_root=project_root,
        collection="rag_quality_lab",
        recreate=True,
        embedding_provider=fake_embedding_provider,
        qdrant_store=qdrant_store,
    )

    assert ingestion.collection == "rag_quality_lab"
    assert ingestion.source_count == inspection.source_count
    assert ingestion.chunk_count == len(ingestion.ingested_chunks)
    assert ingestion.chunk_count >= inspection.source_count
    assert ingestion.category_counts == {
        category: 3 for category in REQUIRED_KNOWLEDGE_CATEGORIES
    }
    assert ingestion.embedding_model == "embedding-test"
    assert ingestion.validation_errors == []

    first_chunk = ingestion.ingested_chunks[0]
    assert first_chunk.chunk_id
    assert first_chunk.source_slug == "source-01"
    assert first_chunk.category == "prompting techniques"
    assert first_chunk.section_path
    assert first_chunk.content_hash
    assert first_chunk.estimated_tokens > 0
    assert first_chunk.provenance.url == "https://example.test/prompt-guide/source-01"
    assert first_chunk.provenance.license == "MIT"
    assert first_chunk.provenance.pinned_version == "dair-ai-prompt-guide@abc123"
    assert first_chunk.provenance.local_ref == "corpus/sources/source-01.md"

    assert fake_foundry_client.embeddings.calls
    embedded_texts = fake_foundry_client.embeddings.calls[0]["input"]
    assert embedded_texts == [chunk.content for chunk in ingestion.ingested_chunks]

    assert qdrant_store.operations == ["ensure_collection", "upsert_chunks"]
    assert qdrant_store.ensure_calls == [
        {
            "collection": "rag_quality_lab",
            "vector_size": 3,
            "recreate": True,
        }
    ]
    assert len(qdrant_store.upserted_chunks) == ingestion.chunk_count
    assert len(qdrant_store.upserted_vectors) == ingestion.chunk_count
    assert qdrant_store.upserted_chunks[0] == first_chunk


class FakeQdrantStore:
    def __init__(self) -> None:
        self.operations: list[str] = []
        self.ensure_calls: list[dict[str, object]] = []
        self.upserted_chunks: list[Chunk] = []
        self.upserted_vectors: list[list[float]] = []

    def ensure_collection(
        self,
        *,
        collection: str,
        vector_size: int,
        recreate: bool = False,
    ) -> None:
        self.operations.append("ensure_collection")
        self.ensure_calls.append(
            {
                "collection": collection,
                "vector_size": vector_size,
                "recreate": recreate,
            }
        )

    def upsert_chunks(
        self,
        *,
        collection: str,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> int:
        self.operations.append("upsert_chunks")
        assert collection == "rag_quality_lab"
        assert len(chunks) == len(vectors)
        self.upserted_chunks.extend(chunks)
        self.upserted_vectors.extend([list(vector) for vector in vectors])
        return len(chunks)


def _corpus_workflow_api() -> tuple[Any, Any]:
    from rag_quality_lab.corpus.ingest import ingest_corpus
    from rag_quality_lab.corpus.inspect import inspect_corpus

    return inspect_corpus, ingest_corpus
