"""CAS controller for independent provider configuration and active state."""

from __future__ import annotations

import threading
from datetime import UTC, datetime

from ..domain.identifiers import ModelRole
from ..domain.provider_selection import (
    ProviderIndependence,
    ProviderKind,
    ProviderOption,
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
    ProviderSelectionSnapshot,
    RoleProviderSelection,
    provider_selection_digest,
)

QWEN_MAIN = "main.qwen3-4b-q4-k-m"
DEEPSEEK_MAIN = "main.deepseek-r1-0528-qwen3-8b-q4-k-m"
SELENE_JUDGE = "judge.selene-1-mini-llama-3.1-8b-q5-k-m"
QWEN3_GUARD = "guard.qwen3guard-gen-0.6b-q8-0"
NONE_PROVIDER = "none"
BUILT_IN_GUARD = "built_in.rule_pattern"
BUILT_IN_JUDGE = "built_in.deterministic"

_SELENE_DIGEST = (
    "6d5472911fc347d51a73e57077dd34353c3e134a0af67b0dbe4e4df7d980e3246"
    "f0253ee16e5a241a41904d37e73ab3ba11ce5d800de37b9adddb2ada9b6c50d"
)
_QWEN3_GUARD_DIGEST = (
    "0b8d213fd487980ce2667acaaf042d228486d9b467cd90ab6bfbe490527fa1b51"
    "d7a318af593bc920d59f5b22759196c09eaf8cba1974766ab170e6d6f6c19cb"
)


def default_provider_options() -> tuple[ProviderOption, ...]:
    return (
        ProviderOption(
            provider_id=QWEN_MAIN,
            role=ModelRole.MAIN,
            kind=ProviderKind.MODEL,
            display_name="Qwen3 4B",
            model_key=QWEN_MAIN,
            model_family="qwen3",
        ),
        ProviderOption(
            provider_id=DEEPSEEK_MAIN,
            role=ModelRole.MAIN,
            kind=ProviderKind.MODEL,
            display_name="DeepSeek R1 Qwen3 8B",
            model_key=DEEPSEEK_MAIN,
            model_family="qwen3",
        ),
        ProviderOption(
            provider_id=NONE_PROVIDER,
            role=ModelRole.GUARD,
            kind=ProviderKind.NONE,
            display_name="None",
        ),
        ProviderOption(
            provider_id=BUILT_IN_GUARD,
            role=ModelRole.GUARD,
            kind=ProviderKind.BUILT_IN,
            display_name="Built-in Rule / Pattern",
        ),
        ProviderOption(
            provider_id=QWEN3_GUARD,
            role=ModelRole.GUARD,
            kind=ProviderKind.MODEL,
            display_name="Qwen3Guard-Gen 0.6B",
            model_key=QWEN3_GUARD,
            artifact_relative_path=(
                "guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf"
            ),
            artifact_digest_sha512=_QWEN3_GUARD_DIGEST,
            model_family="qwen3guard",
        ),
        ProviderOption(
            provider_id=NONE_PROVIDER,
            role=ModelRole.JUDGE,
            kind=ProviderKind.NONE,
            display_name="None",
        ),
        ProviderOption(
            provider_id=BUILT_IN_JUDGE,
            role=ModelRole.JUDGE,
            kind=ProviderKind.BUILT_IN,
            display_name="Built-in Deterministic",
        ),
        ProviderOption(
            provider_id=SELENE_JUDGE,
            role=ModelRole.JUDGE,
            kind=ProviderKind.MODEL,
            display_name="Selene 1 Mini",
            model_key=SELENE_JUDGE,
            artifact_relative_path=(
                "judge/selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf"
            ),
            artifact_digest_sha512=_SELENE_DIGEST,
            model_family="llama3",
        ),
        ProviderOption(
            provider_id=QWEN_MAIN,
            role=ModelRole.JUDGE,
            kind=ProviderKind.MODEL,
            display_name="Qwen3 4B (self when Main is Qwen)",
            model_key=QWEN_MAIN,
            model_family="qwen3",
        ),
        ProviderOption(
            provider_id=DEEPSEEK_MAIN,
            role=ModelRole.JUDGE,
            kind=ProviderKind.MODEL,
            display_name="DeepSeek R1 Qwen3 8B",
            model_key=DEEPSEEK_MAIN,
            model_family="qwen3",
        ),
    )


