"""Phase 7 (P7-E): deterministic Fixture Search/Fetch Providers.

The Handoff explicitly scopes this Task's Manual Search Golden Path to a
Fixture/Fake Provider (no paid/credentialed Search API is set up — see the
P7-E Recovery Index for the Bounded Network decision). This Provider pair
returns a small, honestly-labelled canned corpus rather than pretending to
be a real Search Engine; every returned URL is a real, stable, publicly
documented address (so the Security Boundary's real DNS/IP checks still
apply and can genuinely pass), but no live Search API is queried.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from margpa_runtime_llm.modules.web_knowledge.contracts import (
    MAX_SNIPPET_CHARACTERS,
    UrlRejectionReason,
    WebSearchQuery,
    WebSearchResultItem,
)
from margpa_runtime_llm.modules.web_knowledge.ports import FetchedContent, FetchRejected


@dataclass(frozen=True, slots=True)
class _FixtureEntry:
    keywords: tuple[str, ...]
    title: str
    url: str
    snippet: str
    content: str
    content_type: str = "text/html"


_ENTRIES: tuple[_FixtureEntry, ...] = (
    _FixtureEntry(
        keywords=("python",),
        title="Python公式Documentation (Fixture)",
        url="https://www.python.org/doc/",
        snippet="Fixture Providerによる固定Sampleです。実Search APIには接続していません。",
        content=(
            "Python is a programming language that lets you work quickly and "
            "integrate systems more effectively. (Fixture content, not fetched live.)"
        ),
    ),
    _FixtureEntry(
        keywords=("fastapi",),
        title="FastAPI公式Documentation (Fixture)",
        url="https://fastapi.tiangolo.com/",
        snippet="Fixture Providerによる固定Sampleです。実Search APIには接続していません。",
        content=(
            "FastAPI is a modern, fast web framework for building APIs with "
            "Python. (Fixture content, not fetched live.)"
        ),
    ),
    _FixtureEntry(
        keywords=("wikipedia",),
        title="Wikipedia (Fixture)",
        url="https://www.wikipedia.org/",
        snippet="Fixture Providerによる固定Sampleです。実Search APIには接続していません。",
        content="Wikipedia is a free online encyclopedia. (Fixture content, not fetched live.)",
    ),
)
_DEFAULT_ENTRY = _FixtureEntry(
    keywords=(),
    title="Fixture Web Search Result",
    url="https://www.python.org/doc/",
    snippet="本ResultはFixture Providerによる固定Sampleです。実Search APIには接続していません。",
    content="This is placeholder Fixture content; no live Search API was queried.",
)


class FixtureWebSearchProvider:
    """Real Public Web is not exercised (Bounded Network decision, P7-E
    Recovery Index §1); this returns a small, deterministic, honestly
    fixture-labelled result set keyed by a simple keyword match."""

    provider_key = "fixture_search"
    provider_version = "1"

    def search(
        self,
        query: WebSearchQuery,
        *,
        max_results: int,
    ) -> tuple[WebSearchResultItem, ...]:
        lowered = query.query_text.casefold()
        matched = [entry for entry in _ENTRIES if any(word in lowered for word in entry.keywords)]
        if not matched:
            matched = [_DEFAULT_ENTRY]
        return tuple(
            WebSearchResultItem(
                result_id=_digest(f"{query.query_digest}\0{entry.url}"),
                title=entry.title,
                url=entry.url,
                snippet=entry.snippet[:MAX_SNIPPET_CHARACTERS],
                rank=index + 1,
            )
            for index, entry in enumerate(matched[:max_results])
        )


class FixtureWebFetchProvider:
    """Never opens a real socket — returns canned content for the fixed
    URL set `FixtureWebSearchProvider` produces. An unrecognized URL is
    rejected rather than silently fabricating content for it."""

    def fetch(
        self,
        url: str,
        *,
        timeout_seconds: float,
        max_response_bytes: int,
        max_redirects: int,
    ) -> FetchedContent | FetchRejected:
        del timeout_seconds, max_response_bytes, max_redirects
        for entry in (*_ENTRIES, _DEFAULT_ENTRY):
            if entry.url == url:
                return FetchedContent(
                    content=entry.content,
                    content_type=entry.content_type,
                    fetched_at=datetime.now(UTC).isoformat(),
                    canonical_url=url,
                )
        return FetchRejected(reason=UrlRejectionReason.DNS_RESOLUTION_FAILED)


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()
