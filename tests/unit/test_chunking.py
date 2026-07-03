from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.schemas import SourcePage, SourceSection


pytestmark = pytest.mark.unit


def test_chunk_source_page_produces_deterministic_chunk_ids(
    sample_source_page: SourcePage,
) -> None:
    chunk_source_page, _, _, _ = _chunking_api()
    markdown = _sample_markdown()

    first_run = chunk_source_page(sample_source_page, markdown, max_chunk_tokens=80)
    second_run = chunk_source_page(sample_source_page, markdown, max_chunk_tokens=80)

    assert [chunk.chunk_id for chunk in first_run] == [
        chunk.chunk_id for chunk in second_run
    ]
    assert [chunk.content_hash for chunk in first_run] == [
        chunk.content_hash for chunk in second_run
    ]
    assert first_run

    for chunk in first_run:
        assert chunk.chunk_id.startswith(f"{sample_source_page.source_slug}:")
        assert f":{chunk.ordinal:04d}:" in chunk.chunk_id
        assert chunk.chunk_id.endswith(chunk.content_hash[:12])


def test_content_hash_uses_normalized_chunk_content() -> None:
    _, normalize_chunk_content, compute_content_hash, _ = _chunking_api()

    noisy_content = "  Retrieval   augmented\r\n generation\tgrounds answers.  "
    normalized = normalize_chunk_content(noisy_content)

    assert normalized == "Retrieval augmented generation grounds answers."
    assert compute_content_hash(noisy_content) == compute_content_hash(normalized)
    assert compute_content_hash(noisy_content) == hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def test_chunk_source_page_preserves_section_metadata_and_provenance(
    sample_source_page: SourcePage,
) -> None:
    chunk_source_page, _, _, _ = _chunking_api()

    chunks = chunk_source_page(sample_source_page, _sample_markdown(), max_chunk_tokens=80)
    section_paths = {tuple(chunk.section_path) for chunk in chunks}

    assert ("Overview",) in section_paths
    assert ("Overview", "Retrieval Details") in section_paths
    assert ("Token Budget",) in section_paths

    for chunk in chunks:
        assert chunk.source_slug == sample_source_page.source_slug
        assert chunk.category == sample_source_page.category
        assert chunk.provenance == sample_source_page.provenance
        assert chunk.section_path
        assert all(section.strip() for section in chunk.section_path)


def test_chunk_token_estimates_use_tiktoken_and_are_stored_on_chunks(
    sample_source_page: SourcePage,
) -> None:
    chunk_source_page, _, _, estimate_token_count = _chunking_api()
    text = "Retrieval augmented generation grounds answers in selected context."

    assert estimate_token_count(text) == 11
    assert estimate_token_count(text * 4) > estimate_token_count(text)

    chunks = chunk_source_page(sample_source_page, _sample_markdown(), max_chunk_tokens=80)

    assert chunks
    assert all(chunk.estimated_tokens > 0 for chunk in chunks)
    assert all(
        chunk.estimated_tokens == estimate_token_count(chunk.content)
        for chunk in chunks
    )


@pytest.fixture
def sample_source_page(tmp_path: Path) -> SourcePage:
    local_ref = tmp_path / "corpus" / "sources" / "rag-overview.md"
    local_ref.parent.mkdir(parents=True)
    local_ref.write_text(_sample_markdown(), encoding="utf-8")

    return SourcePage(
        source_slug="rag-overview",
        title="RAG Overview",
        category="RAG and context handling",
        url="https://example.test/rag-overview",
        license="MIT",
        pinned_version="example@abc123",
        local_ref="corpus/sources/rag-overview.md",
        sections=[
            SourceSection(heading="Overview", level=1, ordinal=0),
            SourceSection(heading="Retrieval Details", level=2, ordinal=1),
            SourceSection(heading="Token Budget", level=1, ordinal=2),
        ],
    )


def _sample_markdown() -> str:
    return """# Overview

Retrieval augmented generation uses selected context to ground answers.

## Retrieval Details

Retrieved chunks must keep source metadata so citations can be validated.

# Token Budget

Estimated token counts make context inclusion decisions reproducible.
"""


def _chunking_api() -> tuple[Any, Any, Any, Any]:
    from rag_quality_lab.corpus.chunking import (
        chunk_source_page,
        compute_content_hash,
        estimate_token_count,
        normalize_chunk_content,
    )

    return (
        chunk_source_page,
        normalize_chunk_content,
        compute_content_hash,
        estimate_token_count,
    )
