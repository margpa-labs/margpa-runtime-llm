"""Production Turn Variant Adapter -- pure projection layer (Phase 9-2 R1,
WU-03).

Handoff R1 Section 6.1: "Production AdapterはMain/Judge/Guard/Repairの内部実装を
再実装せず、Phase 9-1のComposition/Correlation/Recording/Cancellationを
再利用する... 既存の実Turn Compositionを「1 Variant Run」として包む". This
module never imports `modules.conversation`/`bootstrap.judge_live_integration`/
etc. directly -- it only defines the narrow `ProductionTurnPort` a real
Bootstrap-layer Adapter implements (`bootstrap/experiment_production_turn_
adapter.py`), plus the one function that turns a real Turn's Observation into
the same `ActorInvocationRecord` shape the Fixture `composition_runner.
run_variant()` produces, so downstream Comparison/Reporting code never needs
to know whether a given Run's Evidence came from a Fixture or a real
Production Turn.

R1 Section 6.2's Config-Isolation decision: a genuinely separate Experiment-scoped
Runtime instance was judged too large a lift to build and safely exercise
concurrently with the live server this Round (see the Exact Return); this
module instead implements Option 2 -- it NEVER requests a different Judge/
Guard/Provider selection than whatever the live Runtime already has active.
`ProductionTurnObservation` is always the REAL, already-observed shape of one
real Turn, never a caller's requested one restated back."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ..domain.composition import ActorInvocationRecord
from ..domain.identity import ComponentKey


@dataclass(frozen=True, slots=True)
class ProductionTurnObservation:
    """The real, already-computed Evidence one real Production Turn
    produced. `request_id` is the REAL identifier Phase 9-1's own
    `ConversationGenerationSession` assigned to this Turn (`start()`
    generates it internally -- a caller cannot choose it), never an
    Experiment-side id restated back. Every `*_called`/`*_outcome` pair
    reports what ACTUALLY happened for that Component during this one
    Turn -- never what a Variant's `ComponentSelection` merely requested
    (a live Guard could be OFF regardless of what an Experiment Variant
    would have liked, and this Observation must say so truthfully).

    R2-WU-02 (IR-P9-2-R1-02 fix): `repair_adopted` is a field distinct
    from `repair_called` -- a real Repair Attempt can be Called (a Repair
    Turn actually ran) without being Adopted (its output was rejected/
    withheld, never Presented). `None` means "Repair was never Called at
    all" (`repair_called is False`); `False` means "Called, but NOT
    Adopted" (the specific False-Evidence gap the Controller's Review
    confirmed R1 had -- `repair_called` alone was previously used to set
    a Metric's `repair_adopted=True`, crediting an unaccepted Repair).

    R3-WU-02 (IR-P9-2-R2-04 MAJOR fix): `main_called`/`judge_called`/
    `guard_called` are now `bool | None` -- `None` means this Round's real
    Evidence source genuinely cannot tell whether the Component was
    called (Guard's `unavailable_correlation`; an ambiguous Main event
    `code`), and is never collapsed into a confirmed `False`."""

    request_id: str
    main_called: bool | None
    main_outcome: str
    judge_called: bool | None
    judge_outcome: str
    guard_called: bool | None
    guard_outcome: str
    repair_called: bool
    repair_outcome: str
    repair_adopted: bool | None
    final_disposition: str
    assistant_content: str | None
    failure_reason: str | None = None


class ProductionTurnPort(Protocol):
    """The minimum real Phase 9-1 surface this Adapter needs -- deliberately
    narrower than the full `ConversationGenerationService`, so this module
    (and every test against it) never requires a real Model. A concrete
    Bootstrap-layer Adapter (`bootstrap/experiment_production_turn_
    adapter.py`) implements this against the real, live
    `ConversationGenerationService`/`JudgeGovernanceComposition`/
    `GuardrailGovernanceComposition`. `request_id` is never an input here
    -- Phase 9-1's own `ConversationGenerationService.start()` assigns it
    internally; the real value comes back on the returned Observation, and
    is additionally reported early through `on_request_id` (as soon as it
    is known, before the Turn finishes) so a caller (R1-WU-05's
    `ExperimentRunWorker`) can register a real Cancel hook for this
    specific in-flight Run."""

    def run_turn(
        self, *, user_input: str, on_request_id: Callable[[str], None] | None = None
    ) -> ProductionTurnObservation: ...


@dataclass(frozen=True, slots=True)
class ProductionVariantExecution:
    """The full result of one `run_production_turn_variant()` call: the
    real `ProductionTurnObservation` (for `request_id`/`assistant_content`/
    `failure_reason`/`final_disposition`) alongside its projected
    `ActorInvocationRecord`s (for the same Raw Evidence shape a Fixture
    Run's `VariantExecutionResult.invocations` already has)."""

    observation: ProductionTurnObservation
    invocations: tuple[ActorInvocationRecord, ...]


def run_production_turn_variant(
    *,
    port: ProductionTurnPort,
    user_input: str,
    on_request_id: Callable[[str], None] | None = None,
) -> ProductionVariantExecution:
    """R1-WU-03 / R2-WU-02: runs exactly ONE real Production Turn through
    `port` and projects its Observation into `ActorInvocationRecord`s --
    one per `ComponentKey` this Adapter can ever report on (MAIN/JUDGE/
    GUARD/REPAIR; MAIN_GOVERNANCE/DEFINITION_SET/RAG/RECORDING/
    PRESENTATION stay unmodeled here and are reported `outcome=
    "not_observed"`, `called=False`, since this Round's Production
    Adapter does not yet have a real per-Component Evidence source for
    them -- `"not_observed"`, never a fabricated `"off"`/`"not_applicable"`
    that would falsely claim a verified absence rather than an honestly
    unobserved one, R2-WU-02 IR-P9-2-R1-02 fix)."""

    observation = port.run_turn(user_input=user_input, on_request_id=on_request_id)

    def _record(key: ComponentKey, called: bool | None, outcome: str) -> ActorInvocationRecord:
        # R2-WU-02: `outcome` is always reported verbatim, even when
        # `called` is not a confirmed `True` -- R1's own `outcome if
        # called else "off"` here silently discarded a real, honest
        # `outcome` (e.g. Guard's `"unavailable_correlation"`) and
        # replaced it with a fabricated `"off"` the instant `called` was
        # anything but `True`.
        #
        # R3-WU-02 (IR-P9-2-R2-04 fix): `called=None` (this Round's
        # Evidence source genuinely cannot tell) reports Mutation/
        # Evidence/Authority as `None` too -- never folded into a
        # confirmed-zero `False` Call the way R2 always did.
        if called is None:
            return ActorInvocationRecord(
                component_key=key,
                called=None,
                mutation_count=None,
                evidence_count=None,
                authority_exercised=None,
                outcome=outcome,
            )
        return ActorInvocationRecord(
            component_key=key,
            called=called,
            mutation_count=1 if called else 0,
            evidence_count=1 if called else 0,
            authority_exercised=called,
            outcome=outcome,
        )

    unmodeled = (
        ComponentKey.MAIN_GOVERNANCE,
        ComponentKey.DEFINITION_SET,
        ComponentKey.RAG,
        ComponentKey.RECORDING,
        ComponentKey.PRESENTATION,
    )
    invocations = (
        _record(ComponentKey.MAIN, observation.main_called, observation.main_outcome),
        _record(ComponentKey.JUDGE, observation.judge_called, observation.judge_outcome),
        _record(ComponentKey.GUARD, observation.guard_called, observation.guard_outcome),
        _record(ComponentKey.REPAIR, observation.repair_called, observation.repair_outcome),
        *(
            # R3-WU-02 (IR-P9-2-R2-04 fix): these five Components have no
            # real per-Component Evidence source this Round at all -- a
            # genuine `not_observed`, so `called=None`, never the
            # confirmed-`False` R2 reported alongside the same
            # `outcome="not_observed"` string (a direct contradiction: a
            # `bool` `called=False` claims a verified absence).
            ActorInvocationRecord(
                component_key=key,
                called=None,
                mutation_count=None,
                evidence_count=None,
                authority_exercised=None,
                outcome="not_observed",
            )
            for key in unmodeled
        ),
    )
    return ProductionVariantExecution(observation=observation, invocations=invocations)
