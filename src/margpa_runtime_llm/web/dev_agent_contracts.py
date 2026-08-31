"""Local-private `/api/v2/dev-agent` request/response contracts (P8-D)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.modules.dev_agent import (
    DEFAULT_RUN_BUDGET_LIMIT,
    MAX_PLAN_STEPS,
    STEP_ID_PATTERN,
    TOOL_ID_PATTERN,
    ApprovalDecision,
    ApprovalEvidence,
    ApprovalProfile,
    AuthorizationEnvelope,
    CapabilityId,
    CompletionApprovalEvidence,
    ImportantGateReason,
    Plan,
    PlanStep,
    RetryPolicy,
    RunCompletionOutcome,
    RunSnapshot,
    RunState,
    StepState,
    ToolDescriptor,
)


class _DevAgentContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DevAgentCapabilityResponse(_DevAgentContract):
    capability_id: CapabilityId


class DevAgentToolDescriptorResponse(_DevAgentContract):
    tool_id: str
    name: str
    description: str
    important_gate_reason: ImportantGateReason | None
    budget_cost: int


class DevAgentPlanStepRequest(_DevAgentContract):
    step_id: str = Field(pattern=STEP_ID_PATTERN)
    tool_id: str = Field(pattern=TOOL_ID_PATTERN)
    input: dict[str, object] = Field(default_factory=dict)


class DevAgentStartRunRequest(_DevAgentContract):
    capability_id: CapabilityId
    steps: tuple[DevAgentPlanStepRequest, ...] = Field(min_length=1, max_length=MAX_PLAN_STEPS)
    # P8-REQ-025 (mirrors P8-REQ-016's "OFF/never allow-all" discipline):
    # the default Profile gates important Tools rather than never gating
    # anything — a caller must explicitly opt into `MANUAL`/`RISK_BASED`/
    # `PLAN_ONLY` for a different posture.
    approval_profile: ApprovalProfile = ApprovalProfile.IMPORTANT_GATE_ONLY
    max_steps: int = Field(ge=1, le=MAX_PLAN_STEPS, default=20)
    max_attempts: int = Field(ge=1, le=5, default=1)
    deadline_seconds: float | None = Field(default=None, ge=1, le=3600)
    budget_limit: int = Field(ge=1, le=100_000, default=DEFAULT_RUN_BUDGET_LIMIT)

    def to_plan(self) -> Plan:
        return Plan(
            steps=tuple(
                PlanStep(step_id=step.step_id, tool_id=step.tool_id, input=step.input)
                for step in self.steps
            )
        )

    def to_retry_policy(self) -> RetryPolicy:
        return RetryPolicy(max_attempts=self.max_attempts)


class DevAgentApprovalRequest(_DevAgentContract):
    step_id: str = Field(pattern=STEP_ID_PATTERN)
    decision: ApprovalDecision


class DevAgentCompletionApprovalRequest(_DevAgentContract):
    """P8-RW6-C (P8-CODEX-007): no `step_id`/`tool_id` — mirrors
    `CompletionApprovalEvidence` itself; Completion is a Run Lifecycle
    event, not a Step's Tool call."""

    decision: ApprovalDecision


class DevAgentStepRecordResponse(_DevAgentContract):
    step_id: str
    tool_id: str
    state: StepState
    attempt_count: int
    input: dict[str, object]
    """P8-MR5 (P8-MANUAL-005): the Step's own real `PlanStep.input` from the
    Server's Frozen `RunSnapshot.plan` — the exact Actual Server Plan a
    User is being asked to Approve, never a Frontend-only Hard-coded
    display value that could silently diverge from what the Server will
    actually execute."""
    output: dict[str, object] | None
    error: str | None
    completed_at: str | None
    approved: bool


class DevAgentRunCompletionResponse(_DevAgentContract):
    outcome: RunCompletionOutcome
    reason: str


class DevAgentAuthorizationEnvelopeResponse(_DevAgentContract):
    """P8-CR2: projects the Frozen Envelope issued at `start_run()` so a
    Controller/User can see, via REST, exactly what a Run was authorized to
    do — never something the Response schema lets a caller submit back in."""

    run_id: str
    allowed_step_ids: tuple[str, ...]
    allowed_tool_ids: tuple[str, ...]
    resource_scope: str
    max_steps: int
    max_attempts: int
    expires_at: str | None
    gate_reasons: tuple[ImportantGateReason, ...]
    issued_at: str


class DevAgentApprovalEvidenceResponse(_DevAgentContract):
    run_id: str
    step_id: str
    tool_id: str
    decision: ApprovalDecision
    actor_class: str
    decided_at: str
    gate_reason: ImportantGateReason | None


