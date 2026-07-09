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


def test_foundry_responses_chat_model_sends_configured_reasoning_effort() -> None:
    client = FakeFoundryClient()
    chat_model = FoundryResponsesChatModel(
        model="gpt-5.1",
        client=client,
        reasoning_effort="None",
    )

    response = chat_model.invoke([HumanMessage(content="What is RAG?")])

    assert response.content == "RAG uses retrieved context. [chunk-1]"
    assert client.responses.calls == [
        {
            "model": "gpt-5.1",
            "input": [{"role": "user", "content": "What is RAG?"}],
            "reasoning": {"effort": "none"},
        }
    ]


def test_foundry_responses_chat_model_extracts_dict_shaped_output() -> None:
    client = FakeFoundryClient(
        response={
            "output_text": "",
            "model": "gpt-4o-mini",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Use explicit no-answer behavior. [chunk-1]",
                        }
                    ],
                }
            ],
            "usage": {
                "input_tokens": 12,
                "output_tokens": 6,
                "total_tokens": 18,
            },
        }
    )
    chat_model = FoundryResponsesChatModel(model="gpt-4o-mini", client=client)

    response = chat_model.invoke([HumanMessage(content="What should RAG do?")])

    assert response.content == "Use explicit no-answer behavior. [chunk-1]"
    assert response.usage_metadata == {
        "input_tokens": 12,
        "output_tokens": 6,
        "total_tokens": 18,
    }


def test_foundry_responses_chat_model_reports_incomplete_empty_response() -> None:
    client = FakeFoundryClient(
        response=SimpleNamespace(
            output_text="",
            model="gpt-4o-mini",
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            output=[SimpleNamespace(type="reasoning", content=[])],
            usage=SimpleNamespace(
                input_tokens=15,
                output_tokens=500,
                total_tokens=515,
            ),
        )
    )
    chat_model = FoundryResponsesChatModel(model="gpt-4o-mini", client=client)

    with pytest.raises(ProviderError, match="max_output_tokens"):
        chat_model.invoke([HumanMessage(content="What is RAG?")])


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
    def __init__(self, response=None) -> None:
        self.calls: list[dict[str, object]] = []
        self.response = response

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.response is not None:
            return self.response
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
    def __init__(self, response=None) -> None:
        self.responses = FakeResponsesResource(response)


class FailingResponsesResource:
    def create(self, **kwargs):
        raise RuntimeError("not found")


class FailingFoundryClient:
    def __init__(self) -> None:
        self.responses = FailingResponsesResource()
