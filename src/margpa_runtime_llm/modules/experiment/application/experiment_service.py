"""Experiment Core Minimal API (Phase 9-2, WU-A A4).

Plan creation, Run start, status read, Cancel, and result read -- the
five operations WU-A A4 names as the minimum, exposed as a plain Python
class rather than a fixed HTTP/UI contract (WU-A A4: "Phase 10右Panel
向け最終APIへ固定せず、Versioned Port/DTOとする"). A Web route layer
(WU-A/E) wraps this unchanged; this class itself has no FastAPI or
frontend dependency.

Late-Result rejection (WU-A A3): each `start_run()` call establishes a
fresh in-memory `generation` counter for that `run_id`; `publish_result()`
rejects any call whose `generation` is not the current one, so a stale
in-flight Call that finishes after a newer generation (or after the Run
already reached a terminal state) can never overwrite a more recent or
already-terminal result. This counter is process-local by design -- it
is a race guard against concurrent same-process publishers, not itself
the durable state (`ExperimentStorePort` is)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Literal

from ..domain.errors import ExperimentCoreError, ExperimentCoreErrorCode
from ..domain.identity import ExperimentPlan, StopPolicy
from ..domain.run import RunState, VariantRun, is_terminal, validate_transition
from ..ports import ExperimentStorePort


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class VariantRunResult:
    run: VariantRun
    raw_evidence: dict[str, object] | None


def _next_startable_variant_id(
    *, plan: ExperimentPlan, existing_runs: tuple[VariantRun, ...]
) -> str | None:
    """R1-WU-02: only consulted when `plan.budget.stop_policy` is set --
    walks `plan.execution_order` and returns the one `variant_id` allowed
    to start next, or `None` if nothing may start right now: an earlier
    Variant in the order is still in flight (not yet terminal), a prior
    Variant Failed under `HALT_ON_FIRST_FAILURE`, or every Variant already
    has a terminal Run (the Plan is exhausted)."""

    runs_by_variant: dict[str, list[VariantRun]] = {}
    for run in existing_runs:
        runs_by_variant.setdefault(run.variant_id, []).append(run)
    for variant_id in plan.execution_order:
        runs_for_variant = runs_by_variant.get(variant_id, [])
        if not runs_for_variant:
            return variant_id
        if any(not is_terminal(run.state) for run in runs_for_variant):
            return None
        if plan.budget.stop_policy is StopPolicy.HALT_ON_FIRST_FAILURE and any(
            run.state is RunState.FAILED for run in runs_for_variant
        ):
            return None
    return None


class ExperimentService:
    def __init__(self, *, store: ExperimentStorePort) -> None:
        self._store = store
        self._lock = Lock()
        self._generations: dict[str, int] = {}

    @property
    def store(self) -> ExperimentStorePort:
        """Read-only access to the underlying `ExperimentStorePort` -- WU-F
        F1's `comparison_service.build_comparison_report()` reads every
        persisted `VariantRun`/Raw Evidence back out through this same
        Port rather than a second, parallel bookkeeping structure."""

        return self._store

    def create_plan(self, plan: ExperimentPlan) -> ExperimentPlan:
        with self._lock:
            if self._store.load_plan(plan.experiment_id) is not None:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                    safe_message=f"experiment_id {plan.experiment_id!r} already has a Plan",
                )
            self._store.save_plan(plan)
            return plan

    def start_run(
        self,
        *,
        experiment_id: str,
        variant_id: str,
        run_id: str,
        request_id: str,
        execution_mode: Literal["fixture", "production"],
    ) -> VariantRun:
        with self._lock:
            plan = self._store.load_plan(experiment_id)
            if plan is None:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.NOT_FOUND,
                    safe_message=f"experiment_id {experiment_id!r} has no Plan",
                )
            # Raises UNKNOWN_VARIANT itself if variant_id is not in the Plan.
            plan.variant(variant_id)
            if self._store.load_run(run_id) is not None:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                    safe_message=f"run_id {run_id!r} already exists",
                )
            existing_runs = self._store.list_runs(experiment_id)
            # R1-WU-02 (IR-P9-2-06 fix): `max_variant_runs`/Execution Order
            # are enforced HERE, before any Run object (let alone an Actor
            # Call) is created -- a violation is Call 0, never a Run that
            # starts and then gets cut short.
            if (
                plan.budget.max_variant_runs is not None
                and len(existing_runs) >= plan.budget.max_variant_runs
            ):
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.MAX_VARIANT_RUNS_EXCEEDED,
                    safe_message=(
                        f"experiment_id {experiment_id!r} already has "
                        f"{len(existing_runs)} Run(s), at its budget.max_variant_runs="
                        f"{plan.budget.max_variant_runs} limit"
                    ),
                )
            if plan.budget.stop_policy is not None:
                next_allowed = _next_startable_variant_id(plan=plan, existing_runs=existing_runs)
                if next_allowed != variant_id:
                    raise ExperimentCoreError(
                        code=ExperimentCoreErrorCode.EXECUTION_ORDER_VIOLATION,
                        safe_message=(
                            f"variant_id {variant_id!r} may not start next for "
                            f"experiment_id {experiment_id!r} under stop_policy="
                            f"{plan.budget.stop_policy.value!r} "
                            f"(next allowed: {next_allowed!r})"
                        ),
                    )
            # Genuinely passes through `planned` before `running` (both
            # persisted) rather than materializing directly in `running`:
            # a crash between the two saves leaves a Restart-readable
            # `planned` Run, never an unrecorded one, and the
            # `planned -> running` edge in `_ALLOWED_TRANSITIONS` stays a
            # real, reachable transition rather than dead code.
            planned = VariantRun(
                run_id=run_id,
                experiment_id=experiment_id,
                variant_id=variant_id,
                request_id=request_id,
                execution_mode=execution_mode,
                state=RunState.PLANNED,
                generation=1,
            )
            self._store.save_run(planned)
            validate_transition(planned.state, RunState.RUNNING)
            running = planned.model_copy(
                update={"state": RunState.RUNNING, "started_at": _now_iso()}
            )
            self._store.save_run(running)
            self._generations[run_id] = 1
            return running

    def get_run(self, run_id: str) -> VariantRun:
        run = self._store.load_run(run_id)
        if run is None:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.NOT_FOUND,
                safe_message=f"run_id {run_id!r} does not exist",
            )
        return run

    def list_runs(self, experiment_id: str) -> tuple[VariantRun, ...]:
        return self._store.list_runs(experiment_id)

    def cancel_run(self, run_id: str) -> VariantRun:
        with self._lock:
            run = self.get_run(run_id)
            validate_transition(run.state, RunState.CANCELLED)
            updated = run.model_copy(
                update={"state": RunState.CANCELLED, "completed_at": _now_iso()}
            )
            self._store.save_run(updated)
            self._generations[run_id] = self._generations.get(run_id, run.generation) + 1
            return updated

    def publish_result(
        self,
        run_id: str,
        *,
        generation: int,
        target_state: RunState,
        failure_reason: str | None = None,
        raw_evidence: dict[str, object] | None = None,
    ) -> VariantRun:
        with self._lock:
            run = self.get_run(run_id)
            current_generation = self._generations.get(run_id, run.generation)
            if generation != current_generation or is_terminal(run.state):
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.LATE_RESULT_REJECTED,
                    safe_message=(
                        f"run_id {run_id!r} rejected a stale publish "
                        f"(generation={generation}, current={current_generation}, "
                        f"state={run.state.value})"
                    ),
                )
            validate_transition(run.state, target_state)
            updated = run.model_copy(
                update={
                    "state": target_state,
                    "completed_at": _now_iso(),
                    "failure_reason": failure_reason,
                }
            )
            # R1-WU-05: Raw Evidence is persisted BEFORE the terminal
            # state transition, never after -- `get_run()`/`get_result()`
            # take no lock (by design: reads must never block a
            # concurrent Worker's publish), so a concurrent Web request
            # polling a Run started asynchronously could otherwise
            # observe `state=completed` with `raw_evidence=None` in the
            # window between two separate writes. Once a reader observes
            # a terminal `state`, its Raw Evidence (if any) is always
            # already fully written.
            if raw_evidence is not None:
                self._store.save_raw_evidence(run_id, raw_evidence)
            self._store.save_run(updated)
            return updated

    def get_result(self, run_id: str) -> VariantRunResult:
        run = self.get_run(run_id)
        return VariantRunResult(run=run, raw_evidence=self._store.load_raw_evidence(run_id))

    def reconcile_orphaned_running_runs(self) -> tuple[VariantRun, ...]:
        """R2-WU-04 (IR-P9-2-R1-06 fix): called exactly once, at process
        start (`bootstrap.web_application.build_phase1_web_runtime`),
        BEFORE this fresh `ExperimentService`/`ExperimentRunWorker` pair
        ever accepts a new Run. A `planned`/`running` Run found here was
        left behind by a PREVIOUS process (a crash, or an ordinary
        restart) -- this process's own `_generations` counter and
        `ExperimentRunWorker` have no Task backing it and never will, so
        without this it would show `running` forever rather than ever
        reaching a real terminal state. Each is force-terminated to
        `CANCELLED`/`failure_reason="interrupted_by_restart"` -- `CANCELLED`
        (never `COMPLETED`, and never `FAILED` either) is the one target
        state `_ALLOWED_TRANSITIONS` (`domain/run.py`) permits from BOTH
        `planned` and `running`, and it is the honest description here: this
        Run's own Actor was never observed to fail on its own terms, its
        lifecycle was simply cut short by the process that was running it."""

        with self._lock:
            orphans = [
                run
                for run in self._store.list_all_runs()
                if run.state in (RunState.PLANNED, RunState.RUNNING)
            ]
            reconciled: list[VariantRun] = []
            for run in orphans:
                validate_transition(run.state, RunState.CANCELLED)
                updated = run.model_copy(
                    update={
                        "state": RunState.CANCELLED,
                        "completed_at": _now_iso(),
                        "failure_reason": "interrupted_by_restart",
                    }
                )
                self._store.save_run(updated)
                self._generations[run.run_id] = run.generation + 1
                reconciled.append(updated)
            return tuple(reconciled)
