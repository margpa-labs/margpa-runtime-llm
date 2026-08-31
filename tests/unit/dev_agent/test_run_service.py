"""Unit tests for Phase 8 (P8-D/P8-E) DevAgentRunService: the Run/Step
engine's Max Step/Deadline/Retry/Approval-Gate/Cancel/Late-Result discipline,
Constitution correlation, and Restart Recovery via a persisted Run Store."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.adapters.dev_agent import FakeToolPort
from margpa_runtime_llm.modules.dev_agent import (
    ApprovalDecision,
    ApprovalEvidence,
    ApprovalProfile,
    CapabilityId,
    DevAgentRunService,
    ImportantGateReason,
    InvalidRunTransitionError,
    Plan,
    PlanStep,
    RetryPolicy,
    RunNotFoundError,
    RunSnapshot,
    RunState,
    StepRecord,
    StepState,
    ToolDescriptor,
    ToolExecutionFailed,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
    ToolRegistry,
)


class FakeRunStore:
    """In-memory stand-in for `DevAgentRunStorePort` — a real filesystem
    round trip is covered separately in `test_json_file_run_store.py`; here
    the point is exercising `DevAgentRunService`'s own persistence and
    reload contract, isolated from file I/O."""

    def __init__(self) -> None:
        self.saved: dict[str, RunSnapshot] = {}
        self.save_calls = 0

    def save(self, run: RunSnapshot) -> None:
        self.save_calls += 1
        self.saved[run.run_id] = run

    def load_all(self) -> tuple[RunSnapshot, ...]:
        return tuple(self.saved.values())


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def __call__(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)


class CountingFailThenSucceedPort:
    """A Tool that fails its first `fail_times` calls, then succeeds."""

    def __init__(self, fail_times: int) -> None:
        self._fail_times = fail_times
        self.calls = 0

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        self.calls += 1
        if self.calls <= self._fail_times:
            return ToolExecutionFailed(reason="transient_failure")
        return ToolExecutionSucceeded(output={"ok": True})


class AlwaysFailPort:
    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        return ToolExecutionFailed(reason="permanent_failure")


class CountingPort:
    """P8-CR2: counts `execute()` invocations — used to prove an Envelope
    mismatch converges to `authority_denied` with zero Tool executions."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        self.calls += 1
        return ToolExecutionSucceeded(output={"ok": True})


def _registry_with_fixture_tools() -> ToolRegistry:
    registry = ToolRegistry()
    fake_tool = FakeToolPort()
    registry.register(
        ToolDescriptor(tool_id="list_files", name="List", description="List."),
        fake_tool,
    )
    registry.register(
        ToolDescriptor(tool_id="read_file", name="Read", description="Read."),
        fake_tool,
    )
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        fake_tool,
    )
    return registry


def _service(
    *, registry: ToolRegistry | None = None, clock: FakeClock | None = None
) -> tuple[DevAgentRunService, FakeClock]:
    fake_clock = clock or FakeClock(datetime(2026, 8, 30, 0, 0, 0, tzinfo=UTC))
    service = DevAgentRunService(
        tool_registry=registry or _registry_with_fixture_tools(), clock=fake_clock
    )
    return service, fake_clock


def _multi_step_plan() -> Plan:
    return Plan(
        steps=(
            PlanStep(step_id="list", tool_id="list_files", input={}),
            PlanStep(step_id="read", tool_id="read_file", input={"path": "notes/readme.md"}),
            PlanStep(
                step_id="write",
                tool_id="write_note",
                input={"path": "notes/new.md", "content": "hi"},
            ),
        )
    )


def _two_non_important_step_plan() -> Plan:
    return Plan(
        steps=(
            PlanStep(step_id="list", tool_id="list_files", input={}),
            PlanStep(step_id="read", tool_id="read_file", input={"path": "notes/readme.md"}),
        )
    )


def test_golden_path_multi_step_completes_with_zero_gates() -> None:
    """A Plan containing only non-important Tools under `IMPORTANT_GATE_ONLY`
    completes end to end with no *Step* Approval Gate ever encountered — the
    baseline Golden Path (P8-ACC-030). Since P8-RW6-C (P8-CODEX-007), the
    Run-level Completion Gate still applies (Completion is itself an
    Important-Gated Lifecycle event under this Profile), so one explicit
    Completion Approval is required before the final `completed`."""

    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    for _ in range(3):
        run = service.advance(run.run_id)

    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL
    assert all(step.state is StepState.SUCCEEDED for step in run.steps)

    run = service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)

    assert run.state is RunState.COMPLETED
    assert run.completion is not None
    assert run.completion.outcome == "completed"


def test_plan_only_profile_never_executes_any_step() -> None:
    """P8-REQ-025/P8-ACC-032: `PLAN_ONLY` is a dry run — the Plan is
    produced but nothing ever executes, even a Tool with no side effects."""

    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.PLAN_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)

    assert run.state is RunState.COMPLETED
    assert run.completion is not None
    assert run.completion.outcome == "plan_only"
    assert all(step.state is StepState.PENDING for step in run.steps)

    # Idempotent: a further advance() call changes nothing further.
    unchanged = service.advance(run.run_id)
    assert unchanged == run


def test_risk_based_profile_gates_important_tools() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.RISK_BASED,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list_files, not important -> runs
    assert run.steps[0].state is StepState.SUCCEEDED
    run = service.advance(run.run_id)  # read_file, not important -> runs
    assert run.steps[1].state is StepState.SUCCEEDED
    run = service.advance(run.run_id)  # write_note, important -> gated
    assert run.state is RunState.AWAITING_APPROVAL


