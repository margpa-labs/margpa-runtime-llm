from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeTransitionError,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    MainGovernanceModeController,
    SemanticRuntimeCoordinator,
    freeze_semantic_turn,
    merge_structural_and_semantic_observations,
    resolve_semantic_action,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    Observation,
    ObservationOutcome,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationMethod,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticFinalDisposition,
    SemanticProviderState,
    SemanticTurnSnapshot,
    Severity,
)

_DIGEST = "a" * 128


def _criterion(index: int = 1) -> SemanticCriterion:
    return SemanticCriterion(
        criterion_id=f"semantic.argd.rule.{index}",
        descriptor_id=f"argd.rule.{index}",
        source_definition_id="argd",
        source_definition_digest_sha512=_DIGEST,
        source_pointer=f"/rules/{index}",
        source_text_digest_sha512=_DIGEST,
        instruction="Do not contradict the supplied evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


def _result(
    criterion: SemanticCriterion,
    disposition: SemanticCriterionDisposition,
    *,
    reason: str | None = None,
) -> SemanticCriterionResult:
    return SemanticCriterionResult(
        criterion_id=criterion.criterion_id,
        descriptor_id=criterion.descriptor_id,
        disposition=disposition,
        confidence=0.9,
        reason_code=reason,
    )


def test_structural_placeholder_is_replaced_but_core_observation_is_retained() -> None:
    criterion = _criterion()
    merged = merge_structural_and_semantic_observations(
        structural=(
            Observation(
                descriptor_id=criterion.descriptor_id,
                evaluation_method="requires_semantic_evaluator",
                outcome=ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR,
            ),
            Observation(
                descriptor_id="core.structural.empty_output",
                evaluation_method="deterministic",
                outcome=ObservationOutcome.DEVIATION,
                severity=Severity.HIGH,
                detail_code="empty_output",
            ),
        ),
        criteria=(criterion,),
        semantic_results=(_result(criterion, SemanticCriterionDisposition.PASS),),
    )
    assert [item.descriptor_id for item in merged] == [
        criterion.descriptor_id,
        "core.structural.empty_output",
    ]
    assert merged[0].outcome is ObservationOutcome.PASS
    assert merged[1].outcome is ObservationOutcome.DEVIATION


def test_duplicate_criterion_result_is_rejected_not_double_recorded() -> None:
    criterion = _criterion()
    result = _result(criterion, SemanticCriterionDisposition.PASS)
    with pytest.raises(ValueError, match="duplicate semantic criterion result"):
        merge_structural_and_semantic_observations(
            structural=(), criteria=(criterion,), semantic_results=(result, result)
        )


def test_turn_snapshot_freezes_provider_budget_language_and_modes() -> None:
    frozen = freeze_semantic_turn(
        request_id="req-1",
        generation=1,
        criteria=(_criterion(1), _criterion(2)),
        language="ja",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=1,
    )
    assert frozen.snapshot.language == "ja"
    assert frozen.snapshot.configured_provider == "judge.selene"
    assert len(frozen.snapshot.criteria) == 1
    assert frozen.initially_deferred[0].reason_code == "budget_exhausted"


def test_coordinator_rejects_exact_duplicate_republication() -> None:
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    first = coordinator.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    response = SemanticEvaluationResponse(
        request_id="req-1",
        generation=first.generation,
        provider_id="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        results=(_result(criterion, SemanticCriterionDisposition.PASS),),
        latency_ms=1,
    )
    assert coordinator.record_response(response=response, structural=()) is not None
    assert coordinator.record_response(response=response, structural=()) is None


def test_coordinator_records_a_genuinely_new_late_response_after_a_different_turn_begins() -> None:
    """R4-WU-01 (Controller Review IR-R3-01): before this fix, a single
    `_current` slot meant a different Turn ("req-2") beginning made "req-1"
    unreachable, so its own genuine (never-before-recorded) later Response
    was silently rejected -- neither its Evidence nor its Action were ever
    recorded. The corrected, request-local contract requires the opposite:
    a genuinely new Response for an EARLIER `request_id`, arriving AFTER a
    different Turn has begun, must still be recorded onto its own Turn --
    never silently dropped -- while the later Turn's own Current/Evidence
    stay completely unaffected."""
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    first = coordinator.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    coordinator.begin(
        request_id="req-2",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    late_response = SemanticEvaluationResponse(
        request_id="req-1",
        generation=first.generation,
        provider_id="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        results=(_result(criterion, SemanticCriterionDisposition.PASS),),
        latency_ms=1,
    )

    evidence = coordinator.record_response(response=late_response, structural=())

    assert evidence is not None
    assert evidence.request_id == "req-1"
    assert coordinator.evidence_for(request_id="req-1") is not None
    # "req-2" (the later, current Turn) stays unaffected by "req-1"'s own
    # late recording -- it never had a Response recorded at all.
    assert coordinator.evidence_for(request_id="req-2") is None
    assert coordinator.latest_evidence() is None


def test_a_begin_b_begin_a_reentry_never_rewinds_the_latest_current_pointer() -> None:
    """R5-WU-01 (Controller Review): `begin()`'s own idempotent re-hit path
    for an ALREADY-begun `request_id` must never touch the Latest Current
    Pointer, the Ledger's FIFO order, generation, digest, or rotation
    cursor -- before this fix, re-Beginning "A" after "B" had already begun
    silently wound the Latest Current Pointer back to "A", even though "A"
    was never actually re-frozen. This is the Handoff's own literal probe:
    A begin -> B begin -> A begin re-entry -> A keeps its original
    generation/digest, Current stays on B throughout, and A's own later
    Evidence recording still never contaminates B's own Current/Latest
    Evidence."""
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))

    a_first = coordinator.begin(
        request_id="req-a",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    b_first = coordinator.begin(
        request_id="req-b",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    current_after_b = coordinator.current_snapshot()
    assert current_after_b is not None
    assert current_after_b.request_id == "req-b"

    a_reentry = coordinator.begin(
        request_id="req-a",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    assert a_reentry.generation == a_first.generation
    assert a_reentry.frozen_digest_sha512 == a_first.frozen_digest_sha512

    current_after_a_reentry = coordinator.current_snapshot()
    assert current_after_a_reentry is not None
    assert current_after_a_reentry.request_id == "req-b"
    assert current_after_a_reentry.generation == b_first.generation

    a_response = SemanticEvaluationResponse(
        request_id="req-a",
        generation=a_first.generation,
        provider_id="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        results=(_result(criterion, SemanticCriterionDisposition.PASS),),
        latency_ms=1,
    )
    a_evidence = coordinator.record_response(response=a_response, structural=())
    assert a_evidence is not None
    assert coordinator.evidence_for(request_id="req-a") is not None
    assert coordinator.evidence_for(request_id="req-b") is None

    current_after_a_recorded = coordinator.current_snapshot()
    assert current_after_a_recorded is not None
    assert current_after_a_recorded.request_id == "req-b"
    assert coordinator.latest_evidence() is None


def test_129_distinct_requests_evict_the_oldest_and_keep_latest_pointer_on_the_newest() -> None:
    """R5-WU-01: the Handoff's own explicit additional requirement --
    Beginning 129 genuinely distinct `request_id`s must never let the
    Ledger exceed its `_MAX_TRACKED_TURNS=128` bound, must evict the
    OLDEST-begun entry first (FIFO, not an arbitrary one), and must leave
    the Latest Current Pointer on the newest genuinely-new `request_id`."""
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))

    for index in range(129):
        coordinator.begin(
            request_id=f"req-{index}",
            language="en",
            main_mode="observe",
            judge_mode="observe",
            repair_mode="off",
            configured_provider="judge.selene",
            active_provider="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="local",
            max_criteria=8,
        )

    assert coordinator.snapshot_for(request_id="req-0") is None
    for index in range(1, 129):
        assert coordinator.snapshot_for(request_id=f"req-{index}") is not None

    current = coordinator.current_snapshot()
    assert current is not None
    assert current.request_id == "req-128"


def test_provider_short_result_becomes_typed_unknown_not_pass() -> None:
    criteria = (_criterion(1), _criterion(2))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-1",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            results=(_result(criteria[0], SemanticCriterionDisposition.PASS),),
            latency_ms=1,
        ),
        structural=(),
    )
    assert evidence is not None
    assert [item.disposition for item in evidence.criterion_results] == [
        SemanticCriterionDisposition.PASS,
        SemanticCriterionDisposition.UNKNOWN,
    ]
    assert evidence.criterion_results[1].reason_code == "malformed_result"


