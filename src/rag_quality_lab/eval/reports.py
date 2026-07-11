"""Evaluation run orchestration and report helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol, TypedDict

from rag_quality_lab.config import RuntimeConfig
from rag_quality_lab.eval.golden import load_golden_set
from rag_quality_lab.eval.metrics import (
    EvaluationResultSetError,
    calculate_evaluation_metrics,
    match_questions_to_traces,
    searched_categories,
)
from rag_quality_lab.retrieval.modes import validate_retrieval_mode
from rag_quality_lab.schemas.eval import MetricName, REQUIRED_EVALUATION_METRICS
from rag_quality_lab.schemas import (
    BENCHMARK_SCOPE_STATEMENT,
    EvaluationArtifactPaths,
    EvaluationMetricCount,
    EvaluationQuestionResult,
    EvaluationRun,
    QueryTrace,
    Question,
    RetrievalMode,
    read_json_artifact,
    write_json_artifact,
)


class EvaluationRunError(Exception):
    """Raised when an evaluation run cannot execute or assemble trace results."""


class EvaluationQueryResult(TypedDict):
    trace: QueryTrace
    trace_path: Path


class EvaluationQueryRunner(Protocol):
    def __call__(
        self,
        question: Question | str,
        *,
        mode: RetrievalMode,
        top_k: int,
        max_context_tokens: int,
        output_token_limit: int,
        trace_dir: Path | None = None,
        **kwargs: Any,
    ) -> Mapping[str, object]: ...


QUALITY_METRICS: tuple[MetricName, ...] = (
    "routing_accuracy",
    "average_searched_categories",
    "hit_rate_at_k",
    "mrr",
    "citation_source_match",
    "no_answer_accuracy",
)
TOKEN_BUDGET_METRICS: tuple[MetricName, ...] = (
    "average_context_tokens",
    "average_included_chunks",
)
LOWER_IS_BETTER_METRICS: frozenset[MetricName] = frozenset(
    (
        "average_searched_categories",
        "average_context_tokens",
        "average_included_chunks",
    )
)

RATE_METRICS: tuple[MetricName, ...] = (
    "routing_accuracy",
    "hit_rate_at_k",
    "citation_source_match",
    "no_answer_accuracy",
)

def run_evaluation(
    *,
    mode: str,
    golden_path: str | Path,
    artifacts_dir: str | Path,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
    router_category_margin: float | None = None,
    query_runner: EvaluationQueryRunner | None = None,
    trace_dir: str | Path | None = None,
) -> EvaluationRun:
    """Run one retrieval mode over the golden set and return an evaluation model."""

    retrieval_mode = validate_retrieval_mode(mode)
    effective_router_category_margin = (
        RuntimeConfig().router_category_margin
        if router_category_margin is None
        else router_category_margin
    )
    golden_file = Path(golden_path)
    artifact_directory = Path(artifacts_dir)
    trace_directory = (
        Path(trace_dir)
        if trace_dir is not None
        else artifact_directory / "traces" / retrieval_mode
    )
    golden_set = load_golden_set(golden_file)
    runner = query_runner or _run_query_for_evaluation

    execution_results: list[EvaluationQueryResult] = []

    for question in golden_set.questions:
        result = _execute_golden_question(
            runner,
            question,
            mode=retrieval_mode,
            top_k=top_k,
            max_context_tokens=max_context_tokens,
            output_token_limit=output_token_limit,
            trace_dir=trace_directory,
        )
        trace = result["trace"]
        trace_path = result["trace_path"]
        execution_results.append({"trace": trace, "trace_path": trace_path})

    traces = [result["trace"] for result in execution_results]
    try:
        matched_pairs = match_questions_to_traces(golden_set.questions, traces)
    except EvaluationResultSetError as exc:
        raise EvaluationRunError(str(exc)) from exc
    trace_path_by_question_id = {
        result["trace"].question.question_id: result["trace_path"]
        for result in execution_results
        if result["trace"].question.question_id is not None
    }
    trace_paths = [
        trace_path_by_question_id[question.question_id]
        for question, _ in matched_pairs
    ]
    question_results = [
        _question_result(
            question,
            trace,
            trace_path=trace_path_by_question_id[question.question_id],
            retrieval_mode=retrieval_mode,
            router_category_margin=effective_router_category_margin,
        )
        for question, trace in matched_pairs
    ]

    metrics = calculate_evaluation_metrics(
        golden_set.questions,
        traces,
        retrieval_mode=retrieval_mode,
        category_margin=effective_router_category_margin,
    )
    if retrieval_mode == "baseline-vector":
        metrics = metrics.model_copy(update={"routing_accuracy": None})

    run = EvaluationRun(
        run_id=f"eval-{retrieval_mode}",
        retrieval_mode=retrieval_mode,
        golden_set_path=golden_file,
        configuration={
            "top_k": top_k,
            "max_context_tokens": max_context_tokens,
            "output_token_limit": output_token_limit,
            "router_category_margin": effective_router_category_margin,
        },
        metrics=metrics,
        metric_counts=_metric_counts(question_results),
        questions=question_results,
        trace_paths=trace_paths,
    )
    return write_evaluation_artifact(run, artifact_directory)


def write_evaluation_artifact(
    run: EvaluationRun,
    artifacts_dir: str | Path,
) -> EvaluationRun:
    """Write evaluation JSON and Markdown artifacts and return updated paths."""

    artifact_directory = Path(artifacts_dir)
    json_path = artifact_directory / f"{run.run_id}.json"
    markdown_path = artifact_directory / f"{run.run_id}.md"
    run_with_paths = run.model_copy(
        update={
            "artifact_paths": EvaluationArtifactPaths(
                json_path=json_path,
                markdown_path=markdown_path,
            )
        }
    )
    write_json_artifact(json_path, run_with_paths)
    write_markdown_report(markdown_path, run_with_paths)
    return run_with_paths


def write_markdown_report(path: str | Path, run: EvaluationRun) -> Path:
    """Write a human-readable Markdown evaluation report and return the path."""

    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown_report(run), encoding="utf-8")
    return report_path


def compare_evaluation_artifacts(
    artifact_paths: list[Path],
    *,
    markdown: Path | None = None,
) -> dict[str, Any]:
    """Compare one or more evaluation artifacts and optionally write Markdown."""

    if not artifact_paths:
        raise EvaluationRunError("At least one evaluation artifact path is required")

    runs = [read_json_artifact(path, EvaluationRun) for path in artifact_paths]
    _validate_comparable_runs(runs)

    result = {
        "schema_version": "1.0",
        "benchmark_scope": BENCHMARK_SCOPE_STATEMENT,
        "artifact_paths": [str(path) for path in artifact_paths],
        "markdown_path": str(markdown) if markdown is not None else None,
        "metrics": [
            _comparison_row(metric, runs)
            for metric in QUALITY_METRICS
            if metric in REQUIRED_EVALUATION_METRICS
        ],
        "token_budget": {
            metric: _comparison_row(metric, runs)
            for metric in TOKEN_BUDGET_METRICS
            if metric in REQUIRED_EVALUATION_METRICS
        },
    }

    if markdown is not None:
        write_comparison_markdown(markdown, result)
    return result


def write_comparison_markdown(path: str | Path, comparison: Mapping[str, Any]) -> Path:
    """Write a Markdown comparison table and return the path."""

    markdown_path = Path(path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_comparison_markdown(comparison), encoding="utf-8")
    return markdown_path


def render_comparison_markdown(comparison: Mapping[str, Any]) -> str:
    """Render a Markdown comparison report for evaluation artifacts."""

    sections = [
        "# Evaluation comparison",
        str(comparison.get("benchmark_scope", BENCHMARK_SCOPE_STATEMENT)),
        "## Compared artifacts",
        _render_compared_artifacts(comparison),
        "## Metric comparison",
        _render_comparison_rows(comparison.get("metrics", [])),
        "## Token-budget diagnostics",
        _render_comparison_rows(comparison.get("token_budget", {}).values()),
        "## Interpretation notes",
        _render_comparison_notes(comparison),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def render_markdown_report(run: EvaluationRun) -> str:
    """Render the Markdown evaluation report for one evaluation run."""

    case_counts: dict[str, int] = {}
    for result in run.questions:
        case_counts[result.case_type] = case_counts.get(result.case_type, 0) + 1

    json_path = (
        run.artifact_paths.json_path
        if run.artifact_paths is not None
        else None
    )

    sections = [
        f"# Evaluation report: {run.run_id}",
        run.benchmark_scope,
        "## Run summary",
        _render_run_summary(run, case_counts, json_path),
        "## Retrieval mode and configuration",
        _render_configuration(run),
        "## Aggregate metrics",
        _render_aggregate_metrics(run),
        "## Per-question table",
        _render_question_table(run.questions, retrieval_mode=run.retrieval_mode),
        "## Request-response pairs",
        _render_request_response_pairs(run.questions, retrieval_mode=run.retrieval_mode),
        "## Token-budget diagnostics",
        _render_token_budget_diagnostics(run),
        "## No-answer cases",
        _render_no_answer_cases(run.questions),
        "## Citation validation failures",
        _render_citation_failures(run.questions),
        "## Limitations and interpretation notes",
        _render_limitations(),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def _validate_comparable_runs(runs: list[EvaluationRun]) -> None:
    modes: set[str] = set()
    for run in runs:
        if run.retrieval_mode in modes:
            raise EvaluationRunError(
                f"Duplicate evaluation artifact for retrieval mode {run.retrieval_mode}"
            )
        modes.add(run.retrieval_mode)


def _comparison_row(metric: MetricName, runs: list[EvaluationRun]) -> dict[str, Any]:
    values = {
        run.retrieval_mode: getattr(run.metrics, metric)
        for run in runs
    }
    row = {
        "metric": metric,
        "values": values,
        "included_benchmark_mode": _included_benchmark_mode(
            values, lower_is_better=metric in LOWER_IS_BETTER_METRICS
        ),
    }
    counts = {
        run.retrieval_mode: count.model_dump(mode="json")
        for run in runs
        if (count := _counts_for_run(run).get(metric)) is not None
    }
    if counts:
        row["counts"] = counts
    if metric == "routing_accuracy":
        row["reason"] = (
            "Routing accuracy is not applicable to baseline-vector because baseline "
            "retrieval does not use route filtering."
        )
    return row


def _included_benchmark_mode(
    values: Mapping[str, float | None],
    *,
    lower_is_better: bool,
) -> str | None:
    numeric_values = {
        mode: value
        for mode, value in values.items()
        if isinstance(value, int | float)
    }
    if len(numeric_values) < 2:
        return None

    best_value = (
        min(numeric_values.values())
        if lower_is_better
        else max(numeric_values.values())
    )
    observed_modes = [
        mode
        for mode, value in numeric_values.items()
        if value == best_value
    ]
    return "tie" if len(observed_modes) > 1 else observed_modes[0]


def _render_compared_artifacts(comparison: Mapping[str, Any]) -> str:
    artifact_paths = comparison.get("artifact_paths", [])
    if not artifact_paths:
        return "No artifacts were compared."
    lines = [
        "| Artifact |",
        "| --- |",
    ]
    lines.extend(f"| {_escape_table(path)} |" for path in artifact_paths)
    return "\n".join(lines)


def _render_comparison_rows(rows: Any) -> str:
    row_list = list(rows)
    if not row_list:
        return "No comparable metrics were present."

    modes = sorted(
        {
            mode
            for row in row_list
            for mode in row.get("values", {})
        }
    )
    header = ["Metric", *modes, "Observed value on included benchmark"]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in row_list:
        values = row.get("values", {})
        counts = row.get("counts", {})
        cells = [
            row.get("metric", "unknown"),
            *[
                _format_metric_result(
                    row.get("metric"), values.get(mode), counts.get(mode)
                )
                for mode in modes
            ],
            row.get("included_benchmark_mode") or "n/a",
        ]
        lines.append("| " + " | ".join(_escape_table(cell) for cell in cells) + " |")
    return "\n".join(lines)


def _render_comparison_notes(comparison: Mapping[str, Any]) -> str:
    notes = [
        BENCHMARK_SCOPE_STATEMENT,
        "With 14 retrieval-scored questions, a one-question change moves hit rate by 7.1 percentage points.",
        "Top-category routing accuracy and retrieval hit rate measure different behavior: soft multi-category routing can retain the expected category and recover a hit even when the top category is incorrect.",
        "Category margins are heuristic, and configuration was adjusted while inspecting this same small benchmark.",
    ] + [
        row.get("reason")
        for row in comparison.get("metrics", [])
        if row.get("reason")
    ]
    if not notes:
        return "No metric-specific notes."
    unique_notes = list(dict.fromkeys(str(note) for note in notes))
    return "\n".join(f"- {note}" for note in unique_notes)


def _run_query_for_evaluation(
    question: Question | str,
    *,
    mode: RetrievalMode,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
    trace_dir: Path | None = None,
    **_: Any,
) -> Mapping[str, object]:
    from rag_quality_lab.rag.pipeline import run_query

    return run_query(
        question,
        mode=mode,
        top_k=top_k,
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
        trace_dir=trace_dir or Path("artifacts/traces") / mode,
    )


def _execute_golden_question(
    runner: EvaluationQueryRunner,
    question: Question,
    *,
    mode: RetrievalMode,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
    trace_dir: Path,
) -> EvaluationQueryResult:
    try:
        raw_result = runner(
            question,
            mode=mode,
            top_k=top_k,
            max_context_tokens=max_context_tokens,
            output_token_limit=output_token_limit,
            trace_dir=trace_dir,
        )
    except Exception as exc:
        question_id = question.question_id or question.text
        raise EvaluationRunError(f"Evaluation query failed for {question_id}: {exc}") from exc

    trace = raw_result.get("trace")
    trace_path = raw_result.get("trace_path")
    if not isinstance(trace, QueryTrace):
        raise EvaluationRunError("Evaluation query runner returned no QueryTrace")
    if not isinstance(trace_path, Path):
        raise EvaluationRunError("Evaluation query runner returned no trace Path")
    return {"trace": trace, "trace_path": trace_path}


def _question_result(
    question: Question,
    trace: QueryTrace,
    *,
    trace_path: Path,
    retrieval_mode: RetrievalMode,
    router_category_margin: float,
) -> EvaluationQuestionResult:
    if question.question_id is None:
        raise EvaluationRunError("Cannot build evaluation result without question_id")
    return EvaluationQuestionResult(
        question_id=question.question_id,
        question_text=question.text,
        case_type=question.case_type,
        trace_path=trace_path,
        metrics=_per_question_metrics(
            question,
            trace,
            retrieval_mode=retrieval_mode,
        ),
        expected_category=question.expected_category,
        selected_category=(
            trace.route_decision.selected_category
            if trace.route_decision is not None
            else None
        ),
        searched_categories=searched_categories(
            trace,
            retrieval_mode=retrieval_mode,
            category_margin=router_category_margin,
        ),
        answer_text=trace.answer_result.answer_text,
        is_no_answer=trace.answer_result.is_no_answer,
        expected_relevant_sources=list(question.expected_relevant_sources),
        retrieved_sources=_unique_retrieved_sources(trace),
        errors=_trace_errors(trace),
    )


def _per_question_metrics(
    question: Question,
    trace: QueryTrace,
    *,
    retrieval_mode: RetrievalMode,
) -> dict[MetricName, float | None]:
    metrics: dict[MetricName, float | None] = {
        "routing_accuracy": (
            None
            if retrieval_mode == "baseline-vector"
            else _routing_match(question, trace)
        ),
        "hit_rate_at_k": _retrieval_hit(question, trace),
        "mrr": _reciprocal_rank(question, trace),
        "citation_source_match": _citation_match(question, trace),
        "no_answer_accuracy": (
            1.0
            if (question.answerability == "no_answer") == trace.answer_result.is_no_answer
            else 0.0
        ),
        "average_context_tokens": float(trace.context_build.final_estimated_context_tokens),
        "average_included_chunks": float(len(trace.context_build.included_chunks)),
    }
    return metrics


def _routing_match(question: Question, trace: QueryTrace) -> float | None:
    if question.expected_category is None or trace.route_decision is None:
        return None
    return 1.0 if trace.route_decision.selected_category == question.expected_category else 0.0


def _retrieval_hit(question: Question, trace: QueryTrace) -> float | None:
    if question.answerability != "answerable" or not question.expected_relevant_sources:
        return None
    return 1.0 if _first_relevant_rank(question, trace) is not None else 0.0


def _reciprocal_rank(question: Question, trace: QueryTrace) -> float | None:
    if question.answerability != "answerable" or not question.expected_relevant_sources:
        return None
    rank = _first_relevant_rank(question, trace)
    return 0.0 if rank is None else 1.0 / rank


def _citation_match(question: Question, trace: QueryTrace) -> float | None:
    if question.answerability != "answerable" or not question.expected_relevant_sources:
        return None
    expected = set(question.expected_relevant_sources)
    cited_chunk_ids = set(trace.citation_validation.cited_chunk_ids)
    for chunk in trace.context_build.included_chunks:
        if chunk.chunk_id not in cited_chunk_ids:
            continue
        if chunk.source_slug in expected or chunk.chunk_id in expected:
            return 1.0
    return 0.0


def _first_relevant_rank(question: Question, trace: QueryTrace) -> int | None:
    expected = set(question.expected_relevant_sources)
    for result in trace.retrieval_results:
        if result.source_slug in expected or result.chunk_id in expected:
            return result.rank
    return None


def _unique_retrieved_sources(trace: QueryTrace) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for result in trace.retrieval_results:
        if result.source_slug in seen:
            continue
        seen.add(result.source_slug)
        sources.append(result.source_slug)
    return sources


def _trace_errors(trace: QueryTrace) -> list[str]:
    errors: list[str] = []
    errors.extend(trace.answer_result.validation_errors)
    errors.extend(trace.citation_validation.validation_errors)
    errors.extend(f"invalid citation: {citation}" for citation in trace.citation_validation.invalid_citations)
    return errors


def _render_run_summary(
    run: EvaluationRun,
    case_counts: Mapping[str, int],
    json_path: Path | None,
) -> str:
    rows = [
        ("Run ID", run.run_id),
        ("Created at", run.created_at.isoformat()),
        ("Retrieval mode", run.retrieval_mode),
        ("Golden set", run.golden_set_path),
        ("Question count", len(run.questions)),
        ("Trace count", len(run.trace_paths)),
        ("JSON artifact", json_path or "not written"),
        ("Case mix", _format_mapping(case_counts)),
    ]
    return _render_key_value_table(rows)


def _render_configuration(run: EvaluationRun) -> str:
    rows = [("Retrieval mode", run.retrieval_mode)]
    rows.extend((key, value) for key, value in run.configuration.items())
    return _render_key_value_table(rows)


def _render_aggregate_metrics(run: EvaluationRun) -> str:
    lines = [
        "| Metric | Value | Reason |",
        "| --- | --- | --- |",
    ]
    counts = _counts_for_run(run)
    for name, value in run.metrics.model_dump().items():
        reason = ""
        if value is None:
            reason = "Not applicable for this run or no eligible golden questions."
        lines.append(
            "| "
            f"{_escape_table(name)} | "
            f"{_escape_table(_format_metric_result(name, value, counts.get(name)))} | "
            f"{_escape_table(reason)} |"
        )
    return "\n".join(lines)


def _render_question_table(
    questions: list[EvaluationQuestionResult],
    *,
    retrieval_mode: RetrievalMode,
) -> str:
    lines = [
        "| Question | Case type | Status | Top category | Searched categories | Trace | Expected sources | Retrieved sources | Errors |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in questions:
        lines.append(
            "| "
            f"{_escape_table(result.question_id)} | "
            f"{_escape_table(result.case_type)} | "
            f"{_escape_table(_question_status(result, retrieval_mode=retrieval_mode))} | "
            f"{_escape_table(result.selected_category or 'none')} | "
            f"{_escape_table(_format_list(result.searched_categories))} | "
            f"{_escape_table(result.trace_path)} | "
            f"{_escape_table(_format_list(result.expected_relevant_sources))} | "
            f"{_escape_table(_format_list(result.retrieved_sources))} | "
            f"{_escape_table(_format_list(result.errors))} |"
        )
    return "\n".join(lines)


def _question_status(
    result: EvaluationQuestionResult,
    *,
    retrieval_mode: RetrievalMode,
) -> str:
    status: list[str] = []
    if result.errors:
        status.append("runtime/citation error")
    route_filter_miss = _route_filter_missed(result, retrieval_mode=retrieval_mode)
    if route_filter_miss:
        status.append("route filter miss")
    source_retrieval_miss = result.metrics.get("hit_rate_at_k") == 0.0
    if not route_filter_miss and source_retrieval_miss:
        status.append("source retrieval miss")
    if (
        not route_filter_miss
        and not source_retrieval_miss
        and result.metrics.get("citation_source_match") == 0.0
    ):
        status.append("citation source miss")
    if result.metrics.get("no_answer_accuracy") == 0.0:
        status.append("answerability miss")
    return ", ".join(status) if status else "pass"


def _route_filter_missed(
    result: EvaluationQuestionResult,
    *,
    retrieval_mode: RetrievalMode,
) -> bool:
    if retrieval_mode != "routed-vector":
        return False
    if result.expected_category is None:
        return False
    if not result.searched_categories:
        return result.selected_category != result.expected_category
    return result.expected_category not in result.searched_categories


def _render_request_response_pairs(
    questions: list[EvaluationQuestionResult],
    *,
    retrieval_mode: RetrievalMode,
) -> str:
    if not questions:
        return "No question responses were recorded."

    sections: list[str] = []
    for result in questions:
        sections.extend(
            [
                f"### {_escape_heading(result.question_id)}",
                _render_key_value_table(
                    [
                        ("Case type", result.case_type),
                        ("Status", _question_status(result, retrieval_mode=retrieval_mode)),
                        (
                            "No-answer response",
                            (
                                "yes"
                                if result.is_no_answer is True
                                else "no" if result.is_no_answer is False else "unknown"
                            ),
                        ),
                    ]
                ),
                "**Request**",
                _fenced_text(result.question_text),
                "**Response**",
                _fenced_text(result.answer_text or "No answer text was recorded."),
            ]
        )
    return "\n\n".join(sections)


def _render_token_budget_diagnostics(run: EvaluationRun) -> str:
    rows = [
        ("Configured max context tokens", run.configuration.get("max_context_tokens", "n/a")),
        ("Configured output token limit", run.configuration.get("output_token_limit", "n/a")),
        ("Average context tokens", run.metrics.average_context_tokens),
        ("Average included chunks", run.metrics.average_included_chunks),
    ]
    lines = [_render_key_value_table(rows), ""]
    lines.extend(
        [
            "| Question | Context tokens | Included chunks |",
            "| --- | --- | --- |",
        ]
    )
    for result in run.questions:
        lines.append(
            "| "
            f"{_escape_table(result.question_id)} | "
            f"{_escape_table(_format_metric_value(result.metrics.get('average_context_tokens')))} | "
            f"{_escape_table(_format_metric_value(result.metrics.get('average_included_chunks')))} |"
        )
    return "\n".join(lines)


def _render_no_answer_cases(questions: list[EvaluationQuestionResult]) -> str:
    no_answer_results = [result for result in questions if result.case_type == "no_answer"]
    if not no_answer_results:
        return "No no-answer golden cases were present in this run."

    lines = [
        "| Question | No-answer accuracy | Retrieved sources | Errors |",
        "| --- | --- | --- | --- |",
    ]
    for result in no_answer_results:
        lines.append(
            "| "
            f"{_escape_table(result.question_id)} | "
            f"{_escape_table(_format_metric_value(result.metrics.get('no_answer_accuracy')))} | "
            f"{_escape_table(_format_list(result.retrieved_sources))} | "
            f"{_escape_table(_format_list(result.errors))} |"
        )
    return "\n".join(lines)


def _render_citation_failures(questions: list[EvaluationQuestionResult]) -> str:
    failures = [result for result in questions if result.errors]
    if not failures:
        return "None recorded."

    lines = [
        "| Question | Case type | Failures |",
        "| --- | --- | --- |",
    ]
    for result in failures:
        lines.append(
            "| "
            f"{_escape_table(result.question_id)} | "
            f"{_escape_table(result.case_type)} | "
            f"{_escape_table(_format_list(result.errors))} |"
        )
    return "\n".join(lines)


def _render_limitations() -> str:
    return "\n".join(
        [
            f"- {BENCHMARK_SCOPE_STATEMENT}",
            "- The benchmark is small enough that a difference between modes may represent only one changed question; the current hit-rate difference is exactly one of 14 retrieval-scored questions.",
            "- Top-category routing accuracy can be lower than retrieval hit rate because soft multi-category routing may search the expected category even when it is not ranked first.",
            "- Category margins are heuristic rather than calibrated probabilities.",
            "- Retrieval and routing configuration was adjusted while inspecting this same small benchmark, so these results are useful engineering evidence, not holdout validation.",
            "- Citation validation checks whether cited chunk IDs were included in the selected context; it does not prove claim-level factual correctness.",
            "- No-answer accuracy depends on the selected context and generation behavior for this run.",
            "- Token diagnostics use recorded estimates and model usage when available; provider-side accounting can differ.",
        ]
    )


def _metric_counts(
    questions: list[EvaluationQuestionResult],
) -> dict[MetricName, EvaluationMetricCount]:
    counts: dict[MetricName, EvaluationMetricCount] = {}
    for metric in RATE_METRICS:
        values = [
            question.metrics.get(metric)
            for question in questions
            if question.metrics.get(metric) is not None
        ]
        if values:
            counts[metric] = EvaluationMetricCount(
                numerator=sum(1 for value in values if value == 1.0),
                denominator=len(values),
            )
    return counts


def _counts_for_run(
    run: EvaluationRun,
) -> dict[MetricName, EvaluationMetricCount]:
    return run.metric_counts or _metric_counts(run.questions)


def _format_metric_result(
    metric: object,
    value: object,
    count: Mapping[str, Any] | EvaluationMetricCount | None,
) -> str:
    if value is None:
        return "n/a"
    if metric not in RATE_METRICS or not isinstance(value, int | float):
        return _format_metric_value(value)
    if isinstance(count, EvaluationMetricCount):
        numerator, denominator = count.numerator, count.denominator
    elif count:
        numerator, denominator = count["numerator"], count["denominator"]
    else:
        return f"{value:.1%}"
    return f"{numerator}/{denominator} questions, {value:.1%}"


def _render_key_value_table(rows: list[tuple[str, object]]) -> str:
    lines = [
        "| Field | Value |",
        "| --- | --- |",
    ]
    for key, value in rows:
        lines.append(f"| {_escape_table(key)} | {_escape_table(value)} |")
    return "\n".join(lines)


def _format_mapping(mapping: Mapping[str, int]) -> str:
    if not mapping:
        return "none"
    return ", ".join(f"{key}: {value}" for key, value in sorted(mapping.items()))


def _format_list(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


def _format_metric_value(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _escape_table(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _escape_heading(value: object) -> str:
    return str(value).replace("\n", " ").strip()


def _fenced_text(value: str) -> str:
    return f"````text\n{value.rstrip()}\n````"
