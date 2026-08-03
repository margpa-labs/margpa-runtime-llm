"""Concrete local adapters for the initial sparse documentation RAG."""

from .bm25_retriever import Bm25DocumentationRetriever
from .bounded_context_assembler import BoundedDocumentationContextAssembler
from .in_memory_lexical_index import InMemoryLexicalIndexStore
from .local_filesystem_source import (
    ExplicitMarkdownDocumentSource,
    LocalMarkdownDocumentSource,
)
from .markdown_chunker import DeterministicMarkdownChunker
from .system_citation_adapter import SystemCitationAdapter

__all__ = [
    "Bm25DocumentationRetriever",
    "BoundedDocumentationContextAssembler",
    "DeterministicMarkdownChunker",
    "ExplicitMarkdownDocumentSource",
    "InMemoryLexicalIndexStore",
    "LocalMarkdownDocumentSource",
    "SystemCitationAdapter",
]
