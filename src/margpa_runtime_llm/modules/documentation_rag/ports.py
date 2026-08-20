"""Replaceable ports for documentation RAG sources, indexes, and output."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Protocol, runtime_checkable

from .contracts import (
    AssembledDocumentationContext,
    CitationUnavailable,
    CorpusManifest,
    DocumentationAugmentation,
    DocumentationChunk,
    DocumentationCitation,
    DocumentationContextBudget,
    DocumentationRagRequestContext,
    DocumentationWarning,
    DocumentSource,
    PersistedTurnCitationEvidence,
    RetrievalQuery,
    RetrievalResult,
)

CancellationCheck = Callable[[], bool]


class DocumentationIndex(Protocol):
    @property
    def cache_key(self) -> str: ...

    @property
    def corpus_manifest_digest(self) -> str: ...

    @property
    def document_count(self) -> int: ...

    @property
    def chunk_count(self) -> int: ...


class DocumentSourcePort(Protocol):
    @property
    def schema_version(self) -> str: ...

    def load_manifest(self) -> CorpusManifest: ...

    def load_documents(
        self,
        manifest: CorpusManifest,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> tuple[tuple[DocumentSource, ...], tuple[DocumentationWarning, ...]]: ...


class ChunkerPort(Protocol):
    @property
    def key(self) -> str: ...

    @property
    def version(self) -> str: ...

    def chunk(self, document: DocumentSource) -> tuple[DocumentationChunk, ...]: ...


class EmbeddingPort(Protocol):
    """Reserved semantic boundary; the initial lexical pipeline never calls it."""

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]: ...


class IndexStorePort(Protocol):
    def get(self, cache_key: str) -> DocumentationIndex | None: ...

    def replace(self, index: DocumentationIndex) -> None: ...


class RetrieverPort(Protocol):
    @property
    def key(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def tokenizer_key(self) -> str: ...

    @property
    def tokenizer_version(self) -> str: ...

    def build(
        self,
        *,
        cache_key: str,
        corpus_manifest_digest: str,
        chunker_key: str,
        chunker_version: str,
        chunks: tuple[DocumentationChunk, ...],
    ) -> DocumentationIndex: ...

    def retrieve(
        self,
        index: DocumentationIndex,
        query: RetrievalQuery,
    ) -> RetrievalResult: ...


class ContextAssemblerPort(Protocol):
    @property
    def key(self) -> str: ...

    @property
    def version(self) -> str: ...

    def assemble(
        self,
        retrieval: RetrievalResult,
        budget: DocumentationContextBudget,
    ) -> AssembledDocumentationContext: ...


class CitationPort(Protocol):
    @property
    def schema_version(self) -> str: ...

    def build(
        self,
        retrieval: RetrievalResult,
        context: AssembledDocumentationContext,
    ) -> tuple[DocumentationCitation, ...]: ...


class RagOrchestratorPort(Protocol):
    """Compatibility boundary for pre-request-context orchestrators."""

    def augment(
        self,
        query_text: str,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation: ...


@runtime_checkable
class ContextualRagOrchestratorPort(Protocol):
    """Request-aware boundary used by production documentation RAG composition."""

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation: ...


@runtime_checkable
class CitationEvidenceStorePort(Protocol):
    """Fail-closed read boundary for persisted per-turn citation evidence.

    Writes are not exposed here: they are committed atomically alongside the
    owning turn through `ConversationRepositoryPort.commit()` so that the
    assistant completion and its citation evidence can never diverge.
    """

    def get_turn_citations(
        self,
        conversation_id: str,
        turn_id: str,
    ) -> PersistedTurnCitationEvidence | CitationUnavailable: ...

    def get_conversation_citations(
        self,
        conversation_id: str,
    ) -> Mapping[str, PersistedTurnCitationEvidence | CitationUnavailable]: ...
