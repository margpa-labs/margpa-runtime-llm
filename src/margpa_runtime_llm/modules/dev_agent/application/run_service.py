"""Phase 8 (P8-D/P8-E/P8-CR): the Dev Agent Run/Step engine.

Deliberately synchronous and single-step-per-call (`advance()` executes at
most one Step attempt per invocation) — there is no background thread and no
real concurrency *within* one call. This keeps Max Step/Deadline/Retry/
Cancel/Late-Result discipline simple to reason about and simple to Test
exhaustively, at the cost of not yet being a live streaming Run surface.

P8-E: every state transition is persisted through the optional
`DevAgentRunStorePort` immediately (before returning to the caller), and
every persisted Run is reloaded at Composition time — this is what makes a
Restart/Reload/Shutdown lose nothing already committed, and what makes two
browser tabs hitting this same Service see identical state (there is no
per-connection state to diverge).

P8-CR1: the Service *itself* can be entered concurrently — the REST layer
runs every handler via `asyncio.to_thread()`, so two overlapping requests
for the same Run are two real OS threads inside this object at once. Each
mutating method (`advance`/`submit_approval`/`cancel_run`/
`record_late_result`) therefore acquires a per-Run `threading.Lock` for its
entire read-decide-execute-persist body — never a single Service-wide lock,
so unrelated Runs never serialize against each other. This is a single
local-process guarantee only; Cross-process/Distributed locking is out of
this Task's scope.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from threading import Lock

from ..contracts import (
    DEFAULT_APPROVAL_ACTOR_CLASS,
    SUPPORTED_RESOURCE_SCOPES,
    ApprovalDecision,
    ApprovalEvidence,
    ApprovalProfile,
    AuthorizationEnvelope,
    CapabilityId,
    CompletionApprovalEvidence,
    Plan,
    RetryPolicy,
    RunCompletion,
    RunCompletionOutcome,
    RunSnapshot,
    RunState,
    StepRecord,
    StepState,
    ToolDescriptor,
)
from ..ports import (
    DevAgentRunStorePort,
    ToolExecutionFailed,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
)
from .tool_registry import ToolRegistry


class RunNotFoundError(KeyError):
    pass


class InvalidRunTransitionError(ValueError):
    pass


def _finalize(
    run: RunSnapshot,
    *,
    state: RunState,
    outcome: RunCompletionOutcome,
    reason: str,
) -> RunSnapshot:
    return run.model_copy(
        update={
            "state": state,
            "completion": RunCompletion(outcome=outcome, reason=reason),
        }
    )


def _replace_step(run: RunSnapshot, step_id: str, updated: StepRecord) -> RunSnapshot:
    steps = tuple(updated if step.step_id == step_id else step for step in run.steps)
    return run.model_copy(update={"steps": steps})


def _requires_approval(
    *,
    approval_profile: ApprovalProfile,
    descriptor: ToolDescriptor | None,
    step: StepRecord,
) -> bool:
    important = descriptor is not None and descriptor.important_gate_reason is not None
    if approval_profile is ApprovalProfile.MANUAL:
        return True
    if approval_profile is ApprovalProfile.IMPORTANT_GATE_ONLY:
        return important
    if approval_profile is ApprovalProfile.RISK_BASED:
        return important or step.attempt_count > 0
    # PLAN_ONLY never reaches here — `advance()` short-circuits before any
    # Step is considered for execution.
    return False


def _has_approval_evidence(
    run: RunSnapshot, step: StepRecord, *, descriptor: ToolDescriptor | None
) -> bool:
    """P8-CR5 (P8-CODEX-004): the real gate-bypass check — a Typed
    `ApprovalEvidence` must match this exact `(run_id, step_id, tool_id)`
    triple with an `APPROVED` Decision, and — when the Tool carries an
    Important Gate Reason — the Evidence's own recorded `gate_reason` must
    still match the Tool's *current* Descriptor (guards against a Tool's
    Gate classification drifting between Approval and execution).

    The `run_id` check is not redundant with `run.approvals` "naturally"
    only ever holding this Run's own Evidence: `RunSnapshot` is a Pydantic
    model reconstructible from arbitrary (Store-file/REST) input, so a
    corrupted or tampered payload could carry another Run's Evidence in
    this field. `RunSnapshot.validate_approvals_belong_to_this_run()`
    rejects that at the persistence/REST boundary; this check is the
    second, independent layer that closes the same gap at the point the
    Gate decision is actually made — Defense in Depth, not decoration."""

    expected_gate_reason = descriptor.important_gate_reason if descriptor is not None else None
    return any(
        evidence.run_id == run.run_id
        and evidence.step_id == step.step_id
        and evidence.tool_id == step.tool_id
        and evidence.decision is ApprovalDecision.APPROVED
        and evidence.gate_reason == expected_gate_reason
        for evidence in run.approvals
    )


def _has_completion_evidence(run: RunSnapshot) -> bool:
    """P8-RW6-C (P8-CODEX-007): the Run-level analogue of
    `_has_approval_evidence()` — `True` only if a `CompletionApprovalEvidence`
    scoped to this exact `run_id` with an `APPROVED` Decision exists.
    Structurally distinct from Step Evidence: no Step's `ApprovalEvidence`,
    however it is shaped, can ever satisfy this — `run.approvals` and
    `run.completion_approvals` are different Fields of different Types."""

    return any(
        evidence.run_id == run.run_id and evidence.decision is ApprovalDecision.APPROVED
        for evidence in run.completion_approvals
    )


DEFAULT_RUN_BUDGET_LIMIT = 100
"""P8-RW6-B (P8-CODEX-006): the default `budget_limit` a Run receives when
`start_run()`'s caller doesn't specify one — a `start_run()` parameter
default, not a per-Run sentinel, so every existing caller/Test constructing
a Run without mentioning Budget at all keeps working unchanged, while every
Run this Service creates always has a concrete, non-`None` Limit."""


def _budget_violation(run: RunSnapshot, cost: int) -> bool:
    """P8-RW6-B: `True` if spending `cost` more Budget Units would exceed
    `run.budget_limit`. `budget_limit is None` only for a Run persisted
    before P8-RW6-B existed — Backward Compatibility, not a bypass, mirrors
    `_envelope_violation()`'s treatment of a missing Envelope."""

    return run.budget_limit is not None and run.budget_consumed + cost > run.budget_limit


