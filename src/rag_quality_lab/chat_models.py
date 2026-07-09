"""LangChain chat model construction for answer generation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
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
        reasoning_effort=config.reasoning_effort,
    )


class FoundryResponsesChatModel:
    """Minimal LangChain-compatible wrapper around OpenAI Responses."""

    def __init__(
        self,
        *,
        model: str,
        client: Any,
        reasoning_effort: str | None = None,
    ) -> None:
        self.model_name = model
        self.deployment_name = model
        self.reasoning_effort = (
            reasoning_effort.strip().lower() if reasoning_effort else None
        )
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
        if self.reasoning_effort is not None:
            request["reasoning"] = {"effort": self.reasoning_effort}
        if max_tokens is not None:
            request["max_output_tokens"] = max_tokens

        try:
            response = self._client.responses.create(**request)
        except Exception as exc:
            raise ProviderError(
                f"Responses request failed for Foundry model {self.model_name!r}: {exc}"
            ) from exc
        content = _response_text(response)
        if not content.strip():
            incomplete_reason = _response_incomplete_reason(response)
            if incomplete_reason is not None:
                raise ProviderError(
                    "Responses request returned no assistant text "
                    f"(status=incomplete, reason={incomplete_reason}). "
                    "Increase --output-token-limit or use a non-reasoning chat model."
                )
        return AIMessage(
            content=content,
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
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = _get(response, "output", []) or []
    parts: list[str] = []
    for item in output:
        for content in _get(item, "content", []) or []:
            text = _get(content, "text")
            if isinstance(text, str):
                parts.append(text)
    if parts:
        return "\n".join(parts)
    return output_text if isinstance(output_text, str) else ""


def _response_model(response: Any) -> str | None:
    model = _get(response, "model")
    return str(model) if model else None


def _response_usage(response: Any) -> dict[str, int]:
    usage = _get(response, "usage")
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
    value = _get(usage, key)
    return int(value) if value is not None else None


def _response_incomplete_reason(response: Any) -> str | None:
    if _get(response, "status") != "incomplete":
        return None
    details = _get(response, "incomplete_details")
    reason = _get(details, "reason")
    return str(reason) if reason else "unknown"


def _get(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(name, default)
    return getattr(source, name, default)
