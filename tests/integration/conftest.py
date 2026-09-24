"""Offline query services shared by evaluation workflow tests."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage
from qdrant_client import QdrantClient, models

from rag_quality_lab.config import AppConfig, FoundryOpenAIConfig, QdrantConfig
from rag_quality_lab.providers import EmbeddingResponse
from rag_quality_lab.retrieval.qdrant_store import QdrantStore

pytestmark = pytest.mark.integration


@pytest.fixture
def capture_env(tmp_path, monkeypatch):
    client = QdrantClient(":memory:")
    store = QdrantStore(client=client)
    store.ensure_collection(collection="capture", vector_size=2)
    data = json.loads(Path("golden/questions.json").read_text())
    sources = sorted(
        {s for q in data["questions"] for s in q["expected_relevant_sources"]}
    )
    client.upsert(
        "capture",
        [
            models.PointStruct(
                id=i,
                vector=[1.0, 0.0],
                payload={
                    "chunk_id": f"{source}:chunk",
                    "source_slug": source,
                    "index_fingerprint": "stored-fingerprint",
                    "category": "prompting techniques",
                    "section_path": ["Section"],
                    "content": "Evidence from the index.",
                    "estimated_tokens": 8,
                },
            )
            for i, source in enumerate(sources)
        ],
    )
    config = AppConfig(
        foundry_openai=FoundryOpenAIConfig(
            base_url="https://example.test/openai/v1",
            api_key="secret-key",
            chat_model="generator",
            embedding_model="embedding",
        ),
        qdrant=QdrantConfig(url="http://localhost:6333", collection="capture"),
    )
    state = SimpleNamespace(
        client=client,
        store=store,
        config=config,
        data=data,
        opened=[],
        closed=[],
        category_calls=0,
        query_calls=0,
        fail_at=None,
        setup_fail=False,
    )

    class Embeddings:
        def __init__(self, config):
            state.opened.append("embedding")

        def embed_text(self, text):
            state.query_calls += 1
            if state.query_calls == state.fail_at:
                raise RuntimeError("secret-key bearer-token")
            return [1.0, 0.0]

        def embed_texts(self, texts):
            if len(texts) == 5:
                state.category_calls += 1
            return EmbeddingResponse(vectors=[[1.0, 0.0] for _ in texts])

        def close(self):
            state.closed.append("embedding")

    class Chat:
        def invoke(self, messages, **kwargs):
            return AIMessage(
                content="Evidence from the index. [C1]",
                usage_metadata={
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                },
                response_metadata={"model_name": "reported-model"},
            )

        def close(self):
            state.closed.append("chat")

    def create_chat(config):
        if state.setup_fail:
            raise RuntimeError("secret-key")
        state.opened.append("chat")
        return Chat()

    monkeypatch.setattr(
        "rag_quality_lab.rag.pipeline.FoundryOpenAIEmbeddingProvider", Embeddings
    )
    monkeypatch.setattr(
        "rag_quality_lab.rag.pipeline.create_foundry_chat_model", create_chat
    )
    monkeypatch.setattr(
        "rag_quality_lab.retrieval.qdrant_store.create_qdrant_client",
        lambda config: client,
    )
    # Factory-owned adapters still exercise cleanup, but the fixture owns this local client.
    monkeypatch.setattr(client, "close", lambda: state.closed.append("store"))
    yield state
    client._client.close()
