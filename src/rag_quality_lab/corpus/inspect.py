"""Corpus inspection summaries for validated manifest metadata."""

from __future__ import annotations

from pathlib import Path

from rag_quality_lab.corpus.manifest import (
    DEFAULT_CATEGORIES_PATH,
    DEFAULT_MANIFEST_PATH,
    ManifestValidationError,
    load_categories,
    load_manifest,
)
from rag_quality_lab.schemas import CorpusSummaryArtifact


class CorpusInspectionError(Exception):
    """Raised when corpus inspection cannot produce a valid summary."""


def inspect_corpus(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    categories_path: str | Path = DEFAULT_CATEGORIES_PATH,
    *,
    project_root: str | Path | None = None,
) -> CorpusSummaryArtifact:
    """Load corpus metadata and return the machine-readable inspection summary."""

    try:
        manifest = load_manifest(manifest_path, project_root=project_root)
        load_categories(categories_path, project_root=project_root)
    except ManifestValidationError as exc:
        raise CorpusInspectionError(_inspection_error_message(str(exc))) from exc

    return CorpusSummaryArtifact(
        source_count=manifest.source_count,
        categories=manifest.category_counts,
        license_summary=manifest.license_summary,
        pinned_version=_summarize_pinned_versions(manifest.pinned_versions),
        sources=list(manifest.sources),
        validation_errors=[],
    )


def _summarize_pinned_versions(pinned_versions: set[str]) -> str | None:
    if not pinned_versions:
        return None
    versions = sorted(pinned_versions)
    if len(versions) == 1:
        return versions[0]
    return ", ".join(versions)


def _inspection_error_message(message: str) -> str:
    if message.startswith("Missing local snapshot for "):
        return message.replace(
            "Missing local snapshot", "missing local source snapshot", 1
        )
    return message
