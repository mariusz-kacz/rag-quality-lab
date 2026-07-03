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
from rag_quality_lab.config import ConfigurationError, InvalidConfigurationError, MissingSettingError
from rag_quality_lab.providers import ProviderError
from rag_quality_lab.schemas import ArtifactIOError, ArtifactSchemaVersionError


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
    typer.Option("--top-k", min=1, help="Maximum number of retrieval results to request."),
]
MaxContextTokensOption = Annotated[
    int,
    typer.Option("--max-context-tokens", min=1, help="Estimated context token budget."),
]
OutputTokenLimitOption = Annotated[
    int,
    typer.Option("--output-token-limit", min=1, help="Maximum answer generation tokens."),
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
corpus_app = typer.Typer(help="Inspect and ingest the curated corpus.", no_args_is_help=True)
trace_app = typer.Typer(help="Inspect persisted query traces.", no_args_is_help=True)
eval_app = typer.Typer(help="Run and compare retrieval evaluations.", no_args_is_help=True)

app.add_typer(corpus_app, name="corpus")
app.add_typer(trace_app, name="trace")
app.add_typer(eval_app, name="eval")


@app.command()
def version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


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

    if isinstance(error, (MissingSettingError, InvalidConfigurationError, ConfigurationError)):
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
    if isinstance(error, ConfigurationError):
        return "configuration"
    if isinstance(error, ArtifactIOError):
        return "artifact"
    if isinstance(error, ProviderError):
        return "provider"
    return "application"


if __name__ == "__main__":
    app()
