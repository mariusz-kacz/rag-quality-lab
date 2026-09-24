from types import SimpleNamespace
import sys

import pytest

from rag_quality_lab.retrieval.reranking import FastEmbedReranker, RerankingError
from rag_quality_lab.config import InvalidConfigurationError
from rag_quality_lab.schemas import RetrievalResult


pytestmark = pytest.mark.unit


def candidates():
    return [
        RetrievalResult(
            mode="baseline-vector",
            rank=i,
            chunk_id=f"c{i}",
            source_slug="source",
            category="RAG and context handling",
            section_path=["Evidence"],
            score=1 / i,
            estimated_tokens=10,
            content=f"Passage {i}",
        )
        for i in range(1, 4)
    ]


def test_reranker_preserves_vector_ranks_and_breaks_ties_by_vector_rank():
    calls = []

    def score(query, documents):
        calls.append((query, documents))
        return iter([0.1, 0.9, 0.9])

    original = candidates()
    reranker = FastEmbedReranker(model=SimpleNamespace(rerank=score))
    result = reranker.rerank("Which evidence?", original)

    assert calls == [
        ("Which evidence?", [f"Evidence\n\nPassage {i}" for i in range(1, 4)])
    ]
    assert [
        (r.chunk_id, r.retrieval_rank, r.rank, r.score) for r in result.results
    ] == [
        ("c2", 2, 1, 0.9),
        ("c3", 3, 2, 0.9),
        ("c1", 1, 3, 0.1),
    ]
    assert [r.rank for r in original] == [1, 2, 3]
    assert [r.score for r in original] == [1, 0.5, 1 / 3]


@pytest.mark.parametrize(
    "scores", [[0.1], [0.1, float("nan"), 0.3], [0.1, float("inf"), 0.3]]
)
def test_reranker_rejects_incomplete_or_nonfinite_scores(scores):
    reranker = FastEmbedReranker(model=SimpleNamespace(rerank=lambda *args: scores))
    with pytest.raises(RerankingError, match="scores"):
        reranker.rerank("question", candidates())


def test_empty_candidates_do_not_load_model():
    assert FastEmbedReranker().rerank("question", []).results == []


def test_reranking_failure_does_not_silently_return_vector_order():
    def score(*args):
        raise RuntimeError("model failure")

    with pytest.raises(RerankingError, match="Reranking failed"):
        FastEmbedReranker(model=SimpleNamespace(rerank=score)).rerank(
            "question", candidates()
        )


def test_missing_optional_dependency_reports_install_command(monkeypatch):
    monkeypatch.setitem(sys.modules, "fastembed.rerank.cross_encoder", None)
    with pytest.raises(
        InvalidConfigurationError, match="uv sync --locked --extra rerank"
    ):
        FastEmbedReranker().rerank("question", candidates())