def test_live_turn_covers_all_109_criteria_with_selected_and_budget_deferred_counts() -> None:
    criteria = tuple(_criterion(index) for index in range(1, 110))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-109",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=32,
    )
    assert len(snapshot.criteria) == 32
    assert snapshot.deferred_criteria_count == 77
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-109",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            results=tuple(
                _result(item, SemanticCriterionDisposition.PASS) for item in snapshot.criteria
            ),
            latency_ms=1,
        ),
        structural=(),
    )
    assert evidence is not None
    assert len(evidence.criterion_results) == 109
    assert (
        sum(
            item.disposition is SemanticCriterionDisposition.PASS
            for item in evidence.criterion_results
        )
        == 32
    )
    deferred = tuple(
        item
        for item in evidence.criterion_results
        if item.disposition is SemanticCriterionDisposition.DEFERRED
    )
    assert len(deferred) == 77
    assert {item.reason_code for item in deferred} == {"budget_exhausted"}


def test_freeze_semantic_turn_rotation_wraps_around_the_applicable_sequence() -> None:
    """P9-1 Package 2 OF-P2-001, precise small-N proof of the wrap-around
    arithmetic itself (independent of the Coordinator's own cursor
    bookkeeping, exercised separately below)."""
    criteria = tuple(_criterion(index) for index in range(1, 6))  # 5 criteria, ids .1.._.5
    ids = [item.criterion_id for item in criteria]

    def _selected_and_next(offset: int) -> tuple[list[str], int]:
        frozen = freeze_semantic_turn(
            request_id="req-rotation",
            generation=1,
            criteria=criteria,
            language="en",
            main_mode="observe",
            judge_mode="observe",
            repair_mode="off",
            configured_provider="judge.selene",
            active_provider="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="local",
            max_criteria=2,
            rotation_offset=offset,
        )
        return [item.criterion_id for item in frozen.snapshot.criteria], frozen.next_rotation_offset

    selected, next_offset = _selected_and_next(0)
    assert selected == [ids[0], ids[1]]
    assert next_offset == 2

    selected, next_offset = _selected_and_next(2)
    assert selected == [ids[2], ids[3]]
    assert next_offset == 4

    # Wraps past the end of the sequence back to the start.
    selected, next_offset = _selected_and_next(4)
    assert selected == [ids[4], ids[0]]
    assert next_offset == 1

    selected, next_offset = _selected_and_next(1)
    assert selected == [ids[1], ids[2]]
    assert next_offset == 3