def test_risk_based_profile_gates_a_retry_after_failure() -> None:
    """`RISK_BASED`'s distinguishing behavior versus `IMPORTANT_GATE_ONLY`:
    a non-important Tool's first attempt runs freely, but a retry of a
    failed attempt is itself a risk signal that requires Approval."""

    registry = ToolRegistry()
    flaky_port = CountingFailThenSucceedPort(fail_times=1)
    registry.register(
        ToolDescriptor(tool_id="flaky", name="Flaky", description="Flaky."),
        flaky_port,
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="flaky", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.RISK_BASED,
        max_steps=10,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    run = service.advance(run.run_id)  # attempt 1: fails, not yet a retry
    assert run.state is RunState.RUNNING
    assert run.steps[0].state is StepState.PENDING
    assert run.steps[0].attempt_count == 1

    run = service.advance(run.run_id)  # attempt 2 would be a retry -> gated
    assert run.state is RunState.AWAITING_APPROVAL
    assert run.steps[0].attempt_count == 1  # no attempt consumed while gated

    run = service.submit_approval(run.run_id, "only", ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)
    assert run.steps[0].state is StepState.SUCCEEDED


def test_important_gate_only_golden_path_blocks_then_completes() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list_files, not important -> runs
    assert run.steps[0].state is StepState.SUCCEEDED
    run = service.advance(run.run_id)  # read_file, not important -> runs
    assert run.steps[1].state is StepState.SUCCEEDED
    run = service.advance(run.run_id)  # write_note, important -> pauses
    assert run.state is RunState.AWAITING_APPROVAL
    assert run.steps[2].state is StepState.AWAITING_APPROVAL

    run = service.submit_approval(run.run_id, "write", ApprovalDecision.APPROVED)
    assert run.state is RunState.RUNNING
    run = service.advance(run.run_id)
    assert run.steps[2].state is StepState.SUCCEEDED
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL  # P8-RW6-C

    run = service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)
    assert run.state is RunState.COMPLETED


def test_approval_denied_fails_fast_and_stops_remaining_steps() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.MANUAL,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list_files -> awaiting approval (GATE_ALL)
    assert run.state is RunState.AWAITING_APPROVAL
    run = service.submit_approval(run.run_id, "list", ApprovalDecision.DENIED)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "approval_denied"
    assert run.steps[0].state is StepState.DENIED
    assert run.steps[1].state is StepState.PENDING
    assert run.steps[2].state is StepState.PENDING

    # A finalized Run is a no-op on further advance() calls.
    unchanged = service.advance(run.run_id)
    assert unchanged == run


def test_submit_approval_rejects_wrong_step_id() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.MANUAL,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_APPROVAL
    with pytest.raises(InvalidRunTransitionError):
        service.submit_approval(run.run_id, "write", ApprovalDecision.APPROVED)


def test_submit_approval_rejects_when_not_awaiting_approval() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    with pytest.raises(InvalidRunTransitionError):
        service.submit_approval(run.run_id, "list", ApprovalDecision.APPROVED)


def test_max_steps_exceeded_stops_the_run_honestly() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=2,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "max_steps_exceeded"
    assert run.steps[2].state is StepState.PENDING  # never reached


def test_budget_exceeded_stops_the_run_without_executing_the_tool() -> None:
    """P8-RW6-B (P8-CODEX-006) Required behavior: a Step whose Tool cost
    would push `budget_consumed` past `budget_limit` never executes at
    all — Typed `budget_exceeded` Stop, not a silent skip or a Max-Step
    substitute."""

    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
        budget_limit=1,
    )
    run = service.advance(run.run_id)  # list_files costs 1 -> exactly at the Limit
    assert run.steps[0].state is StepState.SUCCEEDED
    assert run.budget_consumed == 1

    run = service.advance(run.run_id)  # read_file would cost 1 more -> 2 > 1

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "budget_exceeded"
    assert run.steps[1].state is StepState.FAILED
    assert run.steps[1].output is None  # never executed
    assert run.budget_consumed == 1  # unchanged — the exceeding attempt was never made


def test_budget_is_distinct_from_max_steps() -> None:
    """Codex's own distinction: a single expensive Tool call can exceed
    Budget while nowhere near the Run's Max Step limit — the two Limits
    measure genuinely different things."""

    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(
            tool_id="expensive", name="Expensive", description="Costly.", budget_cost=50
        ),
        CountingPort(),
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="expensive", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,  # far from exceeded — only 1 Step in this Plan
        retry_policy=RetryPolicy(),
        budget_limit=40,  # below the single Step's cost of 50
    )
    run = service.advance(run.run_id)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "budget_exceeded"
    # Confirms this was never a Max-Step substitute: only 1 of 10 allowed
    # Steps was even attempted.
    assert run.steps[0].state is StepState.FAILED


def test_budget_is_charged_for_a_failed_attempt_too() -> None:
    """A costly attempt that fails is not free — mirrors a real API call
    costing money whether or not it succeeds."""

    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(tool_id="broken", name="Broken", description="Broken.", budget_cost=7),
        AlwaysFailPort(),
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="broken", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(max_attempts=2),
        budget_limit=100,
    )
    run = service.advance(run.run_id)  # attempt 1: fails, charged anyway
    assert run.budget_consumed == 7
    run = service.advance(run.run_id)  # attempt 2: fails, charged again
    assert run.budget_consumed == 14
    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "tool_failure"


