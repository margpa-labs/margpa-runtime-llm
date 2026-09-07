"""Semantic evaluation orchestration and structural/semantic composition."""

from __future__ import annotations

import threading
from collections import OrderedDict
from dataclasses import dataclass

from ..domain import (
    BudgetSnapshot,
    ExecutionDescriptor,
    Observation,
    ObservationOutcome,
    SemanticActionDecision,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticFinalDisposition,
    SemanticProviderState,
    SemanticRuntimeEvidence,
    SemanticTurnSnapshot,
    Severity,
    semantic_contract_digest,
)
from ..ports import DeterministicEvaluatorPort, SemanticEvaluatorPort


@dataclass(frozen=True, slots=True)
class FrozenSemanticTurn:
    snapshot: SemanticTurnSnapshot
    initially_deferred: tuple[SemanticCriterionResult, ...]
    # P9-1 Package 2 OF-P2-001: where the *next* Turn's rotation window
    # should start (mod the current applicable-criteria count), so a
    # caller holding rotation state (`SemanticRuntimeCoordinator`) never
    # needs to re-derive the POST/BOTH-stage applicable set itself just to
    # advance its own cursor -- this function is the single place that
    # owns "applicable" and the rotation arithmetic over it.
    next_rotation_offset: int


def freeze_semantic_turn(
    *,
    request_id: str,
    generation: int,
    criteria: tuple[SemanticCriterion, ...],
    language: str,
    main_mode: str,
    judge_mode: str,
    repair_mode: str,
    configured_provider: str,
    active_provider: str | None,
    provider_state: SemanticProviderState,
    budget_profile: str,
    max_criteria: int,
    rotation_offset: int = 0,
) -> FrozenSemanticTurn:
    """Capture every mutable semantic input once at the Main pre boundary.

    P9-1 Package 2 OF-P2-001: when the POST/BOTH-stage applicable Criteria
    outnumber `max_criteria`, a single fixed `applicable[:max_criteria]`
    slice would select the identical lexicographically-first criteria on
    every Turn forever, permanently deferring everything after it (Package
    2's own real-corpus Evidence: 32 selected / 77 permanently deferred of
    109). `rotation_offset` instead starts this Turn's selection window at
    an arbitrary point in the sorted `applicable` sequence, wrapping
    around -- across `ceil(len(applicable) / max_criteria)` Turns advancing
    `rotation_offset` by `max_criteria` each time (see
    `next_rotation_offset` above), every applicable Criterion is selected
    at least once, honoring P2-WU-06's "one Run must not force all 109 in
    and break Context/Deadline" by spreading coverage across Turns instead
    of ever forcing a single oversized Run.
    """

    applicable = tuple(
        sorted(
            (
                item
                for item in criteria
                if item.evaluation_stage
                in (SemanticEvaluationStage.POST, SemanticEvaluationStage.BOTH)
            ),
            key=lambda item: item.criterion_id,
        )
    )
    total = len(applicable)
    offset = rotation_offset % total if total > 0 else 0
    rotated = applicable[offset:] + applicable[:offset]
    selected = rotated[:max_criteria]
    deferred_items = rotated[max_criteria:]
    next_rotation_offset = (offset + max_criteria) % total if total > 0 else 0
    deferred = tuple(
        SemanticCriterionResult(
            criterion_id=item.criterion_id,
            descriptor_id=item.descriptor_id,
            disposition=SemanticCriterionDisposition.DEFERRED,
            reason_code=SemanticDeferredReason.BUDGET_EXHAUSTED.value,
        )
        for item in deferred_items
    )
    batch_digest = semantic_contract_digest(
        {
            "stage": SemanticEvaluationStage.POST.value,
            "selected": [item.criterion_id for item in selected],
            "deferred": [item.criterion_id for item in deferred],
        }
    )
    payload = {
        "request_id": request_id,
        "generation": generation,
        "language": language,
        "main_mode": main_mode,
        "judge_mode": judge_mode,
        "repair_mode": repair_mode,
        "configured_provider": configured_provider,
        "active_provider": active_provider,
        "provider_state": provider_state.value,
        "budget_profile": budget_profile,
        "max_criteria": max_criteria,
        "rotation_offset": offset,
        "criterion_ids": [item.criterion_id for item in selected],
        "deferred_criteria_count": len(deferred),
        "batch_digest": batch_digest,
    }
    snapshot = SemanticTurnSnapshot(
        request_id=request_id,
        generation=generation,
        language=language,
        frozen_main_mode=main_mode,
        frozen_judge_mode=judge_mode,
        frozen_repair_mode=repair_mode,
        configured_provider=configured_provider,
        active_provider=active_provider,
        provider_state=provider_state,
        budget_profile=budget_profile,
        max_criteria=max_criteria,
        criteria=selected,
        deferred_criteria_count=len(deferred),
        rotation_offset=offset,
        batch_digest_sha512=batch_digest,
        frozen_digest_sha512=semantic_contract_digest(payload),
    )
    return FrozenSemanticTurn(
        snapshot=snapshot,
        initially_deferred=deferred,
        next_rotation_offset=next_rotation_offset,
    )


