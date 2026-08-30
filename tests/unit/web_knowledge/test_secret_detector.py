from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.web_knowledge.domain.secret_detector import (
    detect_secret_candidates,
)


@pytest.mark.parametrize(
    "text",
    [
        "here is my key sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "AKIAABCDEFGHIJKLMNOP is my aws key",
        "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "-----BEGIN RSA PRIVATE KEY-----\nMIIExx",
        "api_key=abcdef1234567890",
        "password: hunter2hunter2",
        "Authorization: Bearer abcdef1234567890xyz",
    ],
)
def test_known_secret_shapes_are_detected(text: str) -> None:
    assert detect_secret_candidates(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "python programming tutorial",
        "how to configure an api gateway",
        "contact page email format best practices",
        "what is a bearer",
    ],
)
def test_ordinary_queries_are_not_flagged(text: str) -> None:
    assert detect_secret_candidates(text) is False
