"""Typed, framework-independent contracts for the runtime composition switchboard.

Phase 2-E scope only: this module describes and reports the state of existing,
independently-gated runtime components (Documentation RAG, Conversation
Persistence, Configuration Control). It does not implement Agent/Tool
components, a governance evaluator, or any permission-granting mechanism.
Registration here never creates execution authority for a component; it only
projects the state that component's own (unchanged) gate already resolved.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from margpa_runtime_llm.modules.configuration_control.contracts import (
    ApplyDisposition,
    ConfigurationSource,
)

_COMPONENT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{128}$")


class ComponentState(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"


class ComponentSideEffectLevel(StrEnum):
    NONE = "none"
    READ_ONLY = "read_only"
    LOCAL_WRITE = "local_write"
    EXTERNAL = "external"


class ComponentRegistrationErrorCode(StrEnum):
    DUPLICATE_COMPONENT = "duplicate_component"
    CONFLICTING_COMPONENTS_ENABLED = "conflicting_components_enabled"
    UNRESOLVED_REQUIRED_DEPENDENCY = "unresolved_required_dependency"


@dataclass(frozen=True, slots=True)
class ComponentRegistrationError(Exception):
    code: ComponentRegistrationErrorCode
    safe_message: str
    component_key: str


def _validate_component_key(value: str) -> str:
    if not isinstance(value, str) or _COMPONENT_KEY_PATTERN.fullmatch(value) is None:
        raise ValueError("component key is invalid")
    return value


def _digest_payload(
    *,
    component_key: str,
    kind: str,
    version: str,
    state: ComponentState,
    capabilities: tuple[str, ...],
    required_dependencies: tuple[str, ...],
    optional_dependencies: tuple[str, ...],
    conflicts_with: tuple[str, ...],
    degraded_reasons: tuple[str, ...],
    side_effect_level: ComponentSideEffectLevel,
    apply_disposition: ApplyDisposition,
    restart_required: bool,
    effective_source: ConfigurationSource,
    revision: int,
    governance_seam_mode: str,
) -> dict[str, object]:
    """Canonical payload hashed into `canonical_digest`; excludes the digest itself."""

    return {
        "component_key": component_key,
        "kind": kind,
        "version": version,
        "state": state.value,
        "capabilities": sorted(capabilities),
        "required_dependencies": sorted(required_dependencies),
        "optional_dependencies": sorted(optional_dependencies),
        "conflicts_with": sorted(conflicts_with),
        "degraded_reasons": sorted(degraded_reasons),
        "side_effect_level": side_effect_level.value,
        "apply_disposition": apply_disposition.value,
        "restart_required": restart_required,
        "effective_source": effective_source.value,
        "revision": revision,
        "governance_seam_mode": governance_seam_mode,
    }


def _digest_of_payload(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


@dataclass(frozen=True, slots=True)
class ComponentDescriptor:
    """Existence/state description only — never an execution or permission grant.

    Self-verifying: `canonical_digest` must already be the exact SHA-512 of
    this descriptor's own canonical payload. Construct instances through
    `build_component_descriptor()` rather than computing the digest by hand.
    """

    component_key: str
    kind: str
    version: str
    state: ComponentState
    canonical_digest: str
    capabilities: tuple[str, ...] = ()
    required_dependencies: tuple[str, ...] = ()
    optional_dependencies: tuple[str, ...] = ()
    conflicts_with: tuple[str, ...] = ()
    degraded_reasons: tuple[str, ...] = ()
    side_effect_level: ComponentSideEffectLevel = ComponentSideEffectLevel.NONE
    apply_disposition: ApplyDisposition = ApplyDisposition.RESTART_REQUIRED
    restart_required: bool = True
    effective_source: ConfigurationSource = ConfigurationSource.APPLICATION
    revision: int = 1
    governance_seam_mode: Literal["off"] = "off"

    def __post_init__(self) -> None:
        _validate_component_key(self.component_key)
        for key in (*self.required_dependencies, *self.optional_dependencies, *self.conflicts_with):
            _validate_component_key(key)
        if not isinstance(self.kind, str) or not self.kind:
            raise ValueError("component kind is invalid")
        if not isinstance(self.version, str) or not self.version:
            raise ValueError("component version is invalid")
        if (
            isinstance(self.revision, bool)
            or not isinstance(self.revision, int)
            or self.revision < 1
        ):
            raise ValueError("component revision is invalid")
        if self.governance_seam_mode != "off":
            raise ValueError("governance seam mode must be off in Phase 2-E")
        if self.state in (ComponentState.UNAVAILABLE, ComponentState.DENIED):
            if self.capabilities:
                raise ValueError("unavailable or denied components must not report capabilities")
            if not self.degraded_reasons:
                raise ValueError("unavailable or denied components must report a reason")
        if len(set(self.required_dependencies)) != len(self.required_dependencies):
            raise ValueError("required dependencies must be distinct")
        if len(set(self.optional_dependencies)) != len(self.optional_dependencies):
            raise ValueError("optional dependencies must be distinct")
        if len(set(self.conflicts_with)) != len(self.conflicts_with):
            raise ValueError("conflicting components must be distinct")
        if set(self.required_dependencies) & set(self.conflicts_with):
            raise ValueError("a component cannot both require and conflict with the same key")
        if set(self.optional_dependencies) & set(self.conflicts_with):
            raise ValueError("a component cannot both depend on and conflict with the same key")
        if self.component_key in self.conflicts_with:
            raise ValueError("a component cannot conflict with itself")
        if (
            self.component_key in self.required_dependencies
            or self.component_key in self.optional_dependencies
        ):
            raise ValueError("a component cannot depend on itself")
        if not self.canonical_digest or _DIGEST_PATTERN.fullmatch(self.canonical_digest) is None:
            raise ValueError("component canonical digest is invalid")
        expected = _digest_of_payload(self.digest_payload)
        if self.canonical_digest != expected:
            raise ValueError("component canonical digest does not match its payload")

    @property
    def digest_payload(self) -> dict[str, object]:
        """Canonical payload used for `canonical_digest`; excludes the digest itself."""

        return _digest_payload(
            component_key=self.component_key,
            kind=self.kind,
            version=self.version,
            state=self.state,
            capabilities=self.capabilities,
            required_dependencies=self.required_dependencies,
            optional_dependencies=self.optional_dependencies,
            conflicts_with=self.conflicts_with,
            degraded_reasons=self.degraded_reasons,
            side_effect_level=self.side_effect_level,
            apply_disposition=self.apply_disposition,
            restart_required=self.restart_required,
            effective_source=self.effective_source,
            revision=self.revision,
            governance_seam_mode=self.governance_seam_mode,
        )


def component_digest(descriptor: ComponentDescriptor) -> str:
    """Recompute the SHA-512 a valid descriptor's `canonical_digest` must equal."""

    return _digest_of_payload(descriptor.digest_payload)