def test_a_run_persisted_before_p8_rw6_b_has_no_budget_limit_and_is_not_checked() -> None:
    """Backward Compatibility: a Run persisted before P8-RW6-B existed has
    `budget_limit is None` — the check is skipped entirely, mirroring
    `_envelope_violation()`'s treatment of a missing Envelope."""

    plan = Plan(steps=(PlanStep(step_id="only", tool_id="list_files", input={}),))
    legacy_run = RunSnapshot(
        run_id="legacy-run",
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        retry_policy=RetryPolicy(),
        max_steps=10,
        state=RunState.RUNNING,
        steps=(StepRecord(step_id="only", tool_id="list_files", state=StepState.PENDING),),
        created_at="2026-08-30T00:00:00+00:00",
    )
    assert legacy_run.budget_limit is None
    assert legacy_run.budget_consumed == 0

    store = FakeRunStore()
    store.saved[legacy_run.run_id] = legacy_run
    service = DevAgentRunService(tool_registry=_registry_with_fixture_tools(), run_store=store)

    result = service.advance("legacy-run")
    assert result.steps[0].state is StepState.SUCCEEDED


def test_budget_persists_and_survives_restart() -> None:
    store = FakeRunStore()
    first_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
        budget_limit=10,
    )
    first_service.advance(started.run_id)  # list_files, cost 1

    second_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    recovered = second_service.get_run(started.run_id)
    assert recovered is not None
    assert recovered.budget_limit == 10
    assert recovered.budget_consumed == 1


def test_deadline_exceeded_stops_the_run_honestly() -> None:
    service, clock = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
        deadline_seconds=5,
    )
    clock.advance(6)
    run = service.advance(run.run_id)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "deadline_exceeded"


def test_retry_recovers_from_a_transient_failure() -> None:
    registry = ToolRegistry()
    flaky_port = CountingFailThenSucceedPort(fail_times=1)
    registry.register(
        ToolDescriptor(tool_id="flaky", name="Flaky", description="Flaky."),
        flaky_port,
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="flaky", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    run = service.advance(run.run_id)  # attempt 1: fails, retry allowed
    assert run.state is RunState.RUNNING
    assert run.steps[0].state is StepState.PENDING
    assert run.steps[0].attempt_count == 1

    run = service.advance(run.run_id)  # attempt 2: succeeds
    assert run.state is RunState.RUNNING
    assert run.steps[0].state is StepState.SUCCEEDED
    assert run.steps[0].attempt_count == 2

    run = service.advance(run.run_id)  # no Step left pending -> Completion Gate (P8-RW6-C)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL

    run = service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)
    assert run.state is RunState.COMPLETED


def test_retry_exhausted_finalizes_as_tool_failure() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(tool_id="broken", name="Broken", description="Broken."),
        AlwaysFailPort(),
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="broken", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "tool_failure"
    assert run.steps[0].state is StepState.FAILED
    assert run.steps[0].attempt_count == 2


def test_cancel_mid_run_marks_unstarted_steps_cancelled() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list_files succeeds
    run = service.cancel_run(run.run_id)

    assert run.state is RunState.CANCELLED
    assert run.completion is not None
    assert run.completion.outcome == "cancelled"
    assert run.steps[0].state is StepState.SUCCEEDED  # already-finished Steps are untouched
    assert run.steps[1].state is StepState.CANCELLED
    assert run.steps[2].state is StepState.CANCELLED


def test_late_result_after_cancel_is_rejected_and_never_merged() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.cancel_run(run.run_id)
    assert run.steps[0].state is StepState.CANCELLED

    late_outcome = ToolExecutionSucceeded(output={"paths": ["should_never_appear.md"]})
    run = service.record_late_result(run.run_id, "list", late_outcome)

    assert run.steps[0].state is StepState.LATE_REJECTED
    assert run.steps[0].output is None


def test_record_late_result_requires_a_finalized_run() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    with pytest.raises(InvalidRunTransitionError):
        service.record_late_result(run.run_id, "list", ToolExecutionSucceeded(output={}))


def test_unknown_run_id_raises() -> None:
    service, _ = _service()
    with pytest.raises(RunNotFoundError):
        service.advance("does-not-exist")


def test_unknown_tool_id_in_plan_fails_closed_as_tool_failure() -> None:
    service, _ = _service()
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="does_not_exist", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "tool_failure"
    assert run.steps[0].error == "unknown_tool"


def test_constitution_correlation_is_recorded_once_and_immutable() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
        constitution_mode="observe",
        constitution_rule_ids=("no-secrets-in-external-evidence",),
    )
    assert run.constitution_mode == "observe"
    assert run.constitution_rule_ids == ("no-secrets-in-external-evidence",)

    run = service.advance(run.run_id)
    # Still present, unchanged, after a state transition.
    assert run.constitution_mode == "observe"
    assert run.constitution_rule_ids == ("no-secrets-in-external-evidence",)


def test_no_constitution_provider_is_recorded_honestly_as_none() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert run.constitution_mode is None
    assert run.constitution_rule_ids is None


def test_every_mutation_is_persisted_to_the_run_store() -> None:
    store = FakeRunStore()
    service = DevAgentRunService(tool_registry=_registry_with_fixture_tools(), run_store=store)
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert store.save_calls == 1
    service.advance(run.run_id)
    assert store.save_calls == 2
    assert store.saved[run.run_id].steps[0].state is StepState.SUCCEEDED


