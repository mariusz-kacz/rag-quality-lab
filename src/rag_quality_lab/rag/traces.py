"""Persistence helpers for query trace artifacts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from rag_quality_lab.schemas import ArtifactIOError, QueryTrace
from rag_quality_lab.schemas.artifacts import read_json_artifact, write_json_artifact


DEFAULT_TRACE_DIR = Path("artifacts/traces")


def new_trace_id() -> str:
    """Return a stable-format identifier for one query trace."""

    return f"trace-{uuid4().hex}"


def trace_path_for(trace: QueryTrace, trace_dir: str | Path = DEFAULT_TRACE_DIR) -> Path:
    """Build the artifact path for a trace without touching the filesystem."""

    return Path(trace_dir) / f"{trace.trace_id}.json"


def save_trace(
    trace: QueryTrace,
    trace_dir: str | Path = DEFAULT_TRACE_DIR,
) -> Path:
    """Persist a query trace as JSON and return the written path."""

    return write_json_artifact(trace_path_for(trace, trace_dir), trace)


def load_trace(path: str | Path) -> QueryTrace:
    """Load and validate a query trace artifact."""

    trace_path = Path(path)
    try:
        return read_json_artifact(trace_path, QueryTrace)
    except FileNotFoundError as exc:
        raise ArtifactIOError(f"Trace artifact not found: {trace_path}") from exc
    except ValidationError as exc:
        raise ArtifactIOError(
            f"Invalid query trace artifact at {trace_path}: {exc.errors(include_url=False)}"
        ) from exc
