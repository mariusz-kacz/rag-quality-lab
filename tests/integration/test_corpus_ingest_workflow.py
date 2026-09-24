from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from qdrant_client import QdrantClient

from rag_quality_lab.corpus.ingest import ingest_corpus
from rag_quality_lab.providers import EmbeddingResponse
from rag_quality_lab.retrieval.qdrant_store import QdrantStore, QdrantStoreError
from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES, Chunk


pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "change",
    [
        "content",
        "chunk_size",
        "source_removed",
        "metadata",
        "model",
        "dimensions",
        "legacy",
        "title",
        "section_heading",
        "body_only_index",
    ],
)
def test_ingestion_requires_explicit_rebuild_for_incompatible_index(
    temporary_corpus: dict[str, Path],
    fake_embedding_provider: Any,
    change: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = temporary_corpus["root"].parent
    kwargs = {
        "project_root": project_root,
        "collection": "rag_quality_lab",
        "embedding_provider": fake_embedding_provider,
    }
    with closing(QdrantClient(":memory:")) as client:
        original = ingest_corpus(**kwargs, qdrant_store=QdrantStore(client=client))
        original_points, _ = client.scroll(
            "rag_quality_lab", limit=1000, with_vectors=True
        )
        assert len(original_points) == original.chunk_count

        store = QdrantStore(client=client)
        ingest_corpus(**kwargs, qdrant_store=store)
        assert client.count("rag_quality_lab", exact=True).count == original.chunk_count

        if change == "content":
            source = temporary_corpus["sources"] / "source-01.md"
            source.write_text("# Changed\n\nReplacement content.\n", encoding="utf-8")
        elif change == "chunk_size":
            kwargs["max_chunk_tokens"] = 5
        elif change in {"source_removed", "metadata", "title"}:
            manifest_path = temporary_corpus["manifest"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if change == "source_removed":
                manifest["sources"].pop()
            elif change == "title":
                manifest["sources"][0]["title"] = "New source title"
            else:
                manifest["sources"][0]["pinned_version"] = "changed-revision"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        elif change == "section_heading":
            source = temporary_corpus["sources"] / "source-01.md"
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "# Source 01", "# New heading"
                ),
                encoding="utf-8",
            )
        elif change == "body_only_index":
            # The previous format embedded only bodies, even for identical chunks.
            old_inputs = {
                "version": 1,
                "chunks": [
                    chunk.model_dump(mode="json")
                    for chunk in sorted(
                        original.ingested_chunks, key=lambda c: c.chunk_id
                    )
                ],
                "max_chunk_tokens": 500,
                "deployment": fake_embedding_provider.deployment,
                "model": original.embedding_model,
                "vector_size": 3,
            }
            old_fingerprint = hashlib.sha256(
                json.dumps(old_inputs, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            client.set_payload(
                "rag_quality_lab",
                payload={"index_fingerprint": old_fingerprint},
                points=[point.id for point in original_points],
                wait=True,
            )
        elif change in {"model", "dimensions"}:
            embed_texts = fake_embedding_provider.embed_texts

            def changed_embeddings(texts: Sequence[str]) -> EmbeddingResponse:
                response = embed_texts(texts)
                if change == "model":
                    return replace(response, model="changed-model")
                return replace(
                    response, vectors=[vector + [1.0] for vector in response.vectors]
                )

            monkeypatch.setattr(
                fake_embedding_provider, "embed_texts", changed_embeddings
            )
        else:
            client.delete_payload(
                "rag_quality_lab",
                keys=["index_fingerprint"],
                points=[original_points[0].id],
                wait=True,
            )

        before, _ = client.scroll("rag_quality_lab", limit=1000, with_vectors=True)
        with pytest.raises(QdrantStoreError, match="--recreate"):
            ingest_corpus(**kwargs, qdrant_store=store)
        after, _ = client.scroll("rag_quality_lab", limit=1000, with_vectors=True)
        assert after == before

        rebuilt = ingest_corpus(**kwargs, qdrant_store=store, recreate=True)
        points, _ = client.scroll("rag_quality_lab", limit=1000)
        assert {point.payload["chunk_id"] for point in points} == {
            chunk.chunk_id for chunk in rebuilt.ingested_chunks
        }
        ingest_corpus(**kwargs, qdrant_store=store)
        assert client.count("rag_quality_lab", exact=True).count == rebuilt.chunk_count


def test_index_fingerprint_survives_qdrant_client_restart(
    temporary_corpus: dict[str, Path],
    fake_embedding_provider: Any,
) -> None:
    project_root = temporary_corpus["root"].parent
    storage_path = project_root / "qdrant"
    kwargs = {
        "project_root": project_root,
        "collection": "rag_quality_lab",
        "embedding_provider": fake_embedding_provider,
    }
    with closing(QdrantClient(path=str(storage_path))) as client:
        original = ingest_corpus(**kwargs, qdrant_store=QdrantStore(client=client))

    with closing(QdrantClient(path=str(storage_path))) as client:
        store = QdrantStore(client=client)
        ingest_corpus(**kwargs, qdrant_store=store)
        source = temporary_corpus["sources"] / "source-01.md"
        source.write_text("# Changed\n\nReplacement content.\n", encoding="utf-8")
        with pytest.raises(QdrantStoreError, match="--recreate"):
            ingest_corpus(**kwargs, qdrant_store=store)
        assert client.count("rag_quality_lab", exact=True).count == original.chunk_count


def test_clean_corpus_inspection_and_fake_qdrant_ingestion_workflow(
    temporary_corpus: dict[str, Path],
    fake_embedding_provider: Any,
    fake_foundry_client: Any,
) -> None:
    inspect_corpus, ingest_corpus = _corpus_workflow_api()
    project_root = temporary_corpus["root"].parent
    qdrant_store = FakeQdrantStore()
    (temporary_corpus["sources"] / "source-01.md").write_text(
        "# Source snapshot\n\nSource metadata: administrative details.\n\n"
        "# Mitigations\n\n## Least privilege\n\n"
        "Restrict tool permissions with application code.\n\n"
        "## Related references and provenance\n\nReference-list summary.\n",
        encoding="utf-8",
    )

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
    assert embedded_texts[0] == (
        "Title: Source 01\nSection: Mitigations > Least privilege\n\n"
        "Restrict tool permissions with application code."
    )
    assert first_chunk.content == "Restrict tool permissions with application code."
    assert len(embedded_texts) == ingestion.chunk_count
    assert all(
        text.endswith(chunk.content)
        for text, chunk in zip(embedded_texts, ingestion.ingested_chunks, strict=True)
    )
    assert all("administrative details" not in text for text in embedded_texts)
    assert all("Reference-list summary" not in text for text in embedded_texts)

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
        index_fingerprint: str,
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
