"""Typed web exposure, feature-capability, and disabled control-profile contracts."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)


class WebExposureMode(StrEnum):
    LOCAL = "local"
    BASIC_PREVIEW = "basic_preview"
    PUBLIC_DEMO = "public_demo"


class WebAuthenticationMode(StrEnum):
    NONE = "none"
    BASIC = "basic"


class DocumentationRagCapability(StrEnum):
    DENIED = "denied"
    ELIGIBLE = "eligible"


class DocumentationRagFeatureMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class DocumentationRagEffectiveState(StrEnum):
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ENABLED = "enabled"
    DENIED = "denied"


class OptionalControlMode(StrEnum):
    OFF = "off"


class _FrozenProfileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class WebAccessConfig(_FrozenProfileModel):
    mode: WebExposureMode
    authentication: WebAuthenticationMode
    non_loopback_allowed: bool


class WebFeatureCapability(_FrozenProfileModel):
    documentation_rag: DocumentationRagCapability


class DocumentationRagFeatureProfile(_FrozenProfileModel):
    """Independent feature selection; access profiles only define the ceiling."""

    schema_version: Literal["1"] = "1"
    mode: DocumentationRagFeatureMode = DocumentationRagFeatureMode.DISABLED


class OptionalControlConfig(_FrozenProfileModel):
    mode: OptionalControlMode = OptionalControlMode.OFF


class WebControlConfig(_FrozenProfileModel):
    rate_limit: OptionalControlConfig = OptionalControlConfig()
    generation_budget: OptionalControlConfig = OptionalControlConfig()
    cooldown: OptionalControlConfig = OptionalControlConfig()
    public_max_new_tokens: OptionalControlConfig = OptionalControlConfig()
    request_quota: OptionalControlConfig = OptionalControlConfig()
    cost_guard: OptionalControlConfig = OptionalControlConfig()

    @property
    def effective_modes(self) -> dict[str, OptionalControlMode]:
        return {
            name: control.mode
            for name, control in (
                ("rate_limit", self.rate_limit),
                ("generation_budget", self.generation_budget),
                ("cooldown", self.cooldown),
                ("public_max_new_tokens", self.public_max_new_tokens),
                ("request_quota", self.request_quota),
                ("cost_guard", self.cost_guard),
            )
        }


class WebAccessProfile(_FrozenProfileModel):
    schema_version: Literal["1"] = "1"
    profile_key: WebExposureMode
    access: WebAccessConfig
    features: WebFeatureCapability
    controls: WebControlConfig

    @model_validator(mode="after")
    def validate_profile_contract(self) -> WebAccessProfile:
        if self.profile_key is not self.access.mode:
            raise ValueError("profile key and access mode must match")

        expected_authentication = {
            WebExposureMode.LOCAL: WebAuthenticationMode.NONE,
            WebExposureMode.BASIC_PREVIEW: WebAuthenticationMode.BASIC,
            WebExposureMode.PUBLIC_DEMO: WebAuthenticationMode.NONE,
        }[self.access.mode]
        if self.access.authentication is not expected_authentication:
            raise ValueError("access mode and authentication mode are inconsistent")

        if self.access.mode is WebExposureMode.LOCAL and self.access.non_loopback_allowed:
            raise ValueError("local access must remain loopback-only")
        if (
            self.access.mode in {WebExposureMode.BASIC_PREVIEW, WebExposureMode.PUBLIC_DEMO}
            and not self.access.non_loopback_allowed
        ):
            raise ValueError("preview access profiles must explicitly allow non-loopback bind")

        return self


class PublicControlPolicyPort(Protocol):
    @property
    def mode(self) -> OptionalControlMode: ...

    def check_request(self) -> None: ...

    def before_generation(self) -> None: ...

    def observe_generation(self) -> None: ...

    def after_generation(self) -> None: ...


@dataclass(frozen=True, slots=True)
class DisabledPublicControlPolicy:
    """Side-effect-free placeholder for future independently injected controls."""

    mode: OptionalControlMode = OptionalControlMode.OFF

    def check_request(self) -> None:
        return None

    def before_generation(self) -> None:
        return None

    def observe_generation(self) -> None:
        return None

    def after_generation(self) -> None:
        return None


def load_web_access_profile(path: Path) -> WebAccessProfile:
    try:
        with path.open("rb") as profile_file:
            return WebAccessProfile.model_validate(tomllib.load(profile_file))
    except FileNotFoundError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The web access profile was not found.",
        ) from exc
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The web access profile is invalid.",
        ) from exc


def local_web_access_profile() -> WebAccessProfile:
    return WebAccessProfile(
        profile_key=WebExposureMode.LOCAL,
        access=WebAccessConfig(
            mode=WebExposureMode.LOCAL,
            authentication=WebAuthenticationMode.NONE,
            non_loopback_allowed=False,
        ),
        features=WebFeatureCapability(
            documentation_rag=DocumentationRagCapability.ELIGIBLE,
        ),
        controls=WebControlConfig(),
    )


def resolve_documentation_rag_state(
    *,
    access_profile: WebAccessProfile,
    feature_profile: DocumentationRagFeatureProfile,
    adapter_available: bool,
) -> DocumentationRagEffectiveState:
    capability = access_profile.features.documentation_rag
    if capability is DocumentationRagCapability.DENIED:
        return DocumentationRagEffectiveState.DENIED
    if not adapter_available:
        return DocumentationRagEffectiveState.UNAVAILABLE
    if feature_profile.mode is DocumentationRagFeatureMode.DISABLED:
        return DocumentationRagEffectiveState.DISABLED
    return DocumentationRagEffectiveState.ENABLED


def build_disabled_control_policy(
    profile: WebAccessProfile,
) -> PublicControlPolicyPort:
    if any(
        mode is not OptionalControlMode.OFF for mode in profile.controls.effective_modes.values()
    ):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The configured web controls are not implemented.",
        )
    return DisabledPublicControlPolicy()
