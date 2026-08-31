"""Phase 7 (P7-F): URL Security Boundary tests — every rejection path is
exercised without ever opening a real socket to the public internet."""

from __future__ import annotations

import socket

import pytest

from margpa_runtime_llm.modules.web_knowledge.contracts import UrlRejectionReason
from margpa_runtime_llm.modules.web_knowledge.domain.url_security import (
    GetAddrInfoResult,
    validate_url_before_connect,
)


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "gopher://example.com/",
        "data:text/plain;base64,aGVsbG8=",
    ],
)
def test_unsupported_scheme_is_rejected(url: str) -> None:
    assert validate_url_before_connect(url) is UrlRejectionReason.UNSUPPORTED_SCHEME


def test_credentials_in_url_are_rejected() -> None:
    assert (
        validate_url_before_connect("https://user:pass@example.com/")
        is UrlRejectionReason.CREDENTIALS_IN_URL
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://0.0.0.0/",
        "http://[::1]/",
        "http://10.0.0.5/",
        "http://172.16.0.5/",
        "http://192.168.1.1/",
    ],
)
def test_loopback_and_private_ip_literals_are_rejected(url: str) -> None:
    assert (
        validate_url_before_connect(url) is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS
        or validate_url_before_connect(url) is UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    )


def test_cloud_metadata_ip_is_rejected() -> None:
    assert (
        validate_url_before_connect("http://169.254.169.254/latest/meta-data/")
        is UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    )


def test_cloud_metadata_hostname_is_rejected() -> None:
    assert (
        validate_url_before_connect("http://metadata.google.internal/computeMetadata/v1/")
        is UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    )


def test_dns_resolution_failure_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_resolve(*args: object, **kwargs: object) -> object:
        raise OSError("simulated resolution failure")

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolve)
    assert (
        validate_url_before_connect("https://this-host-does-not-resolve.example/")
        is UrlRejectionReason.DNS_RESOLUTION_FAILED
    )


def test_domain_resolving_to_a_private_address_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, port, proto
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.1.2.3", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert (
        validate_url_before_connect("https://looks-public.example/")
        is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS
    )


def test_domain_resolving_to_a_public_address_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, port, proto
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert validate_url_before_connect("https://public.example/path?query=1") is None


def test_malformed_url_is_rejected() -> None:
    assert validate_url_before_connect("not a url at all") is UrlRejectionReason.UNSUPPORTED_SCHEME


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org:22/",
        "https://example.org:3306/",
        "https://example.org:6379/",
        "https://example.org:27017/",
        "http://example.org:2375/",
    ],
)
def test_dangerous_port_is_rejected_before_dns_resolution(
    monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    def fail_resolve(*args: object, **kwargs: object) -> object:
        raise AssertionError("DNS must never be resolved for a Dangerous Port URL")

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolve)
    assert validate_url_before_connect(url) is UrlRejectionReason.DANGEROUS_PORT


def test_standard_https_port_is_not_treated_as_dangerous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert validate_url_before_connect("https://public.example/") is None
    assert validate_url_before_connect("https://public.example:8443/") is None


def test_out_of_range_port_is_rejected_not_raised() -> None:
    assert (
        validate_url_before_connect("https://example.org:99999999/")
        is UrlRejectionReason.UNSUPPORTED_SCHEME
    )


# -- P8-MR1 (P8-MANUAL-001): IPv4/IPv6 Candidate classification -------------


def test_domain_resolving_to_a_public_ipv6_address_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        # A genuinely publicly-routable IPv6 literal — deliberately not the
        # `2001:db8::/32` documentation-reserved prefix (RFC 3849), which
        # Python's own `ipaddress.IPv6Address.is_private` correctly flags
        # as non-public.
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:4700:4700::1111", port, 0, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert validate_url_before_connect("https://public-v6.example/") is None


def test_domain_resolving_to_an_ipv6_loopback_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", port, 0, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    # `::1` is simultaneously `is_loopback` and `is_reserved` in Python's
    # `ipaddress` module, and `_reject_if_unsafe_ip()` checks `is_reserved`
    # first (same "either Reason is acceptable" allowance the existing
    # `test_loopback_and_private_ip_literals_are_rejected` above already
    # uses for this exact literal) — what matters is that it is rejected.
    assert validate_url_before_connect("https://loopback-v6.example/") in (
        UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS,
        UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS,
    )


def test_domain_resolving_to_an_ipv6_unique_local_address_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fd12:3456:789a::1", port, 0, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert (
        validate_url_before_connect("https://ula-v6.example/")
        is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS
    )


def test_domain_resolving_to_an_ipv6_link_local_address_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::1", port, 0, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert (
        validate_url_before_connect("https://link-local-v6.example/")
        is UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    )


def test_domain_resolving_to_mixed_public_v4_and_v6_candidates_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A host advertising both a Public IPv4 and a Public IPv6 Candidate
    (the ordinary "dual-stack" case) must be accepted — every resolved
    Candidate is Public, regardless of Address Family."""

    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:4700:4700::1111", port, 0, 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert validate_url_before_connect("https://dual-stack.example/") is None


def test_domain_resolving_to_mixed_public_and_private_candidates_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Conservative-by-design (SSRF defense-in-depth, unchanged by P8-MR1):
    a Candidate set containing even one unsafe Address rejects the whole
    Resolution — a DNS answer mixing Public and Private Addresses is itself
    suspicious, so this Task never selectively "falls back" to only the
    Public Candidate among a mixed set. Explicit Non-goal (Exact Handoff
    §1 / P8-MR1 Required list): a Custom Transport that Pins a per-Candidate
    verified IP is Phase 10+ Hardening, not this Bounded Rework."""

    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::1", port, 0, 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
    assert (
        validate_url_before_connect("https://mixed-candidates.example/")
        is UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    )


# -- P8-MR7-1 (P8-CODEX-013): constructor-level `resolver=` injection ------
#
# The tests above prove the Security Boundary's classification logic by
# monkeypatching the *global* `socket.getaddrinfo` — legitimate, but it only
# proves the logic is correct, not that the `resolver` parameter itself
# (the actual injection seam `WebKnowledgeService` and `HttpxWebFetchProvider`
# now both accept) is honored instead of falling through to the real
# resolver. Every test below monkeypatches `socket.getaddrinfo` to *raise*,
# proving a supplied `resolver` is used exclusively and the real symbol is
# never consulted at all.


def test_injected_resolver_parameter_is_used_instead_of_the_real_socket_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def injected_resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    result = validate_url_before_connect("https://injected.example/", resolver=injected_resolver)
    assert result is None


def test_injected_resolver_permanent_failure_is_classified_without_touching_real_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def failing_resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host, port
        raise OSError("simulated permanent resolution failure via the injected Resolver")

    assert (
        validate_url_before_connect("https://injected-failure.example/", resolver=failing_resolver)
        is UrlRejectionReason.DNS_RESOLUTION_FAILED
    )


def test_injected_resolver_rejects_a_hostname_resolving_to_a_private_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def real_getaddrinfo_must_never_be_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("the real socket.getaddrinfo must never be reached")

    monkeypatch.setattr(socket, "getaddrinfo", real_getaddrinfo_must_never_be_called)

    def rebinding_resolver(host: str, port: int) -> list[GetAddrInfoResult]:
        del host
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.9.9.9", port))]

    assert (
        validate_url_before_connect(
            "https://looks-public-but-rebinds.example/", resolver=rebinding_resolver
        )
        is UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS
    )