def test_multiple_turns_rotate_through_all_109_criteria_instead_of_repeating_the_same_32() -> None:
    """P9-1 Package 2 OF-P2-001: the reported symptom was the identical
    lexicographically-first 32 of 109 Criteria being selected on every
    Turn, forever, with the remaining 77 permanently Deferred. Across
    `ceil(109 / 32) == 4` consecutive Turns, every one of the 109 must be
    selected at least once."""
    criteria = tuple(_criterion(index) for index in range(1, 110))
    all_ids = {item.criterion_id for item in criteria}
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)

    per_turn_selected: list[frozenset[str]] = []
    per_turn_offset: list[int] = []
    for turn_index in range(4):
        snapshot = coordinator.begin(
            request_id=f"req-rotation-{turn_index}",
            language="en",
            main_mode="observe",
            judge_mode="observe",
            repair_mode="off",
            configured_provider="judge.selene",
            active_provider="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="local",
            max_criteria=32,
        )
        per_turn_selected.append(frozenset(item.criterion_id for item in snapshot.criteria))
        per_turn_offset.append(snapshot.rotation_offset)

    assert per_turn_offset == [0, 32, 64, 96]
    union_of_all_turns = frozenset().union(*per_turn_selected)
    assert union_of_all_turns == all_ids
    # Genuine rotation, not the same 32 every Turn.
    assert per_turn_selected[0] != per_turn_selected[1]
    assert per_turn_selected[1] != per_turn_selected[2]
    assert per_turn_selected[2] != per_turn_selected[3]


def test_provider_failure_is_not_mislabeled_as_malformed_result() -> None:
    criteria = (_criterion(1), _criterion(2))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-provider-failure",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-provider-failure",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.FAILED,
            results=(),
            latency_ms=1,
            failure_reason="provider_transport_failed",
        ),
        structural=(),
    )
    assert evidence is not None
    assert all(
        item.disposition is SemanticCriterionDisposition.UNKNOWN
        and item.reason_code == "provider_failure"
        for item in evidence.criterion_results
    )


