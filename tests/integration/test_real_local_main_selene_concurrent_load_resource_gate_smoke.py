"""P9-1 Package 2 OF-P2-003/OF-P2-006/OF-P2-007 real-hardware evidence:
`SystemMemoryRoleResourceGate`'s decision, against real Registry-declared
Artifact sizes and a real, live `psutil.virtual_memory()` reading on this
deployment Mac, for every real Main x dedicated-Role combination the
Provider Catalog actually exposes.

Deliberately does NOT load any real Model. The fixture-level tests in
`tests/unit/adapters/runtime_model_control/test_memory_resource_gate.py`
already prove the Gate's arithmetic/wiring with fake inputs; every
standalone real Load (Selene, Gemma, Qwen3Guard, Main) is already proven
in the Package 2 Return (§6, 3/3 each) and is not repeated here (no
redundant reruns of an already-passing real Load).

This test's only job: with real Registry-declared Artifact sizes and a
real, live, unstubbed memory reading, does the Gate produce a
well-formed, internally consistent decision for *every* real Main
(Qwen 4B / DeepSeek 8B) x dedicated Role (Selene, Gemma, Qwen3Guard)
combination -- an exhaustive 2x3 matrix over the Provider Catalog's
entire actual MODEL-kind surface, not a single spot-checked pair.

History of what this matrix caught (own honest record, not a claim about
the Gate's correctness -- the Gate has behaved exactly as designed the
whole time; what changed is how thoroughly its consequences were checked
before "done" was declared):

- Qwen 4B + Selene: the pair implicated in the 2026-09-01 Incident itself
  (OF-P2-003).
- Qwen 4B + Gemma: found only after the User asked Claude to re-check
  Package 2's own already-shipped 8-item Fresh-default-Judge contract
  against this new Gate (OF-P2-006) -- missed by the original two-round
  Internal Review, because that Review checked the new Gate's own
  correctness/safety but never cross-checked it against every
  already-shipped feature it could interact with.
- DeepSeek 8B + Qwen3Guard: found only when this matrix was made
  genuinely exhaustive over the full Catalog, rather than re-checking one
  more pair the User happened to name (OF-P2-007).

Current disposition for all of the above (User, 2026-09-02): keep the
Gate/margin exactly as implemented, no Source change, revisit later. This
Test records the real numbers each combination actually produces so that
revisit has real, re-runnable Evidence to start from rather than a
one-off script's output.

P9-1 SSS Recovery (2026-09-03, targeted repair): `SystemMemoryRoleResourceGate`
was found wired into `bootstrap/web_application.py`'s Production Composition
Root and denying ordinary Main+Gemma/Main+Qwen3Guard activation outright --
see docs/project/shared/history/ai_system_anomalies/claude_code/
claude_code_sss_resource_gate_foundation_destruction_and_resource_exhaustion_incident_ja_20260903001814.md.
That wiring has been removed; Production now uses `RoleProviderLifecycleManager`'s
own `AllowAllRoleResourceGate` default. This file's own `independently_expected_
allow` oracle recomputes this Gate's own `required`/`available` arithmetic --
by design (see module docstring above), so a Green result here proves only
that this now-unwired class is internally self-consistent against real
Registry sizes and a real live memory reading. It is NOT evidence that any
real Main+dedicated-Role activation is denied in Production, and must not be
read as such -- Production behavior for that is proven by
`tests/unit/web/test_web_cli.py::
test_web_runtime_never_gates_dedicated_role_activation_on_a_memory_estimate`
and by real-Load Evidence, not by this file. `memory_resource_gate.py` and
this Test are kept as Incident Evidence / Quarantined-Unused, not deleted;
final disposition (delete vs. redesign vs. keep dormant) is a Controller
decision.
"""

from __future__ import annotations

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_model_control.memory_resource_gate import (
    ROLE_MEMORY_SAFETY_MARGIN_BYTES,
    SystemMemoryRoleResourceGate,
    real_available_memory_bytes,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderKind,
    ProviderOption,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_MAIN_CANDIDATES = ((QWEN_MAIN, "Qwen4B"), (DEEPSEEK_MAIN, "DeepSeek8B"))
_DEDICATED_CANDIDATES = (
    (SELENE_JUDGE, ModelRole.JUDGE, "Selene", "OF-P2-003"),
    (GEMMA_E2B_JUDGE, ModelRole.JUDGE, "Gemma", "OF-P2-006"),
    (QWEN3_GUARD, ModelRole.GUARD, "Qwen3Guard", "OF-P2-007"),
)


class _FakeMainSnapshot:
    def __init__(self, *, selected_model_key: str) -> None:
        self.selected_model_key = selected_model_key
        self.runtime_state = RuntimeState.ACTIVE


class _FakeActiveMainController:
    """Reports Main as genuinely ACTIVE with a real `model_key` -- stands
    in for a real, loaded `RuntimeModelController` without this Test
    itself paying for a real Main Load (that real Load path is already
    covered by Package 2's own Real Model Smoke; this Test isolates the
    Gate's own decision)."""

    def __init__(self, *, selected_model_key: str) -> None:
        self._snapshot = _FakeMainSnapshot(selected_model_key=selected_model_key)

    def snapshot(self) -> _FakeMainSnapshot:
        return self._snapshot


def _matrix_id(value: object) -> str:
    return str(value)


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6/9 model smoke requires Apple Silicon",
)
@pytest.mark.parametrize("main_provider_id,main_display_name", _MAIN_CANDIDATES, ids=_matrix_id)
@pytest.mark.parametrize(
    "candidate_provider_id,candidate_role,candidate_display_name,finding_label",
    _DEDICATED_CANDIDATES,
    ids=_matrix_id,
)
def test_gate_decision_matches_real_registry_and_real_memory_for_every_main_and_dedicated_role(
    main_provider_id: str,
    main_display_name: str,
    candidate_provider_id: str,
    candidate_role: ModelRole,
    candidate_display_name: str,
    finding_label: str,
) -> None:
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    candidate_bytes = definitions.resolve(model_key=candidate_provider_id).artifact.size_bytes
    main_bytes = definitions.resolve(model_key=main_provider_id).artifact.size_bytes
    assert candidate_bytes > 0
    assert main_bytes > 0

    gate = SystemMemoryRoleResourceGate(
        definitions=definitions,
        runtime_model_control_ref=[
            _FakeActiveMainController(selected_model_key=main_provider_id)  # type: ignore[list-item]
        ],
    )
    option = ProviderOption(
        provider_id=candidate_provider_id,
        role=candidate_role,
        kind=ProviderKind.MODEL,
        display_name=candidate_display_name,
        model_key=candidate_provider_id,
    )
    allowed, reason = gate.allow_activation(role=candidate_role, option=option)

    available_bytes = real_available_memory_bytes()
    required_bytes = candidate_bytes + main_bytes + ROLE_MEMORY_SAFETY_MARGIN_BYTES
    independently_expected_allow = required_bytes <= available_bytes

    print(
        f"\n{finding_label} real-hardware Gate Evidence "
        f"(Main={main_provider_id} {main_bytes} bytes, "
        f"{candidate_display_name}={candidate_provider_id} {candidate_bytes} bytes, "
        f"margin={ROLE_MEMORY_SAFETY_MARGIN_BYTES} bytes, required={required_bytes} bytes, "
        f"real_available={available_bytes} bytes): "
        f"allowed={allowed} reason={reason}"
    )

    assert allowed is independently_expected_allow
    if allowed:
        assert reason is None
    else:
        assert reason is not None and reason.startswith("resource_gate_denied:")
