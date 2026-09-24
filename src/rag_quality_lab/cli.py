"""Command line interface for RAG Quality Lab."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Annotated, TypeVar

import typer

from rag_quality_lab import __version__
from rag_quality_lab.config import (
    ConfigurationError,
    InvalidConfigurationError,
    MissingSettingError,
    RuntimeConfig,
    load_app_config,
    load_runtime_config,
)
from rag_quality_lab.corpus.ingest import IngestionError, ingest_corpus
from rag_quality_lab.corpus.inspect import CorpusInspectionError, inspect_corpus
from rag_quality_lab.providers import ProviderError
from rag_quality_lab.rag.traces import load_trace
from rag_quality_lab.retrieval.modes import RetrievalModeError, validate_retrieval_mode
from rag_quality_lab.schemas import (
    ArtifactIOError,
    ArtifactSchemaVersionError,
    CorpusSummaryArtifact,
    IngestionSummaryArtifact,
    QueryTrace,
)


class ExitCode(IntEnum):
    """Process exit codes used by CLI command wrappers."""

    SUCCESS = 0
    ERROR = 1
    CONFIGURATION = 2
    ARTIFACT = 3
    PROVIDER = 4


JsonOutputOption = Annotated[
    bool,
    typer.Option("--json", help="Emit machine-readable JSON output."),
]
TopKOption = Annotated[
    int,
    typer.Option(
        "--top-k",
        min=1,
        envvar="RAGLAB_TOP_K",
        help="Maximum context chunks; also retrieval depth when reranking is off.",
    ),
]
RerankOption = Annotated[
    bool,
    typer.Option(
        "--rerank/--no-rerank",
        envvar="RAGLAB_RERANK_ENABLED",
        help="Rerank vector candidates with a local cross-encoder.",
    ),
]
CandidateKOption = Annotated[
    int,
    typer.Option(
        "--candidate-k",
        min=1,
        envvar="RAGLAB_CANDIDATE_K",
        help="Vector candidates to retrieve when reranking is enabled.",
    ),
]
MaxContextTokensOption = Annotated[
    int,
    typer.Option(
        "--max-context-tokens",
        min=1,
        envvar="RAGLAB_MAX_CONTEXT_TOKENS",
        help="Estimated context token budget.",
    ),
]
OutputTokenLimitOption = Annotated[
    int,
    typer.Option(
        "--output-token-limit",
        min=1,
        envvar="RAGLAB_OUTPUT_TOKEN_LIMIT",
        help="Maximum answer generation tokens.",
    ),
]
TraceDirOption = Annotated[
    Path,
    typer.Option("--trace-dir", help="Directory where query traces are written."),
]

CommandResult = TypeVar("CommandResult")


@dataclass(frozen=True)
class SharedOptions:
    """Common command output controls."""

    json_output: bool = False


app = typer.Typer(
    name="raglab",
    help="CLI-first RAG quality engineering lab.",
    no_args_is_help=True,
)
corpus_app = typer.Typer(
    help="Inspect and ingest the curated corpus.", no_args_is_help=True
)
trace_app = typer.Typer(help="Inspect persisted query traces.", no_args_is_help=True)
eval_app = typer.Typer(
    help="Evaluate RAG answers with Ragas.",
    no_args_is_help=True,
)

app.add_typer(corpus_app, name="corpus")
app.add_typer(trace_app, name="trace")
app.add_typer(eval_app, name="eval")


def _evaluation_command(operation, json_output):
    """Keep Ragas progress separate from one JSON result or error."""
    try:
        with redirect_stdout(sys.stderr):
            result = operation()
    except Exception as exc:
        path = getattr(exc, "dataset_path", None)
        results_path = getattr(exc, "results_path", None)
        stage = getattr(exc, "stage", stage_for_error(exc))
        payload = {
            "ok": False,
            "stage": stage,
            "message": str(exc),
            "dataset_path": str(path) if path else None,
            "results_path": str(results_path) if results_path else None,
        }
        if json_output:
            typer.echo(json.dumps(payload), err=True)
        else:
            typer.echo(
                f"Error: {exc}" + (f"\nSaved run: {path}" if path else ""), err=True
            )
        code = {
            "evaluation": ExitCode.PROVIDER,
            "retrieval": ExitCode.PROVIDER,
            "artifact": ExitCode.ARTIFACT,
        }.get(stage, exit_code_for_error(exc))
        raise typer.Exit(int(code)) from None
    if json_output:
        typer.echo(json.dumps(result, allow_nan=False))
    else:
        typer.echo(
            f"Answers: {result['dataset_path']}\nResults: {result['results_path']}"
        )
        for name, metric in result["metrics"].items():
            typer.echo(
                f"{name}: {metric['mean']} ({metric['scored_count']}/{metric['eligible_count']} scored)"
            )
        typer.echo(f"Refusal detection (diagnostic): {result['diagnostics']}")


@eval_app.callback()
def eval_main():
    """Evaluate RAG answers with Ragas."""


@eval_app.command("run")
def eval_run(
    mode: Annotated[str, typer.Option("--mode")] = "baseline-vector",
    golden: Annotated[Path, typer.Option("--golden")] = Path("golden/questions.json"),
    artifacts_dir: Annotated[Path, typer.Option("--artifacts-dir")] = Path(
        "artifacts/eval"
    ),
    question_ids: Annotated[list[str] | None, typer.Option("--question-id")] = None,
    top_k: TopKOption = RuntimeConfig().top_k,
    max_context_tokens: MaxContextTokensOption = RuntimeConfig().max_context_tokens,
    output_token_limit: OutputTokenLimitOption = RuntimeConfig().output_token_limit,
    rerank_enabled: RerankOption = RuntimeConfig().rerank_enabled,
    candidate_k: CandidateKOption = RuntimeConfig().candidate_k,
    json_output: JsonOutputOption = False,
) -> None:
    """Capture answers with the lab pipeline, then score them with Ragas."""

    def operation():
        from rag_quality_lab.eval.runner import run_evaluation

        return run_evaluation(
            mode=mode,
            golden_path=golden,
            artifacts_dir=artifacts_dir,
            question_ids=question_ids,
            runtime=load_runtime_config(
                top_k=top_k,
                max_context_tokens=max_context_tokens,
                output_token_limit=output_token_limit,
                rerank_enabled=rerank_enabled,
                candidate_k=candidate_k,
            ),
        )

    _evaluation_command(operation, json_output)


@app.callback()
def main(
    env_file: Annotated[
        Path | None,
        typer.Option(
            "--env-file",
            help=(
                "Load local environment variables from a dotenv-style file. "
                "Existing process environment variables take precedence."
            ),
        ),
    ] = None,
) -> None:
    """Apply global CLI options before running a command."""

    if env_file is not None:
        load_env_file(env_file)


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


@app.command("query")
def query(
    question: Annotated[str, typer.Argument(help="Question to run through RAG.")],
    mode: Annotated[
        str,
        typer.Option("--mode", help="Retrieval mode to use."),
    ] = "baseline-vector",
    top_k: TopKOption = RuntimeConfig().top_k,
    max_context_tokens: MaxContextTokensOption = RuntimeConfig().max_context_tokens,
    output_token_limit: OutputTokenLimitOption = RuntimeConfig().output_token_limit,
    trace_dir: TraceDirOption = RuntimeConfig().trace_dir,
    rerank_enabled: RerankOption = RuntimeConfig().rerank_enabled,
    candidate_k: CandidateKOption = RuntimeConfig().candidate_k,
    json_output: JsonOutputOption = False,
) -> None:
    """Run one traced RAG query."""

    result = run_cli_command(
        lambda: run_query(
            question,
            mode=validate_retrieval_mode(mode),
            top_k=top_k,
            max_context_tokens=max_context_tokens,
            output_token_limit=output_token_limit,
            trace_dir=trace_dir,
            rerank_enabled=rerank_enabled,
            candidate_k=candidate_k,
        ),
        json_output=json_output,
    )
    trace = result["trace"]
    trace_path = Path(result["trace_path"])
    if json_output:
        _echo_query_result_json(trace, trace_path)
        return
    _echo_query_result(trace, trace_path)


@corpus_app.command("inspect")
def corpus_inspect(
    json_output: JsonOutputOption = False,
) -> None:
    """Inspect the curated corpus manifest and local source snapshots."""

    summary = run_cli_command(
        inspect_corpus,
        json_output=json_output,
    )
    if json_output:
        _echo_json_artifact(summary)
        return
    _echo_corpus_summary(summary)


@corpus_app.command("ingest")
def corpus_ingest(
    collection: Annotated[
        str | None,
        typer.Option("--collection", help="Target Qdrant collection."),
    ] = None,
    recreate: Annotated[
        bool,
        typer.Option(
            "--recreate", help="Recreate the target collection before ingestion."
        ),
    ] = False,
    json_output: JsonOutputOption = False,
) -> None:
    """Validate, chunk, embed, and load the corpus into Qdrant."""

    summary = run_cli_command(
        lambda: ingest_corpus(collection=collection, recreate=recreate),
        json_output=json_output,
    )
    if json_output:
        _echo_json_artifact(summary)
        return
    _echo_ingestion_summary(summary)


@trace_app.command("inspect")
def trace_inspect(
    trace_path: Annotated[Path, typer.Argument(help="Path to a persisted trace JSON.")],
    json_output: JsonOutputOption = False,
) -> None:
    """Inspect a persisted query trace."""

    trace = run_cli_command(
        lambda: load_trace(trace_path),
        json_output=json_output,
    )
    if json_output:
        typer.echo(trace.model_dump_json(indent=2))
        return
    _echo_trace_summary(trace)


def build_shared_options(json_output: bool = False) -> SharedOptions:
    """Create shared command options from Typer parameters."""

    return SharedOptions(json_output=json_output)


def load_env_file(path: str | Path) -> dict[str, str]:
    """Load missing process environment variables from a dotenv-style file."""

    env_path = Path(path)
    if not env_path.exists():
        raise typer.BadParameter(f"env file not found: {env_path}")
    if not env_path.is_file():
        raise typer.BadParameter(f"env file is not a file: {env_path}")

    loaded: dict[str, str] = {}
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise typer.BadParameter(f"env file could not be read: {env_path}") from exc

    for line_number, raw_line in enumerate(lines, start=1):
        parsed = _parse_env_line(raw_line, line_number=line_number, path=env_path)
        if parsed is None:
            continue
        name, value = parsed
        if os.environ.get(name) is None:
            os.environ[name] = value
            loaded[name] = value
    return loaded


def _parse_env_line(
    raw_line: str,
    *,
    line_number: int,
    path: Path,
) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line.removeprefix("export ").strip()
    if "=" not in line:
        raise typer.BadParameter(
            f"invalid env file line {line_number} in {path}: expected NAME=VALUE"
        )

    name, value = line.split("=", 1)
    clean_name = name.strip()
    if not clean_name:
        raise typer.BadParameter(
            f"invalid env file line {line_number} in {path}: variable name is empty"
        )
    return clean_name, _clean_env_value(value)


def _clean_env_value(value: str) -> str:
    clean = value.strip()
    if len(clean) >= 2 and clean[0] == clean[-1] and clean[0] in {'"', "'"}:
        return clean[1:-1]
    return clean


def run_cli_command(
    operation: Callable[[], CommandResult],
    *,
    json_output: bool = False,
) -> CommandResult:
    """Run a command operation and convert project errors into CLI exits."""

    try:
        return operation()
    except Exception as exc:
        handle_cli_error(exc, json_output=json_output)
        raise


def handle_cli_error(error: Exception, *, json_output: bool = False) -> None:
    """Render a project exception and raise a Typer exit with the mapped code."""

    exit_code = exit_code_for_error(error)
    stage = stage_for_error(error)
    message = str(error)

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "ok": False,
                    "stage": stage,
                    "error_type": type(error).__name__,
                    "message": message,
                },
                sort_keys=True,
            ),
            err=True,
        )
        if isinstance(error, ArtifactIOError):
            typer.echo(message, err=True)
    else:
        typer.secho(
            f"Error [{stage}]: {message}",
            fg=typer.colors.RED,
            err=True,
        )

    raise typer.Exit(int(exit_code))


def exit_code_for_error(error: Exception) -> ExitCode:
    """Map known project exceptions to stable process exit codes."""

    if isinstance(
        error, (MissingSettingError, InvalidConfigurationError, ConfigurationError)
    ):
        return ExitCode.CONFIGURATION
    if isinstance(error, (ArtifactSchemaVersionError, ArtifactIOError)):
        return ExitCode.ARTIFACT
    if isinstance(error, RetrievalModeError):
        return ExitCode.ERROR
    if isinstance(error, ProviderError):
        return ExitCode.PROVIDER
    return ExitCode.ERROR


def stage_for_error(error: Exception) -> str:
    """Return a reviewer-readable failing stage for an exception."""

    if isinstance(error, MissingSettingError):
        return error.stage
    if isinstance(error, CorpusInspectionError):
        return "corpus inspect"
    if isinstance(error, IngestionError):
        return "corpus ingest"
    if isinstance(error, ConfigurationError):
        return "configuration"
    if isinstance(error, ArtifactIOError):
        return "artifact"
    if isinstance(error, RetrievalModeError):
        return "retrieval mode"
    if isinstance(error, ProviderError):
        return "provider"
    return "application"


def run_query(
    question: str,
    *,
    mode: str,
    top_k: int,
    max_context_tokens: int,
    output_token_limit: int,
    trace_dir: Path,
    rerank_enabled: bool = False,
    candidate_k: int = 20,
) -> dict[str, object]:
    """Lazy wrapper for the query pipeline, kept patchable in CLI tests."""

    from rag_quality_lab.rag.pipeline import run_query as pipeline_run_query

    if not question.strip():
        raise ValueError("question cannot be empty")
    runtime = load_runtime_config(
        top_k=top_k,
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
        trace_dir=trace_dir,
        rerank_enabled=rerank_enabled,
        candidate_k=candidate_k,
    )
    return pipeline_run_query(
        question,
        mode=mode,
        top_k=top_k,
        max_context_tokens=max_context_tokens,
        output_token_limit=output_token_limit,
        trace_dir=trace_dir,
        rerank_enabled=rerank_enabled,
        candidate_k=candidate_k,
        config=load_app_config(runtime=runtime),
    )


def _echo_json_artifact(
    artifact: CorpusSummaryArtifact | IngestionSummaryArtifact,
) -> None:
    typer.echo(artifact.model_dump_json(indent=2))


def _echo_query_result_json(trace: QueryTrace, trace_path: Path) -> None:
    payload = {
        "schema_version": trace.schema_version,
        "question": trace.question.text,
        "retrieval_mode": trace.retrieval_mode,
        "answer_text": trace.answer_result.answer_text,
        "is_no_answer": trace.answer_result.is_no_answer,
        "citations": trace.answer_result.citations,
        "validation_status": trace.answer_result.validation_status,
        "route_decision": (
            trace.route_decision.model_dump(mode="json")
            if trace.route_decision is not None
            else None
        ),
        "retrieval_result_count": len(trace.retrieval_results),
        "rerank_model": trace.reranking.model if trace.reranking else None,
        "rerank_elapsed_ms": trace.reranking.elapsed_ms if trace.reranking else None,
        "included_chunk_count": len(trace.context_build.included_chunks),
        "excluded_chunk_count": len(trace.context_build.excluded_chunks),
        "final_estimated_context_tokens": (
            trace.context_build.final_estimated_context_tokens
        ),
        "output_token_limit": trace.context_build.output_token_limit,
        "trace_id": trace.trace_id,
        "trace_path": str(trace_path),
    }
    typer.echo(json.dumps(payload, indent=2))


def _echo_query_result(trace: QueryTrace, trace_path: Path) -> None:
    typer.echo(trace.answer_result.answer_text)
    citations = ", ".join(trace.answer_result.citations) or "none"
    typer.echo(f"Citations: {citations}")
    typer.echo(f"Validation: {trace.answer_result.validation_status}")
    typer.echo(f"Mode: {trace.retrieval_mode}")
    typer.echo(f"Route: {_route_label(trace)}")
    typer.echo(f"Retrieved chunks: {len(trace.retrieval_results)}")
    if trace.reranking:
        typer.echo(
            f"Reranker: {trace.reranking.model} ({trace.reranking.elapsed_ms:.0f} ms)"
        )
    typer.echo(f"Included chunks: {len(trace.context_build.included_chunks)}")
    typer.echo(f"Excluded chunks: {len(trace.context_build.excluded_chunks)}")
    typer.echo(f"Trace: {trace_path}")


def _echo_trace_summary(trace: QueryTrace) -> None:
    total_tokens = (
        trace.model_usage.total_tokens
        if trace.model_usage is not None and trace.model_usage.total_tokens is not None
        else "unknown"
    )
    typer.echo(f"Trace: {trace.trace_id}")
    typer.echo(f"Question: {trace.question.text}")
    typer.echo(f"Mode: {trace.retrieval_mode}")
    typer.echo(f"Route: {_route_label(trace)}")
    typer.echo(f"Retrieved chunks: {len(trace.retrieval_results)}")
    if trace.reranking:
        typer.echo(
            f"Reranker: {trace.reranking.model} ({trace.reranking.elapsed_ms:.0f} ms)"
        )
    typer.echo(f"Included chunks: {len(trace.context_build.included_chunks)}")
    typer.echo(f"Excluded chunks: {len(trace.context_build.excluded_chunks)}")
    typer.echo(f"Citation validation: {trace.citation_validation.status}")
    typer.echo(f"Model usage: {total_tokens} tokens")


def _route_label(trace: QueryTrace) -> str:
    if trace.route_decision is None:
        return "not applicable"
    if trace.route_decision.fallback_all_categories:
        return "all categories"
    return str(trace.route_decision.selected_category)


def _echo_corpus_summary(summary: CorpusSummaryArtifact) -> None:
    typer.echo("Corpus inspection")
    typer.echo(f"Sources: {summary.source_count}")
    typer.echo(f"Pinned version: {summary.pinned_version or 'mixed'}")
    typer.echo("Categories:")
    for category, count in summary.categories.items():
        typer.echo(f"  - {category}: {count}")
    typer.echo("Licenses:")
    for license_name, count in summary.license_summary.items():
        typer.echo(f"  - {license_name}: {count}")
    if summary.validation_errors:
        typer.echo("Validation errors:")
        for error in summary.validation_errors:
            typer.echo(f"  - {error}")
    else:
        typer.echo("Validation errors: none")


def _echo_ingestion_summary(summary: IngestionSummaryArtifact) -> None:
    typer.echo("Corpus ingestion")
    typer.echo(f"Collection: {summary.collection}")
    typer.echo(f"Sources: {summary.source_count}")
    typer.echo(f"Chunks: {summary.chunk_count}")
    typer.echo(f"Embedding model: {summary.embedding_model}")
    typer.echo("Categories:")
    for category, count in summary.category_counts.items():
        typer.echo(f"  - {category}: {count}")
    if summary.validation_errors:
        typer.echo("Validation errors:")
        for error in summary.validation_errors:
            typer.echo(f"  - {error}")
    else:
        typer.echo("Validation errors: none")


if __name__ == "__main__":
    app()
