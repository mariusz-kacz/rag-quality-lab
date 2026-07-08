"""LangChain chat model construction for answer generation."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from rag_quality_lab.config import AzureOpenAIConfig


def create_azure_chat_model(config: AzureOpenAIConfig) -> BaseChatModel:
    """Create the LangChain Azure chat model used by generation."""

    config.require_chat()
    return AzureChatOpenAI(
        azure_deployment=config.chat_deployment,
        api_version=config.api_version,
        azure_endpoint=config.endpoint,
        api_key=config.api_key.get_secret_value(),
        temperature=0.0,
    )