def build_component_descriptor(
    *,
    component_key: str,
    kind: str,
    version: str,
    state: ComponentState,
    capabilities: tuple[str, ...] = (),
    required_dependencies: tuple[str, ...] = (),
    optional_dependencies: tuple[str, ...] = (),
    conflicts_with: tuple[str, ...] = (),
    degraded_reasons: tuple[str, ...] = (),
    side_effect_level: ComponentSideEffectLevel = ComponentSideEffectLevel.NONE,
    apply_disposition: ApplyDisposition = ApplyDisposition.RESTART_REQUIRED,
    restart_required: bool = True,
    effective_source: ConfigurationSource = ConfigurationSource.APPLICATION,
    revision: int = 1,
    governance_seam_mode: Literal["off"] = "off",
) -> ComponentDescriptor:
    """The normal way to construct a `ComponentDescriptor`: computes its own digest."""

    payload = _digest_payload(
        component_key=component_key,
        kind=kind,
        version=version,
        state=state,
        capabilities=capabilities,
        required_dependencies=required_dependencies,
        optional_dependencies=optional_dependencies,
        conflicts_with=conflicts_with,
        degraded_reasons=degraded_reasons,
        side_effect_level=side_effect_level,
        apply_disposition=apply_disposition,
        restart_required=restart_required,
        effective_source=effective_source,
        revision=revision,
        governance_seam_mode=governance_seam_mode,
    )
    return ComponentDescriptor(
        component_key=component_key,
        kind=kind,
        version=version,
        state=state,
        canonical_digest=_digest_of_payload(payload),
        capabilities=capabilities,
        required_dependencies=required_dependencies,
        optional_dependencies=optional_dependencies,
        conflicts_with=conflicts_with,
        degraded_reasons=degraded_reasons,
        side_effect_level=side_effect_level,
        apply_disposition=apply_disposition,
        restart_required=restart_required,
        effective_source=effective_source,
        revision=revision,
        governance_seam_mode=governance_seam_mode,
    )
