"""Manifest loading and validation for the curated corpus."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from rag_quality_lab.schemas import (
    DEFAULT_SCHEMA_VERSION,
    REQUIRED_KNOWLEDGE_CATEGORIES,
    SourcePage,
)
from rag_quality_lab.schemas.categories import KnowledgeCategory


RECOMMENDED_MIN_SOURCE_COUNT = 15
RECOMMENDED_MAX_SOURCE_COUNT = 30
DEFAULT_CORPUS_DIR = "corpus"
DEFAULT_MANIFEST_PATH = Path(DEFAULT_CORPUS_DIR) / "manifest.json"
DEFAULT_CATEGORIES_PATH = Path(DEFAULT_CORPUS_DIR) / "categories.json"


class ManifestValidationError(Exception):
    """Raised when corpus manifest metadata is invalid."""


@dataclass(frozen=True)
class CorpusManifest:
    """Validated source manifest and derived inspection summaries."""

    schema_version: str
    sources: tuple[SourcePage, ...]
    manifest_path: Path

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def category_counts(self) -> dict[str, int]:
        counts = Counter(str(source.category) for source in self.sources)
        return {
            category: counts[category] for category in REQUIRED_KNOWLEDGE_CATEGORIES
        }

    @property
    def license_summary(self) -> dict[str, int]:
        return dict(Counter(source.license for source in self.sources))

    @property
    def pinned_versions(self) -> set[str]:
        return {source.pinned_version for source in self.sources}


@dataclass(frozen=True)
class CategoryManifest:
    """Validated routing category manifest."""

    schema_version: str
    categories: tuple[KnowledgeCategory, ...]
    categories_path: Path

    @property
    def category_count(self) -> int:
        return len(self.categories)

    @property
    def by_name(self) -> dict[str, KnowledgeCategory]:
        return {str(category.name): category for category in self.categories}


def load_manifest(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    *,
    project_root: str | Path | None = None,
) -> CorpusManifest:
    """Load and validate the selected corpus source manifest."""

    resolved_manifest_path = _resolve_input_path(
        manifest_path, project_root=project_root
    )
    raw_manifest = _read_json_object(resolved_manifest_path, label="manifest")
    schema_version = _validate_schema_version(raw_manifest, resolved_manifest_path)

    raw_sources = raw_manifest.get("sources")
    if not isinstance(raw_sources, list):
        raise ManifestValidationError(
            f"Manifest at {resolved_manifest_path} must contain a sources array"
        )

    sources = tuple(
        _validate_source(raw_source, index)
        for index, raw_source in enumerate(raw_sources)
    )
    _validate_unique_source_slugs(sources)
    _validate_required_categories_present(sources)

    root = (
        Path(project_root).resolve()
        if project_root is not None
        else resolved_manifest_path.parent.parent
    )
    for source in sources:
        _validate_local_ref(source, project_root=root)

    return CorpusManifest(
        schema_version=schema_version,
        sources=sources,
        manifest_path=resolved_manifest_path,
    )


def load_categories(
    categories_path: str | Path = DEFAULT_CATEGORIES_PATH,
    *,
    project_root: str | Path | None = None,
) -> CategoryManifest:
    """Load and validate deterministic routing category definitions."""

    resolved_categories_path = _resolve_input_path(
        categories_path, project_root=project_root
    )
    raw_categories_payload = _read_json_object(
        resolved_categories_path, label="categories"
    )
    schema_version = _validate_schema_version(
        raw_categories_payload, resolved_categories_path
    )

    raw_categories = raw_categories_payload.get("categories")
    if not isinstance(raw_categories, list):
        raise ManifestValidationError(
            f"Categories file at {resolved_categories_path} must contain a categories array"
        )

    categories = tuple(
        _validate_category(raw_category, index)
        for index, raw_category in enumerate(raw_categories)
    )
    _validate_exact_required_categories(categories)

    return CategoryManifest(
        schema_version=schema_version,
        categories=categories,
        categories_path=resolved_categories_path,
    )


def _resolve_input_path(path: str | Path, *, project_root: str | Path | None) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() and project_root is not None:
        candidate = Path(project_root) / candidate
    return candidate.resolve()


def _read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestValidationError(f"Missing {label} file at {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestValidationError(
            f"Invalid JSON in {label} file at {path}: {exc.msg}"
        ) from exc

    if not isinstance(payload, dict):
        raise ManifestValidationError(
            f"{label.capitalize()} file at {path} must contain a JSON object"
        )
    return payload


def _validate_schema_version(payload: dict[str, Any], path: Path) -> str:
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise ManifestValidationError(
            f"File at {path} is missing required schema_version"
        )
    if schema_version != DEFAULT_SCHEMA_VERSION:
        raise ManifestValidationError(
            f"File at {path} uses schema_version {schema_version!r}; "
            f"expected {DEFAULT_SCHEMA_VERSION!r}"
        )
    return schema_version


def _validate_source(raw_source: object, index: int) -> SourcePage:
    if not isinstance(raw_source, dict):
        raise ManifestValidationError(
            f"Manifest source at index {index} must be a JSON object"
        )
    try:
        return SourcePage.model_validate(raw_source)
    except ValidationError as exc:
        raise ManifestValidationError(
            f"Invalid manifest source at index {index}: {_format_validation_error(exc)}"
        ) from exc


def _validate_category(raw_category: object, index: int) -> KnowledgeCategory:
    if not isinstance(raw_category, dict):
        raise ManifestValidationError(
            f"Category at index {index} must be a JSON object"
        )
    try:
        return KnowledgeCategory.model_validate(raw_category)
    except ValidationError as exc:
        raise ManifestValidationError(
            f"Invalid category at index {index}: {_format_validation_error(exc)}"
        ) from exc


def _validate_unique_source_slugs(sources: tuple[SourcePage, ...]) -> None:
    counts = Counter(source.source_slug for source in sources)
    duplicate_slugs = sorted(slug for slug, count in counts.items() if count > 1)
    if duplicate_slugs:
        raise ManifestValidationError(
            f"Manifest contains duplicate source_slug values: {', '.join(duplicate_slugs)}"
        )


def _validate_required_categories_present(sources: tuple[SourcePage, ...]) -> None:
    present_categories = {str(source.category) for source in sources}
    missing_categories = [
        category
        for category in REQUIRED_KNOWLEDGE_CATEGORIES
        if category not in present_categories
    ]
    if missing_categories:
        raise ManifestValidationError(
            f"Manifest must include all required categories; missing: {', '.join(missing_categories)}"
        )


def _validate_exact_required_categories(
    categories: tuple[KnowledgeCategory, ...],
) -> None:
    names = [str(category.name) for category in categories]
    counts = Counter(names)
    duplicate_names = sorted(name for name, count in counts.items() if count > 1)
    if duplicate_names:
        raise ManifestValidationError(
            f"Categories file contains duplicate category names: {', '.join(duplicate_names)}"
        )

    expected = set(REQUIRED_KNOWLEDGE_CATEGORIES)
    actual = set(names)
    missing = [
        category for category in REQUIRED_KNOWLEDGE_CATEGORIES if category not in actual
    ]
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected: {', '.join(unexpected)}")
        raise ManifestValidationError(
            "Categories file must contain exactly the five required categories; "
            + "; ".join(details)
        )


def _validate_local_ref(source: SourcePage, *, project_root: Path) -> None:
    local_ref = Path(source.local_ref)
    if local_ref.is_absolute():
        raise ManifestValidationError(
            f"local_ref for {source.source_slug} must be project-relative: {source.local_ref}"
        )

    root = project_root.resolve()
    source_path = (root / local_ref).resolve()
    try:
        source_path.relative_to(root)
    except ValueError as exc:
        raise ManifestValidationError(
            f"local_ref for {source.source_slug} escapes the project root: {source.local_ref}"
        ) from exc

    if not source_path.is_file():
        raise ManifestValidationError(
            f"Missing local snapshot for {source.source_slug}: {source.local_ref}"
        )
    try:
        with source_path.open("r", encoding="utf-8") as source_file:
            source_file.read(1)
    except OSError as exc:
        raise ManifestValidationError(
            f"Local snapshot for {source.source_slug} is not readable: {source.local_ref}"
        ) from exc


def _format_validation_error(exc: ValidationError) -> str:
    first_error = exc.errors()[0]
    location = ".".join(str(part) for part in first_error.get("loc", ())) or "<root>"
    message = first_error.get("msg", "validation failed")
    return f"{location}: {message}"
