from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from rag_quality_lab.providers import ProviderError
from rag_quality_lab.rag.citations import citation_aliases_for_context, validate_citations
from rag_quality_lab.schemas import (
    AnswerResult,
    ContextChunk,
    GenerationResult,
    ModelUsage,
    Question,
    SelectedContext,
)


NO_ANSWER_TEXT = "There is not enough evidence in the selected context to answer."

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using only the selected context. Cite every factual claim with "
            "the citation labels shown in square brackets, for example [C1]. Do not "
            "cite source names or chunk ids. Keep the answer concise: use at most "
            "five bullets or three short paragraphs, and prefer one or two citations "
            "per sentence. If the selected context is insufficient, say exactly: "
            f"{NO_ANSWER_TEXT}",
        ),
        (
            "human",
            "Question:\n{question}\n\nSelected context:\n{selected_context}",
        ),
    ]
)


class ChatModel(Protocol):
    """LangChain-compatible chat model boundary used by generation."""

    def invoke(
        self,
        input: Sequence[BaseMessage],
        config: Any | None = None,
        **kwargs: Any,
    ) -> BaseMessage:
        ...


def generate_answer(
    *,
    question: Question,
    selected_context: SelectedContext,
    chat_model: ChatModel,
) -> GenerationResult:
    """Generate a cited answer from selected chunks using a LangChain chat model."""

    if not selected_context.included_chunks:
        return GenerationResult(
            answer=_no_answer_result(NO_ANSWER_TEXT),
            model_usage=None,
        )

    citation_aliases = citation_aliases_for_context(selected_context.included_chunks)
    messages = ANSWER_PROMPT.format_messages(
        question=question.text,
        selected_context=_format_selected_context(selected_context.included_chunks),
    )
    response = chat_model.invoke(
        messages,
        max_tokens=selected_context.output_token_limit,
    )
    answer_text = _extract_message_text(response)
    if not answer_text.strip():
        raise ProviderError("Chat model returned an empty message")

    if _is_no_answer(answer_text):
        answer = _no_answer_result(answer_text.strip())
    else:
        citation_validation = validate_citations(
            answer_text,
            selected_context.included_chunks,
            citation_aliases=citation_aliases,
        )
        answer = AnswerResult(
            answer_text=answer_text.strip(),
            is_no_answer=False,
            citations=citation_validation.cited_chunk_ids,
            validation_status=citation_validation.status,
            validation_errors=citation_validation.validation_errors,
        )

    return GenerationResult(
        answer=answer,
        model_usage=_model_usage(response, chat_model),
    )


def _format_selected_context(chunks: Sequence[ContextChunk]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        section = " > ".join(chunk.section_path)
        blocks.append(
            f"[C{index}]\n"
            f"Source: {chunk.source_slug}\n"
            f"Category: {chunk.category}\n"
            f"Section: {section}\n"
            f"Text:\n{chunk.content}"
        )
    return "\n\n".join(blocks)


def _extract_message_text(message: BaseMessage) -> str:
    if not isinstance(message.content, str):
        raise ProviderError("Chat model returned non-text content")
    return message.content


def _is_no_answer(answer_text: str) -> bool:
    normalized = " ".join(answer_text.lower().split())
    return normalized.rstrip(".") in {
        NO_ANSWER_TEXT.lower().rstrip("."),
        "i do not have enough evidence in the selected context to answer",
        "the selected context is insufficient to answer",
    } or normalized.startswith(
        (
            "there is not enough evidence in the selected context to answer.",
            "i do not have enough evidence in the selected context to answer.",
            "the selected context is insufficient to answer.",
        )
    )


def _no_answer_result(answer_text: str) -> AnswerResult:
    return AnswerResult(
        answer_text=answer_text,
        is_no_answer=True,
        citations=[],
        validation_status="not_applicable",
    )


def _model_usage(response: BaseMessage, chat_model: ChatModel) -> ModelUsage | None:
    usage = getattr(response, "usage_metadata", None)
    if not usage:
        return None

    return ModelUsage(
        input_tokens=_usage_value(usage, "input_tokens"),
        output_tokens=_usage_value(usage, "output_tokens"),
        total_tokens=_usage_value(usage, "total_tokens"),
        model=_response_model(response) or _model_attribute(chat_model, "model_name"),
        deployment=(
            _model_attribute(chat_model, "azure_deployment")
            or _model_attribute(chat_model, "deployment_name")
            or _model_attribute(chat_model, "deployment")
            or _model_attribute(chat_model, "model_name")
        ),
    )


def _usage_value(usage: Any, key: str) -> int | None:
    if isinstance(usage, dict):
        value = usage.get(key)
    else:
        value = getattr(usage, key, None)
    return int(value) if value is not None else None


def _response_model(response: BaseMessage) -> str | None:
    metadata = getattr(response, "response_metadata", None)
    if isinstance(metadata, dict):
        value = metadata.get("model_name") or metadata.get("model")
        return str(value) if value else None
    return None


def _model_attribute(chat_model: ChatModel, name: str) -> str | None:
    value = getattr(chat_model, name, None)
    return str(value) if value else None
