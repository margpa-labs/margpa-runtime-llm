"""Real-memory `RoleResourceGatePort` (P9-1 Package 2 OF-P2-003).

2026-09-01 real Incident: activating Selene (Judge) while Main was already
loaded crashed Main and required a Server restart, on this deployment's
16GB unified-memory Mac. Production wired zero Resource Gate before this
Package (`RoleProviderLifecycleManager`'s own default, `AllowAllRole
ResourceGate`, always allows activation) -- nothing stood between a
dedicated-Role activation and whatever the real memory conditions were at
that moment.

The exact backend-level mechanism was never conclusively isolated (the
Package 2 Return's leading hypothesis is a shared Apple Silicon
llama.cpp/Metal backend interaction; a second, independently plausible
mechanism -- and the one this Gate directly targets -- is a genuine OOM: a
real dev Mac running other work alongside the server can have only a few
GB of *actually available* memory at the moment Selene's ~5.7GB Q5
Artifact is requested on top of an already-resident Main model. This Gate
does not claim to resolve which mechanism fired in the original Incident;
it targets the one it can concretely observe and refuse against --
insufficient *real* available memory -- with a typed, safe refusal instead
of letting Load proceed into an unknown-safety condition.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

import psutil  # type: ignore[import-untyped]

from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    QWEN_MAIN,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderKind,
    ProviderOption,
)
from margpa_runtime_llm.modules.runtime_model_control.ports import ModelDefinitionResolverPort

# Reserved headroom (OS + server process + KV cache + general overhead)
# on top of the two Artifacts' own declared file sizes. A documented,
# round heuristic -- not a precise per-architecture KV-cache computation
# (no per-model KV-cache metadata is tracked in the Registry today).
# Deliberately conservative: this Gate's purpose is destruction
# prevention, not maximizing how often concurrent Load is permitted.
ROLE_MEMORY_SAFETY_MARGIN_BYTES = 3 * 1024**3

_MAIN_SHARED_JUDGE_PROVIDER_IDS = frozenset({QWEN_MAIN, DEEPSEEK_MAIN})

_logger = logging.getLogger(__name__)


def real_available_memory_bytes() -> int:
    """Real, current, point-in-time available memory (`psutil`, an
    existing project dependency -- no new install)."""
    return int(psutil.virtual_memory().available)


class SystemMemoryRoleResourceGate:
    """`RoleResourceGatePort`: refuses a dedicated (`ProviderKind.MODEL`)
    Judge/Guard Role activation whose declared Artifact size, combined
    with an already-ACTIVE Main model's own declared Artifact size plus
    `safety_margin_bytes`, would exceed real available memory at the
    moment of activation.

    Deliberately scoped to *only* the Main-genuinely-ACTIVE case -- the
    exact shape of the 2026-09-01 Incident and P2-WU-03's own wording
    ("Selene切替後のMain Load破壊防止"). When Main is not currently ACTIVE
    (`_active_main_bytes()` returns 0), this Gate allows unconditionally
    without even resolving the candidate's own size: a lone dedicated-Role
    Load (no Main concurrently resident) is the pre-Package-2 baseline
    behavior, already real-hardware-proven safe on this exact hardware
    (Package 2 Return §6, Selene/Gemma each 3/3 standalone) -- this Gate
    must never regress that already-working case by applying a Main+
    Dedicated-shaped margin to a Load that has no Main to collide with.

    An explicit Main-shared Judge selection (`QWEN_MAIN`/`DEEPSEEK_MAIN`
    chosen as the JUDGE Role's Provider) is always allowed unconditionally
    -- it never loads a second concurrent copy of a Main-sized model
    (`MainSharedJudgeRoleAdapter.load()` is a no-op; mirrors
    `ProductionRoleAdapterFactory.create()`'s own dispatch for that exact
    pair of provider_ids) and so can never contribute to the risk this
    Gate exists for.

    Any internal fault (a Definition that fails to resolve, a memory
    probe that raises) fails OPEN -- this Gate can only ever be more
    restrictive than the pre-Package-2 baseline (`AllowAllRoleResourceGate`)
    on its success path, never less available due to its own error."""

    def __init__(
        self,
        *,
        definitions: ModelDefinitionResolverPort,
        runtime_model_control_ref: list[RuntimeModelController | None],
        safety_margin_bytes: int = ROLE_MEMORY_SAFETY_MARGIN_BYTES,
        available_memory_probe: Callable[[], int] = real_available_memory_bytes,
    ) -> None:
        self._definitions = definitions
        self._runtime_model_control_ref = runtime_model_control_ref
        self._safety_margin_bytes = safety_margin_bytes
        self._available_memory_probe = available_memory_probe

    def allow_activation(
        self, *, role: ModelRole, option: ProviderOption
    ) -> tuple[bool, str | None]:
        try:
            return self._allow_activation(role=role, option=option)
        except Exception:
            # Fail-open (see class docstring), but not silently: an
            # internal fault here means this Gate's own destruction-
            # prevention check did not actually run for this activation,
            # which is worth a trace even though the request itself
            # still proceeds exactly as the pre-Package-2 baseline would.
            _logger.warning(
                "SystemMemoryRoleResourceGate failed open for provider_id=%r "
                "(internal error, activation allowed unconditionally)",
                option.provider_id,
                exc_info=True,
            )
            return True, None

    def _allow_activation(
        self, *, role: ModelRole, option: ProviderOption
    ) -> tuple[bool, str | None]:
        del role
        if option.kind is not ProviderKind.MODEL:
            return True, None
        if option.provider_id in _MAIN_SHARED_JUDGE_PROVIDER_IDS:
            return True, None
        main_bytes = self._active_main_bytes()
        if main_bytes == 0:
            return True, None
        if option.model_key is None:
            return True, None
        candidate_bytes = self._definition_size_bytes(option.model_key)
        if candidate_bytes is None:
            return True, None
        available = self._available_memory_probe()
        required = candidate_bytes + main_bytes + self._safety_margin_bytes
        if required > available:
            return False, "resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role"
        return True, None

    def _definition_size_bytes(self, model_key: str) -> int | None:
        try:
            return self._definitions.resolve(model_key=model_key).artifact.size_bytes
        except Exception:
            return None

    def _active_main_bytes(self) -> int:
        controller = self._runtime_model_control_ref[0]
        if controller is None:
            return 0
        snapshot = controller.snapshot()
        if snapshot.runtime_state is not RuntimeState.ACTIVE:
            return 0
        return self._definition_size_bytes(snapshot.selected_model_key) or 0


__all__ = [
    "ROLE_MEMORY_SAFETY_MARGIN_BYTES",
    "SystemMemoryRoleResourceGate",
    "real_available_memory_bytes",
]
