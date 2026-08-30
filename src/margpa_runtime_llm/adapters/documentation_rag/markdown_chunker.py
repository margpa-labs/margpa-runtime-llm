"""Deterministic ATX-heading and fenced-code aware Markdown chunking."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationChunk,
    DocumentationChunkingConfig,
    DocumentSource,
)

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


@dataclass(frozen=True, slots=True)
class _Block:
    breadcrumb: str
    content: str
    oversized_split: bool = False


class DeterministicMarkdownChunker:
    key = "markdown_heading_chunker"
    version = "1"

    def __init__(self, config: DocumentationChunkingConfig) -> None:
        self._config = config

    def chunk(self, document: DocumentSource) -> tuple[DocumentationChunk, ...]:
        blocks = self._parse(document.content)
        raw_chunks: list[tuple[str, str, bool]] = []
        current_heading = ""
        current_parts: list[str] = []
        current_oversized = False

        def flush() -> None:
            nonlocal current_parts, current_oversized
            content = "\n\n".join(part for part in current_parts if part).strip()
            if content:
                raw_chunks.append((current_heading, content, current_oversized))
            current_parts = []
            current_oversized = False

        previous_content = ""
        for block in blocks:
            if current_parts and block.breadcrumb != current_heading:
                flush()
                previous_content = raw_chunks[-1][1] if raw_chunks else ""
            if not current_parts:
                current_heading = block.breadcrumb
            for piece, split in self._bounded_pieces(block):
                if (
                    not current_parts
                    and previous_content
                    and raw_chunks
                    and raw_chunks[-1][0] == block.breadcrumb
                ):
                    overlap = previous_content[-self._config.overlap_characters :].strip()
                    if overlap and len(overlap) + 2 + len(piece) <= (
                        self._config.maximum_characters
                    ):
                        current_parts.append(overlap)
                separator = 2 if current_parts else 0
                current_length = (
                    sum(len(part) for part in current_parts) + max(0, len(current_parts) - 1) * 2
                )
                if current_parts and (
                    current_length + separator + len(piece) > self._config.target_characters
                ):
                    flush()
                    previous_content = raw_chunks[-1][1]
                    current_heading = block.breadcrumb
                    overlap = previous_content[-self._config.overlap_characters :].strip()
                    if overlap and len(overlap) + 2 + len(piece) <= (
                        self._config.maximum_characters
                    ):
                        current_parts.append(overlap)
                current_parts.append(piece)
                current_oversized = current_oversized or split
                assembled_length = len("\n\n".join(current_parts))
                if assembled_length >= self._config.target_characters:
                    flush()
                    previous_content = raw_chunks[-1][1]
        flush()

        chunks: list[DocumentationChunk] = []
        for ordinal, (breadcrumb, content, oversized) in enumerate(raw_chunks):
            bounded = content[: self._config.maximum_characters]
            content_digest = _digest(bounded)
            chunk_id = _digest(
                "\0".join(
                    (
                        document.manifest.source_id,
                        str(ordinal),
                        breadcrumb,
                        content_digest,
                    )
                )
            )
            chunks.append(
                DocumentationChunk(
                    chunk_id=chunk_id,
                    source_id=document.manifest.source_id,
                    project_relative_path=document.manifest.project_relative_path,
                    corpus_priority=document.manifest.corpus_priority,
                    heading_breadcrumb=breadcrumb,
                    ordinal=ordinal,
                    content=bounded,
                    content_sha512=content_digest,
                    document_sha512=document.manifest.document_sha512,
                    character_count=len(bounded),
                    split_from_oversized_block=oversized or len(content) > len(bounded),
                    corpus_source_class=document.manifest.corpus_source_class,
                    document_title=document.manifest.document_title,
                    storage_display_path=document.manifest.storage_display_path,
                )
            )
        return tuple(chunks)

    def _parse(self, content: str) -> tuple[_Block, ...]:
        lines = content.splitlines()
        heading_stack: list[str] = []
        blocks: list[_Block] = []
        paragraph: list[str] = []
        code: list[str] = []
        fence_marker: str | None = None

        def breadcrumb() -> str:
            return " > ".join(heading_stack)

        def flush_paragraph() -> None:
            nonlocal paragraph
            value = "\n".join(paragraph).strip()
            if value:
                blocks.append(_Block(breadcrumb(), value))
            paragraph = []

        for line in lines:
            if fence_marker is not None:
                code.append(line)
                stripped = line.lstrip()
                if stripped.startswith(fence_marker):
                    blocks.append(_Block(breadcrumb(), "\n".join(code).strip()))
                    code = []
                    fence_marker = None
                continue

            fence = _FENCE.match(line)
            if fence is not None:
                flush_paragraph()
                marker = fence.group(1)
                fence_marker = marker[0] * len(marker)
                code = [line]
                continue

            heading = _HEADING.match(line)
            if heading is not None:
                flush_paragraph()
                level = len(heading.group(1))
                text = heading.group(2).strip()
                heading_stack[level - 1 :] = [text]
                blocks.append(_Block(breadcrumb(), line.strip()))
                continue

            if not line.strip():
                flush_paragraph()
                continue
            paragraph.append(line)

        flush_paragraph()
        if code:
            blocks.append(_Block(breadcrumb(), "\n".join(code).strip()))
        return tuple(blocks)

    def _bounded_pieces(self, block: _Block) -> tuple[tuple[str, bool], ...]:
        maximum = self._config.target_characters
        if len(block.content) <= maximum:
            return ((block.content, block.oversized_split),)
        pieces: list[tuple[str, bool]] = []
        remaining = block.content
        while remaining:
            if len(remaining) <= maximum:
                pieces.append((remaining.strip(), True))
                break
            split_at = max(
                remaining.rfind("\n", 0, maximum + 1),
                remaining.rfind("。", 0, maximum + 1),
                remaining.rfind(". ", 0, maximum + 1),
                remaining.rfind(" ", 0, maximum + 1),
            )
            if split_at < maximum // 2:
                split_at = maximum
            elif remaining[split_at : split_at + 2] in {"。", ". "}:
                split_at += 1
            piece = remaining[:split_at].strip()
            if piece:
                pieces.append((piece, True))
            remaining = remaining[split_at:].strip()
        return tuple(pieces)


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()
