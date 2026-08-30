"""Concrete local adapters for the initial sparse documentation RAG."""

from .bm25_retriever import Bm25DocumentationRetriever
from .bounded_context_assembler import BoundedDocumentationContextAssembler
from .composite_document_source import CompositeDocumentSource
from .in_memory_lexical_index import InMemoryLexicalIndexStore
from .local_corpus_document_source import LocalCorpusDocumentSource
from .local_corpus_registry import (
    JsonFileLocalCorpusRegistry,
    LocalCorpusRegistryCorrupt,
    LocalCorpusRegistryUnsafePath,
)
from .local_filesystem_source import (
    ExplicitMarkdownDocumentSource,
    LocalMarkdownDocumentSource,
)
from .markdown_chunker import DeterministicMarkdownChunker
from .system_citation_adapter import SystemCitationAdapter

__all__ = [
    "Bm25DocumentationRetriever",
    "BoundedDocumentationContextAssembler",
    "CompositeDocumentSource",
    "DeterministicMarkdownChunker",
    "ExplicitMarkdownDocumentSource",
    "InMemoryLexicalIndexStore",
    "JsonFileLocalCorpusRegistry",
    "LocalCorpusDocumentSource",
    "LocalCorpusRegistryCorrupt",
    "LocalCorpusRegistryUnsafePath",
    "LocalMarkdownDocumentSource",
    "SystemCitationAdapter",
]
