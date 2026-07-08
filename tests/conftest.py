from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from rag_quality_lab.config import AzureOpenAIConfig
from rag_quality_lab.providers import (
    AzureOpenAIChatProvider,
    AzureOpenAIEmbeddingProvider,
)
from rag_quality_lab.routing.categories import REQUIRED_CATEGORIES
from rag_quality_lab.schemas import (
    REQUIRED_KNOWLEDGE_CATEGORIES,
    AnswerResult,
    CitationValidation,
    ContextBuild,
    ContextChunk,
    GoldenSet,
    ModelUsage,
    QueryTrace,
    Question,
    RetrievalResult,
    RouteDecision,
    SourcePage,
    SourceSection,
)


@pytest.fixture
def sample_source_pages() -> list[SourcePage]:
    pages: list[SourcePage] = []
    categories = list(REQUIRED_KNOWLEDGE_CATEGORIES)

    for index in range(15):
        category = categories[index % len(categories)]
        slug = f"source-{index + 1:02d}"
        pages.append(
            SourcePage(
                source_slug=slug,
                title=f"Source {index + 1:02d}",
                category=category,
                url=f"https://example.test/prompt-guide/{slug}",
                license="MIT",
                pinned_version="dair-ai-prompt-guide@abc123",
                local_ref=f"corpus/sources/{slug}.md",
                sections=[
                    SourceSection(heading="Overview", level=1, ordinal=0),
                    SourceSection(heading="Details", level=2, ordinal=1),
                ],
            )
        )

    return pages