def test_restart_recovers_an_in_flight_run_from_the_store() -> None:
    """Models a process Restart: a brand-new `DevAgentRunService` pointed at
    the same (in this Test, in-memory) Store must see the Run the previous
    Service instance started, and be able to keep driving it forward."""

    store = FakeRunStore()
    first_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    first_service.advance(started.run_id)  # list_files succeeds

    second_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    recovered = second_service.get_run(started.run_id)
    assert recovered is not None
    assert recovered.steps[0].state is StepState.SUCCEEDED
    assert recovered.steps[1].state is StepState.PENDING

    advanced = second_service.advance(started.run_id)
    assert advanced.steps[1].state is StepState.SUCCEEDED


def test_restart_after_approval_does_not_re_request_it() -> None:
    """The bug this Test guards against: an in-memory-only approval side
    table would forget a granted Approval across a Restart and incorrectly
    re-request it. `approved` living on the persisted `StepRecord` itself
    prevents that."""

    store = FakeRunStore()
    first_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    plan = Plan(
        steps=(
            PlanStep(
                step_id="write",
                tool_id="write_note",
                input={"path": "notes/new.md", "content": "hi"},
            ),
        )
    )
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    awaiting = first_service.advance(started.run_id)
    assert awaiting.state is RunState.AWAITING_APPROVAL
    approved = first_service.submit_approval(started.run_id, "write", ApprovalDecision.APPROVED)
    assert approved.state is RunState.RUNNING
    assert approved.steps[0].approved is True
    # The process stops here, before the approved Step ever executed.

    second_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    resumed = second_service.advance(started.run_id)
    # Must execute directly, never re-enter AWAITING_APPROVAL.
    assert resumed.state is RunState.RUNNING
    assert resumed.steps[0].state is StepState.SUCCEEDED


# -- P8-CR2: Authorization Envelope / Approval Evidence ----------------------


def test_start_run_issues_a_frozen_envelope_matching_the_plan() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=7,
        retry_policy=RetryPolicy(max_attempts=3),
        deadline_seconds=60,
    )
    envelope = run.envelope
    assert envelope is not None
    assert envelope.run_id == run.run_id
    assert set(envelope.allowed_step_ids) == {"list", "read", "write"}
    assert set(envelope.allowed_tool_ids) == {"list_files", "read_file", "write_note"}
    assert envelope.resource_scope == "fixture_only"
    assert envelope.max_steps == 7
    assert envelope.max_attempts == 3
    assert envelope.expires_at == run.deadline_at
    assert envelope.gate_reasons == (ImportantGateReason.EXTERNAL_WRITE,)


def test_step_outside_the_envelope_is_authority_denied_with_zero_executions() -> None:
    """P8-CR2 Required Test: an Envelope/Step mismatch converges to a Typed
    Failure and the Tool Port is never called. A caller cannot construct
    this through the public API (the Envelope is server-issued and Frozen)
    — this models a Run reloaded from a Store whose Envelope no longer
    covers one of its own Steps (e.g. a hand-edited/corrupted-but-schema-
    valid file), which `advance()` must still fail closed against rather
    than trusting blindly."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(tool_id="only_tool", name="Only", description="Only."), counting_port
    )
    first_service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="only_tool", input={}),))
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert started.envelope is not None

    # Narrow the persisted Envelope so it no longer authorizes the Plan's
    # own Step — never reachable via `start_run()`/`submit_approval()`,
    # only by tampering with what the Store hands back.
    narrowed = started.model_copy(
        update={"envelope": started.envelope.model_copy(update={"allowed_step_ids": ()})}
    )
    store.saved[started.run_id] = narrowed

    second_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = second_service.advance(started.run_id)

    assert counting_port.calls == 0
    assert result.state is RunState.FAILED
    assert result.completion is not None
    assert result.completion.outcome == "authority_denied"
    assert result.steps[0].state is StepState.FAILED
    assert result.steps[0].error is not None
    assert "step_not_authorized" in result.steps[0].error


def test_run_identity_mismatch_envelope_is_authority_denied() -> None:
    """The `Run` leg of the Run/Step/Tool/Resource/Expiry check: an Envelope
    whose own `run_id` no longer matches the Run it is attached to (only
    reachable via a tampered/corrupted-but-schema-valid Store file, never
    via `start_run()`/`submit_approval()`) must fail closed too."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(tool_id="only_tool", name="Only", description="Only."), counting_port
    )
    first_service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="only_tool", input={}),))
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert started.envelope is not None
    mismatched = started.model_copy(
        update={"envelope": started.envelope.model_copy(update={"run_id": "some-other-run"})}
    )
    store.saved[started.run_id] = mismatched

    second_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = second_service.advance(started.run_id)

    assert counting_port.calls == 0
    assert result.completion is not None
    assert result.completion.outcome == "authority_denied"
    assert result.steps[0].error is not None
    assert "run_identity_mismatch" in result.steps[0].error


def test_expired_envelope_is_authority_denied_even_without_a_run_level_deadline() -> None:
    """The `Expiry` leg: a Run with no `deadline_at` (so the earlier
    `deadline_exceeded` check never fires) but a tampered Envelope whose own
    `expires_at` is already in the past must still fail closed at the
    Envelope check, never silently execute."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(tool_id="only_tool", name="Only", description="Only."), counting_port
    )
    first_service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="only_tool", input={}),))
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert started.deadline_at is None
    assert started.envelope is not None
    expired = started.model_copy(
        update={
            "envelope": started.envelope.model_copy(
                update={"expires_at": "2000-01-01T00:00:00+00:00"}
            )
        }
    )
    store.saved[started.run_id] = expired

    second_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = second_service.advance(started.run_id)

    assert counting_port.calls == 0
    assert result.completion is not None
    assert result.completion.outcome == "authority_denied"
    assert result.steps[0].error is not None
    assert "envelope_expired" in result.steps[0].error


def test_tool_not_authorized_by_envelope_is_authority_denied() -> None:
    """The `Tool` leg, isolated from the `Step` leg: the Step ID is still
    Allowed, but its Tool ID has been narrowed out of the Envelope."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(tool_id="only_tool", name="Only", description="Only."), counting_port
    )
    first_service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="only_tool", input={}),))
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert started.envelope is not None
    narrowed = started.model_copy(
        update={"envelope": started.envelope.model_copy(update={"allowed_tool_ids": ()})}
    )
    store.saved[started.run_id] = narrowed

    second_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = second_service.advance(started.run_id)

    assert counting_port.calls == 0
    assert result.completion is not None
    assert result.completion.outcome == "authority_denied"
    assert result.steps[0].error is not None
    assert "tool_not_authorized" in result.steps[0].error