def merge_structural_and_semantic_observations(
    *,
    structural: tuple[Observation, ...],
    criteria: tuple[SemanticCriterion, ...],
    semantic_results: tuple[SemanticCriterionResult, ...],
) -> tuple[Observation, ...]:
    """Replace semantic placeholders, retaining independent structural checks.

    A criterion/result identity may occur only once.  Duplicate provider output
    is rejected instead of being recorded twice or silently last-write-wins.
    """

    criteria_by_id = {item.criterion_id: item for item in criteria}
    if len(criteria_by_id) != len(criteria):
        raise ValueError("duplicate semantic criterion identity")
    result_ids = [item.criterion_id for item in semantic_results]
    if len(set(result_ids)) != len(result_ids):
        raise ValueError("duplicate semantic criterion result")

    semantic_by_descriptor: dict[str, Observation] = {}
    for result in semantic_results:
        criterion = criteria_by_id.get(result.criterion_id)
        if criterion is None or criterion.descriptor_id != result.descriptor_id:
            raise ValueError("semantic result identity does not match the frozen criterion")
        if criterion.descriptor_id in semantic_by_descriptor:
            raise ValueError("multiple semantic results target one descriptor")
        semantic_by_descriptor[criterion.descriptor_id] = _semantic_observation(
            criterion=criterion, result=result
        )

    merged: dict[str, Observation] = {}
    for observation in structural:
        if (
            observation.descriptor_id in semantic_by_descriptor
            and observation.outcome is ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR
        ):
            continue
        if observation.descriptor_id in merged:
            raise ValueError("duplicate structural observation identity")
        merged[observation.descriptor_id] = observation
    merged.update(semantic_by_descriptor)
    return tuple(merged[key] for key in sorted(merged))


def _semantic_observation(
    *, criterion: SemanticCriterion, result: SemanticCriterionResult
) -> Observation:
    outcome = {
        SemanticCriterionDisposition.PASS: ObservationOutcome.PASS,
        SemanticCriterionDisposition.DEVIATION: ObservationOutcome.DEVIATION,
        SemanticCriterionDisposition.UNKNOWN: ObservationOutcome.UNKNOWN,
        SemanticCriterionDisposition.DEFERRED: (ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR),
        SemanticCriterionDisposition.NOT_APPLICABLE: (
            ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR
        ),
    }[result.disposition]
    severity = (
        Severity(criterion.severity_policy)
        if result.disposition is SemanticCriterionDisposition.DEVIATION
        else Severity.NONE
    )
    return Observation(
        descriptor_id=criterion.descriptor_id,
        evaluation_method=criterion.evaluation_method.value,
        outcome=outcome,
        detail_code=result.reason_code or result.disposition.value,
        severity=severity,
        recommended_action_id=(
            "warn" if result.disposition is SemanticCriterionDisposition.DEVIATION else None
        ),
    )