@pytest.fixture
def temporary_corpus(
    tmp_path: Path, sample_source_pages: list[SourcePage]
) -> dict[str, Path]:
    corpus_dir = tmp_path / "corpus"
    sources_dir = corpus_dir / "sources"
    sources_dir.mkdir(parents=True)

    for page in sample_source_pages:
        source_path = tmp_path / page.local_ref
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            f"# {page.title}\n\n"
            f"Category: {page.category}\n\n"
            "Retrieval augmented generation uses retrieved context to ground answers.\n",
            encoding="utf-8",
        )

    manifest_path = corpus_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "sources": [
                    page.model_dump(mode="json") for page in sample_source_pages
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    categories_path = corpus_dir / "categories.json"
    categories_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "categories": [
                    category.model_dump(mode="json") for category in REQUIRED_CATEGORIES
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "root": corpus_dir,
        "manifest": manifest_path,
        "categories": categories_path,
        "sources": sources_dir,
    }


@pytest.fixture
def golden_questions() -> GoldenSet:
    questions = [
        Question(
            question_id="q-answerable-01",
            text="How does RAG ground answers in context?",
            expected_category="RAG and context handling",
            expected_relevant_sources=["source-02"],
            answerability="answerable",
            case_type="answerable",
        ),
        Question(
            question_id="q-no-answer-01",
            text="What production warranty does this portfolio project provide?",
            expected_relevant_sources=[],
            answerability="no_answer",
            case_type="no_answer",
        ),
        Question(
            question_id="q-ambiguous-01",
            text="How should a prompt handle missing retrieved evidence?",
            expected_category="RAG and context handling",
            expected_relevant_sources=["source-02"],
            answerability="answerable",
            case_type="ambiguous_boundary",
        ),
        Question(
            question_id="q-fallback-01",
            text="How do tokens, risk, and evaluation interact in a RAG workflow?",
            expected_relevant_sources=["source-05"],
            answerability="answerable",
            case_type="fallback_routing",
        ),
    ]

    for index in range(8):
        questions.append(
            Question(
                question_id=f"q-answerable-{index + 2:02d}",
                text=f"What is useful about curated context example {index + 2}?",
                expected_category="prompting techniques",
                expected_relevant_sources=[f"source-{index + 1:02d}"],
                answerability="answerable",
                case_type="answerable",
            )
        )

    return GoldenSet(questions=questions)


@pytest.fixture
def temporary_golden_file(tmp_path: Path, golden_questions: GoldenSet) -> Path:
    golden_dir = tmp_path / "golden"
    golden_dir.mkdir()
    golden_path = golden_dir / "questions.json"
    golden_path.write_text(
        golden_questions.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return golden_path


@pytest.fixture
def sample_context_chunk() -> ContextChunk:
    return ContextChunk(
        chunk_id="source-02:overview:0001",
        source_slug="source-02",
        category="RAG and context handling",
        section_path=["Overview"],
        retrieval_rank=1,
        content="Retrieval augmented generation grounds answers in selected context.",
        estimated_tokens=10,
    )


@pytest.fixture
def sample_route_decision() -> RouteDecision:
    scores = {category: 0.05 for category in REQUIRED_KNOWLEDGE_CATEGORIES}
    scores["RAG and context handling"] = 0.82
    return RouteDecision(
        selected_category="RAG and context handling",
        fallback_all_categories=False,
        confidence=0.82,
        threshold=0.2,
        category_scores=scores,
    )


@pytest.fixture
def sample_query_trace(
    sample_context_chunk: ContextChunk,
    sample_route_decision: RouteDecision,
) -> QueryTrace:
    return QueryTrace(
        trace_id="trace-test-001",
        question=Question(text="How does RAG ground answers?"),
        retrieval_mode="routed-vector",
        route_decision=sample_route_decision,
        retrieval_results=[
            RetrievalResult(
                mode="routed-vector",
                rank=1,
                chunk_id=sample_context_chunk.chunk_id,
                source_slug=sample_context_chunk.source_slug,
                category=sample_context_chunk.category,
                section_path=sample_context_chunk.section_path,
                score=0.91,
                estimated_tokens=sample_context_chunk.estimated_tokens,
                content=sample_context_chunk.content,
            )
        ],
        context_build=ContextBuild(
            max_context_tokens=500,
            output_token_limit=100,
            included_chunks=[sample_context_chunk],
            excluded_chunks=[],
            final_estimated_context_tokens=sample_context_chunk.estimated_tokens,
        ),
        answer_result=AnswerResult(
            answer_text="RAG grounds answers in selected context. [source-02:overview:0001]",
            is_no_answer=False,
            citations=[sample_context_chunk.chunk_id],
            validation_status="valid",
        ),
        citation_validation=CitationValidation(
            status="valid",
            cited_chunk_ids=[sample_context_chunk.chunk_id],
        ),
        model_usage=ModelUsage(
            input_tokens=42,
            output_tokens=12,
            total_tokens=54,
            model="gpt-test",
            deployment="chat-test",
        ),
    )


@pytest.fixture
def temporary_trace_file(tmp_path: Path, sample_query_trace: QueryTrace) -> Path:
    trace_dir = tmp_path / "artifacts" / "traces"
    trace_dir.mkdir(parents=True)
    trace_path = trace_dir / f"{sample_query_trace.trace_id}.json"
    trace_path.write_text(
        sample_query_trace.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return trace_path


@pytest.fixture
def azure_test_config() -> AzureOpenAIConfig:
    return AzureOpenAIConfig(
        endpoint="https://example.openai.azure.com",
        api_key="test-key",
        api_version="2024-02-15-preview",
        embedding_deployment="embedding-test",
        chat_deployment="chat-test",
    )


class FakeEmbeddingsResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, *, model: str, input: list[str]) -> SimpleNamespace:
        self.calls.append({"model": model, "input": input})
        return SimpleNamespace(
            model=model,
            data=[
                SimpleNamespace(embedding=_fake_embedding(text, index))
                for index, text in enumerate(input)
            ],
            usage=SimpleNamespace(prompt_tokens=len(input), total_tokens=len(input)),
        )


class FakeChatCompletionsResource:
    def __init__(
        self, content: str = "Grounded answer [source-02:overview:0001]"
    ) -> None:
        self.content = content
        self.calls: list[dict[str, object]] = []

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None = None,
    ) -> SimpleNamespace:
        self.calls.append(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return SimpleNamespace(
            model=model,
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))],
            usage=SimpleNamespace(
                prompt_tokens=20, completion_tokens=7, total_tokens=27
            ),
        )


class FakeAzureOpenAIClient:
    def __init__(
        self, chat_content: str = "Grounded answer [source-02:overview:0001]"
    ) -> None:
        self.embeddings = FakeEmbeddingsResource()
        self.chat = SimpleNamespace(
            completions=FakeChatCompletionsResource(chat_content)
        )


@pytest.fixture
def fake_azure_client() -> FakeAzureOpenAIClient:
    return FakeAzureOpenAIClient()


@pytest.fixture
def fake_embedding_provider(
    azure_test_config: AzureOpenAIConfig,
    fake_azure_client: FakeAzureOpenAIClient,
) -> AzureOpenAIEmbeddingProvider:
    return AzureOpenAIEmbeddingProvider(azure_test_config, client=fake_azure_client)


@pytest.fixture
def fake_chat_provider(
    azure_test_config: AzureOpenAIConfig,
    fake_azure_client: FakeAzureOpenAIClient,
) -> AzureOpenAIChatProvider:
    return AzureOpenAIChatProvider(azure_test_config, client=fake_azure_client)


def _fake_embedding(text: str, index: int) -> list[float]:
    checksum = sum(ord(character) for character in text) % 100
    return [float(index), float(len(text)), checksum / 100.0]