def test_unsupported_resource_scope_is_authority_denied() -> None:
    """The `Resource` leg: an Envelope whose `resource_scope` has been
    tampered to a value outside `SUPPORTED_RESOURCE_SCOPES` fails closed,
    even though Step/Tool would otherwise be perfectly Allowed."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(tool_id="only_tool", name="Only", description="Only."), counting_port
    )
    first_service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="only_tool", input={}),))
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert started.envelope is not None
    tampered = started.model_copy(
        update={
            "envelope": started.envelope.model_copy(update={"resource_scope": "real_filesystem"})
        }
    )
    store.saved[started.run_id] = tampered

    second_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = second_service.advance(started.run_id)

    assert counting_port.calls == 0
    assert result.completion is not None
    assert result.completion.outcome == "authority_denied"
    assert result.steps[0].error is not None
    assert "resource_scope_unsupported" in result.steps[0].error


def test_a_run_persisted_before_p8_cr2_has_no_envelope_and_is_not_corrupt() -> None:
    """Backward Compatibility: a `RunSnapshot` built the way a pre-P8-CR2
    Run Store file would deserialize (no `envelope`/`approvals` keys) must
    still validate and still be advanceable — a missing Envelope is treated
    as "nothing to check against", never a hard failure."""

    plan = Plan(steps=(PlanStep(step_id="only", tool_id="list_files", input={}),))
    legacy_run = RunSnapshot(
        run_id="legacy-run",
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        retry_policy=RetryPolicy(),
        max_steps=5,
        state=RunState.RUNNING,
        steps=(StepRecord(step_id="only", tool_id="list_files", state=StepState.PENDING),),
        created_at="2026-08-30T00:00:00+00:00",
    )
    assert legacy_run.envelope is None
    assert legacy_run.approvals == ()


def test_approval_evidence_is_recorded_and_scoped_to_its_own_step_and_tool() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list
    run = service.advance(run.run_id)  # read
    run = service.advance(run.run_id)  # write -> awaiting approval
    assert run.state is RunState.AWAITING_APPROVAL

    run = service.submit_approval(run.run_id, "write", ApprovalDecision.APPROVED)
    assert len(run.approvals) == 1
    evidence = run.approvals[0]
    assert evidence.run_id == run.run_id
    assert evidence.step_id == "write"
    assert evidence.tool_id == "write_note"
    assert evidence.decision is ApprovalDecision.APPROVED
    assert evidence.actor_class == "human_reviewer"
    assert evidence.gate_reason is ImportantGateReason.EXTERNAL_WRITE

    run = service.advance(run.run_id)
    assert run.steps[2].state is StepState.SUCCEEDED


def test_denied_approval_is_also_recorded_as_typed_evidence() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),
        approval_profile=ApprovalProfile.MANUAL,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_APPROVAL
    run = service.submit_approval(run.run_id, "list", ApprovalDecision.DENIED)

    assert len(run.approvals) == 1
    assert run.approvals[0].decision is ApprovalDecision.DENIED
    assert run.state is RunState.FAILED


def test_approval_evidence_for_one_step_never_authorizes_a_different_step() -> None:
    """A same-Tool, same-Profile Plan with two Steps: approving Step A must
    never let Step B skip its own Gate, even though both Steps share the
    same `tool_id` and thus the same `important_gate_reason`."""

    registry = ToolRegistry()
    fake_tool = FakeToolPort()
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        fake_tool,
    )
    service, _ = _service(registry=registry)
    plan = Plan(
        steps=(
            PlanStep(
                step_id="write-a", tool_id="write_note", input={"path": "a.md", "content": "a"}
            ),
            PlanStep(
                step_id="write-b", tool_id="write_note", input={"path": "b.md", "content": "b"}
            ),
        )
    )
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_APPROVAL
    run = service.submit_approval(run.run_id, "write-a", ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)
    assert run.steps[0].state is StepState.SUCCEEDED

    # Step B must still Gate on its own — Step A's Evidence must not carry
    # over even though the Tool (and Gate Reason) is identical.
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_APPROVAL
    assert run.steps[1].state is StepState.AWAITING_APPROVAL


def test_approval_evidence_and_envelope_never_cross_runs() -> None:
    """P8-CR2 Required behavior: Approval/Envelope reuse across a *different*
    Run must be impossible, not merely across a different Step within one
    Run. Two independent Runs with an identical Plan (same `step_id`/
    `tool_id`) — approving one must never gate-bypass the other."""

    service, _ = _service()
    plan = Plan(
        steps=(
            PlanStep(step_id="write", tool_id="write_note", input={"path": "a.md", "content": "a"}),
        )
    )
    run_a = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run_b = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert run_a.run_id != run_b.run_id
    assert run_a.envelope is not None
    assert run_b.envelope is not None
    assert run_a.envelope.run_id == run_a.run_id
    assert run_b.envelope.run_id == run_b.run_id

    run_a = service.advance(run_a.run_id)
    assert run_a.state is RunState.AWAITING_APPROVAL
    run_a = service.submit_approval(run_a.run_id, "write", ApprovalDecision.APPROVED)
    run_a = service.advance(run_a.run_id)
    assert run_a.steps[0].state is StepState.SUCCEEDED

    # Run B has never had its own Step approved — it must still Gate even
    # though Run A's identically-shaped Step was just approved and executed.
    run_b = service.advance(run_b.run_id)
    assert run_b.state is RunState.AWAITING_APPROVAL
    assert run_b.steps[0].state is StepState.AWAITING_APPROVAL
    assert run_b.approvals == ()


# -- P8-CR5 (P8-CODEX-004): Approval Evidence Scope Final Micro Rework -------


def test_transplanted_evidence_from_another_run_is_rejected_and_never_executes() -> None:
    """P8-CODEX-004's exact Controller Probe, reproduced: Run A's own
    (validly constructed) `ApprovalEvidence` is spliced directly into Run
    B's `approvals` (the way a corrupted/tampered persisted State could
    smuggle it in — `model_copy()` bypasses `RunSnapshot`'s own
    `run_id`-correlation validator, which only fires on
    `__init__`/`model_validate()`). Before the P8-CR5 fix this made Run B's
    Gate pass and the Tool execute; `_has_approval_evidence()` must now
    reject it on the `run_id` mismatch alone, independent of the Contract
    validator."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        counting_port,
    )
    service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(
        steps=(
            PlanStep(step_id="write", tool_id="write_note", input={"path": "a.md", "content": "a"}),
        )
    )
    run_a = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run_b = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    service.advance(run_a.run_id)
    approved_a = service.submit_approval(run_a.run_id, "write", ApprovalDecision.APPROVED)
    assert len(approved_a.approvals) == 1
    transplanted_evidence = approved_a.approvals[0]
    assert transplanted_evidence.run_id == run_a.run_id

    tampered_run_b = run_b.model_copy(update={"approvals": (transplanted_evidence,)})
    store.saved[run_b.run_id] = tampered_run_b

    fresh_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = fresh_service.advance(run_b.run_id)

    assert counting_port.calls == 0
    assert result.state is RunState.AWAITING_APPROVAL
    assert result.steps[0].state is StepState.AWAITING_APPROVAL


