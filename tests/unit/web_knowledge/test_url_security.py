"""Phase 7 (P7-F): URL Security Boundary tests — every rejection path is
exercised without ever opening a real socket to the public internet."""

from __future__ import annotations

import socket

import pytest

from margpa_runtime_llm.modules.web_knowledge.contracts import UrlRejectionReason
from margpa_runtime_llm.modules.web_knowledge.domain.url_security import (
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
