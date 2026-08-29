"""Standard Governance Result (architecture §3.3, P4-RES-001..005).

Fact/Observation/Recommendation/Execution stay in separate fields —
`recommended_actions` and `executed_actions` are never merged into one
ambiguous list (P4-RES-004), and `severity`/`deviations` are never
collapsed into a single opaque score (P4-EVL-004).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"


class ExecutionState(StrEnum):
    NOT_EVALUATED = "not_evaluated"
    """Mode is OFF: the Point was never invoked (P4-MOD-002)."""

    EVALUATED = "evaluated"
    """The Point ran (observe or enforce) and this Result is its output."""

    DEGRADED = "degraded"
    """A component (Mode Provider, Evidence, Evaluator, Binder, Resolver,
    Adapter) failed. Observe never mutates Model I/O even here — this
    state exists so the failure is still visible, not silently absorbed
    into a false `evaluated`/`not_evaluated` Result (P4-CODEX-005)."""

    UNAVAILABLE = "unavailable"
    """Enforce was requested but a required Binding/Action/Authority/Budget
    input is missing — never silently downgraded to observe (P4-MOD-005)."""

    INACTIVE_NO_DEFINITIONS = "inactive_no_definitions"
    """Observe (or Enforce, pre-Binding-check) with zero bound Execution
    Descriptors — the Definitions-0 Baseline (P4-GD-005/P4-ACC-001). The
    Evaluator is never invoked here: a Core-owned structural check firing
    on zero Definitions would contradict the Frozen Acceptance Matrix row
    `Definitions 0 + observe: inactive_no_definitions / output unchanged`
    (P4-CODEX-004)."""


class Severity(StrEnum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ObservationOutcome(StrEnum):
    PASS = "pass"
    DEVIATION = "deviation"
    UNKNOWN = "unknown"
    DEFERRED_TO_SEMANTIC_EVALUATOR = "deferred_to_semantic_evaluator"


class Observation(ImmutableContract):
    descriptor_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    evaluation_method: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    outcome: ObservationOutcome
    detail_code: str | None = Field(default=None, max_length=64, pattern=_IDENTIFIER_PATTERN)
    severity: Severity = Severity.NONE
    recommended_action_id: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )


class Deviation(ImmutableContract):
    descriptor_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    severity: Severity
    detail_code: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    recommended_action_id: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )


class RecommendedAction(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    reason_descriptor_id: str | None = Field(
        default=None, max_length=128, pattern=_IDENTIFIER_PATTERN
    )
    severity: Severity


class ExecutedAction(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    executed: bool
    # Whether this Action, when Executed, actually changes Model Input,
    # Generation Config, Terminal Output or Conversation Persistence
    # (`stop_before_generation`/`reject_output`/`constrain_generation_config`)
    # versus being purely observational (`pass`/`recommend_only`/`warn`).
    # Always explicit — never defaulted — so a Result can never blur
    # "did something happen" into "was it enforced" (P4-CODEX-006).
    intervening: bool
    not_executed_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )


class StandardGovernanceResult(ImmutableContract):
    invocation_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    point_id: str = Field(min_length=1, max_length=128)
    stage: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    mode: str = Field(min_length=1, max_length=16, pattern=_IDENTIFIER_PATTERN)
    execution_state: ExecutionState
    # Populated only for UNAVAILABLE/INACTIVE_NO_DEFINITIONS/DEGRADED —
    # Typed, Safe-projectable reasons (P4-STS-001/002), never a raw
    # exception message or Definition-specific vocabulary.
    unavailable_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )
    binding_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    selected_descriptor_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=4096)
    observations: tuple[Observation, ...] = Field(default_factory=tuple, max_length=4096)
    deviations: tuple[Deviation, ...] = Field(default_factory=tuple, max_length=4096)
    severity: Severity = Severity.NONE
    recommended_actions: tuple[RecommendedAction, ...] = Field(
        default_factory=tuple, max_length=256
    )
    executed_actions: tuple[ExecutedAction, ...] = Field(default_factory=tuple, max_length=256)
    warnings: tuple[str, ...] = Field(default_factory=tuple, max_length=256)
    latency_ms: int = Field(ge=0, default=0)
    call_count: int = Field(ge=0, default=0)
