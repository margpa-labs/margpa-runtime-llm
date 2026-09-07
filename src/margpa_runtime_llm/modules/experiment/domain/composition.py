"""Variant Composition and Multi-Governance Result Contracts (Phase 9-2, WU-C).

`ActorInvocationRecord`/`VariantExecutionResult` are what the Independence
Matrix (WU-C C3) Hard Asserts against: for a Component that is absent,
`mode="off"`, or has no registered Actor, the Composition Runner
(`application/composition_runner.py`) never calls that Actor's `invoke()`
at all -- there is no `ActorInvocationRecord` with `called=True` for that
`component_key`, ever, for that Variant Run.

`GovernanceCompositionResult`/`resolve_governance_composition()` are
WU-C C4's Multiple-Definition Conflict/Suppression/Routing/Repair-
Propagation Contract -- `repair_propagation` can only ever be one of the
explicitly registered Actor identities (never invented ad hoc for an
unregistered one, WU-C C4: "未登録Actorへ Authorityを自動生成しない")."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import ComponentKey, require_safe_identifier


class ActorInvocationRecord(ImmutableContract):
    """One Component's real observed involvement in one Variant Run --
    a genuine THREE-state Contract (R3-WU-02, IR-P9-2-R2-04 MAJOR fix):

    - `called=True` ("observed_called"): the Actor's `invoke()` genuinely
      ran; `mutation_count`/`evidence_count`/`authority_exercised` are
      concrete, known values (never `None`).
    - `called=False` ("observed_not_called"): a CONFIRMED negative -- the
      Composition Runner is certain this Actor's `invoke()` never ran
      (absent/off/unregistered, or a Fixture's own deterministic Call
      Zero). `mutation_count`/`evidence_count` are always exactly `0` and
      `authority_exercised` is always exactly `False`, enforced below.
    - `called=None` ("not_observed" / `unavailable_correlation`): this
      Round's Evidence source genuinely cannot tell whether this Actor was
      called at all (e.g. Guard has no request-scoped correlation
      anywhere in this codebase; an ambiguous Main event `code` reachable
      from both a pre- and post-call path). `mutation_count`/
      `evidence_count`/`authority_exercised` MUST also all be `None` --
      Handoff R3 SS5.1's "未観測時はcalled、Mutation Count、Evidence
      Count、Authorityを`None`...にし、False/0へ固定しない" is enforced
      as a single all-or-nothing state, never a partial guess."""

    component_key: ComponentKey
    called: bool | None
    mutation_count: int | None = 0
    evidence_count: int | None = 0
    authority_exercised: bool | None = False
    outcome: str = "not_run"

    @model_validator(mode="after")
    def _validate_called_state_consistency(self) -> ActorInvocationRecord:
        if self.called is None:
            if (
                self.mutation_count is not None
                or self.evidence_count is not None
                or self.authority_exercised is not None
            ):
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
                    safe_message=(
                        f"component {self.component_key.value!r} reports called=None "
                        "(not_observed) but a non-None Mutation/Evidence/Authority -- an "
                        "unobserved Component must leave all three as None, never a partial "
                        "guess"
                    ),
                )
            return self
        if self.called is False:
            if (
                self.mutation_count != 0
                or self.evidence_count != 0
                or self.authority_exercised is not False
            ):
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
                    safe_message=(
                        f"component {self.component_key.value!r} reports called=False but "
                        "non-zero Mutation/Evidence/Authority -- a Component the Runner "
                        "confirmed it never invoked must report exactly zero of each"
                    ),
                )
            return self
        if (
            self.mutation_count is None
            or self.evidence_count is None
            or self.authority_exercised is None
        ):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
                safe_message=(
                    f"component {self.component_key.value!r} reports called=True but a "
                    "None Mutation/Evidence/Authority -- a confirmed Call must report "
                    "concrete values for all three"
                ),
            )
        return self


class VariantExecutionResult(ImmutableContract):
    variant_id: str
    invocations: tuple[ActorInvocationRecord, ...] = ()

    @model_validator(mode="after")
    def _validate_ids_and_unique_components(self) -> VariantExecutionResult:
        require_safe_identifier(self.variant_id, field_name="variant_id")
        keys = [item.component_key for item in self.invocations]
        if len(keys) != len(set(keys)):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                safe_message=(
                    f"variant execution {self.variant_id!r} reports the same "
                    "component_key more than once"
                ),
            )
        return self

    def invocation(self, key: ComponentKey) -> ActorInvocationRecord | None:
        for item in self.invocations:
            if item.component_key is key:
                return item
        return None

    def was_called(self, key: ComponentKey) -> bool:
        """`True` only for a CONFIRMED Call -- `called=None` (not_observed)
        is never conflated with a confirmed `True` here."""

        record = self.invocation(key)
        return record is not None and record.called is True


@runtime_checkable
class ActorPort(Protocol):
    """WU-C C2: a single, generic shape shared by every Component kind
    (Main/Judge/Guard/Main Governance/RAG/Repair/Recording/Presentation/
    Definition Set) -- Experiment Core never has a Main-specific or
    Judge-specific Port; a concrete Adapter (Fixture or Production) knows
    what its own `invoke()` actually does."""

    def invoke(self, *, component_key: ComponentKey, mode: str | None) -> ActorInvocationRecord: ...


class RepairOrigin(StrEnum):
    """WU-C C4: `OTHER_REGISTERED_ACTOR` is a real, distinct value -- not
    a catch-all default an unregistered caller can silently fall into
    (`resolve_governance_composition()` rejects an unregistered
    `repair_requested_by` outright, it never maps it to this value)."""

    JUDGE = "judge"
    MAIN_GOVERNANCE = "main_governance"
    JUDGE_AND_MAIN = "judge_and_main"
    OTHER_REGISTERED_ACTOR = "other_registered_actor"


class DefinitionVerdictOutcome(StrEnum):
    MATCH = "match"
    CONFLICT = "conflict"
    NO_MATCH = "no_match"


class DefinitionVerdict(ImmutableContract):
    definition_id: str
    outcome: DefinitionVerdictOutcome
    authority_weight: int = 0

    @model_validator(mode="after")
    def _validate_id(self) -> DefinitionVerdict:
        require_safe_identifier(self.definition_id, field_name="definition_id")
        return self


class RoutingStrategyKind(StrEnum):
    MANUAL = "manual"
    STATIC = "static"
    DYNAMIC = "dynamic"


@runtime_checkable
class RoutingStrategyPort(Protocol):
    """WU-C C4: Manual/Static/Dynamic Routing are compared as interchangeable
    Strategy Adapters over the identical `verdicts` input -- Experiment
    Core's own resolution logic (`resolve_governance_composition`) never
    hard-codes which strategy "wins"; it only ever asks the supplied
    Strategy which Definitions are Selected vs. Suppressed among the ones
    already known to MATCH."""

    kind: RoutingStrategyKind

    def select(
        self, matches: tuple[DefinitionVerdict, ...]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Returns (selected_definition_ids, suppressed_definition_ids) --
        both drawn only from `matches`' own `definition_id`s."""
        ...