def test_main_enforce_activation_is_rejected_without_active_enforcing_judge() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    controller.set_semantic_enforce_gate(lambda: (False, "judge_enforce_required"))
    with pytest.raises(GovernanceModeTransitionError, match="judge_enforce_required"):
        controller.apply_mode(GovernanceMode.ENFORCE)


def test_action_resolver_keeps_recommendation_separate_from_execution() -> None:
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    decision = resolve_semantic_action(
        snapshot=frozen.snapshot,
        results=(_result(criterion, SemanticCriterionDisposition.DEVIATION),),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.executed_disposition is SemanticFinalDisposition.OBSERVED


def test_all_not_applicable_results_are_never_mistaken_for_candidate_accepted() -> None:
    """P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 3,
    Finding 1 from an independent boundary-value audit): `has_uncertain`
    used to check only `UNKNOWN`/`DEFERRED`, omitting `NOT_APPLICABLE` --
    so a `results` batch where every Criterion is `NOT_APPLICABLE` (the
    exact shape `_run_built_in_semantic_judge()` in
    `bootstrap/judge_live_integration.py` produces whenever the Built-in
    Deterministic Judge is Active, since it performs no real evaluation by
    design) made both `has_deviation` and `has_uncertain` False and this
    function reported `CANDIDATE_ACCEPTED`/`all_selected_criteria_passed`
    -- mislabeling "zero Criteria were actually evaluated" as "every
    Criterion passed"."""
    criterion = _criterion()
    results = (_result(criterion, SemanticCriterionDisposition.NOT_APPLICABLE),)

    enforce_snapshot = _enforce_snapshot(criteria=(criterion,), repair_mode="enforce")
    enforce_decision = resolve_semantic_action(snapshot=enforce_snapshot, results=results)
    assert enforce_decision.recommended_disposition is SemanticFinalDisposition.SAFE_FALLBACK
    assert enforce_decision.executed_disposition is SemanticFinalDisposition.SAFE_FALLBACK
    assert enforce_decision.reason_code == "semantic_result_inconclusive"

    frozen = freeze_semantic_turn(
        request_id="req-not-applicable-observe",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    observe_decision = resolve_semantic_action(snapshot=frozen.snapshot, results=results)
    assert observe_decision.recommended_disposition is SemanticFinalDisposition.NOT_EVALUATED


def _enforce_snapshot(
    *, criteria: tuple[SemanticCriterion, ...], repair_mode: str
) -> SemanticTurnSnapshot:
    frozen = freeze_semantic_turn(
        request_id="req-enforce-conflict",
        generation=1,
        criteria=criteria,
        language="en",
        main_mode="enforce",
        judge_mode="enforce",
        repair_mode=repair_mode,
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    return frozen.snapshot


def test_enforce_conflict_deviation_takes_priority_over_uncertain() -> None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 6): `resolve_semantic_
    action()`'s Enforce branch now checks `has_deviation` BEFORE
    `has_uncertain` -- matching the Observe branch above (its own ternary
    already resolves `has_deviation ? REPAIR_REQUESTED : has_uncertain ?
    NOT_EVALUATED : CANDIDATE_ACCEPTED`) and the identical priority
    `_judge_response_from_semantic_results()`
    (bootstrap/judge_live_integration.py) and
    `_recommendation_from_criterion_results()`
    (modules/evaluation/application/judge_output_decoder.py) both already
    use. Before this fix, this Enforce branch alone checked `has_uncertain`
    first, so a single genuinely UNCERTAIN Criterion forced Safe Fallback
    even when a different Criterion in the same batch showed a clear
    Deviation that should have earned a Repair attempt -- and made
    `recommended_disposition` diverge from what the identical evaluation
    result would have produced under Observe. This Test replaces
    `test_enforce_conflict_uncertain_takes_priority_over_deviation`, which
    asserted the old (pre-fix) priority.

    P9-1 Judge/Governance Rework (WU-03): `reason_code` is now
    `"main_governance_repair_authorized"`, not `"repair_authorized"` --
    Main Governance's own authorization no longer depends on
    `frozen_repair_mode` (see `resolve_semantic_action()`'s own WU-03
    docstring), so the reason code names the actual authorizing party."""
    criteria = (_criterion(1), _criterion(2))
    snapshot = _enforce_snapshot(criteria=criteria, repair_mode="enforce")
    decision = resolve_semantic_action(
        snapshot=snapshot,
        results=(
            _result(criteria[0], SemanticCriterionDisposition.DEVIATION),
            _result(criteria[1], SemanticCriterionDisposition.UNKNOWN),
        ),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.executed_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.repair_eligible is True
    assert decision.reason_code == "main_governance_repair_authorized"


def test_enforce_uncertain_only_still_forces_safe_fallback() -> None:
    """The has_uncertain branch is still reachable, and still forces Safe
    Fallback, when NO Criterion in the batch shows a Deviation -- only the
    relative priority against a co-occurring Deviation changed (see
    `test_enforce_conflict_deviation_takes_priority_over_uncertain`)."""
    criteria = (_criterion(1), _criterion(2))
    snapshot = _enforce_snapshot(criteria=criteria, repair_mode="enforce")
    decision = resolve_semantic_action(
        snapshot=snapshot,
        results=(
            _result(criteria[0], SemanticCriterionDisposition.PASS),
            _result(criteria[1], SemanticCriterionDisposition.UNKNOWN),
        ),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.SAFE_FALLBACK
    assert decision.executed_disposition is SemanticFinalDisposition.SAFE_FALLBACK
    assert decision.repair_eligible is False
    assert decision.reason_code == "semantic_result_inconclusive"


def test_enforce_multiple_deviations_resolve_as_one_repair_request_when_authorized() -> None:
    """A Conflict between two simultaneously-DEVIATION Criteria (no
    Uncertain one) resolves to exactly one coherent Repair Request, not a
    per-Criterion split decision -- `resolve_semantic_action()` decides
    once for the whole batch."""
    criteria = (_criterion(1), _criterion(2))
    snapshot = _enforce_snapshot(criteria=criteria, repair_mode="enforce")
    decision = resolve_semantic_action(
        snapshot=snapshot,
        results=(
            _result(criteria[0], SemanticCriterionDisposition.PASS),
            _result(criteria[1], SemanticCriterionDisposition.DEVIATION),
        ),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.executed_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.repair_eligible is True
    assert decision.reason_code == "main_governance_repair_authorized"


def test_enforce_deviation_authorizes_a_main_origin_repair_even_when_repair_mode_is_off() -> None:
    """P9-1 Judge/Governance Rework (WU-03), replacing the pre-Rework
    `test_enforce_deviation_never_executes_repair_when_repair_authority_
    is_off` (P9-1-C-WU-004 "ENFORCE Judge alone never expands into an
    executed Repair"): Codex Controller Handoff WU-03's Matrix explicitly
    authorizes a Main Governance-origin repair when Main=ENFORCE and
    Judge=ENFORCE&Active, *regardless* of the separate (Judge-side) Repair
    Mode's own value -- Main Governance's own ENFORCE decision to request
    a correction for a confirmed Rule violation must not be powerless just
    because an unrelated toggle happens to be off. `executed_disposition`
    now matches `recommended_disposition` here (both REPAIR_REQUESTED),
    and `repair_eligible` is True -- this is still only a recommendation
    for `_finalize_judge_dispatch()` to independently authorize (Guardrail
    Deny/Budget via the shared Resolver) before ever invoking the Repair
    Executor; this module never runs a Repair itself."""
    criteria = (_criterion(1),)
    snapshot = _enforce_snapshot(criteria=criteria, repair_mode="off")
    decision = resolve_semantic_action(
        snapshot=snapshot,
        results=(_result(criteria[0], SemanticCriterionDisposition.DEVIATION),),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.executed_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.repair_eligible is True
    assert decision.reason_code == "main_governance_repair_authorized"


def test_judge_off_is_recorded_per_criterion_with_reason() -> None:
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    coordinator.begin(
        request_id="req-off",
        language="en",
        main_mode="observe",
        judge_mode="off",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider=None,
        provider_state=SemanticProviderState.NONE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_deferred(
        request_id="req-off", reason=SemanticDeferredReason.JUDGE_OFF
    )
    assert evidence is not None
    assert evidence.criterion_results[0].reason_code == "judge_off"
    assert evidence.criterion_results[0].disposition is SemanticCriterionDisposition.DEFERRED
