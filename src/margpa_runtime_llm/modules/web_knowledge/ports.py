"""Phase 7 (P7-E/F): replaceable ports for Web Search/Fetch providers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .contracts import (
    PersistedTurnWebCitationEvidence,
    UrlRejectionReason,
    WebCitationUnavailable,
    WebFetchFailureReason,
    WebSearchQuery,
    WebSearchResultItem,
)


class WebSearchProviderPort(Protocol):
    @property
    def provider_key(self) -> str: ...

    @property
    def provider_version(self) -> str: ...

    def search(
        self,
        query: WebSearchQuery,
        *,
        max_results: int,
    ) -> tuple[WebSearchResultItem, ...]: ...


@dataclass(frozen=True, slots=True)
class FetchedContent:
    content: str
    content_type: str
    fetched_at: str
    canonical_url: str
    """P8-A / Controller Recovery §6 item 2: the *final* URL the content was
    actually read from, after every redirect hop a Provider followed — never
    the originally requested address when the two differ. A Provider that
    never redirects (e.g. the Fixture Provider) sets this to the same value
    it was asked to fetch."""
    published_or_updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class FetchRejected:
    reason: UrlRejectionReason | WebFetchFailureReason


class WebFetchProviderPort(Protocol):
    def fetch(
        self,
        url: str,
        *,
        timeout_seconds: float,
        max_response_bytes: int,
        max_redirects: int,
    ) -> FetchedContent | FetchRejected: ...


@runtime_checkable
class WebCitationEvidenceStorePort(Protocol):
    """Fail-closed read boundary for persisted per-turn Manual URL Fetch
    Evidence (P8-A). Mirrors `documentation_rag.ports.CitationEvidenceStorePort`
    exactly, including its write-exclusion rationale: writes are not exposed
    here — they are committed atomically alongside the owning Turn through
    `ConversationRepositoryPort.commit()` so the assistant completion and its
    Web Citation Evidence can never diverge."""

    def get_turn_web_citations(
        self,
        conversation_id: str,
        turn_id: str,
    ) -> PersistedTurnWebCitationEvidence | WebCitationUnavailable: ...

    def get_conversation_web_citations(
        self,
        conversation_id: str,
    ) -> Mapping[str, PersistedTurnWebCitationEvidence | WebCitationUnavailable]: ...
