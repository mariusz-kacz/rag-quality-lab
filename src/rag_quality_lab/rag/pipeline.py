"""End-to-end orchestration for one traced RAG query."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypedDict

from rag_quality_lab.chat_models import (
    create_foundry_chat_model,
)
from rag_quality_lab.config import load_app_config
from rag_quality_lab.providers import (
    FoundryOpenAIEmbeddingProvider,
)
from rag_quality_lab.rag.citations import validate_citations
from rag_quality_lab.rag.context import build_context
from rag_quality_lab.rag.generation import ChatModel, generate_answer
from rag_quality_lab.rag.traces import new_trace_id, save_trace
from rag_quality_lab.retrieval.modes import validate_retrieval_mode
from rag_quality_lab.retrieval.qdrant_store import QdrantStore
from rag_quality_lab.routing.embedding_router import EmbeddingCategoryRouter
from rag_quality_lab.schemas import (
    CitationValidation,
    ContextChunk,
    QueryTrace,
    Question,
    RetrievalResult,
    RouteDecision,
)


DEFAULT_PROMPT_OVERHEAD_TOKENS = 0


class QueryPipelineResult(TypedDict):
    trace: QueryTrace
    trace_path: Path


class QueryRouter(Protocol):
    def route(self, question: str) -> RouteDecision: ...


class QueryRetriever(Protocol):
    def retrieve(
        self,
        *,
        question: str,
        mode: str,
        top_k: int,
        route_decision: RouteDecision,
    ) -> list[RetrievalResult]: ...


class QueryEmbeddingProvider(Protocol):
    def embed_text(self, text: str) -> list[float]: ...


def run_query(
    question: str,
    *,
    mode: str,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
    trace_dir: str | Path,
    router: QueryRouter | None = None,
    retriever: QueryRetriever | None = None,
    chat_model: ChatModel | None = None,
    prompt_overhead_tokens: int = DEFAULT_PROMPT_OVERHEAD_TOKENS,
) -> QueryPipelineResult:
    """Run one query through route, retrieve, context, generation, and tracing."""

    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question cannot be empty")

    retrieval_mode = validate_retrieval_mode(mode)
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    components = _resolve_components(
        router=router,
        retriever=retriever,
        chat_model=chat_model,
    )
    question_record = Question(text=clean_question)
    route_decision = components.router.route(clean_question)
    retrieval_results = components.retriever.retrieve(
        question=clean_question,
        mode=retrieval_mode,
        top_k=top_k,
        route_decision=route_decision,
    )
    selected_context = build_context(
        _context_chunks_from_results(retrieval_results),
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
        prompt_overhead_tokens=prompt_overhead_tokens,
    )
    generation = generate_answer(
        question=question_record,
        selected_context=selected_context,
        chat_model=components.chat_model,
    )
    citation_validation = _citation_validation_for_answer(
        generation.answer.is_no_answer,
        generation.answer.answer_text,
        selected_context.included_chunks,
    )
    trace = QueryTrace(
        trace_id=new_trace_id(),
        question=question_record,
        retrieval_mode=retrieval_mode,
        route_decision=route_decision,
        retrieval_results=retrieval_results,
        context_build=selected_context,
        answer_result=generation.answer,
        citation_validation=citation_validation,
        model_usage=generation.model_usage,
    )
    trace_path = save_trace(trace, trace_dir)
    return {"trace": trace, "trace_path": trace_path}


@dataclass(frozen=True)
class _PipelineComponents:
    router: QueryRouter
    retriever: QueryRetriever
    chat_model: ChatModel


class QdrantQueryRetriever:
    """Retriever adapter that embeds the question and searches Qdrant chunks."""

    def __init__(
        self,
        *,
        collection: str,
        embedding_provider: QueryEmbeddingProvider,
        store: QdrantStore,
        category_score_margin: float = 0.0,
    ) -> None:
        self.collection = collection
        self.embedding_provider = embedding_provider
        self.store = store
        self.category_score_margin = category_score_margin

    def retrieve(
        self,
        *,
        question: str,
        mode: str,
        top_k: int,
        route_decision: RouteDecision,
    ) -> list[RetrievalResult]:
        return self.store.search_chunks(
            collection=self.collection,
            query_vector=self.embedding_provider.embed_text(question),
            mode=mode,
            top_k=top_k,
            selected_category=route_decision.selected_category,
            selected_categories=_selected_routed_categories(
                route_decision,
                margin=self.category_score_margin,
            ),
            fallback_all_categories=route_decision.fallback_all_categories,
        )


def _resolve_components(
    *,
    router: QueryRouter | None,
    retriever: QueryRetriever | None,
    chat_model: ChatModel | None,
) -> _PipelineComponents:
    if router is not None and retriever is not None and chat_model is not None:
        return _PipelineComponents(
            router=router,
            retriever=retriever,
            chat_model=chat_model,
        )

    config = load_app_config()
    embedding_provider = FoundryOpenAIEmbeddingProvider(config.foundry_openai)
    chat_model = chat_model or create_foundry_chat_model(config.foundry_openai)

    return _PipelineComponents(
        router=router
        or EmbeddingCategoryRouter(
            embedding_provider,
            threshold=config.runtime.router_confidence_threshold,
        ),
        retriever=retriever
        or QdrantQueryRetriever(
            collection=config.qdrant.collection,
            embedding_provider=embedding_provider,
            store=QdrantStore(config.qdrant),
            category_score_margin=config.runtime.router_category_margin,
        ),
        chat_model=chat_model,
    )


def _selected_routed_categories(
    route_decision: RouteDecision,
    *,
    margin: float,
) -> list[str] | None:
    if route_decision.fallback_all_categories or route_decision.selected_category is None:
        return None
    cutoff = max(0.0, route_decision.confidence - margin)
    categories = [
        category
        for category, score in route_decision.category_scores.items()
        if score >= cutoff
    ]
    return [
        route_decision.selected_category,
        *(category for category in categories if category != route_decision.selected_category),
    ]


def _context_chunks_from_results(
    retrieval_results: list[RetrievalResult],
) -> list[ContextChunk]:
    chunks: list[ContextChunk] = []
    for result in retrieval_results:
        if result.content is None:
            raise ValueError(
                f"retrieval result {result.chunk_id} is missing content for context"
            )
        if result.estimated_tokens is None:
            raise ValueError(
                f"retrieval result {result.chunk_id} is missing estimated_tokens for context"
            )
        chunks.append(
            ContextChunk(
                chunk_id=result.chunk_id,
                source_slug=result.source_slug,
                category=result.category,
                section_path=result.section_path,
                retrieval_rank=result.rank,
                content=result.content,
                estimated_tokens=result.estimated_tokens,
            )
        )
    return chunks


def _citation_validation_for_answer(
    is_no_answer: bool,
    answer_text: str,
    included_chunks: list[ContextChunk],
) -> CitationValidation:
    if is_no_answer:
        return CitationValidation(
            status="not_applicable",
            cited_chunk_ids=[],
            invalid_citations=[],
            validation_errors=[],
        )
    return validate_citations(answer_text, included_chunks)
