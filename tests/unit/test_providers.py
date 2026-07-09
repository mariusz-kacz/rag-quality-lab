from types import SimpleNamespace

import pytest

from rag_quality_lab.config import (
    FoundryOpenAIConfig,
    MissingSettingError,
)
from rag_quality_lab.providers import (
    FoundryOpenAIEmbeddingProvider,
    ProviderError,
)


def foundry_config(
    *,
    embedding_model: str | None = "text-embedding-3-small",
    chat_model: str | None = "gpt-4o-mini",
) -> FoundryOpenAIConfig:
    return FoundryOpenAIConfig(
        base_url="https://example.services.ai.azure.com/api/projects/proj/openai/v1",
        api_key="test-key",
        embedding_model=embedding_model,
        chat_model=chat_model,
    )


class FakeEmbeddingsResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, *, model: str, input: list[str]) -> SimpleNamespace:
        self.calls.append({"model": model, "input": input})
        return SimpleNamespace(
            model=model,
            data=[
                SimpleNamespace(embedding=[float(index), float(index + 1)])
                for index, _ in enumerate(input)
            ],
            usage=SimpleNamespace(prompt_tokens=3, total_tokens=3),
        )


class FakeClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddingsResource()


class FailingEmbeddingsResource:
    def create(self, *, model: str, input: list[str]) -> SimpleNamespace:
        raise RuntimeError("not found")


class FailingClient:
    def __init__(self) -> None:
        self.embeddings = FailingEmbeddingsResource()


def test_foundry_embedding_provider_uses_configured_model() -> None:
    client = FakeClient()
    provider = FoundryOpenAIEmbeddingProvider(foundry_config(), client=client)

    result = provider.embed_texts([" first ", "second"])

    assert client.embeddings.calls == [
        {"model": "text-embedding-3-small", "input": ["first", "second"]}
    ]
    assert result.vectors == [[0.0, 1.0], [1.0, 2.0]]
    assert result.model == "text-embedding-3-small"
    assert result.usage is not None
    assert result.usage.input_tokens == 3
    assert result.usage.total_tokens == 3


def test_embedding_provider_rejects_empty_text() -> None:
    provider = FoundryOpenAIEmbeddingProvider(foundry_config(), client=FakeClient())

    with pytest.raises(ProviderError, match="cannot be empty"):
        provider.embed_text(" ")


def test_foundry_embedding_provider_wraps_sdk_errors() -> None:
    provider = FoundryOpenAIEmbeddingProvider(
        foundry_config(),
        client=FailingClient(),
    )

    with pytest.raises(ProviderError, match="Foundry model"):
        provider.embed_text("hello")


def test_foundry_embedding_provider_requires_embedding_model() -> None:
    with pytest.raises(MissingSettingError, match="Foundry embeddings"):
        FoundryOpenAIEmbeddingProvider(
            foundry_config(embedding_model=None),
            client=FakeClient(),
        )
