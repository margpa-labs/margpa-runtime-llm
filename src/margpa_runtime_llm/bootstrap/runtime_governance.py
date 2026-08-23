"""Composition root for Phase 4 Main Runtime Governance.

Reads the Definition Package once via the same Filesystem Provider Phase
3 already exposes (`FilesystemDefinitionProvider`) — a legitimate
independent consumer of the Provider Port, not a second re-read of
Runtime-internal state (P3-CODEX-007 constrains the *Runtime's own*
Observe pipeline re-reading what it already verified, not other
independent callers of the same Port using their own single verified
read). Definitions absent, unsupported, or a Provider failure never
blocks Main Model Runtime (P4-GD-005) — this module falls back to an
empty Descriptor set rather than raising, but the *reason* the set is
empty (Provider absent vs. failure vs. an Invalid/Quarantined Bundle) is
preserved as a Typed state (P4-CODEX-004 Rework) rather than collapsed
into one indistinguishable empty tuple.

`RuntimeGovernanceComposition` holds every process-local component
`main_model.pre`/`post` needs. `authority`/`policy`/`budget`/the Action
Registry are fixed local defaults for this MVP — a future Phase can make
them Configuration-driven without changing this module's external shape
(P4-COM-004 Capability Snapshot/Adapter isolation).
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.adapters.runtime_governance.deterministic_evaluator import (
    DeterministicEvaluator,
)
from margpa_runtime_llm.adapters.runtime_governance.reference_definition_adapter import (
    build_argd_dagd_descriptors,
)
from margpa_runtime_llm.adapters.runtime_governance.registered_actions import LocalActionAdapter
from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_reference_bundle_adapter_registry,
)
from margpa_runtime_llm.modules.audit_evidence.domain import (
    SafeExecutedActionRecord,
    SafeObservationRecord,
    SafeRecommendedActionRecord,
)
from margpa_runtime_llm.modules.audit_evidence.governance_observation import (
    GovernanceObserverPort,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    CompilerInput,
    DefinitionState,
    DigestedNormalizedGovernanceDefinition,
    compile_plan,
    digest_ir,
    plan_digest_sha512,
)
from margpa_runtime_llm.modules.governance_definitions.ports import (
    PackageLoadRequest,
    PackageSourceResult,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    BoundGovernancePlanCache,
    GovernancePointRuntime,
    MainGovernanceModeController,
    bind,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    resolve_actions as _resolve_actions,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    MAIN_MODEL_PRE_POINT_ID,
    STAGE_POST,
    STAGE_PRE,
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BoundGovernancePlan,
    BudgetSnapshot,
    ExecutedAction,
    ExecutionDescriptor,
    ExecutionState,
    PolicySnapshot,
    RecommendedAction,
    RuntimeCapabilitySnapshot,
    StandardGovernanceResult,
)
from margpa_runtime_llm.modules.runtime_governance.ports import ActionAdapterPort

logger = logging.getLogger(__name__)

_ARGD_DAGD_SOURCE_ID = "argd_v0.3.1_en_dagd_v0.4.4_en"


@dataclass(frozen=True, slots=True)
class ReferenceDescriptorLoadResult:
    """Typed outcome of the single independent Reference Bundle read
    (P4-CODEX-004): `state` distinguishes *why* `descriptors` may be
    empty, so a Binding's `unavailable_reason_code` never collapses
    "nothing configured" and "something was there but invalid" into the
    same opaque signal (Codex Required Correction §5)."""

    descriptors: tuple[ExecutionDescriptor, ...]
    state: str
    """One of `loaded` / `no_provider` / `provider_failure` /
    `invalid_bundle`. `loaded` means the Provider was reachable and the
    requested Source (if any) verified — `descriptors` may still be
    empty in that case (a verified but content-less Source)."""
    reason_code: str | None
    """Populated whenever `state != "loaded"`; `None` otherwise."""
    source_plan_id: str | None = None
    """The real Phase 3 Unbound `CompiledPlan.compiled_plan_id` this read
    also produced (P4-CODEX-008) — `None` whenever `state != "loaded"`,
    or when Plan compilation itself failed even though Descriptors were
    still extracted (P4-GD-005: a Plan-compilation fault never blocks
    Descriptor extraction; it only leaves the Binding non-Executable via
    the `no_source_plan` reason)."""
    source_plan_digest_sha512: str | None = None
    """Digest of the same `CompiledPlan`; `None` under the same
    conditions as `source_plan_id`."""


def _compile_reference_source_plan(
    result: PackageSourceResult,
    *,
    capability: RuntimeCapabilitySnapshot,
    authority: AuthoritySnapshot,
) -> tuple[str | None, str | None]:
    """Reuses the SAME verified read `load_reference_descriptors` already
    performed (never a second disk read, P3-CODEX-007) to also produce a
    real Phase 3 Trusted Adapter -> Normalized IR -> `compile_plan()`
    Unbound Plan Identity for the ARGD/DAGD source (P4-CODEX-008) — a
    Binding must trace back to a genuine Source Plan, never a hardcoded
    `None`. Never raises: any failure here leaves Descriptor extraction
    itself untouched (P4-GD-005); the caller just gets `(None, None)` and
    the resulting Binding stays non-Executable via `no_source_plan`."""

    manifest = result.manifest
    if manifest is None:
        return None, None
    try:
        definition_states = {entry.definition_id: entry.state for entry in result.definition_states}
        sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}
        registry = build_reference_bundle_adapter_registry()
        digested_irs: list[DigestedNormalizedGovernanceDefinition] = []
        for definition in manifest.definition_entries:
            if definition.source_id != _ARGD_DAGD_SOURCE_ID:
                continue
            if definition_states.get(definition.definition_id) is not DefinitionState.VALIDATED:
                continue
            source_entry = sources_by_id.get(definition.source_id)
            if source_entry is None:
                continue
            adapter = registry.resolve(
                schema_id=source_entry.schema_id,
                adapter_id=source_entry.trusted_adapter_id,
                source_media_type=source_entry.media_type,
            )
            if adapter is None:
                continue
            source_json = result.verified_source_json.get(source_entry.source_id)
            if source_json is None:
                continue
            ir = adapter.normalize(
                source_json=source_json, source_entry=source_entry, definition_entry=definition
            )
            digested_irs.append(digest_ir(ir))
        if not digested_irs:
            return None, None
        compiler_input = CompilerInput(
            normalized_ir_refs=tuple(d.ir.ir_id for d in digested_irs),
            normalized_ir_digests=tuple(d.ir_digest_sha512 for d in digested_irs),
            runtime_capability_snapshot_digest=capability.digest_sha512,
            authority_snapshot_digest=authority.digest_sha512,
        )
        plan = compile_plan(compiler_input=compiler_input, definitions=tuple(digested_irs))
        return plan.compiled_plan_id, plan_digest_sha512(plan)
    except Exception:
        logger.warning("runtime_governance: source plan compilation failed", exc_info=True)
        return None, None


def load_reference_descriptors(
    *,
    definitions_root: Path | None,
    capability: RuntimeCapabilitySnapshot,
    authority: AuthoritySnapshot,
) -> ReferenceDescriptorLoadResult:
    """Independently reads the Definition Package (if any) and extracts
    the ARGD/DAGD Trusted Adapter's Descriptors. Never raises — any
    absence/failure is returned as a Typed non-`loaded` state with an
    empty Descriptor tuple (P4-GD-005)."""

    if definitions_root is None:
        return ReferenceDescriptorLoadResult((), "no_provider", "no_definitions_root_configured")
    try:
        provider = FilesystemDefinitionProvider(root=definitions_root)
        result = provider.load_package(PackageLoadRequest())
    except Exception:
        logger.warning("runtime_governance: reference bundle provider failed", exc_info=True)
        return ReferenceDescriptorLoadResult((), "provider_failure", "provider_load_failed")
    if not result.found:
        return ReferenceDescriptorLoadResult((), "no_provider", "package_not_found")
    content = result.verified_source_json.get(_ARGD_DAGD_SOURCE_ID)
    if content is None:
        # The Source either never existed in the Manifest, or existed but
        # failed digest/structural verification (Quarantined) — either
        # way it never reached `verified_source_json` (P3-CODEX-007), so
        # Phase 4 must not fabricate its content. Distinguished from
        # `no_provider`/`provider_failure` because a Package *was*
        # readable, just without a *valid* Reference Bundle inside it.
        return ReferenceDescriptorLoadResult((), "invalid_bundle", "source_not_verified")
    source_plan_id, source_plan_digest_sha512 = _compile_reference_source_plan(
        result, capability=capability, authority=authority
    )
    return ReferenceDescriptorLoadResult(
        build_argd_dagd_descriptors(content),
        "loaded",
        None,
        source_plan_id=source_plan_id,
        source_plan_digest_sha512=source_plan_digest_sha512,
    )


def _default_registry_entries() -> dict[str, ActionRegistryEntry]:
    # Phase 4 MVP registers only the two Actions a real Caller inspects
    # and acts on (P4-CODEX-006 Rework) — `constrain_generation_config`
    # is deliberately *not* registered (no Caller applies a Config Patch
    # yet); `warn` is registered because its real effect is projection
    # into the Evidence/Status pipeline, not a Model-facing mutation.
    return {
        ActionId.WARN.value: ActionRegistryEntry(
            action_id=ActionId.WARN,
            allowed_points=(MAIN_MODEL_PRE_POINT_ID, MAIN_MODEL_POST_POINT_ID),
            allowed_stages=(STAGE_PRE, STAGE_POST),
            side_effect_class="evidence_status_projection",
        ),
        ActionId.STOP_BEFORE_GENERATION.value: ActionRegistryEntry(
            action_id=ActionId.STOP_BEFORE_GENERATION,
            allowed_points=(MAIN_MODEL_PRE_POINT_ID,),
            allowed_stages=(STAGE_PRE,),
            side_effect_class="local",
        ),
        ActionId.REJECT_OUTPUT.value: ActionRegistryEntry(
            action_id=ActionId.REJECT_OUTPUT,
            allowed_points=(MAIN_MODEL_POST_POINT_ID,),
            allowed_stages=(STAGE_POST,),
            side_effect_class="local",
        ),
    }


def default_authority() -> AuthoritySnapshot:
    """Deterministic, standalone from `RuntimeGovernanceComposition` so a
    Composition Root caller can compute the same Authority *before* the
    Composition exists (P4-CODEX-008) — `load_reference_descriptors()`
    needs `authority.digest_sha512` as a `CompilerInput` input, but is
    itself called before `RuntimeGovernanceComposition.__init__` runs.
    Both call sites produce a byte-identical `AuthoritySnapshot` by
    construction, without an actual circular dependency."""
    registered = tuple(entry.action_id.value for entry in _default_registry_entries().values())
    return AuthoritySnapshot(authority_revision=1, granted_action_ids=registered)


class RuntimeGovernanceComposition:
    def __init__(
        self,
        *,
        capability: RuntimeCapabilitySnapshot,
        descriptors: tuple[ExecutionDescriptor, ...] = (),
        descriptor_unavailable_reason_code: str | None = None,
        source_plan_id: str | None = None,
        source_plan_digest_sha512: str | None = None,
    ) -> None:
        self.capability = capability
        self._capability_lock = threading.Lock()
        self.descriptors = descriptors
        # Only meaningful when `descriptors` is empty; `None` means "no
        # descriptors, no further diagnostic" (`bind()` falls back to a
        # generic reason in that case).
        self.descriptor_unavailable_reason_code = descriptor_unavailable_reason_code
        # The real Phase 3 Unbound Plan Identity behind `descriptors`
        # (P4-CODEX-008) — `None` unless a caller (the Composition Root,
        # via `load_reference_descriptors()`) established one from the
        # same verified Package read; non-empty Descriptors without this
        # keep the Binding non-Executable (`no_source_plan`).
        self.source_plan_id = source_plan_id
        self.source_plan_digest_sha512 = source_plan_digest_sha512
        self.policy = PolicySnapshot(policy_revision=1, profile="core")
        self.budget = BudgetSnapshot(
            max_calls_per_invocation=0,
            max_latency_ms=60_000,
            max_snapshot_chars=200_000,
            allowed_generation_config_fields=("thinking_mode",),
        )
        self.authority = default_authority()
        self.action_registry_snapshot = ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=self.authority.granted_action_ids
        )
        self._registry_entries = _default_registry_entries()
        adapter = LocalActionAdapter()
        self._adapters: dict[str, ActionAdapterPort] = dict.fromkeys(
            self._registry_entries, adapter
        )
        self.plan_cache = BoundGovernancePlanCache()
        self.point_runtime = GovernancePointRuntime(evaluator=DeterministicEvaluator())
        # Last observed Result per Point — Best-effort, Process-local Safe
        # Status source (P4-STS-001). Never a second Evaluation: hooks
        # record whatever Result they already computed for their own
        # Stop/Reject decision, exactly once (P4-CODEX-003 §"同じResultを
        # 2回評価しない").
        self._last_results: dict[str, StandardGovernanceResult] = {}
        self._last_results_lock = threading.Lock()
        # Set by the Composition Root after construction, once the
        # Observer itself is built (it needs `mode_controller`, which
        # only exists once this Composition does) — read by the Status
        # route to surface `governance_observer.status()` (P4-STS-001).
        self.governance_observer: GovernanceObserverPort | None = None
        # P4-CODEX-007: an Observer interaction fault (`is_active()` or
        # any `observe_*` call raising) must be visible in Process-local
        # Degraded Status, not merely logged — distinct from the
        # Observer's own self-reported `status().degraded` (a Store
        # Write failure it already catches itself), since this instead
        # tracks faults in the *interaction* with the Observer/Port
        # itself, which the Observer cannot self-report if it is what
        # actually raised.
        self._observer_interaction_degraded = False
        self._observer_interaction_degraded_lock = threading.Lock()
        # `enforce_ready` is computed from a real trial Bind (not
        # hardcoded) — it reflects this Composition's actual Descriptor/
        # Registry/Authority state, not an assumption about what a fixed
        # MVP default table always looks like (P4-MOD-004). With zero
        # Descriptors (Definitions-0 Baseline or an Invalid Bundle) the
        # trial Bind is correctly non-executable, so `enforce_ready` is
        # `False` and the Mode Controller reports ENFORCE unavailable —
        # matching `Definitions 0 + enforce: unsupported` (P4-CODEX-004).
        self.mode_controller = MainGovernanceModeController(
            enforce_ready=self.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID).executable
        )

    def rebind_capability(self, *, capability: RuntimeCapabilitySnapshot) -> None:
        """P6-CODEX-036 (Fifth Rework): updates the live Capability
        `bind_point()` reads on every real Attempt (Pre/Post Hook
        invocation) — closes the gap where a Runtime Model
        Switch/Context Reload updated `RuntimeModelController`'s own
        Snapshot but left this Composition's Capability frozen at
        whatever Model was loaded at Bootstrap. The wiring caller
        (`web_application.py`) invokes this only from `RuntimeModel
        Controller`'s own `on_commit` hook — i.e. only after a Switch/
        Reload has already fully committed — so a rolled-back or failed
        attempt never reaches here and this Composition's Capability
        stays paired with whatever Model Snapshot is actually current.
        `bind_point()` reads `self.capability` fresh on every call (no
        separate cache to invalidate here): `plan_cache` is keyed by
        `binding_digest_sha512`, which already incorporates
        `capability.digest_sha512`, so a genuine Capability change
        naturally misses the old cache entry rather than reusing it."""
        with self._capability_lock:
            self.capability = capability

    def bind_point(self, *, point_id: str) -> BoundGovernancePlan:
        plan = bind(
            point_id=point_id,
            source_plan_id=self.source_plan_id,
            source_plan_digest_sha512=self.source_plan_digest_sha512,
            descriptors=self.descriptors,
            capability=self.capability,
            authority=self.authority,
            policy=self.policy,
            budget=self.budget,
            action_registry=self.action_registry_snapshot,
            descriptor_unavailable_reason_code=self.descriptor_unavailable_reason_code,
        )
        cached = self.plan_cache.get(plan.binding_digest_sha512)
        if cached is not None:
            return cached
        self.plan_cache.put(plan)
        return plan

    def resolver_for(
        self, *, point_id: str, stage: str, binding: BoundGovernancePlan
    ) -> Callable[[tuple[RecommendedAction, ...]], tuple[ExecutedAction, ...]]:
        def _resolve(
            recommended: tuple[RecommendedAction, ...],
        ) -> tuple[ExecutedAction, ...]:
            return _resolve_actions(
                recommended_actions=recommended,
                point_id=point_id,
                stage=stage,
                mode="enforce",
                binding=binding,
                capability=self.capability,
                authority=self.authority,
                policy=self.policy,
                budget=self.budget,
                action_registry=self.action_registry_snapshot,
                registry=self._registry_entries,
                adapters=self._adapters,
            )

        return _resolve

    def record_result(self, *, point_id: str, result: StandardGovernanceResult) -> None:
        with self._last_results_lock:
            self._last_results[point_id] = result

    def mark_observer_interaction_degraded(self) -> None:
        with self._observer_interaction_degraded_lock:
            self._observer_interaction_degraded = True

    def observer_interaction_degraded(self) -> bool:
        with self._observer_interaction_degraded_lock:
            return self._observer_interaction_degraded

    def last_result_for(self, *, point_id: str) -> StandardGovernanceResult | None:
        with self._last_results_lock:
            return self._last_results.get(point_id)


_VALID_MODES = frozenset({"off", "observe", "enforce"})


def _safe_mode(mode_provider: Callable[[], str]) -> str:
    """Never guesses `off` for an Unknown/Unreadable Mode (P4-CODEX-005):
    a Mode Provider exception or an unrecognized value returns the
    distinct `mode_unavailable` sentinel, which the Hooks below route to
    a Fail-closed Safe Stop/Reject — never silently identical to a
    genuine, intentional `off`."""
    try:
        mode = mode_provider()
    except Exception:
        logger.warning("runtime_governance: mode provider raised", exc_info=True)
        return "mode_unavailable"
    return mode if mode in _VALID_MODES else "mode_unavailable"


def _pre_snapshot(request: GenerationRequest) -> str:
    defaults = GenerationParameters()
    changed_fields = [
        field_name
        for field_name in type(defaults).model_fields
        if getattr(request.parameters, field_name) != getattr(defaults, field_name)
    ]
    total_chars = sum(len(message.content) for message in request.messages)
    return json.dumps(
        {
            "message_count": len(request.messages),
            "total_chars": total_chars,
            "generation_config_fields": changed_fields,
        }
    )


def _observer_active(
    composition: RuntimeGovernanceComposition, governance_observer: GovernanceObserverPort | None
) -> bool:
    if governance_observer is None:
        return False
    try:
        return governance_observer.is_active()
    except Exception:
        logger.warning("runtime_governance: evidence observer is_active() failed", exc_info=True)
        # P4-CODEX-007: an Observer interaction fault must be visible in
        # Process-local Degraded Status, not merely logged.
        composition.mark_observer_interaction_degraded()
        return False


def _observe_started(
    composition: RuntimeGovernanceComposition,
    governance_observer: GovernanceObserverPort | None,
    *,
    invocation_id: str,
    point_id: str,
    stage: str,
    mode: str,
) -> None:
    if governance_observer is None:
        return
    try:
        governance_observer.observe_point_started(
            invocation_id=invocation_id, point_id=point_id, stage=stage, mode=mode
        )
    except Exception:
        logger.warning("runtime_governance: evidence observe_point_started failed", exc_info=True)
        composition.mark_observer_interaction_degraded()


def _safe_observations(result: StandardGovernanceResult) -> tuple[SafeObservationRecord, ...]:
    return tuple(
        SafeObservationRecord(
            descriptor_id=observation.descriptor_id,
            outcome=observation.outcome.value,
            detail_code=observation.detail_code,
            severity=observation.severity.value,
        )
        for observation in result.observations
    )


def _safe_recommended_actions(
    result: StandardGovernanceResult,
) -> tuple[SafeRecommendedActionRecord, ...]:
    return tuple(
        SafeRecommendedActionRecord(
            action_id=action.action_id,
            reason_descriptor_id=action.reason_descriptor_id,
            severity=action.severity.value,
        )
        for action in result.recommended_actions
    )


def _safe_executed_actions(
    result: StandardGovernanceResult,
) -> tuple[SafeExecutedActionRecord, ...]:
    return tuple(
        SafeExecutedActionRecord(
            action_id=action.action_id,
            executed=action.executed,
            intervening=action.intervening,
            not_executed_reason_code=action.not_executed_reason_code,
        )
        for action in result.executed_actions
    )


def _observe_terminal_from_result(
    composition: RuntimeGovernanceComposition,
    governance_observer: GovernanceObserverPort | None,
    *,
    invocation_id: str,
    result: StandardGovernanceResult,
    binding: BoundGovernancePlan | None,
) -> None:
    if governance_observer is None:
        return
    try:
        governance_observer.observe_point_terminal(
            invocation_id=invocation_id,
            point_id=result.point_id,
            stage=result.stage,
            mode=result.mode,
            execution_state=result.execution_state.value,
            severity=result.severity.value,
            selected_descriptor_ids=result.selected_descriptor_ids,
            observations=_safe_observations(result),
            recommended_actions=_safe_recommended_actions(result),
            executed_actions=_safe_executed_actions(result),
            unavailable_reason_code=result.unavailable_reason_code,
            degraded_reason_code=result.degraded_reason_code,
            # P4-CODEX-007/008: traces this Evidence back to the exact
            # Binding (and, transitively, Source Plan) that produced it —
            # `None` when no Binding was involved (observe/off/pre-Bind
            # failure), never fabricated.
            binding_digest_sha512=(binding.binding_digest_sha512 if binding is not None else None),
            source_plan_id=(binding.source_plan_id if binding is not None else None),
            source_plan_digest_sha512=(
                binding.source_plan_digest_sha512 if binding is not None else None
            ),
            capability_snapshot_digest_sha512=composition.capability.digest_sha512,
            authority_snapshot_digest_sha512=composition.authority.digest_sha512,
            policy_snapshot_digest_sha512=composition.policy.digest_sha512,
            budget_snapshot_digest_sha512=composition.budget.digest_sha512,
            action_registry_digest_sha512=composition.action_registry_snapshot.digest_sha512,
            latency_ms=result.latency_ms,
            call_count=result.call_count,
        )
    except Exception:
        logger.warning("runtime_governance: evidence observe_point_terminal failed", exc_info=True)
        composition.mark_observer_interaction_degraded()


def _observe_terminal_degraded(
    composition: RuntimeGovernanceComposition,
    governance_observer: GovernanceObserverPort | None,
    *,
    invocation_id: str,
    point_id: str,
    stage: str,
    mode: str,
    degraded_reason_code: str,
) -> None:
    if governance_observer is None:
        return
    try:
        governance_observer.observe_point_terminal(
            invocation_id=invocation_id,
            point_id=point_id,
            stage=stage,
            mode=mode,
            execution_state="degraded",
            severity="none",
            selected_descriptor_ids=(),
            observations=(),
            recommended_actions=(),
            executed_actions=(),
            unavailable_reason_code=None,
            degraded_reason_code=degraded_reason_code,
            binding_digest_sha512=None,
            source_plan_id=None,
            source_plan_digest_sha512=None,
            capability_snapshot_digest_sha512=composition.capability.digest_sha512,
            authority_snapshot_digest_sha512=composition.authority.digest_sha512,
            policy_snapshot_digest_sha512=composition.policy.digest_sha512,
            budget_snapshot_digest_sha512=composition.budget.digest_sha512,
            action_registry_digest_sha512=composition.action_registry_snapshot.digest_sha512,
            latency_ms=0,
            call_count=0,
        )
    except Exception:
        logger.warning("runtime_governance: evidence observe_point_terminal failed", exc_info=True)
        composition.mark_observer_interaction_degraded()


def _mode_unavailable_result(
    *, invocation_id: str, point_id: str, stage: str, mode: str
) -> StandardGovernanceResult:
    """P4-CODEX-007: the Mode Provider Unreadable path Fail-closes the
    Stop/Reject decision correctly, but previously recorded nothing at
    all into Last Result/Evidence — this Typed synthetic Degraded Result
    makes that state visible on the same Process-local Status/Evidence
    surfaces every other path already uses, rather than a silent gap."""
    return StandardGovernanceResult(
        invocation_id=invocation_id,
        point_id=point_id,
        stage=stage,
        mode=mode,
        execution_state=ExecutionState.DEGRADED,
        degraded_reason_code="mode_provider_unavailable",
        latency_ms=0,
        call_count=0,
    )


def build_main_model_governance_hooks(
    *,
    composition: RuntimeGovernanceComposition,
    mode_provider: Callable[[], str],
    governance_observer: GovernanceObserverPort | None = None,
) -> tuple[
    Callable[[GenerationRequest], tuple[bool, str]],
    Callable[[str], tuple[bool, str]],
]:
    """Builds the plain `(pre_hook, post_hook)` pair
    `ConversationGenerationService` accepts — Conversation stays fully
    decoupled from `runtime_governance` (it only sees a Callable), and
    `mode_provider` mirrors `EvidenceGenerationObserver`'s own
    `mode_provider` pattern for reading the live Mode without a hard
    dependency on any concrete Mode type.

    Both hooks only ever return `True` (intervene) when `mode == "enforce"`
    *and* the corresponding Action Resolver decision actually executed,
    OR when Mode/Evaluation/Binding/Resolution itself failed in a context
    that could have been `enforce` (`mode_unavailable`, or any exception
    raised while `mode == "enforce"`) — Fail-closed, never Fail-open
    (P4-CODEX-005). `observe` always returns `False` regardless of any
    Deviation or internal failure found (ADR-4-007 "Observeは絶対に非介入");
    `off` short-circuits before any snapshot is even built, and before
    `governance_observer` is even consulted (P4-MOD-002, Evidence Call 0).

    `governance_observer` (P4-EVD-001) is handed the *same*
    `StandardGovernanceResult` the hook already computed for its own
    Stop/Reject decision — never a second Evaluation just for Evidence's
    sake (P4-CODEX-003). A failure inside the Observer itself is caught
    here too, as a second defensive layer on top of the Observer's own
    contractual never-raise guarantee — Evidence can never alter this
    Stop/Reject decision either way.

    `observe` and `enforce` both Bind (P4-CODEX-011 §1.1) — a Valid
    Bundle Observe Result/Evidence now carries a real
    `binding_digest_sha512`/Source Plan Identity instead of always
    `None`, and a Stale/Unavailable rebind still short-circuits before
    the Evaluator in either Mode. `resolve_actions` is only ever
    constructed (and only ever called by `GovernancePointRuntime.invoke()`)
    when `mode == "enforce"` — Observe never reaches the Action Resolver.
    The `mode_unavailable` Evidence write (P4-CODEX-007/011 §1.2) never
    gates on the Observer's own `is_active()` first: in the real
    Composition Root the Observer's `mode_provider` is the *same*
    Callable as this function's own — a Provider that just failed here
    would make `is_active()` fail closed too, silently skipping the very
    write meant to report the failure.
    """

    def _pre_hook(request: GenerationRequest) -> tuple[bool, str]:
        mode = _safe_mode(mode_provider)
        if mode == "off":
            return False, ""
        if mode == "mode_unavailable":
            # P4-CODEX-007/011: Fail-closed here always meant a correct
            # Stop/Reject decision, but previously left Last Result and
            # Evidence completely untouched — now a synthetic Degraded
            # Result makes this failure visible on the same surfaces
            # every other path already uses. This never gates on
            # `_observer_active()`/`is_active()` first (P4-CODEX-011
            # §1.2): in the real Composition Root, the Observer's own
            # `mode_provider` is the *same* Callable as this Hook's — a
            # Provider that just raised/returned Unreadable here would
            # make `is_active()` fail closed to `False` too, silently
            # skipping the write. Attempting the write unconditionally
            # (still Safe — `_observe_terminal_degraded` never raises,
            # and marks `observer_interaction_degraded` on its own
            # failure) is what actually gets this Degraded Terminal
            # recorded instead of silently gated away by the very same
            # failure it exists to report.
            invocation_id = str(uuid4())
            mode_unavailable_result = _mode_unavailable_result(
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_PRE_POINT_ID,
                stage=STAGE_PRE,
                mode=mode,
            )
            composition.record_result(
                point_id=MAIN_MODEL_PRE_POINT_ID, result=mode_unavailable_result
            )
            if governance_observer is not None:
                _observe_terminal_degraded(
                    composition,
                    governance_observer,
                    invocation_id=invocation_id,
                    point_id=MAIN_MODEL_PRE_POINT_ID,
                    stage=STAGE_PRE,
                    mode=mode,
                    degraded_reason_code="mode_provider_unavailable",
                )
            return True, "governance_mode_unavailable"
        invocation_id = str(uuid4())
        observer_active = _observer_active(composition, governance_observer)
        if observer_active:
            _observe_started(
                composition,
                governance_observer,
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_PRE_POINT_ID,
                stage=STAGE_PRE,
                mode=mode,
            )
        try:
            # P4-CODEX-011 §1.1: `observe` now Binds too, using the same
            # current Source Plan/Capability/Authority/Policy/Budget/
            # Registry as `enforce` — a Valid-Bundle Observe Result now
            # carries a real `binding_digest_sha512`/Source Plan Identity
            # instead of `None`. `resolve_actions` stays gated to
            # `enforce` only (below) — `GovernancePointRuntime.invoke()`
            # never calls it otherwise, but never even constructing it
            # for `observe` keeps that guarantee visible at this call
            # site too (ADR-4-007 "Observeは絶対に非介入").
            binding = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
            result = composition.point_runtime.invoke(
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_PRE_POINT_ID,
                stage=STAGE_PRE,
                mode=mode,
                snapshot=_pre_snapshot(request),
                binding=binding,
                descriptors=composition.descriptors,
                budget=composition.budget,
                resolve_actions=(
                    composition.resolver_for(
                        point_id=MAIN_MODEL_PRE_POINT_ID, stage=STAGE_PRE, binding=binding
                    )
                    if mode == "enforce"
                    else None
                ),
            )
        except Exception:
            logger.warning("runtime_governance: pre-point invocation failed", exc_info=True)
            if observer_active:
                _observe_terminal_degraded(
                    composition,
                    governance_observer,
                    invocation_id=invocation_id,
                    point_id=MAIN_MODEL_PRE_POINT_ID,
                    stage=STAGE_PRE,
                    mode=mode,
                    degraded_reason_code="point_invocation_failed",
                )
            if mode == "enforce":
                return True, "governance_enforce_evaluation_failed"
            return False, ""  # observe: never intervenes, even on internal failure
        composition.record_result(point_id=MAIN_MODEL_PRE_POINT_ID, result=result)
        if observer_active:
            _observe_terminal_from_result(
                composition,
                governance_observer,
                invocation_id=invocation_id,
                result=result,
                binding=binding,
            )
        for action in result.executed_actions:
            if action.action_id == "stop_before_generation" and action.executed:
                return True, "governance_stop_before_generation"
        return False, ""

    def _post_hook(content: str) -> tuple[bool, str]:
        mode = _safe_mode(mode_provider)
        if mode == "off":
            return False, ""
        if mode == "mode_unavailable":
            invocation_id = str(uuid4())
            mode_unavailable_result = _mode_unavailable_result(
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_POST_POINT_ID,
                stage=STAGE_POST,
                mode=mode,
            )
            composition.record_result(
                point_id=MAIN_MODEL_POST_POINT_ID, result=mode_unavailable_result
            )
            if governance_observer is not None:
                _observe_terminal_degraded(
                    composition,
                    governance_observer,
                    invocation_id=invocation_id,
                    point_id=MAIN_MODEL_POST_POINT_ID,
                    stage=STAGE_POST,
                    mode=mode,
                    degraded_reason_code="mode_provider_unavailable",
                )
            return True, "governance_mode_unavailable"
        invocation_id = str(uuid4())
        observer_active = _observer_active(composition, governance_observer)
        if observer_active:
            _observe_started(
                composition,
                governance_observer,
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_POST_POINT_ID,
                stage=STAGE_POST,
                mode=mode,
            )
        try:
            binding = composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
            result = composition.point_runtime.invoke(
                invocation_id=invocation_id,
                point_id=MAIN_MODEL_POST_POINT_ID,
                stage=STAGE_POST,
                mode=mode,
                snapshot=content,
                binding=binding,
                descriptors=composition.descriptors,
                budget=composition.budget,
                resolve_actions=(
                    composition.resolver_for(
                        point_id=MAIN_MODEL_POST_POINT_ID, stage=STAGE_POST, binding=binding
                    )
                    if mode == "enforce"
                    else None
                ),
            )
        except Exception:
            logger.warning("runtime_governance: post-point invocation failed", exc_info=True)
            if observer_active:
                _observe_terminal_degraded(
                    composition,
                    governance_observer,
                    invocation_id=invocation_id,
                    point_id=MAIN_MODEL_POST_POINT_ID,
                    stage=STAGE_POST,
                    mode=mode,
                    degraded_reason_code="point_invocation_failed",
                )
            if mode == "enforce":
                return True, "governance_enforce_evaluation_failed"
            return False, ""  # observe: never intervenes, even on internal failure
        composition.record_result(point_id=MAIN_MODEL_POST_POINT_ID, result=result)
        if observer_active:
            _observe_terminal_from_result(
                composition,
                governance_observer,
                invocation_id=invocation_id,
                result=result,
                binding=binding,
            )
        for action in result.executed_actions:
            if action.action_id == "reject_output" and action.executed:
                return True, "governance_reject_output"
        return False, ""

    return _pre_hook, _post_hook