def _envelope_violation(run: RunSnapshot, step: StepRecord, *, now: datetime) -> str | None:
    """P8-CR2: the Run/Step/Tool/Resource/Expiry check `advance()` performs
    immediately before calling into a Tool Port. Returns `None` (no
    violation) or a short machine-readable reason. A Run persisted before
    P8-CR2 has `envelope is None` — Backward Compatibility, not a bypass:
    there is no second Tool surface such a legacy Run could have drifted
    onto, so a missing Envelope has nothing to guard against here."""

    envelope = run.envelope
    if envelope is None:
        return None
    if envelope.run_id != run.run_id:
        return "run_identity_mismatch"
    if step.step_id not in envelope.allowed_step_ids:
        return "step_not_authorized"
    if step.tool_id not in envelope.allowed_tool_ids:
        return "tool_not_authorized"
    if envelope.resource_scope not in SUPPORTED_RESOURCE_SCOPES:
        return "resource_scope_unsupported"
    if envelope.expires_at is not None and now.isoformat() >= envelope.expires_at:
        return "envelope_expired"
    return None


class DevAgentRunService:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[], str] | None = None,
        run_store: DevAgentRunStorePort | None = None,
    ) -> None:
        self._tool_registry = tool_registry
        self._clock = clock or (lambda: datetime.now(UTC))
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)
        self._run_store = run_store
        self._runs: dict[str, RunSnapshot] = {}
        self._locks_guard = Lock()
        self._run_locks: dict[str, Lock] = {}
        if run_store is not None:
            for run in run_store.load_all():
                self._runs[run.run_id] = run

    def _lock_for(self, run_id: str) -> Lock:
        """P8-CR1: one `Lock` per `run_id`, created on first use. Guarded by
        a small separate meta-lock so two threads racing to create the
        *first* Lock for the same brand-new `run_id` can never end up with
        two different Lock objects (which would defeat the whole point)."""

        with self._locks_guard:
            lock = self._run_locks.get(run_id)
            if lock is None:
                lock = Lock()
                self._run_locks[run_id] = lock
            return lock

    def _persist(self, run: RunSnapshot) -> RunSnapshot:
        self._runs[run.run_id] = run
        if self._run_store is not None:
            self._run_store.save(run)
        return run

    def start_run(
        self,
        *,
        capability_id: CapabilityId,
        plan: Plan,
        approval_profile: ApprovalProfile,
        max_steps: int,
        retry_policy: RetryPolicy,
        deadline_seconds: float | None = None,
        constitution_mode: str | None = None,
        constitution_rule_ids: tuple[str, ...] | None = None,
        budget_limit: int = DEFAULT_RUN_BUDGET_LIMIT,
    ) -> RunSnapshot:
        run_id = self._id_factory()
        now = self._clock()
        deadline_at = (
            (now + timedelta(seconds=deadline_seconds)).isoformat()
            if deadline_seconds is not None
            else None
        )
        steps = tuple(
            StepRecord(step_id=step.step_id, tool_id=step.tool_id, state=StepState.PENDING)
            for step in plan.steps
        )
        envelope = self._issue_envelope(
            run_id=run_id,
            plan=plan,
            max_steps=max_steps,
            retry_policy=retry_policy,
            expires_at=deadline_at,
            issued_at=now,
        )
        run = RunSnapshot(
            run_id=run_id,
            capability_id=capability_id,
            plan=plan,
            approval_profile=approval_profile,
            retry_policy=retry_policy,
            max_steps=max_steps,
            state=RunState.RUNNING,
            steps=steps,
            created_at=now.isoformat(),
            deadline_at=deadline_at,
            completion=None,
            constitution_mode=constitution_mode,
            constitution_rule_ids=constitution_rule_ids,
            envelope=envelope,
            budget_limit=budget_limit,
        )
        return self._persist(run)

    def _issue_envelope(
        self,
        *,
        run_id: str,
        plan: Plan,
        max_steps: int,
        retry_policy: RetryPolicy,
        expires_at: str | None,
        issued_at: datetime,
    ) -> AuthorizationEnvelope:
        """P8-CR2: the one place an `AuthorizationEnvelope` is ever
        constructed — always here, inside `start_run()`, always derived from
        the Server's own Plan/Limits, never from caller input
        (`DevAgentStartRunRequest` carries no Envelope-shaped field)."""

        allowed_step_ids = tuple(step.step_id for step in plan.steps)
        allowed_tool_ids = tuple(dict.fromkeys(step.tool_id for step in plan.steps))
        gate_reasons = tuple(
            dict.fromkeys(
                descriptor.important_gate_reason
                for step in plan.steps
                if (descriptor := self._tool_registry.get_descriptor(step.tool_id)) is not None
                and descriptor.important_gate_reason is not None
            )
        )
        return AuthorizationEnvelope(
            run_id=run_id,
            allowed_step_ids=allowed_step_ids,
            allowed_tool_ids=allowed_tool_ids,
            resource_scope="fixture_only",
            max_steps=max_steps,
            max_attempts=retry_policy.max_attempts,
            expires_at=expires_at,
            gate_reasons=gate_reasons,
            issued_at=issued_at.isoformat(),
        )

    def get_run(self, run_id: str) -> RunSnapshot | None:
        return self._runs.get(run_id)

    def list_tool_descriptors(self) -> tuple[ToolDescriptor, ...]:
        return self._tool_registry.list_descriptors()

    def _require_run(self, run_id: str) -> RunSnapshot:
        run = self._runs.get(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return run

    def advance(self, run_id: str) -> RunSnapshot:
        """P8-CR1: the per-Run Lock is held for this entire call, including
        the Tool Port `execute()` call inside it — so a second concurrent
        `advance()` for the same `run_id` blocks until this one has fully
        persisted its result, then observes the *updated* Step state (no
        longer `PENDING`) and moves on to the next Step or finalizes,
        instead of re-executing the same Tool a second time."""

        with self._lock_for(run_id):
            return self._advance_locked(run_id)

    def _advance_locked(self, run_id: str) -> RunSnapshot:
        run = self._require_run(run_id)
        if run.state in (RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED):
            return run
        if run.state in (RunState.AWAITING_APPROVAL, RunState.AWAITING_COMPLETION_APPROVAL):
            return run

        if run.approval_profile is ApprovalProfile.PLAN_ONLY:
            run = _finalize(
                run,
                state=RunState.COMPLETED,
                outcome="plan_only",
                reason="Plan-only Profile: the Plan was produced but no Step was executed.",
            )
            return self._persist(run)

        next_step = next((s for s in run.steps if s.state is StepState.PENDING), None)
        if next_step is None:
            # P8-RW6-C (P8-CODEX-007): `important_gate_only` treats
            # Completion itself as an Important-Gated Run Lifecycle event
            # (ImportantGateReason.COMPLETION) — every Step already
            # succeeded, but the Run does not auto-finalize until a human
            # explicitly approves Completion too.
            if (
                run.approval_profile is ApprovalProfile.IMPORTANT_GATE_ONLY
                and not _has_completion_evidence(run)
            ):
                run = run.model_copy(update={"state": RunState.AWAITING_COMPLETION_APPROVAL})
                return self._persist(run)
            run = _finalize(
                run,
                state=RunState.COMPLETED,
                outcome="completed",
                reason="All Plan Steps completed successfully.",
            )
            return self._persist(run)

        if run.deadline_at is not None and self._clock().isoformat() >= run.deadline_at:
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="deadline_exceeded",
                reason="The Run's Deadline elapsed before this Step could start.",
            )
            return self._persist(run)

        started_count = sum(
            1 for s in run.steps if s.attempt_count > 0 or s.state is not StepState.PENDING
        )
        if started_count >= run.max_steps:
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="max_steps_exceeded",
                reason="The Run's Max Step limit was reached before the Plan finished.",
            )
            return self._persist(run)

        descriptor = self._tool_registry.get_descriptor(next_step.tool_id)
        # P8-CR5 (P8-CODEX-004): Typed `ApprovalEvidence` is the sole Gate
        # bypass authority for any Run that has an Envelope (i.e. every Run
        # created since P8-CR2) — `StepRecord.approved` alone can never pass
        # the Gate for such a Run. The legacy bool remains a fallback only
        # for a Pre-P8-CR2 Run (`envelope is None`), which never had Typed
        # Evidence to begin with.
        gate_satisfied = _has_approval_evidence(run, next_step, descriptor=descriptor)
        if run.envelope is None:
            gate_satisfied = gate_satisfied or next_step.approved
        if (
            _requires_approval(
                approval_profile=run.approval_profile, descriptor=descriptor, step=next_step
            )
            and not gate_satisfied
        ):
            run = _replace_step(
                run,
                next_step.step_id,
                next_step.model_copy(update={"state": StepState.AWAITING_APPROVAL}),
            )
            run = run.model_copy(update={"state": RunState.AWAITING_APPROVAL})
            return self._persist(run)

        violation = _envelope_violation(run, next_step, now=self._clock())
        if violation is not None:
            run = _replace_step(
                run,
                next_step.step_id,
                next_step.model_copy(
                    update={
                        "state": StepState.FAILED,
                        "error": f"authority_denied: {violation}",
                        "completed_at": self._clock().isoformat(),
                    }
                ),
            )
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="authority_denied",
                reason=(
                    f"Step '{next_step.step_id}' fell outside its Run's Authorization "
                    f"Envelope ({violation}) — never executed."
                ),
            )
            return self._persist(run)

        # P8-RW6-B (P8-CODEX-006): checked immediately before execution, the
        # same position as the Envelope check above — a Step whose Tool
        # would push `budget_consumed` past `budget_limit` never reaches
        # `_execute()` at all.
        cost = descriptor.budget_cost if descriptor is not None else 1
        if _budget_violation(run, cost):
            run = _replace_step(
                run,
                next_step.step_id,
                next_step.model_copy(
                    update={
                        "state": StepState.FAILED,
                        "error": (
                            f"budget_exceeded: {run.budget_consumed}+{cost} > {run.budget_limit}"
                        ),
                        "completed_at": self._clock().isoformat(),
                    }
                ),
            )
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="budget_exceeded",
                reason=(
                    f"Step '{next_step.step_id}' would exceed the Run's Budget Limit "
                    f"({run.budget_consumed}+{cost} > {run.budget_limit}) — never executed."
                ),
            )
            return self._persist(run)

        outcome = self._execute(run.plan, next_step)
        # Budget is charged for the attempt itself, whether it succeeds or
        # fails — mirrors a real costly operation not being free just
        # because it failed.
        run = run.model_copy(update={"budget_consumed": run.budget_consumed + cost})
        attempt_count = next_step.attempt_count + 1
        if isinstance(outcome, ToolExecutionSucceeded):
            run = _replace_step(
                run,
                next_step.step_id,
                next_step.model_copy(
                    update={
                        "state": StepState.SUCCEEDED,
                        "attempt_count": attempt_count,
                        "output": outcome.output,
                        "error": None,
                        "completed_at": self._clock().isoformat(),
                    }
                ),
            )
            return self._persist(run)

        if attempt_count < run.retry_policy.max_attempts:
            run = _replace_step(
                run,
                next_step.step_id,
                next_step.model_copy(
                    update={"attempt_count": attempt_count, "error": outcome.reason}
                ),
            )
            return self._persist(run)

        run = _replace_step(
            run,
            next_step.step_id,
            next_step.model_copy(
                update={
                    "state": StepState.FAILED,
                    "attempt_count": attempt_count,
                    "error": outcome.reason,
                    "completed_at": self._clock().isoformat(),
                }
            ),
        )
        run = _finalize(
            run,
            state=RunState.FAILED,
            outcome="tool_failure",
            reason=(
                f"Step '{next_step.step_id}' failed after {attempt_count} attempt(s): "
                f"{outcome.reason}"
            ),
        )
        return self._persist(run)

    def _execute(self, plan: Plan, step: StepRecord) -> ToolExecutionOutcome:
        port = self._tool_registry.get_port(step.tool_id)
        if port is None:
            return ToolExecutionFailed(reason="unknown_tool")
        plan_step = next(s for s in plan.steps if s.step_id == step.step_id)
        return port.execute(step.tool_id, plan_step.input)

    def submit_approval(self, run_id: str, step_id: str, decision: ApprovalDecision) -> RunSnapshot:
        with self._lock_for(run_id):
            return self._submit_approval_locked(run_id, step_id, decision)

    def _submit_approval_locked(
        self, run_id: str, step_id: str, decision: ApprovalDecision
    ) -> RunSnapshot:
        run = self._require_run(run_id)
        if run.state is not RunState.AWAITING_APPROVAL:
            raise InvalidRunTransitionError(
                f"Run '{run_id}' is not currently Awaiting Approval (state={run.state})."
            )
        target = next((s for s in run.steps if s.state is StepState.AWAITING_APPROVAL), None)
        if target is None or target.step_id != step_id:
            raise InvalidRunTransitionError(
                f"Step '{step_id}' is not the Step currently Awaiting Approval for Run '{run_id}'."
            )

        # P8-CR2: every Decision (approved or denied) becomes Typed Evidence
        # scoped to exactly this `(run_id, step_id, tool_id)` triple —
        # persisted with the Run, so it survives Restart and can never be
        # read back as authorizing a different Step, Tool, or Run.
        descriptor = self._tool_registry.get_descriptor(target.tool_id)
        evidence = ApprovalEvidence(
            run_id=run_id,
            step_id=step_id,
            tool_id=target.tool_id,
            decision=decision,
            actor_class=DEFAULT_APPROVAL_ACTOR_CLASS,
            decided_at=self._clock().isoformat(),
            gate_reason=descriptor.important_gate_reason if descriptor is not None else None,
        )
        run = run.model_copy(update={"approvals": (*run.approvals, evidence)})

        if decision is ApprovalDecision.DENIED:
            run = _replace_step(run, step_id, target.model_copy(update={"state": StepState.DENIED}))
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="approval_denied",
                reason=f"Approval for Step '{step_id}' was denied.",
            )
            return self._persist(run)

        # `approved` on the `StepRecord` itself remains a Backward-Compatible
        # cache of the same fact the `ApprovalEvidence` above now carries as
        # the real source of truth (P8-CR2) — kept so a Restart between
        # Approval and execution never re-asks, same as before.
        run = _replace_step(
            run,
            step_id,
            target.model_copy(update={"state": StepState.PENDING, "approved": True}),
        )
        run = run.model_copy(update={"state": RunState.RUNNING})
        return self._persist(run)

    def submit_completion_approval(self, run_id: str, decision: ApprovalDecision) -> RunSnapshot:
        """P8-RW6-C (P8-CODEX-007): the Run-level counterpart of
        `submit_approval()` — no `step_id`/`tool_id` parameter exists at
        all, because Completion is a Run Lifecycle event, not a Step's
        Tool call."""

        with self._lock_for(run_id):
            return self._submit_completion_approval_locked(run_id, decision)

    def _submit_completion_approval_locked(
        self, run_id: str, decision: ApprovalDecision
    ) -> RunSnapshot:
        run = self._require_run(run_id)
        if run.state is not RunState.AWAITING_COMPLETION_APPROVAL:
            raise InvalidRunTransitionError(
                f"Run '{run_id}' is not currently Awaiting Completion Approval (state={run.state})."
            )

        evidence = CompletionApprovalEvidence(
            run_id=run_id,
            decision=decision,
            actor_class=DEFAULT_APPROVAL_ACTOR_CLASS,
            decided_at=self._clock().isoformat(),
        )
        run = run.model_copy(update={"completion_approvals": (*run.completion_approvals, evidence)})

        if decision is ApprovalDecision.DENIED:
            run = _finalize(
                run,
                state=RunState.FAILED,
                outcome="approval_denied",
                reason=f"Completion Approval for Run '{run_id}' was denied.",
            )
            return self._persist(run)

        # The next `advance()` call re-enters the "no PENDING Step" branch,
        # finds `_has_completion_evidence(run)` now `True`, and finalizes to
        # `completed` — the same one-transition-per-call discipline every
        # other Gate in this Service already follows.
        run = run.model_copy(update={"state": RunState.RUNNING})
        return self._persist(run)

    def cancel_run(self, run_id: str) -> RunSnapshot:
        with self._lock_for(run_id):
            return self._cancel_run_locked(run_id)

    def _cancel_run_locked(self, run_id: str) -> RunSnapshot:
        run = self._require_run(run_id)
        if run.state in (RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED):
            return run
        cancellable = {StepState.PENDING, StepState.RUNNING, StepState.AWAITING_APPROVAL}
        steps = tuple(
            step.model_copy(update={"state": StepState.CANCELLED})
            if step.state in cancellable
            else step
            for step in run.steps
        )
        run = run.model_copy(update={"steps": steps})
        run = _finalize(
            run, state=RunState.CANCELLED, outcome="cancelled", reason="Run was cancelled."
        )
        return self._persist(run)

    def record_late_result(
        self, run_id: str, step_id: str, outcome: ToolExecutionOutcome
    ) -> RunSnapshot:
        """P8-D Late-Result-rejection: models a Tool Result that arrives
        after its Run already finalized (e.g. an async call still in flight
        at Cancel time). `outcome` is intentionally discarded — it is never
        written into any `StepRecord.output` — this method only records
        that a late arrival happened, for observability."""

        with self._lock_for(run_id):
            return self._record_late_result_locked(run_id, step_id, outcome)

    def _record_late_result_locked(
        self, run_id: str, step_id: str, outcome: ToolExecutionOutcome
    ) -> RunSnapshot:
        del outcome
        run = self._require_run(run_id)
        if run.state not in (RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED):
            raise InvalidRunTransitionError(
                "record_late_result only applies to a Run that has already finalized "
                "(it models a race between async completion and Run finalization)."
            )
        target = next((s for s in run.steps if s.step_id == step_id), None)
        if target is not None and target.state is StepState.CANCELLED:
            run = _replace_step(
                run, step_id, target.model_copy(update={"state": StepState.LATE_REJECTED})
            )
            return self._persist(run)
        return run
