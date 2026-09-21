import json
from pathlib import Path

import pytest

from rag_quality_lab.eval.reports import EvaluationRunError, run_evaluation
from rag_quality_lab.providers import EmbeddingResponse
from rag_quality_lab.rag import pipeline
from rag_quality_lab.rag.traces import load_trace
from rag_quality_lab.routing.categories import category_descriptions
from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES, RouteDecision


pytestmark = pytest.mark.integration


@pytest.fixture
def evaluation_environment(monkeypatch):
    for name, value in {
        "FOUNDRY_OPENAI_BASE_URL": "https://example.test/openai/v1",
        "FOUNDRY_EMBEDDING_MODEL": "test-embedding",
        "FOUNDRY_CHAT_MODEL": "test-chat",
        "QDRANT_URL": "http://localhost:6333",
        "RAGLAB_QDRANT_COLLECTION": "test",
    }.items():
        monkeypatch.setenv(name, value)


@pytest.mark.parametrize("mode", ["baseline-vector", "routed-vector"])
@pytest.mark.parametrize("failure", [None, "setup", "query", "trace"])
def test_evaluation_owns_one_component_set_per_run(
    tmp_path, temporary_golden_file, monkeypatch, evaluation_environment, mode, failure
):
    resources = {"embeddings": [], "chat": [], "store": []}
    embedding_batches = []
    searches = []

    class Resource:
        def __init__(self, kind):
            self.closed = 0
            resources[kind].append(self)

        def close(self):
            self.closed += 1

    class Embeddings(Resource):
        def embed_texts(self, texts):
            assert not self.closed
            embedding_batches.append(list(texts))
            return EmbeddingResponse(vectors=[[1.0] for _ in texts])

        def embed_text(self, text):
            return self.embed_texts([text]).vectors[0]

    class Store(Resource):
        def search_chunks(self, **kwargs):
            assert all(not item.closed for group in resources.values() for item in group[-1:])
            searches.append(kwargs)
            if failure == "query" and len(searches) == 2:
                raise RuntimeError("query failed")
            return []

    def make_store(config):
        if failure == "setup":
            raise RuntimeError("setup failed")
        return Store("store")

    def fail_trace(*args):
        raise OSError("trace failed")

    monkeypatch.setattr(pipeline, "FoundryOpenAIEmbeddingProvider", lambda config: Embeddings("embeddings"))
    monkeypatch.setattr(pipeline, "create_foundry_chat_model", lambda config: Resource("chat"))
    monkeypatch.setattr(pipeline, "QdrantStore", make_store)
    if failure == "trace":
        monkeypatch.setattr(pipeline, "save_trace", fail_trace)

    def evaluate():
        return run_evaluation(
            mode=mode, golden_path=temporary_golden_file, artifacts_dir=tmp_path / "eval",
            top_k=3, max_context_tokens=500, output_token_limit=120,
        )

    if failure:
        with pytest.raises(EvaluationRunError, match=f"{failure} failed"):
            evaluate()
        assert all(item.closed == 1 for group in resources.values() for item in group)
    else:
        for run_number in (1, 2):
            run = evaluate()
            assert {kind: len(items) for kind, items in resources.items()} == dict.fromkeys(resources, run_number)
            assert all(item.closed == 1 for group in resources.values() for item in group)
            assert embedding_batches.count(list(category_descriptions().values())) == (
                run_number if mode == "routed-vector" else 0
            )
            traces = [load_trace(path) for path in run.trace_paths]
            expected = json.loads(temporary_golden_file.read_text(encoding="utf-8"))["questions"]
            assert [trace.question.text for trace in traces] == [item["text"] for item in expected]
            assert len({trace.trace_id for trace in traces}) == len(expected)


@pytest.mark.parametrize(
    ("mode", "fallback", "environment_margin", "override", "expected"),
    [
        ("routed-vector", False, 0.0, None, ["prompting techniques"]),
        ("routed-vector", False, 0.15, 0.0, ["prompting techniques"]),
        ("routed-vector", False, 0.0, 0.15, ["prompting techniques", "RAG and context handling"]),
        ("routed-vector", True, 0.0, None, list(REQUIRED_KNOWLEDGE_CATEGORIES)),
        ("baseline-vector", False, 0.0, None, list(REQUIRED_KNOWLEDGE_CATEGORIES)),
    ],
)
def test_evaluation_reports_the_executed_search_scope(
    tmp_path: Path,
    temporary_golden_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    evaluation_environment,
    mode: str,
    fallback: bool,
    environment_margin: float,
    override: float | None,
    expected: list[str],
) -> None:
    monkeypatch.setenv("RAGLAB_ROUTER_CATEGORY_MARGIN", str(environment_margin))

    class Embeddings:
        def close(self):
            pass

        def embed_text(self, text):
            return [1.0]

    class Router:
        def route(self, question):
            scores = dict.fromkeys(REQUIRED_KNOWLEDGE_CATEGORIES, 0.1)
            scores.update({"prompting techniques": 0.8, "RAG and context handling": 0.7})
            return RouteDecision(
                selected_category=None if fallback else "prompting techniques",
                fallback_all_categories=fallback,
                confidence=0.8,
                threshold=0.9 if fallback else 0.18,
                category_scores=scores,
            )

    searches = []

    class Store:
        def close(self):
            pass

        def search_chunks(self, **kwargs):
            searches.append(kwargs)
            # Configuration changes during a run must not affect later questions.
            monkeypatch.setenv("RAGLAB_ROUTER_CATEGORY_MARGIN", "1.0")
            return []

    monkeypatch.setattr(pipeline, "FoundryOpenAIEmbeddingProvider", lambda config: Embeddings())
    monkeypatch.setattr(pipeline, "EmbeddingCategoryRouter", lambda *args, **kwargs: Router())
    monkeypatch.setattr(pipeline, "QdrantStore", lambda config: Store())
    monkeypatch.setattr(pipeline, "create_foundry_chat_model", lambda config: Embeddings())

    run = run_evaluation(
        mode=mode,
        golden_path=temporary_golden_file,
        artifacts_dir=tmp_path / "eval",
        top_k=3,
        max_context_tokens=500,
        output_token_limit=120,
        router_category_margin=override,
    )

    actual_scopes = [
        call["selected_categories"] or list(REQUIRED_KNOWLEDGE_CATEGORIES)
        for call in searches
    ]
    assert [question.searched_categories for question in run.questions] == actual_scopes
    assert actual_scopes == [expected] * len(run.questions)
    effective_margin = environment_margin if override is None else override
    assert run.configuration["router_category_margin"] == effective_margin
    assert run.metrics.average_searched_categories == len(expected)
    assert [load_trace(path).searched_categories for path in run.trace_paths] == actual_scopes
    payload = json.loads(run.artifact_paths.json_path.read_text(encoding="utf-8"))
    assert payload["configuration"]["router_category_margin"] == effective_margin
    assert [question["searched_categories"] for question in payload["questions"]] == actual_scopes
