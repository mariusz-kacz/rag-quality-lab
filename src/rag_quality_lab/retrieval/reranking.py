"""Optional local cross-encoder scoring; vector scores and ranks stay intact."""

import math
from time import perf_counter
from typing import Protocol

from rag_quality_lab.config import DEFAULT_RERANK_MODEL, InvalidConfigurationError
from rag_quality_lab.providers import ProviderError
from rag_quality_lab.schemas.retrieval import (
    RerankedChunk,
    RerankingResult,
    RetrievalResult,
)


class RerankingError(ProviderError):
    """A reranking failure; never silently fall back to vector order."""


class QueryReranker(Protocol):
    def rerank(
        self, question: str, candidates: list[RetrievalResult]
    ) -> RerankingResult: ...


class FastEmbedReranker:
    """Load once per query/evaluation scope and reuse on subsequent questions."""

    def __init__(self, model_name: str = DEFAULT_RERANK_MODEL, *, model=None):
        self.model_name = model_name
        self._model = model

    def rerank(
        self, question: str, candidates: list[RetrievalResult]
    ) -> RerankingResult:
        started = perf_counter()
        if not candidates:
            return RerankingResult(model=self.model_name, elapsed_ms=0)
        if any(not c.content or not c.content.strip() for c in candidates):
            raise RerankingError("Reranking requires passage text for every candidate")
        if self._model is None:
            try:
                from fastembed.rerank.cross_encoder import TextCrossEncoder
            except ImportError:
                raise InvalidConfigurationError(
                    "Reranking requires: uv sync --locked --extra rerank"
                ) from None
            try:
                self._model = TextCrossEncoder(
                    model_name=self.model_name,
                    cache_dir=".cache/fastembed",
                    providers=["CPUExecutionProvider"],
                    threads=4,
                )
            except Exception as exc:
                raise RerankingError(
                    f"Cannot load reranker {self.model_name!r} ({type(exc).__name__}); "
                    "check model support and access to the model cache/download."
                ) from None
        documents = [
            " > ".join(c.section_path) + "\n\n" + c.content for c in candidates
        ]
        try:
            scores = [float(score) for score in self._model.rerank(question, documents)]
        except Exception as exc:
            raise RerankingError(f"Reranking failed ({type(exc).__name__})") from None
        if len(scores) != len(candidates) or not all(math.isfinite(s) for s in scores):
            raise RerankingError(
                "Reranker scores must be finite and cover every candidate"
            )
        ranked = sorted(
            zip(candidates, scores, strict=True),
            key=lambda pair: (-pair[1], pair[0].rank),
        )
        return RerankingResult(
            model=self.model_name,
            elapsed_ms=(perf_counter() - started) * 1000,
            results=[
                RerankedChunk(
                    chunk_id=c.chunk_id,
                    retrieval_rank=c.rank,
                    rank=rank,
                    score=score,
                )
                for rank, (c, score) in enumerate(ranked, 1)
            ],
        )
