from __future__ import annotations

import pytest

from rag_quality_lab.chat_models import create_azure_chat_model
from rag_quality_lab.config import AzureOpenAIConfig, MissingSettingError


pytestmark = pytest.mark.unit


def azure_config(*, chat_deployment: str | None = "gpt-4o-mini") -> AzureOpenAIConfig:
    return AzureOpenAIConfig(
        endpoint="https://example.openai.azure.com",
        api_key="test-key",
        api_version="2024-02-15-preview",
        embedding_deployment="text-embedding-3-small",
        chat_deployment=chat_deployment,
    )


def test_create_azure_chat_model_uses_langchain_azure_chat_model(monkeypatch) -> None:
    calls = []

    class FakeAzureChatOpenAI:
        def __init__(self, **kwargs) -> None:
            calls.append(kwargs)

    monkeypatch.setattr(
        "rag_quality_lab.chat_models.AzureChatOpenAI", FakeAzureChatOpenAI
    )

    model = create_azure_chat_model(azure_config())

    assert isinstance(model, FakeAzureChatOpenAI)
    assert calls == [
        {
            "azure_deployment": "gpt-4o-mini",
            "api_version": "2024-02-15-preview",
            "azure_endpoint": "https://example.openai.azure.com",
            "api_key": "test-key",
            "temperature": 0.0,
        }
    ]


def test_create_azure_chat_model_requires_chat_deployment() -> None:
    with pytest.raises(MissingSettingError, match="chat"):
        create_azure_chat_model(azure_config(chat_deployment=None))
