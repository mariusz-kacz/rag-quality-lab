from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from rag_quality_lab.schemas import SourcePage


pytestmark = pytest.mark.unit


def test_split_into_chunks_strips_headings_and_keeps_sections_separate() -> None:
    split_into_chunks, estimate_token_count = _chunking_api()

    chunks = split_into_chunks(_sample_markdown(), max_chunk_tokens=80)
    _print_chunks(chunks)

    assert chunks == [
        "Retrieval augmented generation uses selected context to ground answers.",
        "Retrieved chunks must keep source metadata so citations can be validated.",
        "Estimated token counts make context inclusion decisions reproducible.",
    ]
    assert all(estimate_token_count(chunk) <= 80 for chunk in chunks)


def test_split_into_chunks_starts_new_chunk_when_next_paragraph_exceeds_limit() -> None:
    split_into_chunks, estimate_token_count = _chunking_api()
    markdown = """# Overview

alpha beta gamma delta epsilon zeta eta theta iota kappa

lambda mu nu xi omicron pi rho sigma tau upsilon

one two three four five six seven eight nine ten
"""

    chunks = split_into_chunks(markdown, max_chunk_tokens=16)
    _print_chunks(chunks)

    assert chunks == [
        "alpha beta gamma delta epsilon zeta eta theta iota kappa",
        "lambda mu nu xi omicron pi rho sigma tau upsilon",
        "one two three four five six seven eight nine ten",
    ]
    assert all(estimate_token_count(chunk) <= 16 for chunk in chunks)


def test_split_into_chunks_does_not_overlap_split_chunks() -> None:
    split_into_chunks, _ = _chunking_api()
    markdown = """# Overview

alpha beta gamma delta epsilon zeta eta theta iota kappa

lambda mu nu xi omicron pi rho sigma tau upsilon
"""

    chunks = split_into_chunks(markdown, max_chunk_tokens=16)
    _print_chunks(chunks)

    assert chunks[0].endswith("theta iota kappa")
    assert chunks[1].startswith("lambda mu nu")
    assert not chunks[1].startswith("theta iota kappa")


def test_split_into_chunks_does_not_merge_content_across_heading_boundaries() -> None:
    split_into_chunks, estimate_token_count = _chunking_api()
    markdown = """# First Section

alpha beta gamma delta epsilon zeta eta theta iota kappa

lambda mu nu xi omicron pi rho sigma tau upsilon

# Second Section

short final paragraph
"""

    chunks = split_into_chunks(markdown, max_chunk_tokens=20)
    _print_chunks(chunks)

    assert chunks == [
        "alpha beta gamma delta epsilon zeta eta theta iota kappa",
        "lambda mu nu xi omicron pi rho sigma tau upsilon",
        "short final paragraph",
    ]
    assert estimate_token_count(f"{chunks[1]} {chunks[2]}") <= 20


def test_split_into_chunks_splits_single_oversized_paragraph_by_words() -> None:
    split_into_chunks, estimate_token_count = _chunking_api()
    markdown = """# Overview

alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon
"""

    chunks = split_into_chunks(markdown, max_chunk_tokens=8)
    _print_chunks(chunks)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert " ".join(chunks) == (
        "alpha beta gamma delta epsilon zeta eta theta iota kappa "
        "lambda mu nu xi omicron pi rho sigma tau upsilon"
    )
    assert all(estimate_token_count(chunk) <= 8 for chunk in chunks)


def test_split_into_chunks_rejects_non_positive_token_limit() -> None:
    split_into_chunks, _ = _chunking_api()

    with pytest.raises(ValueError, match="max_chunk_tokens"):
        split_into_chunks(_sample_markdown(), max_chunk_tokens=0)


def test_compute_content_hash_uses_normalized_content() -> None:
    from rag_quality_lab.corpus.chunking import compute_content_hash, normalize_chunk_content

    noisy_content = "  Retrieval   augmented\r\n generation\tgrounds answers.  "
    normalized = normalize_chunk_content(noisy_content)

    assert normalized == "Retrieval augmented generation grounds answers."
    assert compute_content_hash(noisy_content) == compute_content_hash(normalized)
    assert compute_content_hash(noisy_content) == hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def test_chunk_source_page_builds_valid_chunks_with_section_metadata(
    sample_source_page: SourcePage,
) -> None:
    from rag_quality_lab.corpus.chunking import (
        chunk_source_page,
        compute_content_hash,
        estimate_token_count,
    )

    chunks = chunk_source_page(sample_source_page, _sample_markdown(), max_chunk_tokens=80)

    assert [chunk.section_path for chunk in chunks] == [
        ["Overview"],
        ["Overview", "Retrieval Details"],
        ["Token Budget"],
    ]
    for ordinal, chunk in enumerate(chunks):
        assert chunk.ordinal == ordinal
        assert chunk.chunk_id.startswith(f"{sample_source_page.source_slug}:{ordinal:04d}:")
        assert chunk.chunk_id.endswith(chunk.content_hash[:12])
        assert chunk.content_hash == compute_content_hash(chunk.content)
        assert chunk.estimated_tokens == estimate_token_count(chunk.content)
        assert chunk.source_slug == sample_source_page.source_slug
        assert chunk.category == sample_source_page.category
        assert chunk.provenance == sample_source_page.provenance


def test_chunk_source_page_is_deterministic(sample_source_page: SourcePage) -> None:
    from rag_quality_lab.corpus.chunking import chunk_source_page

    first_run = chunk_source_page(sample_source_page, _sample_markdown(), max_chunk_tokens=80)
    second_run = chunk_source_page(sample_source_page, _sample_markdown(), max_chunk_tokens=80)

    assert first_run == second_run


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
    )


def _sample_markdown() -> str:
    return """# Overview

Retrieval augmented generation uses selected context to ground answers.

## Retrieval Details

Retrieved chunks must keep source metadata so citations can be validated.

# Token Budget

Estimated token counts make context inclusion decisions reproducible.
"""


def _print_chunks(chunks: list[str]) -> None:
    print(f"\nsplit_into_chunks returned {len(chunks)} chunks:")
    for index, chunk in enumerate(chunks):
        print(f"  [{index}] {chunk!r}")


def _chunking_api() -> tuple[Any, Any]:
    from rag_quality_lab.corpus.chunking import estimate_token_count, split_into_chunks

    return split_into_chunks, estimate_token_count
