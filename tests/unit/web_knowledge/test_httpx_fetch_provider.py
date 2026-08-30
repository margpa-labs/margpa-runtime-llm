"""Phase 7 (P7-E/F): `HttpxWebFetchProvider` tests against `httpx.MockTransport`
— real httpx request/redirect/streaming code paths, zero real sockets opened."""

from __future__ import annotations

import httpx
import pytest

from margpa_runtime_llm.adapters.web_knowledge.httpx_fetch_provider import (
    HttpxWebFetchProvider,
)
from margpa_runtime_llm.modules.web_knowledge.contracts import (
    UrlRejectionReason,
    WebFetchFailureReason,
)
from margpa_runtime_llm.modules.web_knowledge.ports import FetchedContent, FetchRejected


def _provider(handler) -> HttpxWebFetchProvider:  # type: ignore[no-untyped-def]
    return HttpxWebFetchProvider(transport=httpx.MockTransport(handler))


def test_successful_fetch_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="<p>hello</p>")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/page",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "<p>hello</p>"
    assert result.content_type == "text/html"


def test_unsupported_content_type_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/file.pdf",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.CONTENT_TYPE_UNSUPPORTED


def test_oversized_response_is_rejected_via_streaming_cap() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/plain"}, text="x" * 10_000)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/big",
        timeout_seconds=5.0,
        max_response_bytes=100,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.RESPONSE_TOO_LARGE


def test_content_length_over_limit_is_rejected_before_streaming() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/plain", "content-length": "999999999"},
            text="short",
        )

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/big",
        timeout_seconds=5.0,
        max_response_bytes=100,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.RESPONSE_TOO_LARGE


def test_redirect_is_followed_within_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/start":
            return httpx.Response(302, headers={"location": "https://example.org/final"})
        return httpx.Response(200, headers={"content-type": "text/html"}, text="landed")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/start",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "landed"


def test_too_many_redirects_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        step = int(request.url.path.strip("/").removeprefix("hop") or "0")
        return httpx.Response(302, headers={"location": f"https://example.org/hop{step + 1}"})

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/hop0",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=2,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.TOO_MANY_REDIRECTS


def test_redirect_to_a_private_address_is_rejected_by_the_security_boundary() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "example.org":
            return httpx.Response(302, headers={"location": "http://10.0.0.5/internal"})
        raise AssertionError("must never actually dial the redirect target")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/start",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS


def test_timeout_is_reported_as_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("simulated timeout", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/slow",
        timeout_seconds=1.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.TIMEOUT


def test_generic_http_error_is_reported_as_fetch_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated connection failure", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/down",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is WebFetchFailureReason.FETCH_REJECTED


def test_private_url_is_rejected_before_any_transport_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("transport must never be reached for an unsafe URL")

    provider = _provider(handler)
    result = provider.fetch(
        "http://127.0.0.1/admin",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