def resolve_semantic_action(
    *, snapshot: SemanticTurnSnapshot, results: tuple[SemanticCriterionResult, ...]
) -> SemanticActionDecision:
    """Resolve recommendation separately from the authority-owned action."""

    if not results:
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            executed_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            repair_eligible=False,
            reason_code="no_semantic_result",
        )
    has_deviation = any(
        item.disposition is SemanticCriterionDisposition.DEVIATION for item in results
    )
    # P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 3,
    # Finding 1 from an independent boundary-value audit): NOT_APPLICABLE
    # must count as uncertain here, same as UNKNOWN/DEFERRED. `_semantic_
    # observation()` above already classifies NOT_APPLICABLE identically to
    # DEFERRED (both -> `ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR`),
    # and `_run_built_in_semantic_judge()` (bootstrap/judge_live_integration.py)
    # tags every Criterion NOT_APPLICABLE when the Built-in Deterministic
    # Judge is Active (it performs no real evaluation by design). Before
    # this fix, an all-NOT_APPLICABLE `results` batch made both
    # `has_deviation` and `has_uncertain` False, so this function reported
    # `CANDIDATE_ACCEPTED`/`all_selected_criteria_passed` -- mislabeling
    # "zero Criteria were actually evaluated" as "every Criterion passed",
    # contradicting this same codebase's own established convention
    # elsewhere that NOT_APPLICABLE is never counted as evaluated (e.g.
    # `_judge_criterion_counts`/`_semantic_criterion_counts` in
    # judge_live_integration.py compute `evaluated = passed + deviated`,
    # excluding both NOT_APPLICABLE and UNKNOWN/DEFERRED).
    has_uncertain = any(
        item.disposition
        in (
            SemanticCriterionDisposition.UNKNOWN,
            SemanticCriterionDisposition.DEFERRED,
            SemanticCriterionDisposition.NOT_APPLICABLE,
        )
        for item in results
    )
    if snapshot.frozen_main_mode != "enforce":
        return SemanticActionDecision(
            recommended_disposition=(
                SemanticFinalDisposition.REPAIR_REQUESTED
                if has_deviation
                else SemanticFinalDisposition.NOT_EVALUATED
                if has_uncertain
                else SemanticFinalDisposition.CANDIDATE_ACCEPTED
            ),
            executed_disposition=SemanticFinalDisposition.OBSERVED,
            repair_eligible=has_deviation,
            reason_code="observe_non_intervening",
        )
    if (
        snapshot.frozen_judge_mode != "enforce"
        or snapshot.provider_state is not SemanticProviderState.ACTIVE
        or snapshot.active_provider is None
    ):
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            executed_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            repair_eligible=False,
            reason_code="false_enforce_prevented",
        )
    # P9-1 Judge Dispatch Fix Round 6 (Finding 6): has_deviation is checked
    # BEFORE has_uncertain here, matching the Observe branch above (its own
    # ternary already resolves `has_deviation ? REPAIR_REQUESTED :
    # has_uncertain ? NOT_EVALUATED : CANDIDATE_ACCEPTED`) and the identical
    # priority `_judge_response_from_semantic_results()`
    # (bootstrap/judge_live_integration.py) and
    # `_recommendation_from_criterion_results()`
    # (modules/evaluation/application/judge_output_decoder.py) both already
    # use. Before this fix, this Enforce branch alone checked has_uncertain
    # first -- so a handful of `unknown`/`deferred` Criteria (e.g. 1-2 of
    # 32) forced the whole Turn to SAFE_FALLBACK even when the remaining
    # Criteria showed clear, numerous Deviations that should have earned a
    # Repair attempt, and made `recommended_disposition` diverge from what
    # the Observe branch would have recommended for the identical evaluation
    # result.
    if has_deviation:
        # P9-1 Judge/Governance Rework (WU-03): Main Governance's own
        # repair authorization no longer defers to the separate Judge-side
        # Repair Mode toggle. Reaching this branch already confirms
        # `frozen_main_mode == "enforce"` (the Observe-branch guard above)
        # and `frozen_judge_mode == "enforce"` with a genuinely Active
        # Judge (the false_enforce_prevented guard above, kept unchanged
        # by this Rework) -- Main Governance's own ENFORCE decision to
        # request a correction for a confirmed Rule violation is
        # independent of whatever the Judge-side Repair Mode toggle
        # separately says (Codex Controller Handoff WU-03's Matrix: with
        # Main=ENFORCE and Judge=ENFORCE&Active, a GD violation authorizes
        # a Main-origin repair request regardless of the existing Repair
        # Mode's own value -- previously this was gated on `frozen_
        # repair_mode == "enforce"`, which made Main Governance's own
        # ENFORCE recommendation powerless whenever the unrelated
        # Judge-side toggle happened to be off/observe).
        #
        # `executed_disposition=REPAIR_REQUESTED` here is still only a
        # recommendation this Coordinator's own caller
        # (`bootstrap/judge_live_integration.py`'s
        # `_finalize_judge_dispatch()`) must independently authorize
        # (Guardrail Deny/Budget checks via the shared `resolve_repair_
        # eligibility()`) before ever invoking the Repair Executor -- this
        # module never runs a Repair itself, and never claims one already
        # ran (Docstring's own "recommendation separately from the
        # authority-owned action" contract, unchanged).
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.REPAIR_REQUESTED,
            executed_disposition=SemanticFinalDisposition.REPAIR_REQUESTED,
            repair_eligible=True,
            reason_code="main_governance_repair_authorized",
        )
    if has_uncertain:
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            executed_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            repair_eligible=False,
            reason_code="semantic_result_inconclusive",
        )
    return SemanticActionDecision(
        recommended_disposition=SemanticFinalDisposition.CANDIDATE_ACCEPTED,
        executed_disposition=SemanticFinalDisposition.CANDIDATE_ACCEPTED,
        repair_eligible=False,
        reason_code="all_selected_criteria_passed",
    )


