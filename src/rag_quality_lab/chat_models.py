"""LangChain chat model construction for answer generation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from rag_quality_lab.config import FoundryOpenAIConfig
from rag_quality_lab.providers import ProviderError, create_foundry_openai_client


def create_foundry_chat_model(
    config: FoundryOpenAIConfig,
) -> "FoundryResponsesChatModel":
    """Create a chat boundary backed by a Foundry OpenAI v1 Responses endpoint."""

    config.require_chat()
    return FoundryResponsesChatModel(
        model=config.chat_model or "",
        client=create_foundry_openai_client(config),
    )


class FoundryResponsesChatModel:
    """Minimal LangChain-compatible wrapper around OpenAI Responses."""

    def __init__(self, *, model: str, client: Any) -> None:
        self.model_name = model
        self.deployment_name = model
        self._client = client

    def invoke(
        self,
        input: Sequence[BaseMessage],
        config: Any | None = None,
        *,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        request: dict[str, Any] = {
            "model": self.model_name,
            "input": _responses_input(input),
        }
        if max_tokens is not None:
            request["max_output_tokens"] = max_tokens

        try:
            response = self._client.responses.create(**request)
        except Exception as exc:
            raise ProviderError(
                f"Responses request failed for Foundry model {self.model_name!r}: {exc}"
            ) from exc
        return AIMessage(
            content=_response_text(response),
            response_metadata={
                "model_name": _response_model(response) or self.model_name
            },
            usage_metadata=_response_usage(response),
        )


def _responses_input(messages: Sequence[BaseMessage]) -> list[dict[str, str]]:
    return [
        {
            "role": _response_role(message),
            "content": _message_content(message),
        }
        for message in messages
    ]


def _response_role(message: BaseMessage) -> str:
    if message.type == "system":
        return "system"
    if message.type == "ai":
        return "assistant"
    return "user"


def _message_content(message: BaseMessage) -> str:
    if isinstance(message.content, str):
        return message.content
    return str(message.content)


def _response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    output = getattr(response, "output", None) or []
    parts: list[str] = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def _response_model(response: Any) -> str | None:
    model = getattr(response, "model", None)
    return str(model) if model else None


def _response_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    input_tokens = _usage_value(usage, "input_tokens")
    output_tokens = _usage_value(usage, "output_tokens")
    total_tokens = _usage_value(usage, "total_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    return {
        key: value
        for key, value in {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }.items()
        if value is not None
    }


def _usage_value(usage: Any, key: str) -> int | None:
    if isinstance(usage, dict):
        value = usage.get(key)
    else:
        value = getattr(usage, key, None)
    return int(value) if value is not None else None
