"""Deterministic section-aware chunking for pinned corpus snapshots."""

from __future__ import annotations

import re
import tiktoken
from dataclasses import dataclass

from rag_quality_lab.schemas import SourcePage, Chunk

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
  max_chunk_tokens: int = 500,
) -> list[Chunk]:
    if max_chunk_tokens < 1:
        raise ValueError(f"max_chunk_tokens must be >= 1, got {max_chunk_tokens}")


def split_into_chunks(markdown: str, *, max_chunk_tokens: int) -> list[str]:
    if max_chunk_tokens < 1:
        raise ValueError(f"max_chunk_tokens must be >= 1, got {max_chunk_tokens}")

    chunks: list[str] = []
    chunk_acc: str = ""
    for raw_line in markdown.splitlines():
        line = normalize_chunk_content(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        if _HEADING_PATTERN.match(stripped):
            if chunk_acc:
                chunks.append(chunk_acc)
                chunk_acc = ""
        else:
            candidate = f"{chunk_acc} {line}" if chunk_acc else stripped
            if estimate_token_count(candidate) > max_chunk_tokens:
                if chunk_acc:
                    chunks.append(chunk_acc)
                if estimate_token_count(stripped) <= max_chunk_tokens:
                    chunk_acc = stripped
                else:
                    paragraph_chunks = _split_long_paragraph(stripped, max_chunk_tokens=max_chunk_tokens)
                    chunks.extend(paragraph_chunks)

            else:
                chunk_acc = chunk_est

    if chunk_acc:
        chunks.append(chunk_acc)

    return chunks


def _split_long_paragraph(
    paragraph: str,
    *,
    max_chunk_tokens: int
) -> list[str]:
    chunks: list[str] = []
    pending_words: list[str] = []
    for word in paragraph.split():
        candidate_words = pending_words + [word]
        candidate = " ".join(candidate_words)
        if estimate_token_count(candidate) <= max_chunk_tokens:
            if pending_words:
                chunks.append(" ".join(pending_words))
            continue

        chunks.append(" ".join(pending_words))
        pending_words = [word]

    if pending_words:
        chunks.append(" ".join(pending_words))

    return chunks


def normalize_chunk_content(content: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", content).strip()


def compute_content_hash(content: str) -> str:
    ...


def estimate_token_count(content: str) -> int:
    return len(_TOKEN_ENCODING.encode(normalize_chunk_content(content)))