class CompositeSemanticEvaluator:
    """Runs structural and semantic ports once and merges their identities."""

    def __init__(
        self,
        *,
        structural_evaluator: DeterministicEvaluatorPort,
        semantic_evaluator: SemanticEvaluatorPort,
    ) -> None:
        self._structural = structural_evaluator
        self._semantic = semantic_evaluator

    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        structural_snapshot: str,
        structural_budget: BudgetSnapshot,
        semantic_request: SemanticEvaluationRequest,
    ) -> tuple[SemanticEvaluationResponse, tuple[Observation, ...]]:
        structural = self._structural.evaluate(
            descriptors=descriptors,
            stage=stage,
            snapshot=structural_snapshot,
            budget=structural_budget,
        )
        response = self._semantic.evaluate(request=semantic_request)
        return response, merge_structural_and_semantic_observations(
            structural=structural,
            criteria=semantic_request.snapshot.criteria,
            semantic_results=response.results,
        )


_MAX_TRACKED_TURNS = 128
"""Bounded per-`request_id` Turn Ledger retention (R4-WU-01, Controller
Review IR-R3-01): a Turn's own frozen Snapshot/Evidence must survive a
DIFFERENT `request_id` beginning afterward -- it is never silently
overwritten or discarded the instant another Turn starts. An unbounded
per-request Ledger would still grow forever over a long-running process, so
this is an explicit FIFO cap (oldest-begun Turn evicted first, alongside its
correlated Evidence/criterion-key bookkeeping) rather than no bound at all.
A live single-session Judge pipeline processes Turns roughly sequentially
with Judge lag measured in seconds, so 128 concurrently-tracked Turns is far
beyond any realistic in-flight count -- only a genuinely abandoned Turn from
long in the past is ever evicted."""


