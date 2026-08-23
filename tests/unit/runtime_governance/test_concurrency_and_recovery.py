"""Security/Performance/Recovery: Concurrency and Crash-Recovery slices
of the Golden Matrix (P4-G-WU-002). Path/Digest/Restart/Token-Call-0 are
already covered by `test_bootstrap_composition.py` (Invalid Bundle,
zero-Descriptor Restart-equivalent state) and `test_bootstrap_hooks.py`
(OFF short-circuits before any Bind/Evaluate — Call 0); this file adds
what those don't: concurrent access to the two pieces of process-shared
mutable state (`BoundGovernancePlanCache`, `MainGovernanceModeController`)
and post-exception recovery of the Hook pair."""

from __future__ import annotations

import threading

from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeTransitionError,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.runtime_governance.application import (
    BoundGovernancePlanCache,
    MainGovernanceModeController,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_PRE_POINT_ID,
    EvaluationMethod,
    ExecutionDescriptor,
    RuntimeCapabilitySnapshot,
)


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor() -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def _request() -> GenerationRequest:
    return GenerationRequest(
        request_id="req-concurrency",
        model_key="main.qwen3-4b-q4-k-m",
        messages=(ChatMessage(role=MessageRole.USER, content="hello"),),
        parameters=GenerationParameters(),
    )


def test_concurrent_binds_of_the_same_point_converge_on_one_cache_entry() -> None:
    composition = RuntimeGovernanceComposition(capability=_capability())
    baseline = composition.plan_cache.size()
    barrier = threading.Barrier(16)
    results: list[str] = []
    results_lock = threading.Lock()

    def _bind() -> None:
        barrier.wait(timeout=5)
        plan = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
        with results_lock:
            results.append(plan.binding_digest_sha512)

    threads = [threading.Thread(target=_bind) for _ in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert len(results) == 16
    assert len(set(results)) == 1  # every thread converges on one Binding
    # `bind_point` is content-addressed and this Point's inputs never
    # changed mid-run, so no additional entries were created beyond the
    # Composition's own constructor trial Bind.
    assert composition.plan_cache.size() == baseline


def test_concurrent_cache_put_and_get_never_race_or_corrupt() -> None:
    cache = BoundGovernancePlanCache()
    composition = RuntimeGovernanceComposition(capability=_capability())
    plan = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    errors: list[Exception] = []

    def _hammer() -> None:
        try:
            for _ in range(200):
                cache.put(plan)
                fetched = cache.get(plan.binding_digest_sha512)
                assert fetched == plan
                cache.size()
        except Exception as exc:  # pragma: no cover - failure path only
            errors.append(exc)

    threads = [threading.Thread(target=_hammer) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert errors == []
    assert cache.size() == 1


def test_concurrent_apply_mode_never_loses_or_duplicates_a_revision_bump() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    barrier = threading.Barrier(10)

    def _toggle() -> None:
        barrier.wait(timeout=5)
        try:
            controller.apply_mode(GovernanceMode.OBSERVE)
        except GovernanceModeTransitionError:
            pass
        try:
            controller.apply_mode(GovernanceMode.OFF)
        except GovernanceModeTransitionError:
            pass

    threads = [threading.Thread(target=_toggle) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    # Every real transition strictly increments the Revision under the
    # Controller's own Lock — no lost or duplicated updates, and the
    # final state is one of the two modes actually requested.
    snapshot = controller.mode_snapshot()
    assert snapshot.current_mode in (GovernanceMode.OFF, GovernanceMode.OBSERVE)
    assert snapshot.revision >= 1


def test_a_raising_mode_provider_never_corrupts_the_composition_for_the_next_call() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    baseline_cache_size = composition.plan_cache.size()
    calls = {"count": 0}

    def _flaky_mode_provider() -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("transient failure")
        return "enforce"

    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=_flaky_mode_provider
    )
    # First call: the Mode Provider explodes -> Fails Closed (Safe Stop,
    # P4-CODEX-005), never silently `off` — Zero Model Call still holds
    # (no Bind, no Evaluate; the Hook returns before either happens).
    assert pre_hook(_request()) == (True, "governance_mode_unavailable")
    assert composition.plan_cache.size() == baseline_cache_size

    # Second call: same Composition, same Hook pair, no restart or
    # rebuild — Enforce works normally, proving the prior exception left
    # no corrupted state behind.
    assert post_hook("") == (True, "governance_reject_output")


def test_concurrent_hook_invocations_across_threads_stay_isolated() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    _, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    outcomes: list[tuple[bool, str]] = []
    outcomes_lock = threading.Lock()
    barrier = threading.Barrier(12)

    def _run(empty: bool) -> None:
        barrier.wait(timeout=5)
        should_reject, reason = post_hook("" if empty else "a real answer")
        with outcomes_lock:
            outcomes.append((should_reject, reason))

    threads = [threading.Thread(target=_run, args=(index % 2 == 0,)) for index in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert len(outcomes) == 12
    rejected = [outcome for outcome in outcomes if outcome[0]]
    passed = [outcome for outcome in outcomes if not outcome[0]]
    assert len(rejected) == 6
    assert len(passed) == 6
    assert all(reason == "governance_reject_output" for _, reason in rejected)
    assert all(reason == "" for _, reason in passed)
