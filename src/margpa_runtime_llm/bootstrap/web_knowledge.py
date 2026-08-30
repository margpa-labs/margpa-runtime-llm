"""Phase 7 (P7-E/F): composition root for Governed Web Search/Fetch.

Real Public Web is out of Bounded Network scope for this Task (no
credential-free Search API is available without an account/contract — see
the P7-E Recovery Index §1 for the explicit decision). The Fixture Provider
pair is wired here as the actual runtime composition, not merely a Test
double — this is the genuine Manual Search Golden Path this Task ships.

`HttpxWebFetchProvider` is still composed and fully tested (real httpx
mechanics against `httpx.MockTransport`) so a future Task can swap in a
real Search Provider by only changing this one composition function.
"""

from __future__ import annotations

from margpa_runtime_llm.adapters.web_knowledge import (
    FixtureWebFetchProvider,
    FixtureWebSearchProvider,
)
from margpa_runtime_llm.modules.web_knowledge.application import WebKnowledgeService
from margpa_runtime_llm.modules.web_knowledge.contracts import WebSearchFeatureConfig


def build_web_knowledge_service() -> WebKnowledgeService:
    """`governance_mode` is deliberately not fixed here: it is a per-call
    argument to `WebKnowledgeService.search_and_fetch()`, resolved by the
    caller (the Web Search route) from the server-configured value at
    request time — see `web/web_search_routes.py`."""

    return WebKnowledgeService(
        search_provider=FixtureWebSearchProvider(),
        fetch_provider=FixtureWebFetchProvider(),
        config=WebSearchFeatureConfig(),
    )