def test_envelope_having_run_cannot_bypass_the_gate_with_bool_alone() -> None:
    """P8-CODEX-004's second required Probe: a Run created after P8-CR2
    always has an `envelope`. Tampering `StepRecord.approved = True` on
    such a Run — with zero Typed `ApprovalEvidence` in `run.approvals` —
    must not pass the Gate. Before the fix, the `not next_step.approved`
    leg of the OR condition let this through regardless of Evidence."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        counting_port,
    )
    service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(
        steps=(
            PlanStep(step_id="write", tool_id="write_note", input={"path": "a.md", "content": "a"}),
        )
    )
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    awaiting = service.advance(run.run_id)
    assert awaiting.state is RunState.AWAITING_APPROVAL
    assert awaiting.envelope is not None
    assert awaiting.approvals == ()

    # Tamper the Step exactly the way a legitimate `submit_approval()` would
    # leave it (`state -> PENDING`, `approved -> True`) but *without* ever
    # creating the Typed `ApprovalEvidence` `submit_approval()` always
    # creates alongside it — isolating the bool from the Evidence it should
    # never be able to stand in for.
    tampered_step = awaiting.steps[0].model_copy(
        update={"approved": True, "state": StepState.PENDING}
    )
    tampered_run = awaiting.model_copy(
        update={"steps": (tampered_step,), "state": RunState.RUNNING}
    )
    store.saved[run.run_id] = tampered_run

    fresh_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = fresh_service.advance(run.run_id)

    assert counting_port.calls == 0
    assert result.state is RunState.AWAITING_APPROVAL
    assert result.steps[0].state is StepState.AWAITING_APPROVAL


def test_legacy_run_without_an_envelope_still_honors_the_bool_alone() -> None:
    """The counterpart proving P8-CR5 did not over-correct: a Pre-P8-CR2
    Legacy Run (`envelope is None`) never had Typed Evidence to begin with,
    so `StepRecord.approved = True` must remain sufficient there — the
    exact Backward Compatibility Contract P8-CR2 established."""

    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        counting_port,
    )
    plan = Plan(
        steps=(
            PlanStep(step_id="write", tool_id="write_note", input={"path": "a.md", "content": "a"}),
        )
    )
    legacy_run = RunSnapshot(
        run_id="legacy-run",
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        retry_policy=RetryPolicy(),
        max_steps=10,
        state=RunState.RUNNING,
        steps=(
            StepRecord(
                step_id="write", tool_id="write_note", state=StepState.PENDING, approved=True
            ),
        ),
        created_at="2026-08-30T00:00:00+00:00",
    )
    assert legacy_run.envelope is None
    assert legacy_run.approvals == ()

    store = FakeRunStore()
    store.saved[legacy_run.run_id] = legacy_run
    service = DevAgentRunService(tool_registry=registry, run_store=store)

    result = service.advance("legacy-run")

    assert counting_port.calls == 1
    assert result.steps[0].state is StepState.SUCCEEDED


def test_gate_reason_drift_between_evidence_and_current_descriptor_is_denied() -> None:
    """P8-CR5 §4.1's Gate Reason correlation: an `ApprovalEvidence` whose
    recorded `gate_reason` no longer matches the Tool's *current*
    `important_gate_reason` must not satisfy the Gate, even though
    `run_id`/`step_id`/`tool_id`/`decision` all line up correctly."""

    store = FakeRunStore()
    registry = ToolRegistry()
    counting_port = CountingPort()
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        counting_port,
    )
    service = DevAgentRunService(tool_registry=registry, run_store=store)
    plan = Plan(
        steps=(
            PlanStep(step_id="write", tool_id="write_note", input={"path": "a.md", "content": "a"}),
        )
    )
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    service.advance(run.run_id)
    approved = service.submit_approval(run.run_id, "write", ApprovalDecision.APPROVED)
    assert len(approved.approvals) == 1
    assert approved.approvals[0].gate_reason is ImportantGateReason.EXTERNAL_WRITE

    # Simulate drift: the Evidence now claims a Gate Reason the current
    # Descriptor no longer agrees with.
    drifted_evidence = approved.approvals[0].model_copy(
        update={"gate_reason": ImportantGateReason.NETWORK}
    )
    tampered_run = approved.model_copy(update={"approvals": (drifted_evidence,)})
    store.saved[run.run_id] = tampered_run

    fresh_service = DevAgentRunService(tool_registry=registry, run_store=store)
    result = fresh_service.advance(run.run_id)

    assert counting_port.calls == 0
    assert result.state is RunState.AWAITING_APPROVAL
    assert result.steps[0].state is StepState.AWAITING_APPROVAL


def test_run_snapshot_rejects_approval_evidence_scoped_to_a_different_run() -> None:
    """P8-CR5 persistence/REST-boundary layer: `RunSnapshot`'s own
    Contract-level validator must reject construction (`__init__`/
    `model_validate()`) of a Run whose `approvals` contains Evidence scoped
    to a different `run_id` — the second, independent layer alongside
    `_has_approval_evidence()`'s Runtime check."""

    plan = Plan(steps=(PlanStep(step_id="write", tool_id="write_note", input={}),))
    foreign_evidence = ApprovalEvidence(
        run_id="some-other-run",
        step_id="write",
        tool_id="write_note",
        decision=ApprovalDecision.APPROVED,
        actor_class="human_reviewer",
        decided_at="2026-08-30T00:00:00+00:00",
        gate_reason=ImportantGateReason.EXTERNAL_WRITE,
    )
    with pytest.raises(ValidationError):
        RunSnapshot(
            run_id="this-run",
            capability_id=CapabilityId.DEV_AGENT,
            plan=plan,
            approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
            retry_policy=RetryPolicy(),
            max_steps=10,
            state=RunState.RUNNING,
            steps=(StepRecord(step_id="write", tool_id="write_note", state=StepState.PENDING),),
            created_at="2026-08-30T00:00:00+00:00",
            approvals=(foreign_evidence,),
        )


