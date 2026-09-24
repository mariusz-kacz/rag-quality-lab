"""Run RAG, save a Ragas dataset, and evaluate it with one experiment."""

import asyncio
import sys
from contextlib import redirect_stdout
from importlib import import_module
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from rag_quality_lab.config import InvalidConfigurationError, load_app_config
from rag_quality_lab.eval.config import load_eval_config, normalize_endpoint
from rag_quality_lab.eval.metrics import ANSWER_SUCCESS_PROMPT, score_row
from rag_quality_lab.eval.providers import evaluator_scope
from rag_quality_lab.rag.pipeline import resolve_query_components, run_query
from rag_quality_lab.retrieval.modes import validate_retrieval_mode
from rag_quality_lab.retrieval.qdrant_store import (
    IndexInventoryError,
    QdrantStore,
    QdrantStoreError,
)
from rag_quality_lab.schemas.eval import GoldenDataset


class EvaluationError(Exception):
    def __init__(
        self, message, dataset_path=None, results_path=None, *, stage="evaluation"
    ):
        self.dataset_path = dataset_path
        self.results_path = results_path
        self.stage = stage
        super().__init__(message)


def require_ragas():
    try:
        from ragas import Dataset, experiment
        from ragas.metrics import DiscreteMetric
        from ragas.metrics.collections import Faithfulness

        import_module("ir_measures")
    except ImportError:
        raise InvalidConfigurationError(
            "Evaluation requires: uv sync --locked --extra eval"
        ) from None
    return Dataset, experiment, Faithfulness, DiscreteMetric


def collect_answers(dataset, questions, mode, config, trace_dir):
    """Reuse query clients and save only the fields needed by the metrics."""
    store = QdrantStore(config.qdrant)
    try:
        inventory = store.inventory(collection=config.qdrant.collection)
    finally:
        store.close()
    relevant = {}
    for question in questions:
        ids = set()
        for label in question.expected_relevant_sources:
            matches = {
                cid
                for cid, source in inventory.chunk_sources.items()
                if label in (cid, source)
            }
            if not matches:
                raise ValueError("A golden relevance label is absent from the index")
            ids.update(matches)
        relevant[question.question_id] = sorted(ids)
    foundry = config.foundry_openai
    settings = {
        **config.runtime.model_dump(
            mode="json", exclude={"trace_dir", "schema_version"}
        ),
        "generator_model": foundry.chat_model,
        "embedding_model": foundry.embedding_model,
        "endpoint": normalize_endpoint(foundry.base_url),
        "reasoning_effort": foundry.reasoning_effort,
        "collection": config.qdrant.collection,
        "index_fingerprint": inventory.index_fingerprint,
    }
    with resolve_query_components(
        retrieval_mode=mode,
        config=config,
        rerank_enabled=config.runtime.rerank_enabled,
    ) as components:
        for question in questions:
            row = {
                "question_id": question.question_id,
                "question": question.model_dump(mode="json"),
                "mode": mode,
                "settings": settings,
                "relevant_ids": relevant[question.question_id],
                "response": None,
                "contexts": [],
                "ranked_ids": [],
                "cited_ids": [],
                "error": None,
                "diagnostics": {},
            }
            try:
                result = run_query(
                    question,
                    mode=mode,
                    config=config,
                    top_k=config.runtime.top_k,
                    max_context_tokens=config.runtime.max_context_tokens,
                    output_token_limit=config.runtime.output_token_limit,
                    trace_dir=trace_dir,
                    router=components.router,
                    retriever=components.retriever,
                    chat_model=components.chat_model,
                    rerank_enabled=config.runtime.rerank_enabled,
                    candidate_k=config.runtime.candidate_k,
                    reranker=components.reranker,
                )
                trace = result["trace"]
                included = trace.context_build.included_chunks
                row.update(
                    response=trace.answer_result.answer_text,
                    contexts=[chunk.content for chunk in included],
                    ranked_ids=[
                        chunk.chunk_id
                        for chunk in (
                            trace.reranking.results
                            if trace.reranking
                            else trace.retrieval_results
                        )
                    ],
                    cited_ids=[
                        chunk.chunk_id
                        for chunk in included
                        if chunk.chunk_id in trace.citation_validation.cited_chunk_ids
                    ],
                    diagnostics={
                        "refused": trace.answer_result.is_no_answer,
                        "route": trace.route_decision.model_dump(mode="json")
                        if trace.route_decision
                        else None,
                        "searched_categories": trace.searched_categories,
                        "citation_validation": trace.citation_validation.model_dump(
                            mode="json"
                        ),
                        "context_chunks": len(included),
                        "context_tokens": trace.context_build.final_estimated_context_tokens,
                        "reranking": trace.reranking.model_dump(mode="json")
                        if trace.reranking
                        else None,
                        "candidate_ranked_ids": [
                            chunk.chunk_id for chunk in trace.retrieval_results
                        ],
                        "generation_usage": trace.model_usage.model_dump(mode="json")
                        if trace.model_usage
                        else None,
                    },
                )
            except Exception as exc:
                row["error"] = f"Query failed ({type(exc).__name__})"
            dataset.append(row)
            dataset.save()