class GovernanceCompositionResult(ImmutableContract):
    selected: tuple[str, ...] = ()
    suppressed: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    routing_strategy_used: RoutingStrategyKind
    repair_propagation: RepairOrigin | None = None


def resolve_governance_composition(
    *,
    verdicts: tuple[DefinitionVerdict, ...],
    routing: RoutingStrategyPort,
    repair_requested_by: str | None,
    registered_actors: frozenset[str],
) -> GovernanceCompositionResult:
    """WU-C C4: `conflicts` is always exactly the `CONFLICT`-outcome
    Definitions, independent of Routing -- a Strategy chooses among
    `MATCH`-outcome Definitions only, never resolves a `CONFLICT` into a
    silent match. `repair_requested_by`, if given, must already be a
    registered Actor identity (WU-C C4: "未登録Actorへ Authorityを自動
    生成しない") -- `judge`/`main_governance`/`judge_and_main` are always
    implicitly registered; anything else must appear in
    `registered_actors` or this raises."""

    conflicts = tuple(
        verdict.definition_id
        for verdict in verdicts
        if verdict.outcome is DefinitionVerdictOutcome.CONFLICT
    )
    matches = tuple(
        verdict for verdict in verdicts if verdict.outcome is DefinitionVerdictOutcome.MATCH
    )
    selected, suppressed = routing.select(matches)

    propagation: RepairOrigin | None = None
    if repair_requested_by is not None:
        implicit = {
            origin.value
            for origin in RepairOrigin
            if origin is not RepairOrigin.OTHER_REGISTERED_ACTOR
        }
        if repair_requested_by in implicit:
            propagation = RepairOrigin(repair_requested_by)
        elif repair_requested_by in registered_actors:
            propagation = RepairOrigin.OTHER_REGISTERED_ACTOR
        else:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.UNREGISTERED_REPAIR_ACTOR,
                safe_message=(
                    f"repair_requested_by {repair_requested_by!r} is not a registered Actor "
                    "-- Authority is never auto-granted to an unregistered requester"
                ),
            )

    return GovernanceCompositionResult(
        selected=selected,
        suppressed=suppressed,
        conflicts=conflicts,
        routing_strategy_used=routing.kind,
        repair_propagation=propagation,
    )