def test_approval_evidence_persists_and_survives_restart() -> None:
    store = FakeRunStore()
    first_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    plan = Plan(
        steps=(
            PlanStep(
                step_id="write",
                tool_id="write_note",
                input={"path": "notes/new.md", "content": "hi"},
            ),
        )
    )
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    first_service.advance(started.run_id)
    approved = first_service.submit_approval(started.run_id, "write", ApprovalDecision.APPROVED)
    assert len(approved.approvals) == 1

    second_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    recovered = second_service.get_run(started.run_id)
    assert recovered is not None
    assert len(recovered.approvals) == 1
    assert recovered.approvals[0].step_id == "write"
    assert recovered.approvals[0].decision is ApprovalDecision.APPROVED
    assert recovered.envelope is not None
    assert recovered.envelope.run_id == started.run_id


# -- P8-RW6-C (P8-CODEX-007): Important Gate Runtime Completion -------------


@pytest.mark.parametrize(
    "gate_reason",
    [
        ImportantGateReason.NETWORK,
        ImportantGateReason.COST,
        ImportantGateReason.IRREVERSIBLE,
        ImportantGateReason.SECRET_OR_PRIVACY,
        ImportantGateReason.SCOPE_EXPANSION,
        ImportantGateReason.CRITICAL_INCIDENT,
    ],
)
def test_generic_gate_engine_handles_every_non_completion_important_gate_reason(
    gate_reason: ImportantGateReason,
) -> None:
    """P8-RW6-C §1 (P8-CODEX-007): the Generic Gate Engine
    (`_requires_approval()`/`_has_approval_evidence()`) must Gate and later
    admit a Step correctly for *every* `ImportantGateReason` category, not
    only `EXTERNAL_WRITE` (the only one Production currently registers a
    real Tool for). Fixture-only — no Real Network/Cost/Secret/Irreversible
    Tool is introduced; only the Tool's Descriptor classification changes."""

    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(
            tool_id="fixture_tool",
            name="Fixture Tool",
            description="A Fixture Tool carrying one non-EXTERNAL_WRITE Gate Reason.",
            important_gate_reason=gate_reason,
        ),
        CountingPort(),
    )
    service, _ = _service(registry=registry)
    plan = Plan(steps=(PlanStep(step_id="only", tool_id="fixture_tool", input={}),))
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=plan,
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    assert run.envelope is not None
    assert run.envelope.gate_reasons == (gate_reason,)

    gated = service.advance(run.run_id)
    assert gated.state is RunState.AWAITING_APPROVAL
    assert gated.steps[0].state is StepState.AWAITING_APPROVAL

    approved = service.submit_approval(run.run_id, "only", ApprovalDecision.APPROVED)
    assert len(approved.approvals) == 1
    assert approved.approvals[0].gate_reason is gate_reason

    executed = service.advance(run.run_id)
    assert executed.steps[0].state is StepState.SUCCEEDED