class DevAgentCompletionApprovalEvidenceResponse(_DevAgentContract):
    run_id: str
    decision: ApprovalDecision
    actor_class: str
    decided_at: str
    gate_reason: ImportantGateReason


class DevAgentRunResponse(_DevAgentContract):
    run_id: str
    capability_id: CapabilityId
    approval_profile: ApprovalProfile
    max_steps: int
    state: RunState
    steps: tuple[DevAgentStepRecordResponse, ...]
    created_at: str
    deadline_at: str | None
    completion: DevAgentRunCompletionResponse | None
    constitution_mode: str | None
    constitution_rule_ids: tuple[str, ...] | None
    envelope: DevAgentAuthorizationEnvelopeResponse | None
    approvals: tuple[DevAgentApprovalEvidenceResponse, ...]
    budget_limit: int | None
    budget_consumed: int
    completion_approvals: tuple[DevAgentCompletionApprovalEvidenceResponse, ...]


def project_tool_descriptor(descriptor: ToolDescriptor) -> DevAgentToolDescriptorResponse:
    return DevAgentToolDescriptorResponse(
        tool_id=descriptor.tool_id,
        name=descriptor.name,
        description=descriptor.description,
        important_gate_reason=descriptor.important_gate_reason,
        budget_cost=descriptor.budget_cost,
    )


def project_envelope(
    envelope: AuthorizationEnvelope,
) -> DevAgentAuthorizationEnvelopeResponse:
    return DevAgentAuthorizationEnvelopeResponse(
        run_id=envelope.run_id,
        allowed_step_ids=envelope.allowed_step_ids,
        allowed_tool_ids=envelope.allowed_tool_ids,
        resource_scope=envelope.resource_scope,
        max_steps=envelope.max_steps,
        max_attempts=envelope.max_attempts,
        expires_at=envelope.expires_at,
        gate_reasons=envelope.gate_reasons,
        issued_at=envelope.issued_at,
    )


def project_approval_evidence(evidence: ApprovalEvidence) -> DevAgentApprovalEvidenceResponse:
    return DevAgentApprovalEvidenceResponse(
        run_id=evidence.run_id,
        step_id=evidence.step_id,
        tool_id=evidence.tool_id,
        decision=evidence.decision,
        actor_class=evidence.actor_class,
        decided_at=evidence.decided_at,
        gate_reason=evidence.gate_reason,
    )


def project_completion_approval_evidence(
    evidence: CompletionApprovalEvidence,
) -> DevAgentCompletionApprovalEvidenceResponse:
    return DevAgentCompletionApprovalEvidenceResponse(
        run_id=evidence.run_id,
        decision=evidence.decision,
        actor_class=evidence.actor_class,
        decided_at=evidence.decided_at,
        gate_reason=evidence.gate_reason,
    )


def project_run(run: RunSnapshot) -> DevAgentRunResponse:
    # P8-MR5 (P8-MANUAL-005): `run.plan` is the Frozen Server Plan set once
    # at `start_run()` and never mutated — matched to each `StepRecord` by
    # `step_id` (the same identity both already share).
    plan_input_by_step_id = {step.step_id: step.input for step in run.plan.steps}
    return DevAgentRunResponse(
        run_id=run.run_id,
        capability_id=run.capability_id,
        approval_profile=run.approval_profile,
        max_steps=run.max_steps,
        state=run.state,
        steps=tuple(
            DevAgentStepRecordResponse(
                step_id=step.step_id,
                tool_id=step.tool_id,
                state=step.state,
                attempt_count=step.attempt_count,
                input=plan_input_by_step_id.get(step.step_id, {}),
                output=step.output,
                error=step.error,
                completed_at=step.completed_at,
                approved=step.approved,
            )
            for step in run.steps
        ),
        created_at=run.created_at,
        deadline_at=run.deadline_at,
        completion=(
            DevAgentRunCompletionResponse(
                outcome=run.completion.outcome, reason=run.completion.reason
            )
            if run.completion is not None
            else None
        ),
        constitution_mode=run.constitution_mode,
        constitution_rule_ids=run.constitution_rule_ids,
        envelope=(project_envelope(run.envelope) if run.envelope is not None else None),
        approvals=tuple(project_approval_evidence(e) for e in run.approvals),
        budget_limit=run.budget_limit,
        budget_consumed=run.budget_consumed,
        completion_approvals=tuple(
            project_completion_approval_evidence(e) for e in run.completion_approvals
        ),
    )
