"""Command line interface for RAG Quality Lab."""

from __future__ import annotations

import json
from collections.abc import Callable
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
)
from rag_quality_lab.corpus.ingest import IngestionError, ingest_corpus
from rag_quality_lab.corpus.inspect import CorpusInspectionError, inspect_corpus
from rag_quality_lab.providers import ProviderError
from rag_quality_lab.schemas import (
    ArtifactIOError,
    ArtifactSchemaVersionError,
    CorpusSummaryArtifact,
    IngestionSummaryArtifact,
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
        "--top-k", min=1, help="Maximum number of retrieval results to request."
    ),
]
MaxContextTokensOption = Annotated[
    int,
    typer.Option("--max-context-tokens", min=1, help="Estimated context token budget."),
]
OutputTokenLimitOption = Annotated[
    int,
    typer.Option(
        "--output-token-limit", min=1, help="Maximum answer generation tokens."
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
    help="Run and compare retrieval evaluations.", no_args_is_help=True
)

app.add_typer(corpus_app, name="corpus")
app.add_typer(trace_app, name="trace")
app.add_typer(eval_app, name="eval")


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


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


def build_shared_options(json_output: bool = False) -> SharedOptions:
    """Create shared command options from Typer parameters."""

    return SharedOptions(json_output=json_output)


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
    if isinstance(error, ProviderError):
        return "provider"
    return "application"


def _echo_json_artifact(
    artifact: CorpusSummaryArtifact | IngestionSummaryArtifact,
) -> None:
    typer.echo(artifact.model_dump_json(indent=2))


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