def test_completion_gate_is_pending_after_the_last_step_succeeds() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    assert all(step.state is StepState.SUCCEEDED for step in run.steps)

    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL
    assert run.completion is None
    assert run.completion_approvals == ()
    # A stray further advance() while awaiting Completion is a safe no-op.
    unchanged = service.advance(run.run_id)
    assert unchanged == run


def test_completion_gate_denied_fails_the_run() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL

    run = service.submit_completion_approval(run.run_id, ApprovalDecision.DENIED)

    assert run.state is RunState.FAILED
    assert run.completion is not None
    assert run.completion.outcome == "approval_denied"
    assert len(run.completion_approvals) == 1
    assert run.completion_approvals[0].decision is ApprovalDecision.DENIED
    assert run.completion_approvals[0].gate_reason is ImportantGateReason.COMPLETION
    # Every Step stays SUCCEEDED — denial is a Completion-level Failure, not
    # a retroactive Step failure.
    assert all(step.state is StepState.SUCCEEDED for step in run.steps)


def test_completion_gate_approved_then_advance_finalizes_completed() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL

    run = service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)
    assert run.state is RunState.RUNNING
    assert len(run.completion_approvals) == 1
    assert run.completion_approvals[0].decision is ApprovalDecision.APPROVED

    run = service.advance(run.run_id)
    assert run.state is RunState.COMPLETED
    assert run.completion is not None
    assert run.completion.outcome == "completed"


def test_completion_approval_rejects_when_not_awaiting_completion() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    with pytest.raises(InvalidRunTransitionError):
        service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)


def test_cancel_while_awaiting_completion_approval_still_cancels() -> None:
    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL

    run = service.cancel_run(run.run_id)

    assert run.state is RunState.CANCELLED
    assert run.completion is not None
    assert run.completion.outcome == "cancelled"
    # Already-succeeded Steps are untouched by Cancel (existing discipline).
    assert all(step.state is StepState.SUCCEEDED for step in run.steps)

    # Subsequent Completion Approval on a Cancelled Run is rejected.
    with pytest.raises(InvalidRunTransitionError):
        service.submit_completion_approval(run.run_id, ApprovalDecision.APPROVED)


def test_completion_approval_persists_and_survives_restart() -> None:
    store = FakeRunStore()
    first_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    started = first_service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    first_service.advance(started.run_id)
    first_service.advance(started.run_id)
    awaiting = first_service.advance(started.run_id)
    assert awaiting.state is RunState.AWAITING_COMPLETION_APPROVAL
    approved = first_service.submit_completion_approval(started.run_id, ApprovalDecision.APPROVED)
    assert approved.state is RunState.RUNNING
    # The process stops here, before the final `advance()` ever ran.

    second_service = DevAgentRunService(
        tool_registry=_registry_with_fixture_tools(), run_store=store
    )
    recovered = second_service.get_run(started.run_id)
    assert recovered is not None
    assert len(recovered.completion_approvals) == 1
    assert recovered.completion_approvals[0].decision is ApprovalDecision.APPROVED

    resumed = second_service.advance(started.run_id)
    # Must finalize directly, never re-enter AWAITING_COMPLETION_APPROVAL.
    assert resumed.state is RunState.COMPLETED


def test_step_approval_evidence_never_satisfies_the_completion_gate() -> None:
    """P8-CODEX-007's explicit Identity/Scope separation: a Step's
    `ApprovalEvidence` — however many, however recently granted — must never
    be misread as a `CompletionApprovalEvidence`. The two are structurally
    different Types stored in different Fields."""

    service, _ = _service()
    run = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_multi_step_plan(),  # includes write_note, itself Step-Gated
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run = service.advance(run.run_id)  # list_files
    run = service.advance(run.run_id)  # read_file
    run = service.advance(run.run_id)  # write_note -> Step Gate
    assert run.state is RunState.AWAITING_APPROVAL
    run = service.submit_approval(run.run_id, "write", ApprovalDecision.APPROVED)
    run = service.advance(run.run_id)
    assert run.steps[2].state is StepState.SUCCEEDED
    assert len(run.approvals) == 1  # a real, granted Step Approval exists

    # All 3 Steps done — the Completion Gate must still trigger, unaffected
    # by the unrelated Step Approval already on file.
    run = service.advance(run.run_id)
    assert run.state is RunState.AWAITING_COMPLETION_APPROVAL
    assert run.completion_approvals == ()


def test_completion_approval_evidence_never_cross_runs() -> None:
    service, _ = _service()
    run_a = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    run_b = service.start_run(
        capability_id=CapabilityId.DEV_AGENT,
        plan=_two_non_important_step_plan(),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        max_steps=10,
        retry_policy=RetryPolicy(),
    )
    service.advance(run_a.run_id)
    service.advance(run_a.run_id)
    service.advance(run_a.run_id)
    service.submit_completion_approval(run_a.run_id, ApprovalDecision.APPROVED)
    finalized_a = service.advance(run_a.run_id)
    assert finalized_a.state is RunState.COMPLETED

    service.advance(run_b.run_id)
    service.advance(run_b.run_id)
    still_awaiting_b = service.advance(run_b.run_id)
    assert still_awaiting_b.state is RunState.AWAITING_COMPLETION_APPROVAL
    assert still_awaiting_b.completion_approvals == ()
