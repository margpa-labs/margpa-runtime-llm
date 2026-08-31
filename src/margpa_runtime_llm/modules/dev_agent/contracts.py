"""Phase 8 (P8-D): framework-independent contracts for the Dev Agent/Tool/
Approval Harness Foundation.

This is deliberately a *Foundation* only — an in-memory Run/Step engine
proving the shape (Stable Capability ID, Plan, Step, Approval Gate, Frozen
Authorization Envelope, Max Step/Deadline/Retry/Cancel/Late-Result
discipline) a real Dev Agent surface would need. Persistence across
Restart/Reload and correlation with Constitution/GD/Guardrail decisions are
explicitly P8-E's scope, not this Package's.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

TOOL_ID_PATTERN = r"^[a-z][a-z0-9_]{1,63}$"
STEP_ID_PATTERN = r"^[a-z][a-z0-9-]{1,63}$"
MAX_PLAN_STEPS = 50


class CapabilityId(StrEnum):
    """P8-D: a small, closed, Stable-ID set the Chat/Dev Agent UI switch is
    keyed by. Deliberately distinct from `ConstitutionView` (which classifies
    *evaluation surfaces* for Rules) — this classifies *which top-level UI
    surface the User is in*, and carries no Rule/Authority meaning itself."""

    CHAT = "chat"
    DEV_AGENT = "dev_agent"


class RunState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    AWAITING_COMPLETION_APPROVAL = "awaiting_completion_approval"
    """P8-RW6-C (P8-CODEX-007): distinct from `AWAITING_APPROVAL` — no
    `StepRecord` is in an Awaiting-Approval state here; the Run itself, not
    any one Step, is paused before its final `completed` transition. Only
    reachable under `ApprovalProfile.IMPORTANT_GATE_ONLY` once every Step
    has already succeeded."""
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DENIED = "denied"
    CANCELLED = "cancelled"
    LATE_REJECTED = "late_rejected"
    """A Tool Result arrived for this Step after its owning Run had already
    left a Result-accepting state (Cancelled/Completed/Failed) — the Result
    itself is discarded, never merged into the Step's `output` (P8-D
    Late-Result-rejection requirement)."""


RunCompletionOutcome = Literal[
    "completed",
    "plan_only",
    "max_steps_exceeded",
    "deadline_exceeded",
    "cancelled",
    "approval_denied",
    "tool_failure",
    "authority_denied",
    "budget_exceeded",
]
"""P8-D/P8-REQ-025: every way a Run can stop is its own explicit, honest
value — never silently coerced to a bare `completed`/`failed` boolean (same
discipline as `ConstitutionDecisionOutcome`). P8-CR2 added `authority_denied`
(Architecture Section 7's own Failure vocabulary): what a Frozen
`AuthorizationEnvelope` mismatch converges to — a Step/Tool/Resource/Expiry
outside the Envelope issued at `start_run()` fails closed here rather than
executing. P8-RW6-B (P8-CODEX-006) added `budget_exceeded` (also already
named in Architecture Section 7): distinct from `max_steps_exceeded` — a
Plan can exhaust its Budget while still well under its Max Step count, since
the two Limits measure different things (Step count vs. cumulative Tool
cost)."""


class ApprovalProfile(StrEnum):
    """P8-REQ-025: the four comparable Approval Profiles — a closed set,
    matching the Phase 8 Acceptance Matrix's literal names exactly (P8-ACC-032)."""

    PLAN_ONLY = "plan_only"
    """The Plan is produced and returned; no Step ever executes, regardless
    of Tool. A dry run — useful for inspecting what a Run *would* do."""
    MANUAL = "manual"
    """Every Step requires an Approval Decision, regardless of Gate Reason."""
    RISK_BASED = "risk_based"
    """A Step requires Approval if its Tool has an `important_gate_reason`,
    OR if this is a retry of a previously-failed attempt (a failure is
    itself a risk signal this Profile reacts to, unlike
    `IMPORTANT_GATE_ONLY` which never re-evaluates based on execution
    history)."""
    IMPORTANT_GATE_ONLY = "important_gate_only"
    """Only Steps whose Tool has a non-`None` `important_gate_reason`
    require Approval; a Plan containing only reason-less Tools completes
    with zero Approval Gates (this is the Profile the Golden Path Tests use)."""


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"


class RetryPolicy(ImmutableContract):
    max_attempts: int = Field(ge=1, le=5, default=1)
    """Total attempts allowed for one Step's Tool call (1 = no retry)."""


class ImportantGateReason(StrEnum):
    """P8-REQ-027/P8-ACC-034: the enumerated situations a Tool's Gate can
    represent. A named reason (rather than a bare `important: bool`) is what
    lets the Approval surface (REST response, future UI) tell a human *why*
    a Step is waiting, not just *that* it is."""

    EXTERNAL_WRITE = "external_write"
    NETWORK = "network"
    COST = "cost"
    IRREVERSIBLE = "irreversible"
    SECRET_OR_PRIVACY = "secret_or_privacy"
    SCOPE_EXPANSION = "scope_expansion"
    CRITICAL_INCIDENT = "critical_incident"
    COMPLETION = "completion"


class ToolDescriptor(ImmutableContract):
    """P8-D: one Tool's Stable Identity plus the Approval-relevant fact
    about it (`important_gate_reason`). Deliberately carries no
    Authority-shaped field — whether a Step actually runs is decided by
    `ApprovalProfile` + this field together, in the Run Service, never by
    the Descriptor alone."""

    tool_id: str = Field(pattern=TOOL_ID_PATTERN)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    important_gate_reason: ImportantGateReason | None = None
    """`None` means this Tool is never itself a reason to Gate (it may still
    be Gated under `ApprovalProfile.MANUAL`, which Gates everything)."""
    budget_cost: int = Field(ge=1, le=1000, default=1)
    """P8-RW6-B (P8-CODEX-006): the abstract Budget Units one invocation of
    this Tool costs — never a real dollar/token amount (the Fake/
    Deterministic Tool Foundation has no real cost to model), but
    deliberately *proportional*: a Tool with a heavier real-world analogue
    (e.g. an External Write) costs more than a read-only one, so a Run's
    cumulative `budget_consumed` means something beyond a bare Step count."""


class PlanStep(ImmutableContract):
    step_id: str = Field(pattern=STEP_ID_PATTERN)
    tool_id: str = Field(pattern=TOOL_ID_PATTERN)
    input: dict[str, object] = Field(default_factory=dict)


class Plan(ImmutableContract):
    steps: tuple[PlanStep, ...] = Field(min_length=1, max_length=MAX_PLAN_STEPS)

    @model_validator(mode="after")
    def validate_unique_step_ids(self) -> Plan:
        ids = [step.step_id for step in self.steps]
        if len(set(ids)) != len(ids):
            raise ValueError("plan step_id values must be unique")
        return self


class StepRecord(ImmutableContract):
    step_id: str = Field(pattern=STEP_ID_PATTERN)
    tool_id: str = Field(pattern=TOOL_ID_PATTERN)
    state: StepState
    attempt_count: int = Field(ge=0, default=0)
    output: dict[str, object] | None = None
    error: str | None = None
    completed_at: str | None = None
    approved: bool = False
    """P8-E: set once an `ApprovalDecision.APPROVED` has been submitted for
    this Step. Originally the only record of Approval; since P8-CR2 it is a
    Backward-Compatible cache superseded by `RunSnapshot.approvals`'s Typed
    `ApprovalEvidence`, which is now the sole Gate-bypass authority for any
    Run that has an `AuthorizationEnvelope` (P8-CR5/P8-CODEX-004 — this
    field alone can no longer pass the Gate on such a Run). It still governs
    a Pre-P8-CR2 Legacy Run (`envelope is None`), which never had Typed
    Evidence to begin with — same Restart-safety reasoning as before,
    narrowed to the Runs where it is still the only signal available."""


class RunCompletion(ImmutableContract):
    outcome: RunCompletionOutcome
    reason: str = Field(min_length=1, max_length=500)


SUPPORTED_RESOURCE_SCOPES = ("fixture_only",)
"""P8-CR2: the closed set of `AuthorizationEnvelope.resource_scope` values
this Foundation can honestly issue. `fixture_only` is the only value in use
— every registered Tool (`bootstrap/dev_agent.py`) touches only the
in-memory Fixture, never a real filesystem or network — so this is a
truthful boundary, not an aspirational one (P8-REQ-033's "never claim more
than is built" discipline applied to Envelope data)."""

DEFAULT_APPROVAL_ACTOR_CLASS = "human_reviewer"
"""P8-CR2: the only Actor Class this Foundation can honestly attribute an
Approval Decision to — `submit_approval()` has exactly one caller path (the
REST Approval endpoint, driven by the Demo Run UI), and no Actor Identity
system exists in Phase 8 scope (Dynamic Sub-agent/Authority is an explicit
Non-goal). A constant Actor *Class* is deliberately as far as this goes;
inventing a richer Actor taxonomy here would be scope creep beyond what
P8-CR2 asks for."""


class AuthorizationEnvelope(ImmutableContract):
    """P8-CR2: a Frozen (`ImmutableContract` is `frozen=True`/`extra="forbid"`),
    Run-scoped grant generated by the Run Service inside `start_run()` and
    persisted alongside the `RunSnapshot` it belongs to. It is never accepted
    as caller-supplied input — `DevAgentStartRunRequest` has no field a
    caller could use to widen or replace it — so its contents are exactly
    what the Server itself derived from the Plan, Profile, and Limits at
    issuance, never something a caller can expand after the fact.

    `advance()` checks every Step/Tool it is about to execute against this
    Envelope's `allowed_step_ids`/`allowed_tool_ids`/`resource_scope`/
    `expires_at` immediately before calling into a Tool Port — a mismatch
    converges to `RunCompletionOutcome` `"authority_denied"` with zero Tool
    executions, never a silent pass-through."""

    run_id: str = Field(min_length=1, max_length=64)
    allowed_step_ids: tuple[str, ...] = Field(min_length=1)
    allowed_tool_ids: tuple[str, ...] = Field(min_length=1)
    resource_scope: str = Field(min_length=1, max_length=64)
    max_steps: int = Field(ge=1, le=MAX_PLAN_STEPS)
    max_attempts: int = Field(ge=1, le=5)
    expires_at: str | None = None
    gate_reasons: tuple[ImportantGateReason, ...] = ()
    issued_at: str = Field(min_length=1)


class ApprovalEvidence(ImmutableContract):
    """P8-CR2: Typed evidence of one Approval Decision, scoped to exactly
    one `(run_id, step_id, tool_id)` triple — the real source of truth for
    "was this Step approved", superseding the bare `StepRecord.approved`
    bool (which remains only as a Backward-Compatible cache of the same
    fact for a Run persisted before this field existed). Persisted with the
    `RunSnapshot`, so it survives Restart, and because matching in
    `advance()`'s gate check requires an exact `(step_id, tool_id)` pair, an
    Evidence record for one Step can never be read as authorizing a
    different Step or a different Tool, even within the same Run."""

    run_id: str = Field(min_length=1, max_length=64)
    step_id: str = Field(pattern=STEP_ID_PATTERN)
    tool_id: str = Field(pattern=TOOL_ID_PATTERN)
    decision: ApprovalDecision
    actor_class: str = Field(min_length=1, max_length=64)
    decided_at: str = Field(min_length=1)
    gate_reason: ImportantGateReason | None = None


class CompletionApprovalEvidence(ImmutableContract):
    """P8-RW6-C (P8-CODEX-007): Typed evidence of a Run-level Completion
    Approval Decision — deliberately a *distinct* type from
    `ApprovalEvidence` (no `step_id`/`tool_id` at all, by construction, not
    merely left `None`), so a Step Approval can never be misread as
    authorizing Completion, and a Completion Approval can never be misread
    as authorizing any one Step's Tool. `gate_reason` is always
    `ImportantGateReason.COMPLETION` — Completion is a Run Lifecycle event,
    never a Tool's own Gate Reason, so no `ToolDescriptor` ever carries this
    value."""

    run_id: str = Field(min_length=1, max_length=64)
    decision: ApprovalDecision
    actor_class: str = Field(min_length=1, max_length=64)
    decided_at: str = Field(min_length=1)
    gate_reason: Literal[ImportantGateReason.COMPLETION] = ImportantGateReason.COMPLETION


class RunSnapshot(ImmutableContract):
    """P8-D: an immutable point-in-time projection of one Run. The Run
    Service never mutates a `RunSnapshot` in place — every state change
    produces a new one via `model_copy(update=...)`."""

    run_id: str = Field(min_length=1, max_length=64)
    capability_id: CapabilityId
    plan: Plan
    approval_profile: ApprovalProfile
    retry_policy: RetryPolicy
    max_steps: int = Field(ge=1, le=MAX_PLAN_STEPS)
    state: RunState
    steps: tuple[StepRecord, ...]
    created_at: str = Field(min_length=1)
    deadline_at: str | None = None
    completion: RunCompletion | None = None
    constitution_mode: str | None = None
    """P8-E: the Constitution Mode value in effect when this Run started,
    recorded once and never revised (Historical Immutability, same
    discipline as this codebase's Branch data). `None` means no Constitution
    Provider was bound at start — an honest "no correlation was possible",
    never coerced to a default Mode value. Deliberately an opaque `str`
    (never `modules.constitution.ConstitutionMode` itself) so this module
    carries no hard dependency on the Constitution module's types — the same
    "opaque, not GD-specific" discipline `resolve_decisions()` already
    applies to Rule IDs."""
    constitution_rule_ids: tuple[str, ...] | None = None
    """The `agent` Capability View's applicable Rule IDs at Run start, or
    `None` under the same "no Provider bound" condition as `constitution_mode`."""
    envelope: AuthorizationEnvelope | None = None
    """P8-CR2: the Frozen Authorization Envelope issued at `start_run()`.
    `None` only for a Run persisted before P8-CR2 existed (Backward
    Compatibility — an old Run Store file must not become unreadable); every
    Run created after this field's introduction always has one, and
    `advance()` skips its Envelope check only for that legacy-`None` case."""
    approvals: tuple[ApprovalEvidence, ...] = ()
    """P8-CR2: every Approval Decision (`APPROVED` or `DENIED`) submitted
    for this Run, in submission order — the Typed Evidence trail
    `StepRecord.approved` is a compatibility cache of. Empty for a Run
    persisted before P8-CR2, same Backward Compatibility reasoning as
    `envelope`."""
    budget_limit: int | None = Field(default=None, ge=1)
    """P8-RW6-B (P8-CODEX-006): the Frozen Budget Limit issued at
    `start_run()`, in the same abstract Budget Units as
    `ToolDescriptor.budget_cost`. `None` only for a Run persisted before
    P8-RW6-B existed (Backward Compatibility, same discipline as `envelope`)
    — every Run created after this field's introduction always has a
    concrete Limit; `start_run()` has no way to omit one (unlike
    `deadline_seconds`, where "no Deadline" is a legitimate choice, "no
    Budget" would defeat this fix's whole purpose)."""
    budget_consumed: int = Field(ge=0, default=0)
    """The cumulative `budget_cost` of every Tool execution *attempted* so
    far (charged whether the attempt succeeds or fails — a real-world
    costly operation is not free just because it failed). Checked against
    `budget_limit` immediately before each Tool call; exceeding it converges
    to `RunCompletionOutcome` `"budget_exceeded"` with that Step's Tool
    never called."""
    completion_approvals: tuple[CompletionApprovalEvidence, ...] = ()
    """P8-RW6-C (P8-CODEX-007): every Run-level Completion Approval Decision
    submitted for this Run, in submission order — structurally distinct
    from `approvals` (Step-scoped), so a Step Approval can never satisfy the
    Completion Gate, and a Completion Approval can never satisfy a Step's
    Gate. Empty for a Run persisted before P8-RW6-C, same Backward
    Compatibility reasoning as `envelope`/`budget_limit`."""

    @model_validator(mode="after")
    def validate_approvals_belong_to_this_run(self) -> RunSnapshot:
        """P8-CR5 (P8-CODEX-004)/P8-RW6-C: a persistence/REST-boundary
        Fail-closed guard — every `ApprovalEvidence`/`CompletionApprovalEvidence`
        this `RunSnapshot` carries must be scoped to this same `run_id`.
        Constructed only via `__init__`/`model_validate()` (never via
        `model_copy()`, which Pydantic never re-validates), so this fires
        exactly where it matters: parsing a Run Store file or a REST
        request body, not on every in-process state transition. A Run whose
        stored Evidence contains another Run's Evidence (e.g. a corrupted/
        tampered file) fails validation here and is treated as
        `DevAgentRunStoreCorrupt` by the Store, never silently accepted."""

        for evidence in self.approvals:
            if evidence.run_id != self.run_id:
                raise ValueError(
                    f"ApprovalEvidence.run_id={evidence.run_id!r} does not match "
                    f"this Run's own run_id={self.run_id!r}"
                )
        for completion_evidence in self.completion_approvals:
            if completion_evidence.run_id != self.run_id:
                raise ValueError(
                    f"CompletionApprovalEvidence.run_id={completion_evidence.run_id!r} "
                    f"does not match this Run's own run_id={self.run_id!r}"
                )
        return self
