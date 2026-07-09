"""Foundry OpenAI-compatible provider boundary for embeddings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from rag_quality_lab.config import FoundryOpenAIConfig


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


class OpenAICompatibleClient(Protocol):
    embeddings: EmbeddingsResource


def create_foundry_openai_client(config: FoundryOpenAIConfig) -> OpenAICompatibleClient:
    """Create an OpenAI-compatible client for a Foundry project endpoint."""

    from openai import OpenAI

    return OpenAI(
        base_url=config.base_url,
        api_key=_foundry_api_key(config),
    )


class FoundryOpenAIEmbeddingProvider:
    """Embedding provider backed by a Foundry project OpenAI v1 endpoint."""

    def __init__(
        self,
        config: FoundryOpenAIConfig,
        *,
        client: OpenAICompatibleClient | None = None,
    ) -> None:
        config.require_embedding()
        self._model = _required(config.embedding_model, "embedding model")
        self._client = client or create_foundry_openai_client(config)

    @property
    def deployment(self) -> str:
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Embed one text and return the vector."""

        return self.embed_texts([text]).vectors[0]

    def embed_texts(self, texts: Sequence[str]) -> EmbeddingResponse:
        """Embed one or more texts with the configured Foundry model."""

        clean_texts = [_clean_text(text) for text in texts]
        if not clean_texts:
            raise ProviderError("Embedding input must include at least one text")

        try:
            response = self._client.embeddings.create(
                model=self._model, input=clean_texts
            )
        except Exception as exc:
            raise ProviderError(
                f"Embedding request failed for Foundry model {self._model!r}: {exc}"
            ) from exc
        vectors = [
            _coerce_embedding_vector(item) for item in _get(response, "data", [])
        ]
        if len(vectors) != len(clean_texts):
            raise ProviderError(
                f"Embedding provider returned {len(vectors)} vector(s) for {len(clean_texts)} text(s)"
            )
        return EmbeddingResponse(
            vectors=vectors,
            model=_get(response, "model") or self._model,
            usage=_extract_usage(_get(response, "usage")),
        )


def _required(value: str | None, label: str) -> str:
    if not value:
        raise ProviderError(f"Model provider {label} is required")
    return value


def _foundry_api_key(config: FoundryOpenAIConfig) -> str:
    if config.api_key is not None:
        return config.api_key.get_secret_value()
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:
        raise ProviderError(
            "Foundry Entra ID authentication requires azure-identity. "
            "Install dependencies with `uv sync`."
        ) from exc

    credential = DefaultAzureCredential()
    return credential.get_token("https://cognitiveservices.azure.com/.default").token


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
