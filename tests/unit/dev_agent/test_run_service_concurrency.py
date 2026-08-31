"""Unit tests for Phase 8 (P8-CR1) DevAgentRunService Concurrent Transition
Atomicity: real `threading.Thread`s racing `advance`/`submit_approval`/
`cancel_run` against the same Run, proving a single local process never
double-executes a Tool and never lands on a torn/inconsistent State."""

from __future__ import annotations

from collections.abc import Mapping
from threading import Barrier, Event, Lock, Thread

from margpa_runtime_llm.modules.dev_agent import (
    ApprovalDecision,
    ApprovalProfile,
    CapabilityId,
    DevAgentRunService,
    InvalidRunTransitionError,
    Plan,
    PlanStep,
    RetryPolicy,
    RunSnapshot,
    RunState,
    StepState,
    ToolDescriptor,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
    ToolRegistry,
)


class BlockingCountingPort:
    """A Tool that blocks inside `execute()` until released, so a Test can
    force two `advance()` calls to genuinely overlap in time rather than
    merely run one after another too fast to matter."""

    def __init__(self) -> None:
        self.calls = 0
        self._count_lock = Lock()
        self.entered = Event()
        self._release = Event()

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        with self._count_lock:
            self.calls += 1
        self.entered.set()
        self._release.wait(timeout=5)
        return ToolExecutionSucceeded(output={"ok": True})

    def release(self) -> None:
        self._release.set()


class AlwaysSucceedPort:
    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        return ToolExecutionSucceeded(output={"ok": True})


def _service_with_blocking_tool() -> tuple[DevAgentRunService, BlockingCountingPort]:
    registry = ToolRegistry()
    port = BlockingCountingPort()
    registry.register(
        ToolDescriptor(tool_id="slow", name="Slow", description="Slow."),
        port,
    )
    service = DevAgentRunService(tool_registry=registry)
    return service, port


def test_concurrent_advance_executes_tool_exactly_once() -> None:
    """P8-CODEX-001's regression guard: two real Threads calling `advance()`
    for the same Run at the same time must result in exactly one Tool
    execution, never two."""

    service, port = _service_with_blocking_tool()
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="slow", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )

    results: list[RunSnapshot] = []
    errors: list[BaseException] = []

    def _advance() -> None:
        try:
            results.append(service.advance(run.run_id))
        except BaseException as exc:
            errors.append(exc)

    threads = [Thread(target=_advance) for _ in range(2)]
    for thread in threads:
        thread.start()

    # One Thread is now inside `execute()`, blocked on `_release`; the other
    # must be blocked on the per-Run Lock (never inside `execute()` too) —
    # proven by neither Thread having produced a result yet.
    assert port.entered.wait(timeout=5)
    assert results == []
    assert errors == []

    port.release()
    for thread in threads:
        thread.join(timeout=5)

    assert errors == []
    assert port.calls == 1

    final = service.get_run(run.run_id)
    assert final is not None
    assert final.steps[0].state is StepState.SUCCEEDED
    assert final.steps[0].attempt_count == 1


def test_concurrent_advance_vs_cancel_is_deterministic() -> None:
    """A representative advance-vs-cancel Race: whichever order the per-Run
    Lock actually grants, the Tool still executes at most once and the Run
    converges to a single coherent final State (`cancelled`), never a torn
    mix of both outcomes."""

    service, port = _service_with_blocking_tool()
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="slow", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )

    advance_errors: list[BaseException] = []
    cancel_errors: list[BaseException] = []

    def _advance() -> None:
        try:
            service.advance(run.run_id)
        except BaseException as exc:
            advance_errors.append(exc)

    def _cancel() -> None:
        try:
            service.cancel_run(run.run_id)
        except BaseException as exc:
            cancel_errors.append(exc)

    advance_thread = Thread(target=_advance)
    advance_thread.start()
    assert port.entered.wait(timeout=5)  # advance is now holding the per-Run Lock

    cancel_thread = Thread(target=_cancel)
    cancel_thread.start()

    port.release()
    advance_thread.join(timeout=5)
    cancel_thread.join(timeout=5)

    assert advance_errors == []
    assert cancel_errors == []
    assert port.calls == 1  # never executed twice regardless of interleaving

    final = service.get_run(run.run_id)
    assert final is not None
    assert final.state is RunState.CANCELLED
    assert final.completion is not None
    assert final.completion.outcome == "cancelled"
    # The one Step ran to completion before Cancel could reach it (Cancel
    # necessarily lost the Lock race here since the Tool was still blocking
    # it) — cancel_run() never touches an already-SUCCEEDED Step's state.
    assert final.steps[0].state is StepState.SUCCEEDED


def test_concurrent_approval_vs_cancel_is_deterministic() -> None:
    """Approval-vs-Cancel Race on a Step already Awaiting Approval: whichever
    of `submit_approval`/`cancel_run` the per-Run Lock admits first, the Run
    converges to exactly one coherent outcome — `cancelled` — and the loser
    either no-ops harmlessly or fails closed with a Typed
    `InvalidRunTransitionError`, never a corrupted/mixed State."""

    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(tool_id="list_files", name="List", description="List."),
        AlwaysSucceedPort(),  # never actually reached — this Test never calls advance() again
    )
    service = DevAgentRunService(tool_registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="list_files", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.MANUAL,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    awaiting = service.advance(run.run_id)
    assert awaiting.state is RunState.AWAITING_APPROVAL

    barrier = Barrier(2)
    approval_outcome: list[RunSnapshot | InvalidRunTransitionError] = []
    cancel_outcome: list[RunSnapshot | InvalidRunTransitionError] = []

    def _approve() -> None:
        barrier.wait(timeout=5)
        try:
            approval_outcome.append(
                service.submit_approval(run.run_id, "only", ApprovalDecision.APPROVED)
            )
        except InvalidRunTransitionError as exc:
            approval_outcome.append(exc)

    def _cancel() -> None:
        barrier.wait(timeout=5)
        try:
            cancel_outcome.append(service.cancel_run(run.run_id))
        except InvalidRunTransitionError as exc:  # pragma: no cover - cancel_run never raises
            cancel_outcome.append(exc)

    threads = [Thread(target=_approve), Thread(target=_cancel)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert len(approval_outcome) == 1
    assert len(cancel_outcome) == 1

    final = service.get_run(run.run_id)
    assert final is not None
    assert final.state is RunState.CANCELLED
    assert final.completion is not None
    assert final.completion.outcome == "cancelled"
