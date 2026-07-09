from __future__ import annotations

from pathlib import Path

import pytest

from rag_quality_lab.rag.traces import (
    load_trace,
    new_trace_id,
    save_trace,
    trace_path_for,
)
from rag_quality_lab.schemas import ArtifactIOError, QueryTrace


pytestmark = pytest.mark.unit


def test_trace_path_save_and_load_round_trip(
    tmp_path: Path,
    sample_query_trace: QueryTrace,
) -> None:
    trace_dir = tmp_path / "traces"

    assert trace_path_for(sample_query_trace, trace_dir) == (
        trace_dir / "trace-test-001.json"
    )

    trace_path = save_trace(sample_query_trace, trace_dir)
    loaded_trace = load_trace(trace_path)

    assert trace_path == trace_dir / "trace-test-001.json"
    assert loaded_trace == sample_query_trace


def test_new_trace_id_uses_trace_prefix() -> None:
    trace_id = new_trace_id()

    assert trace_id.startswith("trace-")
    assert len(trace_id) > len("trace-")


def test_load_trace_reports_missing_file_as_artifact_error(tmp_path: Path) -> None:
    missing_trace = tmp_path / "missing.json"

    with pytest.raises(ArtifactIOError, match="Trace artifact not found"):
        load_trace(missing_trace)
