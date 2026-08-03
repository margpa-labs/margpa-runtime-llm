"""In-memory immutable lexical snapshot and atomic current-index store."""

from __future__ import annotations

import threading
from dataclasses import dataclass

from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationChunk
from margpa_runtime_llm.modules.documentation_rag.ports import DocumentationIndex


@dataclass(frozen=True, slots=True)
class IndexedChunk:
    chunk: DocumentationChunk
    normalized_body: str
    normalized_heading: str
    normalized_path: str
    body_terms: tuple[tuple[str, int], ...]
    heading_terms: tuple[tuple[str, int], ...]
    path_terms: tuple[tuple[str, int], ...]
    body_length: int
    heading_length: int
    path_length: int


@dataclass(frozen=True, slots=True)
class LexicalIndexSnapshot:
    index_id: str
    cache_key: str
    corpus_manifest_digest: str
    chunker_key: str
    chunker_version: str
    tokenizer_key: str
    tokenizer_version: str
    retriever_key: str
    retriever_version: str
    document_count: int
    chunk_count: int
    built_at_monotonic: float
    chunks: tuple[IndexedChunk, ...]
    body_document_frequency: tuple[tuple[str, int], ...]
    heading_document_frequency: tuple[tuple[str, int], ...]
    path_document_frequency: tuple[tuple[str, int], ...]
    average_body_length: float
    average_heading_length: float
    average_path_length: float


class InMemoryLexicalIndexStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current: DocumentationIndex | None = None

    def get(self, cache_key: str) -> DocumentationIndex | None:
        with self._lock:
            current = self._current
            if current is not None and current.cache_key == cache_key:
                return current
            return None

    def replace(self, index: DocumentationIndex) -> None:
        with self._lock:
            self._current = index
