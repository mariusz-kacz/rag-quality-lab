from types import SimpleNamespace

import pytest

from rag_quality_lab.config import AzureOpenAIConfig, MissingSettingError
from rag_quality_lab.providers import (
    AzureOpenAIEmbeddingProvider,
    ProviderError,
)


def azure_config(
    *,
    embedding_deployment: str | None = "text-embedding-3-small",
    chat_deployment: str | None = "gpt-4o-mini",
) -> AzureOpenAIConfig:
    return AzureOpenAIConfig(
        endpoint="https://example.openai.azure.com",
        api_key="test-key",
        api_version="2024-02-15-preview",
        embedding_deployment=embedding_deployment,
        chat_deployment=chat_deployment,
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


def test_embedding_provider_uses_configured_deployment_and_returns_vectors() -> None:
    client = FakeClient()
    provider = AzureOpenAIEmbeddingProvider(azure_config(), client=client)

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
    provider = AzureOpenAIEmbeddingProvider(azure_config(), client=FakeClient())

    with pytest.raises(ProviderError, match="cannot be empty"):
        provider.embed_text(" ")


def test_embedding_provider_requires_embedding_deployment() -> None:
    with pytest.raises(MissingSettingError, match="embeddings"):
        AzureOpenAIEmbeddingProvider(
            azure_config(embedding_deployment=None),
            client=FakeClient(),
        )

