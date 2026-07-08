"""Azure OpenAI provider boundary for embeddings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from rag_quality_lab.config import AzureOpenAIConfig


class ProviderError(Exception):
    """Raised when a model provider call fails or returns an unusable response."""


@dataclass(frozen=True)
class TokenUsage:
    """Provider token usage when the SDK response includes it."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class EmbeddingResponse:
    """Normalized embedding provider response."""

    vectors: list[list[float]]
    model: str | None = None
    usage: TokenUsage | None = None


class EmbeddingsResource(Protocol):
    """Subset of the OpenAI embeddings resource used by this app."""

    def create(self, *, model: str, input: list[str]) -> Any: ...


class AzureOpenAIClient(Protocol):
    embeddings: EmbeddingsResource


def create_azure_openai_client(config: AzureOpenAIConfig) -> AzureOpenAIClient:
    """Create the Azure OpenAI SDK client from validated configuration."""

    from openai import AzureOpenAI

    return AzureOpenAI(
        azure_endpoint=config.endpoint,
        api_key=config.api_key.get_secret_value(),
        api_version=config.api_version,
    )


class AzureOpenAIEmbeddingProvider:
    """Embedding provider wrapper backed by an Azure OpenAI deployment."""

    def __init__(
        self,
        config: AzureOpenAIConfig,
        *,
        client: AzureOpenAIClient | None = None,
    ) -> None:
        config.require_embedding()
        self._deployment = _required(
            config.embedding_deployment, "embedding deployment"
        )
        self._client = client or create_azure_openai_client(config)

    @property
    def deployment(self) -> str:
        return self._deployment

    def embed_text(self, text: str) -> list[float]:
        """Embed one text and return the vector."""

        return self.embed_texts([text]).vectors[0]

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse:
        """Embed one or more texts with the configured Azure OpenAI deployment."""

        clean_texts = [_clean_text(text) for text in texts]
        if not clean_texts:
            raise ProviderError("Embedding input must include at least one text")

        response = self._client.embeddings.create(
            model=self._deployment, input=clean_texts
        )
        vectors = [
            _coerce_embedding_vector(item) for item in _get(response, "data", [])
        ]
        if len(vectors) != len(clean_texts):
            raise ProviderError(
                f"Embedding provider returned {len(vectors)} vector(s) for {len(clean_texts)} text(s)"
            )
        return EmbeddingResponse(
            vectors=vectors,
            model=_get(response, "model"),
            usage=_extract_usage(_get(response, "usage")),
        )


def _required(value: str | None, label: str) -> str:
    if not value:
        raise ProviderError(f"Azure OpenAI {label} is required")
    return value


def _clean_text(text: str) -> str:
    clean = text.strip()
    if not clean:
        raise ProviderError("Embedding input text cannot be empty")
    return clean


def _coerce_embedding_vector(item: Any) -> list[float]:
    embedding = _get(item, "embedding")
    if not isinstance(embedding, list) or not embedding:
        raise ProviderError(
            "Embedding provider returned a missing or empty embedding vector"
        )
    try:
        return [float(value) for value in embedding]
    except (TypeError, ValueError) as exc:
        raise ProviderError(
            "Embedding provider returned a non-numeric embedding vector"
        ) from exc


def _extract_usage(usage: Any) -> TokenUsage | None:
    if usage is None:
        return None
    return TokenUsage(
        input_tokens=_get(usage, "prompt_tokens"),
        output_tokens=_get(usage, "completion_tokens"),
        total_tokens=_get(usage, "total_tokens"),
    )


def _get(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(name, default)
    return getattr(source, name, default)