class SemanticRuntimeCoordinator:
    """Process-local, request-local Turn Ledger with generation-safe
    publication (R4-WU-01, Controller Review IR-R3-01): every Turn this
    Coordinator successfully freezes (`begin()`) is retained under its own
    `request_id` in a bounded Ledger (see `_MAX_TRACKED_TURNS`) -- a
    DIFFERENT `request_id` beginning afterward never overwrites or discards
    it. Before this fix, a single `_current` slot meant Turn B beginning
    silently made Turn A's own Snapshot unreachable via `snapshot_for()`
    and made A's own later-arriving genuine Background Judge Response
    silently rejected by `record_response()` (a real Controller Probe
    reproduced exactly this: "A成功 → B成功 → AのResponseを記録" recorded
    neither the response nor Evidence). `snapshot_for()`/`record_response()`
    /`record_deferred()`/`evidence_for()` now all key off the Ledger by
    `request_id` directly, independent of whichever `request_id` most
    recently began.

    A single most-recently-begun `request_id` is still tracked, but purely
    as a UI "Latest Current" pointer (`current_snapshot()`/
    `latest_evidence()`) -- explicitly separated from the Ledger itself
    (Controller Review IR-R3-01: "UI向けLatest Current Pointerと、実Turn
    Ledgerを分離する"). It updates ONLY when `begin()` genuinely freezes a
    NEW `request_id` for the first time -- never on a plain read
    (`snapshot_for()`), a Response/Deferred recording, or an idempotent
    re-hit of an already-begun `request_id` (R5-WU-01, Controller Review:
    an A->B->A re-Begin sequence must leave the Latest Current Pointer on
    B, not silently wind it back to A just because A happened to call
    `begin()` again).

    `begin()` is idempotent under its own Lock: two threads racing `begin()`
    for the IDENTICAL `request_id` (a real Controller Probe schedule) can
    never both freeze a new generation for it -- whichever reaches the
    check second reads back the exact same generation the first already
    froze ("Lock下で重複Begin/同一request競合を防ぐ"), and this idempotent
    re-hit path never touches the Ledger's FIFO order or the Latest Current
    Pointer -- only a genuinely new `request_id` does either."""

    def __init__(self, *, criteria: tuple[SemanticCriterion, ...]) -> None:
        self._lock = threading.Lock()
        self._criteria = criteria
        self._generation = 0
        # R4-WU-01: request-local Ledger (an `OrderedDict` for FIFO
        # eviction order) -- replaces the single `_current` slot a
        # different Turn's own `begin()` used to silently overwrite.
        self._turns: OrderedDict[str, FrozenSemanticTurn] = OrderedDict()
        self._latest_request_id: str | None = None
        self._history: dict[str, SemanticRuntimeEvidence] = {}
        self._recorded_criterion_keys: set[tuple[str, int, str]] = set()
        # P9-1 Package 2 OF-P2-001: process-local rotation cursor (matches
        # this whole Coordinator's own already-process-local nature, see
        # its class docstring) -- advances by `freeze_semantic_turn()`'s
        # own `next_rotation_offset` every genuinely NEW `begin()` (never
        # on an idempotent re-hit of an already-begun `request_id`), so
        # consecutive distinct Turns sweep across the full
        # applicable-Criteria set instead of `begin()` always starting
        # back at offset 0.
        self._rotation_cursor = 0

    def begin(
        self,
        *,
        request_id: str,
        language: str,
        main_mode: str,
        judge_mode: str,
        repair_mode: str,
        configured_provider: str,
        active_provider: str | None,
        provider_state: SemanticProviderState,
        budget_profile: str,
        max_criteria: int,
    ) -> SemanticTurnSnapshot:
        with self._lock:
            existing = self._turns.get(request_id)
            if existing is not None:
                # R4-WU-01/R5-WU-01: idempotent re-hit under this same
                # Lock -- a genuinely already-begun `request_id` (whether
                # read back normally, or reached by a second thread racing
                # the very first `begin()` for it) never freezes a second
                # generation, and must NOT touch the Ledger's FIFO order or
                # the Latest Current Pointer (Controller Review: an
                # A->B->A re-Begin must leave both on B, not wind Latest
                # Current back to A). Generation, digest and rotation
                # cursor are all left exactly as already frozen.
                return existing.snapshot
            self._generation += 1
            frozen = freeze_semantic_turn(
                request_id=request_id,
                generation=self._generation,
                criteria=self._criteria,
                language=language,
                main_mode=main_mode,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                configured_provider=configured_provider,
                active_provider=active_provider,
                provider_state=provider_state,
                budget_profile=budget_profile,
                max_criteria=max_criteria,
                rotation_offset=self._rotation_cursor,
            )
            self._turns[request_id] = frozen
            self._rotation_cursor = frozen.next_rotation_offset
            self._latest_request_id = request_id
            self._evict_oldest_locked()
            return frozen.snapshot

    def _evict_oldest_locked(self) -> None:
        """Caller must hold `self._lock`. FIFO eviction of the oldest
        tracked Turn (and its correlated Evidence/criterion-key
        bookkeeping) once `_MAX_TRACKED_TURNS` is exceeded."""
        while len(self._turns) > _MAX_TRACKED_TURNS:
            evicted_request_id, _ = self._turns.popitem(last=False)
            self._history.pop(evicted_request_id, None)
            self._recorded_criterion_keys = {
                key for key in self._recorded_criterion_keys if key[0] != evicted_request_id
            }

    def current_snapshot(self) -> SemanticTurnSnapshot | None:
        with self._lock:
            if self._latest_request_id is None:
                return None
            turn = self._turns.get(self._latest_request_id)
            return turn.snapshot if turn is not None else None

    def snapshot_for(self, *, request_id: str) -> SemanticTurnSnapshot | None:
        with self._lock:
            turn = self._turns.get(request_id)
            return turn.snapshot if turn is not None else None

    def record_response(
        self,
        *,
        response: SemanticEvaluationResponse,
        structural: tuple[Observation, ...],
    ) -> SemanticRuntimeEvidence | None:
        with self._lock:
            turn = self._turns.get(response.request_id)
            if turn is None or response.generation != turn.snapshot.generation:
                return None
            provider_results = _complete_provider_results(
                criteria=turn.snapshot.criteria,
                results=response.results,
                missing_result_reason=_missing_result_reason(response.provider_state),
            )
            results = (*provider_results, *turn.initially_deferred)
            keys = {
                (response.request_id, response.generation, item.criterion_id) for item in results
            }
            if len(keys) != len(results) or keys & self._recorded_criterion_keys:
                return None
            merged = merge_structural_and_semantic_observations(
                structural=structural,
                criteria=turn.snapshot.criteria,
                semantic_results=provider_results,
            )
            action = resolve_semantic_action(snapshot=turn.snapshot, results=results)
            payload = {
                "snapshot": turn.snapshot.frozen_digest_sha512,
                "provider": response.provider_id,
                "provider_state": response.provider_state.value,
                "results": [item.model_dump(mode="json") for item in results],
                "merged": [item.model_dump(mode="json") for item in merged],
                "action": action.model_dump(mode="json"),
                "evaluation_budget": (
                    response.budget.model_dump(mode="json") if response.budget is not None else None
                ),
            }
            evidence = SemanticRuntimeEvidence(
                request_id=response.request_id,
                generation=response.generation,
                frozen_snapshot_digest_sha512=turn.snapshot.frozen_digest_sha512,
                configured_provider=turn.snapshot.configured_provider,
                active_provider=turn.snapshot.active_provider,
                provider_state=response.provider_state,
                criterion_results=tuple(results),
                merged_observations=merged,
                action=action,
                evaluation_budget=response.budget,
                evidence_digest_sha512=semantic_contract_digest(payload),
            )
            self._recorded_criterion_keys.update(keys)
            self._history[response.request_id] = evidence
            return evidence

    def record_deferred(
        self,
        *,
        request_id: str,
        reason: SemanticDeferredReason,
        structural: tuple[Observation, ...] = (),
    ) -> SemanticRuntimeEvidence | None:
        snapshot = self.snapshot_for(request_id=request_id)
        if snapshot is None:
            return None
        response = SemanticEvaluationResponse(
            request_id=request_id,
            generation=snapshot.generation,
            provider_id=snapshot.configured_provider,
            provider_state=snapshot.provider_state,
            results=tuple(
                SemanticCriterionResult(
                    criterion_id=item.criterion_id,
                    descriptor_id=item.descriptor_id,
                    disposition=SemanticCriterionDisposition.DEFERRED,
                    reason_code=reason.value,
                )
                for item in snapshot.criteria
            ),
            latency_ms=0,
            failure_reason=reason.value,
        )
        return self.record_response(response=response, structural=structural)

    def evidence_for(self, *, request_id: str) -> SemanticRuntimeEvidence | None:
        with self._lock:
            return self._history.get(request_id)

    def latest_evidence(self) -> SemanticRuntimeEvidence | None:
        with self._lock:
            if self._latest_request_id is None:
                return None
            return self._history.get(self._latest_request_id)


