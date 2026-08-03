"""Stable public surface for the documentation RAG module."""

from .application import DocumentationRagApplicationService
from .contracts import (
    CorpusManifest,
    DocumentationAugmentation,
    DocumentationCitation,
    DocumentationGroundingState,
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagRequestContext,
    DocumentationRetrievalState,
    DocumentationWarning,
    DocumentManifestEntry,
    LocalDocumentationRagFeatureConfig,
)
from .ports import (
    ChunkerPort,
    CitationPort,
    ContextAssemblerPort,
    ContextualRagOrchestratorPort,
    DocumentSourcePort,
    EmbeddingPort,
    IndexStorePort,
    RagOrchestratorPort,
    RetrieverPort,
)

__all__ = [
    "ChunkerPort",
    "CitationPort",
    "ContextAssemblerPort",
    "ContextualRagOrchestratorPort",
    "CorpusManifest",
    "DocumentManifestEntry",
    "DocumentSourcePort",
    "DocumentationAugmentation",
    "DocumentationCitation",
    "DocumentationGroundingState",
    "DocumentationRagApplicationService",
    "DocumentationRagAvailability",
    "DocumentationRagMode",
    "DocumentationRagRequestContext",
    "DocumentationRetrievalState",
    "DocumentationWarning",
    "EmbeddingPort",
    "IndexStorePort",
    "LocalDocumentationRagFeatureConfig",
    "RagOrchestratorPort",
    "RetrieverPort",
]
