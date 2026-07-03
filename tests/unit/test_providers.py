from types import SimpleNamespace

import pytest

from rag_quality_lab.config import AzureOpenAIConfig, MissingSettingError
from rag_quality_lab.providers import (
    AzureOpenAIChatProvider,
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


class FakeChatCompletionsResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None = None,
    ) -> SimpleNamespace:
        self.calls.append(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return SimpleNamespace(
            model=model,
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="Grounded answer [chunk-1]"))
            ],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=4, total_tokens=14),
        )


class FakeClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddingsResource()
        self.chat = SimpleNamespace(completions=FakeChatCompletionsResource())


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


def test_chat_provider_uses_configured_deployment_and_returns_content() -> None:
    client = FakeClient()
    provider = AzureOpenAIChatProvider(azure_config(), client=client)

    result = provider.complete(
        [{"role": "user", "content": "Answer from context only."}],
        temperature=0.1,
        max_tokens=50,
    )

    assert client.chat.completions.calls == [
        {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Answer from context only."}],
            "temperature": 0.1,
            "max_tokens": 50,
        }
    ]
    assert result.content == "Grounded answer [chunk-1]"
    assert result.usage is not None
    assert result.usage.input_tokens == 10
    assert result.usage.output_tokens == 4


def test_chat_provider_requires_non_empty_messages() -> None:
    provider = AzureOpenAIChatProvider(azure_config(), client=FakeClient())

    with pytest.raises(ProviderError, match="at least one message"):
        provider.complete([])


def test_chat_provider_requires_chat_deployment() -> None:
    with pytest.raises(MissingSettingError, match="chat"):
        AzureOpenAIChatProvider(
            azure_config(chat_deployment=None),
            client=FakeClient(),
        )
