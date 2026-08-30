"""Stable public surface for Phase 7 Governed Web Search/Fetch."""

from .application import WebKnowledgeService
from .contracts import (
    PUBLIC_WEB_SOURCE_CLASS,
    SourceAuthorityClass,
    UrlRejectionReason,
    WebCitation,
    WebEvidence,
    WebEvidenceGovernanceMode,
    WebFetchFailureReason,
    WebSearchActivation,
    WebSearchAndFetchResult,
    WebSearchFeatureConfig,
    WebSearchQuery,
    WebSearchResultItem,
    WebSearchRun,
    classify_source_authority,
)
from .ports import FetchedContent, FetchRejected, WebFetchProviderPort, WebSearchProviderPort

__all__ = [
    "PUBLIC_WEB_SOURCE_CLASS",
    "FetchRejected",
    "FetchedContent",
    "SourceAuthorityClass",
    "UrlRejectionReason",
    "WebCitation",
    "WebEvidence",
    "WebEvidenceGovernanceMode",
    "WebFetchFailureReason",
    "WebFetchProviderPort",
    "WebKnowledgeService",
    "WebSearchActivation",
    "WebSearchAndFetchResult",
    "WebSearchFeatureConfig",
    "WebSearchProviderPort",
    "WebSearchQuery",
    "WebSearchResultItem",
    "WebSearchRun",
    "classify_source_authority",
]