async def score_dataset(dataset, config):
    """Score the captured answers with one native Ragas experiment."""
    _, experiment, Faithfulness, DiscreteMetric = require_ragas()
    evaluation = {
        **config.model_dump(mode="json", exclude={"auth_source", "endpoint_source"}),
        "ragas_version": version("ragas"),
        "ir_measures_version": version("ir-measures"),
        "metric_version": 3,
        "answer_success_prompt": ANSWER_SUCCESS_PROMPT,
    }
    gate = asyncio.Semaphore(1)
    async with evaluator_scope(config) as evaluator:
        faithfulness = Faithfulness(llm=evaluator.llm)
        success = DiscreteMetric(
            name="answer_success",
            prompt=ANSWER_SUCCESS_PROMPT,
            allowed_values=["pass", "fail"],
        )

        @experiment()
        async def evaluate(row):
            async with gate:
                scores = await score_row(
                    row, success.ascore, faithfulness.ascore, evaluator
                )
                return {**scores, "evaluation": evaluation}

        with redirect_stdout(sys.stderr):
            return await evaluate.arun(dataset, name="scores")


def run_evaluation(
    *,
    mode="baseline-vector",
    artifacts_dir="artifacts/eval",
    golden_path="golden/questions.json",
    question_ids=None,
    config=None,
    runtime=None,
):
    Dataset, _, _, _ = require_ragas()
    evaluator_config = load_eval_config()
    mode = validate_retrieval_mode(mode)
    questions = GoldenDataset.model_validate_json(
        Path(golden_path).read_bytes()
    ).select(question_ids)
    config = config or load_app_config(runtime=runtime)
    if runtime is not None:
        config = config.model_copy(update={"runtime": runtime})
    root = Path(artifacts_dir) / uuid4().hex
    dataset = Dataset("answers", backend="local/jsonl", root_dir=str(root))
    dataset_path = root / "datasets/answers.jsonl"
    results_path = root / "experiments/scores.jsonl"
    try:
        collect_answers(dataset, questions, mode, config, root / "traces")
        results = list(asyncio.run(score_dataset(dataset, evaluator_config)))
        if len(results) != len(dataset) or {r["question_id"] for r in results} != {
            r["question_id"] for r in dataset
        }:
            raise ValueError("Ragas did not return every question")
    except Exception as exc:
        message = f"Evaluation failed ({type(exc).__name__})"
        stage = "artifact" if isinstance(exc, OSError) else "evaluation"
        if isinstance(exc, IndexInventoryError):
            message = str(exc)
            stage = "retrieval"
        elif isinstance(exc, QdrantStoreError):
            message = (
                "Cannot read the Qdrant index. Check QDRANT_URL, QDRANT_API_KEY, "
                "and RAGLAB_QDRANT_COLLECTION; ensure the collection is ingested."
            )
            stage = "retrieval"
        raise EvaluationError(
            message,
            dataset_path if dataset_path.is_file() else None,
            results_path if results_path.is_file() else None,
            stage=stage,
        ) from None
    if any(
        metric["status"] in ("error", "not_run")
        for row in results
        for metric in row["metrics"].values()
    ):
        raise EvaluationError(
            "Evaluation is incomplete; inspect saved results",
            dataset_path,
            results_path,
        )
    return {
        "dataset_path": str(dataset_path),
        "results_path": str(results_path),
        **summarize(results),
    }


def summarize(rows):
    """Summarize this run's already validated metric outcomes for the CLI."""
    metrics = {}
    for name in rows[0]["metrics"]:
        outcomes = [row["metrics"][name] for row in rows]
        values = [m["value"] for m in outcomes if m["status"] == "ok"]
        metrics[name] = {
            "mean": sum(values) / len(values) if values else None,
            "scored_count": len(values),
            "eligible_count": sum(m["status"] != "not_applicable" for m in outcomes),
        }
    return {
        "question_count": len(rows),
        "metrics": metrics,
        "diagnostics": {
            "expected_no_answer_count": sum(r["expected_no_answer"] for r in rows),
            "recognized_no_answers": sum(
                r["expected_no_answer"] and r["diagnostics"].get("refused", False)
                for r in rows
            ),
            "unexpected_refusals": sum(
                not r["expected_no_answer"] and r["diagnostics"].get("refused", False)
                for r in rows
            ),
        },
    }
