from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_quality_lab.schemas import (
    REQUIRED_KNOWLEDGE_CATEGORIES,
    AnswerResult,
    CitationValidation,
    ContextBuild,
    ContextChunk,
    CorpusSummaryArtifact,
    QueryTrace,
    Question,
    RetrievalResult,
    RouteDecision,
    SourcePage,
)


def category_scores() -> dict[str, float]:
    return {category: 0.1 for category in REQUIRED_KNOWLEDGE_CATEGORIES}


def source_page() -> SourcePage:
    return SourcePage(
        source_slug="rag-overview",
        title="RAG Overview",
        category="RAG and context handling",
        url="https://example.test/rag",
        license="MIT",
        pinned_version="abc123",
        local_ref="corpus/sources/rag-overview.md",
    )


def context_chunk() -> ContextChunk:
    return ContextChunk(
        chunk_id="chunk-1",
        source_slug="rag-overview",
        category="RAG and context handling",
        section_path=["Overview"],
        retrieval_rank=1,
        content="Retrieval augmented generation grounds answers in selected context.",
        estimated_tokens=12,
    )


def test_source_page_accepts_required_category_and_exposes_provenance() -> None:
    page = source_page()

    assert page.provenance.local_ref == "corpus/sources/rag-overview.md"
    assert page.provenance.pinned_version == "abc123"


def test_source_page_rejects_unknown_category() -> None:
    with pytest.raises(ValidationError):
        SourcePage(
            source_slug="unknown",
            title="Unknown",
            category="other",
            url="https://example.test",
            license="MIT",
            pinned_version="abc123",
            local_ref="corpus/sources/unknown.md",
        )


def test_route_decision_requires_all_category_scores() -> None:
    scores = category_scores()
    scores.pop(REQUIRED_KNOWLEDGE_CATEGORIES[0])

    with pytest.raises(ValidationError, match="category_scores"):
        RouteDecision(
            selected_category="RAG and context handling",
            fallback_all_categories=False,
            confidence=0.7,
            threshold=0.2,
            category_scores=scores,
        )


def test_route_decision_requires_empty_category_for_fallback() -> None:
    with pytest.raises(ValidationError, match="selected_category"):
        RouteDecision(
            selected_category="RAG and context handling",
            fallback_all_categories=True,
            confidence=0.1,
            threshold=0.2,
            category_scores=category_scores(),
        )


def test_context_build_rejects_budget_overflow() -> None:
    with pytest.raises(ValidationError, match="max_context_tokens"):
        ContextBuild(
            max_context_tokens=10,
            output_token_limit=50,
            included_chunks=[context_chunk()],
            excluded_chunks=[],
            final_estimated_context_tokens=11,
        )


def test_query_trace_contains_contract_fields() -> None:
    route = RouteDecision(
        selected_category="RAG and context handling",
        fallback_all_categories=False,
        confidence=0.8,
        threshold=0.2,
        category_scores=category_scores(),
    )
    trace = QueryTrace(
        trace_id="trace-1",
        question=Question(text="How does RAG ground answers?"),
        retrieval_mode="routed-vector",
        route_decision=route,
        retrieval_results=[
            RetrievalResult(
                mode="routed-vector",
                rank=1,
                chunk_id="chunk-1",
                source_slug="rag-overview",
                category="RAG and context handling",
                score=0.9,
                estimated_tokens=12,
            )
        ],
        context_build=ContextBuild(
            max_context_tokens=100,
            output_token_limit=50,
            included_chunks=[context_chunk()],
            excluded_chunks=[],
            final_estimated_context_tokens=12,
        ),
        answer_result=AnswerResult(
            answer_text="RAG grounds answers in retrieved context. [chunk-1]",
            is_no_answer=False,
            citations=["chunk-1"],
            validation_status="valid",
        ),
        citation_validation=CitationValidation(
            status="valid",
            cited_chunk_ids=["chunk-1"],
        ),
    )

    dumped = trace.model_dump()

    assert dumped["schema_version"] == "1.0"
    assert dumped["retrieval_mode"] == "routed-vector"
    assert dumped["route_decision"]["selected_category"] == "RAG and context handling"
    assert dumped["context_build"]["included_chunks"][0]["chunk_id"] == "chunk-1"


def test_corpus_summary_artifact_keeps_schema_version_and_sources() -> None:
    artifact = CorpusSummaryArtifact(
        source_count=1,
        categories={"RAG and context handling": 1},
        license_summary={"MIT": 1},
        pinned_version="abc123",
        sources=[source_page()],
        validation_errors=[],
    )

    assert artifact.schema_version == "1.0"
    assert artifact.sources[0].local_ref == Path("corpus/sources/rag-overview.md").as_posix()
