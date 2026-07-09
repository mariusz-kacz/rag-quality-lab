from __future__ import annotations

from types import SimpleNamespace

from langchain_core.messages import HumanMessage, SystemMessage
import pytest

from rag_quality_lab.chat_models import (
    FoundryResponsesChatModel,
    create_foundry_chat_model,
)
from rag_quality_lab.config import (
    FoundryOpenAIConfig,
    MissingSettingError,
)
from rag_quality_lab.providers import ProviderError


pytestmark = pytest.mark.unit


def foundry_config(*, chat_model: str | None = "gpt-4o-mini") -> FoundryOpenAIConfig:
    return FoundryOpenAIConfig(
        base_url="https://example.services.ai.azure.com/api/projects/proj/openai/v1",
        api_key="test-key",
        embedding_model="text-embedding-3-small",
        chat_model=chat_model,
    )


def test_foundry_responses_chat_model_invokes_responses_api() -> None:
    client = FakeFoundryClient()
    chat_model = FoundryResponsesChatModel(model="gpt-4o-mini", client=client)

    response = chat_model.invoke(
        [
            SystemMessage(content="Answer from context."),
            HumanMessage(content="What is RAG?"),
        ],
        max_tokens=120,
    )

    assert response.content == "RAG uses retrieved context. [chunk-1]"
    assert response.response_metadata == {"model_name": "gpt-4o-mini"}
    assert response.usage_metadata == {
        "input_tokens": 15,
        "output_tokens": 7,
        "total_tokens": 22,
    }
    assert client.responses.calls == [
        {
            "model": "gpt-4o-mini",
            "input": [
                {"role": "system", "content": "Answer from context."},
                {"role": "user", "content": "What is RAG?"},
            ],
            "max_output_tokens": 120,
        }
    ]


def test_foundry_responses_chat_model_wraps_sdk_errors() -> None:
    chat_model = FoundryResponsesChatModel(
        model="gpt-4o-mini",
        client=FailingFoundryClient(),
    )

    with pytest.raises(ProviderError, match="Responses request failed"):
        chat_model.invoke([HumanMessage(content="What is RAG?")], max_tokens=120)


def test_create_foundry_chat_model_requires_chat_model() -> None:
    with pytest.raises(MissingSettingError, match="Foundry chat"):
        create_foundry_chat_model(foundry_config(chat_model=None))


class FakeResponsesResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text="RAG uses retrieved context. [chunk-1]",
            model=kwargs["model"],
            usage=SimpleNamespace(
                input_tokens=15,
                output_tokens=7,
                total_tokens=22,
            ),
        )


class FakeFoundryClient:
    def __init__(self) -> None:
        self.responses = FakeResponsesResource()


class FailingResponsesResource:
    def create(self, **kwargs):
        raise RuntimeError("not found")


class FailingFoundryClient:
    def __init__(self) -> None:
        self.responses = FailingResponsesResource()