def _complete_provider_results(
    *,
    criteria: tuple[SemanticCriterion, ...],
    results: tuple[SemanticCriterionResult, ...],
    missing_result_reason: SemanticDeferredReason,
) -> tuple[SemanticCriterionResult, ...]:
    expected = {item.criterion_id: item for item in criteria}
    supplied: dict[str, SemanticCriterionResult] = {}
    for result in results:
        criterion = expected.get(result.criterion_id)
        if (
            criterion is None
            or criterion.descriptor_id != result.descriptor_id
            or result.criterion_id in supplied
        ):
            raise ValueError("provider returned an unexpected or duplicate criterion result")
        supplied[result.criterion_id] = result
    return tuple(
        supplied.get(item.criterion_id)
        or SemanticCriterionResult(
            criterion_id=item.criterion_id,
            descriptor_id=item.descriptor_id,
            disposition=SemanticCriterionDisposition.UNKNOWN,
            reason_code=missing_result_reason.value,
        )
        for item in criteria
    )


def _missing_result_reason(provider_state: SemanticProviderState) -> SemanticDeferredReason:
    return {
        SemanticProviderState.ACTIVE: SemanticDeferredReason.MALFORMED_RESULT,
        SemanticProviderState.NONE: SemanticDeferredReason.PROVIDER_NONE,
        SemanticProviderState.UNAVAILABLE: SemanticDeferredReason.PROVIDER_UNAVAILABLE,
        SemanticProviderState.FAILED: SemanticDeferredReason.PROVIDER_FAILURE,
    }[provider_state]
