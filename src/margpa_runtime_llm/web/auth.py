"""Environment-only preview access control."""

from __future__ import annotations

import base64
import binascii
import ipaddress
import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.web.access_profiles import (
    WebAccessProfile,
    WebAuthenticationMode,
    WebExposureMode,
    local_web_access_profile,
)

AUTH_MODE_ENV = "MARGPA_WEB_AUTH_MODE"
AUTH_USERNAME_ENV = "MARGPA_WEB_AUTH_USERNAME"
AUTH_PASSWORD_ENV = "MARGPA_WEB_AUTH_PASSWORD"


class WebAuthMode(StrEnum):
    DISABLED = "disabled"
    BASIC = "basic"


@dataclass(frozen=True, slots=True)
class WebAccessPolicy:
    mode: WebAuthMode
    exposure_mode: WebExposureMode = WebExposureMode.LOCAL
    non_loopback_allowed: bool = False
    username: str | None = field(default=None, repr=False)
    password: str | None = field(default=None, repr=False)

    @property
    def authentication_required(self) -> bool:
        return self.mode is WebAuthMode.BASIC

    def authorize(self, authorization: str | None) -> bool:
        if self.mode is WebAuthMode.DISABLED:
            return True
        if self.username is None or self.password is None or authorization is None:
            return False
        scheme, separator, encoded = authorization.partition(" ")
        if not separator or scheme.lower() != "basic" or not encoded:
            return False
        try:
            decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return False
        username, separator, password = decoded.partition(":")
        if not separator:
            return False
        username_matches = secrets.compare_digest(
            username.encode("utf-8"), self.username.encode("utf-8")
        )
        password_matches = secrets.compare_digest(
            password.encode("utf-8"), self.password.encode("utf-8")
        )
        return username_matches and password_matches


def load_web_access_policy(
    environment: Mapping[str, str] | None = None,
    *,
    profile: WebAccessProfile | None = None,
) -> WebAccessPolicy:
    current = os.environ if environment is None else environment
    selected_profile = profile or local_web_access_profile()

    if selected_profile.access.authentication is WebAuthenticationMode.NONE:
        if selected_profile.access.mode is WebExposureMode.PUBLIC_DEMO:
            return WebAccessPolicy(
                mode=WebAuthMode.DISABLED,
                exposure_mode=selected_profile.access.mode,
                non_loopback_allowed=selected_profile.access.non_loopback_allowed,
            )
        raw_mode = current.get(AUTH_MODE_ENV, WebAuthMode.DISABLED.value)
        if raw_mode != WebAuthMode.DISABLED.value:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_CONFIGURATION,
                safe_message="Local web access cannot enable preview authentication.",
            )
        return WebAccessPolicy(
            mode=WebAuthMode.DISABLED,
            exposure_mode=selected_profile.access.mode,
            non_loopback_allowed=selected_profile.access.non_loopback_allowed,
        )

    configured_basic_mode = current.get(AUTH_MODE_ENV)
    if configured_basic_mode != WebAuthMode.BASIC.value:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="Basic preview authentication mode is required.",
        )
    username = current.get(AUTH_USERNAME_ENV)
    password = current.get(AUTH_PASSWORD_ENV)
    if not _has_value(username) or not _has_value(password):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="Basic preview authentication requires both credentials.",
        )
    return WebAccessPolicy(
        mode=WebAuthMode.BASIC,
        exposure_mode=selected_profile.access.mode,
        non_loopback_allowed=selected_profile.access.non_loopback_allowed,
        username=username,
        password=password,
    )


def validate_bind_access_policy(host: str, policy: WebAccessPolicy) -> None:
    expected_auth_mode = {
        WebExposureMode.LOCAL: WebAuthMode.DISABLED,
        WebExposureMode.BASIC_PREVIEW: WebAuthMode.BASIC,
        WebExposureMode.PUBLIC_DEMO: WebAuthMode.DISABLED,
    }[policy.exposure_mode]
    if policy.mode is not expected_auth_mode:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The web exposure and authentication policies are inconsistent.",
        )
    if not _is_loopback_host(host) and not policy.non_loopback_allowed:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The selected web access profile does not allow a non-loopback bind.",
        )


def _has_value(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower().strip("[]")
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False
