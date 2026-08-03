"""Preview authentication and fail-closed bind tests."""

import base64
from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.web.access_profiles import (
    WebAccessProfile,
    WebExposureMode,
    load_web_access_profile,
)
from margpa_runtime_llm.web.auth import (
    AUTH_MODE_ENV,
    AUTH_PASSWORD_ENV,
    AUTH_USERNAME_ENV,
    WebAuthMode,
    load_web_access_policy,
    validate_bind_access_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASIC_PROFILE = load_web_access_profile(PROJECT_ROOT / "config/web_profiles/basic_preview.toml")
PUBLIC_PROFILE = load_web_access_profile(PROJECT_ROOT / "config/web_profiles/public_demo.toml")


class CredentialRejectingEnvironment(Mapping[str, str]):
    def __init__(self) -> None:
        self.requested: list[str] = []

    def __getitem__(self, key: str) -> str:
        self.requested.append(key)
        if key in {AUTH_USERNAME_ENV, AUTH_PASSWORD_ENV}:
            raise AssertionError("public profile read a Basic credential")
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return 0


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
        load_web_access_policy(
            {AUTH_MODE_ENV: "basic", AUTH_USERNAME_ENV: "sensitive-user-value"},
            profile=BASIC_PROFILE,
        )

    assert "sensitive-user-value" not in captured.value.safe_message
    with pytest.raises(InferenceError):
        load_web_access_policy({AUTH_MODE_ENV: "unknown"}, profile=BASIC_PROFILE)


def test_basic_auth_uses_server_side_exact_comparison_and_safe_repr() -> None:
    policy = load_web_access_policy(
        {
            AUTH_MODE_ENV: "basic",
            AUTH_USERNAME_ENV: "preview-user",
            AUTH_PASSWORD_ENV: "private-password",
        },
        profile=BASIC_PROFILE,
    )

    validate_bind_access_policy("0.0.0.0", policy)
    assert policy.authorize(basic_header("preview-user", "private-password")) is True
    assert policy.authorize(basic_header("preview-user", "wrong")) is False
    assert policy.authorize("Bearer token") is False
    assert policy.authorize("Basic invalid-base64") is False
    assert "preview-user" not in repr(policy)
    assert "private-password" not in repr(policy)


def test_public_demo_is_explicit_non_loopback_and_never_reads_basic_credentials() -> None:
    environment = CredentialRejectingEnvironment()

    policy = load_web_access_policy(environment, profile=PUBLIC_PROFILE)

    assert policy.exposure_mode is WebExposureMode.PUBLIC_DEMO
    assert policy.mode is WebAuthMode.DISABLED
    assert policy.authorize(None) is True
    assert policy.username is None
    assert policy.password is None
    assert AUTH_USERNAME_ENV not in environment.requested
    assert AUTH_PASSWORD_ENV not in environment.requested
    validate_bind_access_policy("0.0.0.0", policy)


@pytest.mark.parametrize(
    ("profile", "host", "environment", "expected_pass"),
    [
        (None, "127.0.0.1", {}, True),
        (None, "0.0.0.0", {}, False),
        (
            BASIC_PROFILE,
            "0.0.0.0",
            {
                AUTH_MODE_ENV: "basic",
                AUTH_USERNAME_ENV: "user",
                AUTH_PASSWORD_ENV: "password",
            },
            True,
        ),
        (BASIC_PROFILE, "0.0.0.0", {AUTH_MODE_ENV: "basic"}, False),
        (PUBLIC_PROFILE, "0.0.0.0", {}, True),
    ],
)
def test_access_matrix(
    profile: WebAccessProfile | None,
    host: str,
    environment: Mapping[str, str],
    expected_pass: bool,
) -> None:
    try:
        policy = load_web_access_policy(environment, profile=profile)
        validate_bind_access_policy(host, policy)
    except InferenceError:
        assert expected_pass is False
    else:
        assert expected_pass is True
