"""Phase 7 (P7-E/F): replaceable ports for Web Search/Fetch providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import (
    UrlRejectionReason,
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
