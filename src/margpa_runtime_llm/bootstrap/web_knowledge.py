"""Phase 7 (P7-E/F) / Phase 8 (P8-A): composition root for Governed Web
Search/Fetch.

Real Public Web Search is out of Bounded Network scope for this Task (no
credential-free Search API is available without an account/contract — see
the P7-E Recovery Index §1 for the explicit decision). The Fixture Search
Provider is wired here as the actual runtime composition for the Search
Golden Path, not merely a Test double.

Direct URL Fetch (P8-A / P8-REQ-002) is a structurally separate capability:
it never invokes a Search Provider, so it does not inherit the Search Fixture
decision above. `HttpxWebFetchProvider` is genuinely production-wired here as
`direct_fetch_provider` — real httpx request/redirect/streaming mechanics,
bounded by the same URL Security module the Search path uses. This Task does
not obtain User Authority to exercise it against a real socket (Real Network
remains NOT RUN / USER MANUAL GATE); `transport` stays injectable so Tests
exercise the exact same Production code path against `httpx.MockTransport`
instead of a parallel test-only implementation.
"""

from __future__ import annotations

import httpx

from margpa_runtime_llm.adapters.web_knowledge import (
    FixtureWebFetchProvider,
    FixtureWebSearchProvider,
    HttpxWebFetchProvider,
)
from margpa_runtime_llm.modules.web_knowledge.application import WebKnowledgeService
from margpa_runtime_llm.modules.web_knowledge.contracts import WebSearchFeatureConfig


def build_web_knowledge_service(
    *, direct_fetch_transport: httpx.BaseTransport | None = None
) -> WebKnowledgeService:
    """`governance_mode` is deliberately not fixed here: it is a per-call
    argument to `WebKnowledgeService.search_and_fetch()`/`fetch_direct_url()`,
    resolved by the caller (the Web Search route) from the server-configured
    value at request time — see `web/web_search_routes.py`.

    `direct_fetch_transport` is `None` in every real Production call site
    (real httpx transport); Tests pass an `httpx.MockTransport` so the Direct
    URL Fetch route can be exercised end-to-end with zero real sockets."""

    return WebKnowledgeService(
        search_provider=FixtureWebSearchProvider(),
        fetch_provider=FixtureWebFetchProvider(),
        direct_fetch_provider=HttpxWebFetchProvider(transport=direct_fetch_transport),
        config=WebSearchFeatureConfig(),
    )
