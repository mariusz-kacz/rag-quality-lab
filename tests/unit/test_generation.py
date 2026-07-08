from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
import pytest

from rag_quality_lab.providers import ProviderError
from rag_quality_lab.rag.generation import generate_answer
from rag_quality_lab.schemas import SelectedContext, ContextChunk, Question


pytestmark = pytest.mark.unit


def test_generate_answer_builds_grounded_prompt_and_returns_answer_result() -> None:
    chat_model = FakeChatModel(
        "RAG grounds answers in selected context. [chunk-rag-1]"
    )
    selected_context = context_with_chunks(
        [
            context_chunk(
                "chunk-rag-1",
                content="RAG grounds answers in selected context.",
                rank=1,
            )
        ],
        output_token_limit=120,
    )

    result = generate_answer(
        question=Question(text="How does RAG ground answers?"),
        selected_context=selected_context,
        chat_model=chat_model,
    )

    assert result.answer.answer_text == (
        "RAG grounds answers in selected context. [chunk-rag-1]"
    )
    assert result.answer.is_no_answer is False
    assert result.answer.citations == ["chunk-rag-1"]
    assert result.answer.validation_status == "valid"
    assert result.model_usage is not None
    assert result.model_usage.input_tokens == 20
    assert result.model_usage.output_tokens == 7
    assert result.model_usage.total_tokens == 27
    assert result.model_usage.model == "gpt-test"
    assert result.model_usage.deployment == "chat-test"

    assert len(chat_model.calls) == 1
    call = chat_model.calls[0]
    assert call["max_tokens"] == 120
    messages = call["messages"]
    assert messages[0].type == "system"
    assert "selected context" in messages[0].content
    assert "If the selected context is insufficient" in messages[0].content
    assert messages[1].type == "human"
    assert "How does RAG ground answers?" in messages[1].content
    assert "[chunk-rag-1]" in messages[1].content
    assert "RAG grounds answers in selected context." in messages[1].content


def test_generate_answer_returns_no_answer_without_provider_when_context_is_empty() -> None:
    chat_model = FakeChatModel("This should not be called.")
    selected_context = context_with_chunks([], output_token_limit=80)

    result = generate_answer(
        question=Question(text="What warranty does this project provide?"),
        selected_context=selected_context,
        chat_model=chat_model,
    )

    assert chat_model.calls == []
    assert result.model_usage is None
    assert result.answer.is_no_answer is True
    assert result.answer.citations == []
    assert result.answer.validation_status == "not_applicable"
    assert "not enough evidence" in result.answer.answer_text.lower()


def test_generate_answer_marks_explicit_no_answer_response_not_applicable() -> None:
    chat_model = FakeChatModel(
        "I do not have enough evidence in the selected context to answer."
    )
    selected_context = context_with_chunks(
        [
            context_chunk(
                "chunk-scope-1",
                content="The project documents local evaluation workflows.",
                rank=1,
            )
        ],
        output_token_limit=80,
    )

    result = generate_answer(
        question=Question(text="What enterprise warranty is provided?"),
        selected_context=selected_context,
        chat_model=chat_model,
    )

    assert result.answer.is_no_answer is True
    assert result.answer.citations == []
    assert result.answer.validation_status == "not_applicable"
    assert result.model_usage is not None


def test_generate_answer_rejects_empty_provider_response() -> None:
    chat_model = FakeChatModel("   ")
    selected_context = context_with_chunks(
        [context_chunk("chunk-1", content="Useful context.", rank=1)],
        output_token_limit=50,
    )

    with pytest.raises(ProviderError, match="empty"):
        generate_answer(
            question=Question(text="What does the context say?"),
            selected_context=selected_context,
            chat_model=chat_model,
        )


class FakeChatModel:
    deployment_name = "chat-test"

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict[str, Any]] = []

    def invoke(
        self,
        input: list[BaseMessage],
        config: Any | None = None,
        *,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        self.calls.append(
            {
                "messages": input,
                "config": config,
                "max_tokens": max_tokens,
                "kwargs": kwargs,
            }
        )
        return AIMessage(
            content=self.content,
            response_metadata={"model_name": "gpt-test"},
            usage_metadata={
                "input_tokens": 20,
                "output_tokens": 7,
                "total_tokens": 27,
            },
        )


def context_with_chunks(
    chunks: list[ContextChunk],
    *,
    output_token_limit: int,
) -> SelectedContext:
    return SelectedContext(
        max_context_tokens=500,
        output_token_limit=output_token_limit,
        included_chunks=chunks,
        excluded_chunks=[],
        final_estimated_context_tokens=sum(chunk.estimated_tokens for chunk in chunks),
    )


def context_chunk(chunk_id: str, *, content: str, rank: int) -> ContextChunk:
    return ContextChunk(
        chunk_id=chunk_id,
        source_slug=f"source-{rank}",
        category="RAG and context handling",
        section_path=["Overview"],
        retrieval_rank=rank,
        content=content,
        estimated_tokens=20,
    )
