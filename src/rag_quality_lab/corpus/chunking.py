"""Deterministic section-aware chunking for pinned corpus snapshots."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import tiktoken

from rag_quality_lab.schemas import Chunk, SourcePage

DEFAULT_MAX_CHUNK_TOKENS = 500
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
_TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass(frozen=True)
class _SectionBlock:
    section_path: tuple[str, ...]
    lines: tuple[str, ...]


def chunk_source_page(
    source_page: SourcePage,
    markdown: str,
    *,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
) -> list[Chunk]:
    if max_chunk_tokens < 1:
        raise ValueError(f"max_chunk_tokens must be >= 1, got {max_chunk_tokens}")

    chunks: list[Chunk] = []
    for section in _parse_markdown_sections(
        markdown, fallback_heading=source_page.title
    ):
        section_markdown = "\n".join(section.lines)
        for content in split_into_chunks(
            section_markdown, max_chunk_tokens=max_chunk_tokens
        ):
            content_hash = compute_content_hash(content)
            ordinal = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=_build_chunk_id(
                        source_slug=source_page.source_slug,
                        ordinal=ordinal,
                        section_path=section.section_path,
                        content_hash=content_hash,
                    ),
                    source_slug=source_page.source_slug,
                    category=source_page.category,
                    section_path=list(section.section_path),
                    ordinal=ordinal,
                    content=normalize_chunk_content(content),
                    content_hash=content_hash,
                    estimated_tokens=estimate_token_count(content),
                    provenance=source_page.provenance,
                )
            )

    return chunks


def split_into_chunks(markdown: str, *, max_chunk_tokens: int) -> list[str]:
    if max_chunk_tokens < 1:
        raise ValueError(f"max_chunk_tokens must be >= 1, got {max_chunk_tokens}")

    chunks: list[str] = []
    section_paragraphs: list[str] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        paragraph = normalize_chunk_content(" ".join(paragraph_lines))
        if paragraph:
            section_paragraphs.append(paragraph)
        paragraph_lines = []

    def flush_section() -> None:
        nonlocal section_paragraphs
        chunks.extend(
            _split_paragraphs_into_chunks(
                section_paragraphs,
                max_chunk_tokens=max_chunk_tokens,
            )
        )
        section_paragraphs = []

    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            continue

        if _HEADING_PATTERN.match(stripped):
            flush_paragraph()
            flush_section()
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_section()

    return chunks


def _split_paragraphs_into_chunks(
    paragraphs: list[str],
    *,
    max_chunk_tokens: int,
) -> list[str]:
    """Greedily pack contiguous paragraphs without overlap.

    This is intentionally simple and deterministic, but it is not a global
    optimization for retrieval quality. It does not balance chunk sizes, does
    not consider semantic boundaries beyond paragraphs, does not add overlap,
    and splits oversized paragraphs by words rather than sentences or clauses.
    A single word that exceeds max_chunk_tokens may still produce an oversized
    chunk. The implementation also favors clarity over minimizing repeated
    token-count calls.
    """
    chunks: list[str] = []
    pending_paragraphs: list[str] = []

    for paragraph in paragraphs:
        if estimate_token_count(paragraph) > max_chunk_tokens:
            if pending_paragraphs:
                chunks.append(" ".join(pending_paragraphs))
                pending_paragraphs = []
            chunks.extend(
                _split_long_paragraph(paragraph, max_chunk_tokens=max_chunk_tokens)
            )
            continue

        candidate = (
            " ".join([*pending_paragraphs, paragraph])
            if pending_paragraphs
            else paragraph
        )
        if estimate_token_count(candidate) <= max_chunk_tokens:
            pending_paragraphs.append(paragraph)
            continue

        if pending_paragraphs:
            chunks.append(" ".join(pending_paragraphs))
        pending_paragraphs = [paragraph]

    if pending_paragraphs:
        chunks.append(" ".join(pending_paragraphs))

    return chunks


def _split_long_paragraph(
    paragraph: str,
    *,
    max_chunk_tokens: int,
) -> list[str]:
    chunks: list[str] = []
    pending_words: list[str] = []

    for word in paragraph.split():
        candidate_words = pending_words + [word]
        candidate = " ".join(candidate_words)
        if estimate_token_count(candidate) <= max_chunk_tokens:
            pending_words.append(word)
            continue

        if pending_words:
            chunks.append(" ".join(pending_words))
        pending_words = [word]

    if pending_words:
        chunks.append(" ".join(pending_words))

    return chunks


def _parse_markdown_sections(
    markdown: str, *, fallback_heading: str
) -> list[_SectionBlock]:
    sections: list[_SectionBlock] = []
    heading_stack: list[tuple[int, str]] = []
    section_path: tuple[str, ...] = (fallback_heading,)
    lines: list[str] = []

    for raw_line in markdown.splitlines():
        heading_match = _HEADING_PATTERN.match(raw_line.strip())
        if heading_match is not None:
            _append_section(sections, section_path, lines)
            lines = []
            level = len(heading_match.group(1))
            heading = normalize_chunk_content(heading_match.group(2))
            heading_stack = [
                (existing_level, existing_heading)
                for existing_level, existing_heading in heading_stack
                if existing_level < level
            ]
            heading_stack.append((level, heading))
            section_path = tuple(
                existing_heading for _, existing_heading in heading_stack
            )
            continue

        lines.append(raw_line)

    _append_section(sections, section_path, lines)
    return sections


def _append_section(
    sections: list[_SectionBlock],
    section_path: tuple[str, ...],
    lines: list[str],
) -> None:
    if normalize_chunk_content(" ".join(lines)):
        sections.append(_SectionBlock(section_path=section_path, lines=tuple(lines)))


def normalize_chunk_content(content: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", content).strip()


def compute_content_hash(content: str) -> str:
    normalized_content = normalize_chunk_content(content)
    return hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()


def estimate_token_count(content: str) -> int:
    return len(_TOKEN_ENCODING.encode(normalize_chunk_content(content)))


def _build_chunk_id(
    *,
    source_slug: str,
    ordinal: int,
    section_path: tuple[str, ...],
    content_hash: str,
) -> str:
    section_slug = _slugify("-".join(section_path))
    return f"{source_slug}:{ordinal:04d}:{section_slug}:{content_hash[:12]}"


def _slugify(value: str) -> str:
    slug = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "section"
