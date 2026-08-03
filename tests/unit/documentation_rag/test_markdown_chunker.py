"""Markdown structure, overlap, and chunk identity tests."""

from __future__ import annotations

import hashlib

from margpa_runtime_llm.adapters.documentation_rag.markdown_chunker import (
    DeterministicMarkdownChunker,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CorpusPriority,
    DocumentationChunkingConfig,
    DocumentManifestEntry,
    DocumentSource,
)


def document(content: str) -> DocumentSource:
    digest = hashlib.sha512(content.encode()).hexdigest()
    return DocumentSource(
        manifest=DocumentManifestEntry(
            source_id=hashlib.sha512(f"path\0{digest}".encode()).hexdigest(),
            project_relative_path="docs/project/current/example_ja.md",
            corpus_priority=CorpusPriority.CURRENT,
            document_sha512=digest,
            size_bytes=len(content.encode()),
            modified_time_ns=0,
        ),
        content=content,
    )


def test_heading_breadcrumb_and_code_fence_hash_are_stable() -> None:
    content = """# Root

Intro paragraph.

## Child

```python
# not-a-heading
value = "ok"
```

Final paragraph.
"""
    chunker = DeterministicMarkdownChunker(
        DocumentationChunkingConfig(
            target_characters=80,
            overlap_characters=12,
            maximum_characters=140,
        )
    )

    first = chunker.chunk(document(content))
    second = chunker.chunk(document(content))

    assert first == second
    assert any(chunk.heading_breadcrumb == "Root > Child" for chunk in first)
    assert not any("not-a-heading" in chunk.heading_breadcrumb for chunk in first)
    assert all(chunk.character_count <= 140 for chunk in first)
    assert [chunk.ordinal for chunk in first] == list(range(len(first)))


def test_large_section_has_overlap_and_oversized_blocks_are_bounded() -> None:
    content = "# Root\n\n" + " ".join(f"word-{index:03d}" for index in range(120))
    config = DocumentationChunkingConfig(
        target_characters=120,
        overlap_characters=24,
        maximum_characters=180,
    )
    chunks = DeterministicMarkdownChunker(config).chunk(document(content))

    assert len(chunks) > 2
    assert all(chunk.character_count <= config.maximum_characters for chunk in chunks)
    assert any(chunk.split_from_oversized_block for chunk in chunks)
    assert chunks[1].content[-12:].strip() in chunks[2].content


def test_empty_markdown_produces_no_chunks() -> None:
    chunker = DeterministicMarkdownChunker(DocumentationChunkingConfig())
    assert chunker.chunk(document(" \n\n ")) == ()
