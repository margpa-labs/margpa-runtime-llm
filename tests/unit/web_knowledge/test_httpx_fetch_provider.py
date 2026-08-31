"""Phase 7 (P7-E/F): `HttpxWebFetchProvider` tests against `httpx.MockTransport`
— real httpx request/redirect/streaming code paths, zero real sockets opened."""

from __future__ import annotations

import socket

import httpx
import pytest

from margpa_runtime_llm.adapters.web_knowledge.httpx_fetch_provider import (
    HttpxWebFetchProvider,
)
from margpa_runtime_llm.modules.web_knowledge.contracts import (
    UrlRejectionReason,
    WebFetchFailureReason,
)
from margpa_runtime_llm.modules.web_knowledge.domain.url_security import GetAddrInfoResult
from margpa_runtime_llm.modules.web_knowledge.ports import FetchedContent, FetchRejected


def _provider(handler, **kwargs: object) -> HttpxWebFetchProvider:  # type: ignore[no-untyped-def]
    return HttpxWebFetchProvider(
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda seconds: None,
        **kwargs,  # type: ignore[arg-type]
    )


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
    # P8-A / Controller Recovery §6 item 2: `canonical_url` must be the
    # final, post-redirect URL the content was actually read from.
    assert result.canonical_url == "https://example.org/final"


def test_canonical_url_matches_the_requested_url_when_there_is_no_redirect() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="no redirect")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/direct",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.canonical_url == "https://example.org/direct"


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


def test_persistent_connect_error_is_retried_then_reported_as_connect_failed() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise httpx.ConnectError("simulated connection failure", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/down",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.CONNECT_FAILED
    # P8-MR1 (P8-MANUAL-001): DEFAULT_MAX_RETRIES=2 -> 3 attempts total,
    # Network 0 (MockTransport) but proven exercised via the call count.
    assert len(calls) == 3


def test_transient_connect_error_is_retried_then_succeeds() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if len(calls) < 2:
            raise httpx.ConnectError("simulated transient failure", request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text="recovered")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/flaky",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "recovered"
    assert len(calls) == 2


def test_transient_timeout_is_retried_then_succeeds() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if len(calls) < 2:
            raise httpx.ConnectTimeout("simulated timeout", request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text="recovered")

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/slow-then-fast",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "recovered"
    assert len(calls) == 2


def test_connect_error_wrapping_dns_failure_is_classified_and_retried() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        import socket

        exc = httpx.ConnectError("simulated dns failure", request=request)
        exc.__cause__ = socket.gaierror("simulated getaddrinfo failure")
        raise exc

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/dns-down",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.DNS_RESOLUTION_FAILED
    assert len(calls) == 3


def test_connect_error_wrapping_tls_failure_is_classified_and_not_retried() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        import ssl

        exc = httpx.ConnectError("simulated tls failure", request=request)
        exc.__cause__ = ssl.SSLError("simulated certificate failure")
        raise exc

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/tls-down",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.TLS_FAILED
    # TLS failures are not in `_RETRYABLE_REASONS` — exactly one attempt.
    assert len(calls) == 1


def test_protocol_error_is_reported_and_not_retried() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise httpx.RemoteProtocolError("simulated malformed response", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/malformed",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.HTTP_PROTOCOL_ERROR
    assert len(calls) == 1


def test_generic_http_error_is_reported_as_fetch_rejected_and_not_retried() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise httpx.ProxyError("simulated proxy failure", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/down",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is WebFetchFailureReason.FETCH_REJECTED
    assert len(calls) == 1


def test_retry_budget_is_shared_across_redirect_hops_not_per_hop() -> None:
    """P8-MR1: worst-case latency stays bounded by a single shared Retry
    Budget for the whole `fetch()` call, never a fresh Budget per redirect
    hop — a pathological Server that both redirects and fails transiently
    on every hop cannot multiply the total attempt count unboundedly."""

    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise httpx.ConnectError("simulated failure on every hop", request=request)

    provider = _provider(handler)
    result = provider.fetch(
        "https://example.org/start",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=5,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.CONNECT_FAILED
    # DEFAULT_MAX_RETRIES=2 -> exactly 3 attempts total, never per-hop.
    assert len(calls) == 3


def test_permanent_rejection_is_never_retried() -> None:
    """A Permanent Unsafe URL rejection (Security Boundary, not the
    network) must never be retried — `validate_url_before_connect()`
    already rejects `127.0.0.1` before any Transport call is made, so
    `handler` here must never even be invoked, exactly like the pre-Retry
    behavior this Package preserves."""

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
    assert result.reason is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS


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


# -- P8-MR7-1 (P8-CODEX-013): injected `resolver=` at the Hop Boundary -----
#
# Every test below monkeypatches the real `socket.getaddrinfo` to raise,
# proving `HttpxWebFetchProvider`'s own `resolver=` parameter — not this
# suite's directory-level `conftest.py` fallback — is what each hop's
# `validate_url_before_connect()` call actually consults.


def test_injected_resolver_permits_a_public_ipv4_hostname(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="hello v4")

    def resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    provider = _provider(handler, resolver=resolver)
    result = provider.fetch(
        "https://public-v4.example/page",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "hello v4"


def test_injected_resolver_permits_a_public_ipv6_hostname(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="hello v6")

    def resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:4700:4700::1111", port, 0, 0))]

    provider = _provider(handler, resolver=resolver)
    result = provider.fetch(
        "https://public-v6.example/page",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "hello v6"


def test_injected_resolver_rejects_a_hostname_resolving_to_a_private_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("transport must never be reached for an unsafe resolved address")

    def resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.9.9", port))]

    provider = _provider(handler, resolver=resolver)
    result = provider.fetch(
        "https://rebinds-to-private.example/page",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchRejected)
    assert result.reason is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS


def test_injected_resolver_transient_dns_failure_is_retried_then_recovers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Proves the Retry Budget (P8-MR1) and the injected Resolver (P8-MR7-1)
    compose correctly: a Resolver that fails once and then succeeds is
    retried by `fetch()`'s shared Retry Budget exactly like a Transport-level
    transient failure already is, with zero real DNS at any point."""

    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    resolver_calls: list[str] = []

    def flaky_resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        resolver_calls.append(host)
        if len(resolver_calls) < 2:
            raise socket.gaierror("simulated transient resolution failure")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="recovered via dns")

    provider = _provider(handler, resolver=flaky_resolver)
    result = provider.fetch(
        "https://flaky-dns.example/page",
        timeout_seconds=5.0,
        max_response_bytes=1_000_000,
        max_redirects=3,
    )

    assert isinstance(result, FetchedContent)
    assert result.content == "recovered via dns"
    assert len(resolver_calls) == 2
