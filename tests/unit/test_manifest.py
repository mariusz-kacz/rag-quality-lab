from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES


pytestmark = pytest.mark.unit


def test_manifest_loads_valid_sources_with_required_provenance(
    temporary_corpus: dict[str, Path],
) -> None:
    load_manifest, _ = _manifest_api()

    manifest = load_manifest(
        temporary_corpus["manifest"],
        project_root=temporary_corpus["root"].parent,
    )

    assert manifest.source_count == 15
    assert len(manifest.sources) == 15
    assert manifest.category_counts == {
        category: 3 for category in REQUIRED_KNOWLEDGE_CATEGORIES
    }
    assert manifest.license_summary == {"MIT": 15}
    assert manifest.pinned_versions == {"dair-ai-prompt-guide@abc123"}

    first_source = manifest.sources[0]
    assert first_source.source_slug == "source-01"
    assert first_source.category == "prompting techniques"
    assert first_source.url == "https://example.test/prompt-guide/source-01"
    assert first_source.license == "MIT"
    assert first_source.pinned_version == "dair-ai-prompt-guide@abc123"
    assert first_source.local_ref == "corpus/sources/source-01.md"
    assert first_source.provenance.url == first_source.url
    assert first_source.provenance.license == first_source.license
    assert first_source.provenance.pinned_version == first_source.pinned_version
    assert first_source.provenance.local_ref == first_source.local_ref


def test_manifest_loads_source_count_below_documented_target(
    temporary_corpus: dict[str, Path],
) -> None:
    load_manifest, _ = _manifest_api()
    payload = _read_manifest(temporary_corpus["manifest"])
    payload["sources"] = payload["sources"][:14]
    _write_manifest(temporary_corpus["manifest"], payload)

    manifest = load_manifest(
        temporary_corpus["manifest"],
        project_root=temporary_corpus["root"].parent,
    )

    assert manifest.source_count == 14


def test_manifest_loads_source_count_above_documented_target(
    temporary_corpus: dict[str, Path],
) -> None:
    load_manifest, _ = _manifest_api()
    payload = _read_manifest(temporary_corpus["manifest"])
    extras = []
    for index in range(16):
        source = dict(payload["sources"][index % len(payload["sources"])])
        source["source_slug"] = f"extra-source-{index + 1:02d}"
        source["local_ref"] = f"corpus/sources/{source['source_slug']}.md"
        source_path = temporary_corpus["root"].parent / source["local_ref"]
        source_path.write_text("# Extra source\n", encoding="utf-8")
        extras.append(source)
    payload["sources"].extend(extras)
    _write_manifest(temporary_corpus["manifest"], payload)

    manifest = load_manifest(
        temporary_corpus["manifest"],
        project_root=temporary_corpus["root"].parent,
    )

    assert manifest.source_count == 31


def test_manifest_rejects_unknown_category(
    temporary_corpus: dict[str, Path],
) -> None:
    load_manifest, ManifestValidationError = _manifest_api()
    payload = _read_manifest(temporary_corpus["manifest"])
    payload["sources"][0]["category"] = "unsupported category"
    _write_manifest(temporary_corpus["manifest"], payload)

    with pytest.raises(ManifestValidationError, match="category"):
        load_manifest(
            temporary_corpus["manifest"],
            project_root=temporary_corpus["root"].parent,
        )


@pytest.mark.parametrize(
    ("field", "expected_message"),
    [
        ("url", "url"),
        ("license", "license"),
        ("pinned_version", "pinned_version"),
        ("local_ref", "local_ref"),
    ],
)
def test_manifest_rejects_missing_required_provenance_fields(
    temporary_corpus: dict[str, Path],
    field: str,
    expected_message: str,
) -> None:
    load_manifest, ManifestValidationError = _manifest_api()
    payload = _read_manifest(temporary_corpus["manifest"])
    payload["sources"][0].pop(field)
    _write_manifest(temporary_corpus["manifest"], payload)

    with pytest.raises(ManifestValidationError, match=expected_message):
        load_manifest(
            temporary_corpus["manifest"],
            project_root=temporary_corpus["root"].parent,
        )


def test_manifest_rejects_missing_local_ref_file(
    temporary_corpus: dict[str, Path],
) -> None:
    load_manifest, ManifestValidationError = _manifest_api()
    missing_snapshot = temporary_corpus["root"] / "sources" / "source-01.md"
    missing_snapshot.unlink()

    with pytest.raises(ManifestValidationError, match="corpus/sources/source-01.md"):
        load_manifest(
            temporary_corpus["manifest"],
            project_root=temporary_corpus["root"].parent,
        )


def _manifest_api() -> tuple[Any, type[Exception]]:
    from rag_quality_lab.corpus.manifest import ManifestValidationError, load_manifest

    return load_manifest, ManifestValidationError


def _read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
