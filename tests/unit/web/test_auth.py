"""Preview authentication and fail-closed bind tests."""

import base64

import pytest

from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.web.auth import (
    AUTH_MODE_ENV,
    AUTH_PASSWORD_ENV,
    AUTH_USERNAME_ENV,
    WebAuthMode,
    load_web_access_policy,
    validate_bind_access_policy,
)


def basic_header(username: str, password: str) -> str:
    encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {encoded}"


def test_disabled_auth_is_allowed_only_for_loopback_bind() -> None:
    policy = load_web_access_policy({})

    assert policy.mode is WebAuthMode.DISABLED
    validate_bind_access_policy("127.0.0.1", policy)
    validate_bind_access_policy("::1", policy)
    validate_bind_access_policy("localhost", policy)
    with pytest.raises(InferenceError):
        validate_bind_access_policy("0.0.0.0", policy)
    with pytest.raises(InferenceError):
        validate_bind_access_policy("preview.example", policy)


def test_basic_auth_requires_both_credentials_without_exposing_them() -> None:
    with pytest.raises(InferenceError) as captured:
        load_web_access_policy({AUTH_MODE_ENV: "basic", AUTH_USERNAME_ENV: "sensitive-user-value"})

    assert "sensitive-user-value" not in captured.value.safe_message
    with pytest.raises(InferenceError):
        load_web_access_policy({AUTH_MODE_ENV: "unknown"})


def test_basic_auth_uses_server_side_exact_comparison_and_safe_repr() -> None:
    policy = load_web_access_policy(
        {
            AUTH_MODE_ENV: "basic",
            AUTH_USERNAME_ENV: "preview-user",
            AUTH_PASSWORD_ENV: "private-password",
        }
    )

    validate_bind_access_policy("0.0.0.0", policy)
    assert policy.authorize(basic_header("preview-user", "private-password")) is True
    assert policy.authorize(basic_header("preview-user", "wrong")) is False
    assert policy.authorize("Bearer token") is False
    assert policy.authorize("Basic invalid-base64") is False
    assert "preview-user" not in repr(policy)
    assert "private-password" not in repr(policy)