class ProviderSelectionController:
    def __init__(
        self,
        *,
        current_main_provider: str = QWEN_MAIN,
        options: tuple[ProviderOption, ...] | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._options = options or default_provider_options()
        self._revision = 1
        self._selections: dict[ModelRole, RoleProviderSelection] = {
            ModelRole.MAIN: RoleProviderSelection(
                role=ModelRole.MAIN,
                configured_provider=current_main_provider,
                active_provider=current_main_provider,
                state=ProviderRuntimeState.ACTIVE,
                independence=ProviderIndependence.SELF,
            ),
            ModelRole.GUARD: RoleProviderSelection(
                role=ModelRole.GUARD,
                configured_provider=QWEN3_GUARD,
                active_provider=None,
                state=ProviderRuntimeState.CONFIGURED,
                independence=ProviderIndependence.INDEPENDENT_OTHER_MODEL,
            ),
            ModelRole.JUDGE: RoleProviderSelection(
                role=ModelRole.JUDGE,
                configured_provider=SELENE_JUDGE,
                active_provider=None,
                state=ProviderRuntimeState.CONFIGURED,
                independence=ProviderIndependence.INDEPENDENT_OTHER_MODEL,
            ),
        }

    def snapshot(self) -> ProviderSelectionSnapshot:
        with self._lock:
            return self._snapshot()

    def select(
        self,
        *,
        role: ModelRole,
        provider_id: str,
        expected_revision: int,
        expected_digest: str,
    ) -> ProviderSelectionSnapshot:
        with self._lock:
            current = self._snapshot()
            if current.revision != expected_revision or current.digest_sha512 != expected_digest:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.REVISION_CONFLICT,
                    safe_message="The provider selection changed; reload and retry.",
                    current_snapshot=current,
                )
            option = self._option(role=role, provider_id=provider_id)
            if option is None:
                if any(item.provider_id == provider_id for item in self._options):
                    code = ProviderSelectionErrorCode.ROLE_MISMATCH
                    message = "The selected provider is not valid for this role."
                else:
                    code = ProviderSelectionErrorCode.UNKNOWN_PROVIDER
                    message = "The selected provider is not registered."
                raise ProviderSelectionError(code=code, safe_message=message)
            if not option.enabled:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.PROVIDER_DISABLED,
                    safe_message="The selected provider is disabled.",
                )
            previous = self._selections[role]
            if previous.configured_provider == provider_id:
                return current
            self._revision += 1
            self._selections[role] = RoleProviderSelection(
                role=role,
                configured_provider=provider_id,
                # Selection never performs an implicit Load or fallback.
                active_provider=(previous.active_provider if role is ModelRole.MAIN else None),
                state=(
                    ProviderRuntimeState.NONE
                    if option.kind is ProviderKind.NONE
                    else ProviderRuntimeState.CONFIGURED
                ),
                independence=self._independence(role=role, option=option),
            )
            return self._snapshot()

    def select_active(
        self,
        *,
        role: ModelRole,
        provider_id: str,
        expected_revision: int,
        expected_digest: str,
    ) -> ProviderSelectionSnapshot:
        """Commit a pre-activated role provider in one externally visible revision.

        This is intentionally only called by the role lifecycle transition.  A
        plain selection remains configured-only and must never load a provider.
        """
        with self._lock:
            current = self._snapshot()
            if current.revision != expected_revision or current.digest_sha512 != expected_digest:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.REVISION_CONFLICT,
                    safe_message="The provider selection changed; reload and retry.",
                    current_snapshot=current,
                )
            option = self._option(role=role, provider_id=provider_id)
            if option is None or not option.enabled:
                raise ProviderSelectionError(
                    code=(
                        ProviderSelectionErrorCode.UNKNOWN_PROVIDER
                        if option is None
                        else ProviderSelectionErrorCode.PROVIDER_DISABLED
                    ),
                    safe_message="The selected provider is unavailable.",
                )
            self._revision += 1
            self._selections[role] = RoleProviderSelection(
                role=role,
                configured_provider=provider_id,
                active_provider=(None if option.kind is ProviderKind.NONE else provider_id),
                state=(
                    ProviderRuntimeState.NONE
                    if option.kind is ProviderKind.NONE
                    else ProviderRuntimeState.ACTIVE
                ),
                independence=self._independence(role=role, option=option),
            )
            return self._snapshot()

    def selection_for(self, role: ModelRole) -> RoleProviderSelection:
        with self._lock:
            return self._selections[role]

    def option_for(self, *, role: ModelRole, provider_id: str) -> ProviderOption | None:
        with self._lock:
            return self._option(role=role, provider_id=provider_id)

    def replace_runtime_state(
        self,
        *,
        role: ModelRole,
        configured_provider: str,
        active_provider: str | None,
        state: ProviderRuntimeState,
        failure_reason: str | None = None,
    ) -> ProviderSelectionSnapshot:
        """Lifecycle-owned atomic projection; refuses stale configured state."""
        with self._lock:
            previous = self._selections[role]
            if previous.configured_provider != configured_provider:
                return self._snapshot()
            option = self._option(role=role, provider_id=configured_provider)
            if option is None:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.UNKNOWN_PROVIDER,
                    safe_message="The configured provider is no longer registered.",
                )
            self._revision += 1
            self._selections[role] = RoleProviderSelection(
                role=role,
                configured_provider=configured_provider,
                active_provider=active_provider,
                state=state,
                independence=self._independence(
                    role=role,
                    option=(
                        (self._option(role=role, provider_id=active_provider) or option)
                        if active_provider is not None
                        else option
                    ),
                ),
                failure_reason=failure_reason,
                failure_at=(datetime.now(UTC).isoformat() if failure_reason is not None else None),
            )
            return self._snapshot()

    def _option(self, *, role: ModelRole, provider_id: str) -> ProviderOption | None:
        return next(
            (
                item
                for item in self._options
                if item.role is role and item.provider_id == provider_id
            ),
            None,
        )

    def _independence(self, *, role: ModelRole, option: ProviderOption) -> ProviderIndependence:
        if option.kind is ProviderKind.NONE:
            return ProviderIndependence.NONE
        if option.kind is ProviderKind.BUILT_IN:
            return ProviderIndependence.BUILT_IN
        if role is ModelRole.MAIN:
            return ProviderIndependence.SELF
        main = self._selections[ModelRole.MAIN].configured_provider
        if option.provider_id == main:
            return ProviderIndependence.SELF
        main_option = self._option(role=ModelRole.MAIN, provider_id=main)
        if main_option is not None and main_option.model_family == option.model_family:
            return ProviderIndependence.INDEPENDENT_SAME_FAMILY
        return ProviderIndependence.INDEPENDENT_OTHER_MODEL

    def _snapshot(self) -> ProviderSelectionSnapshot:
        selections = tuple(self._selections[role] for role in ModelRole)
        return ProviderSelectionSnapshot(
            revision=self._revision,
            digest_sha512=provider_selection_digest(revision=self._revision, selections=selections),
            selections=selections,
            options=self._options,
        )
