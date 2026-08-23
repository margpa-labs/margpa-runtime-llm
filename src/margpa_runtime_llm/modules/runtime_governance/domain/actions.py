"""Phase 4 Action Allowlist (P4-ACT-001, ADR-4-005, architecture §5).

Enforce touches only these Actions; `repair`/`regenerate`/`redact`/`tool`
stay Recommendation-only or Prohibited until Phase 5/6 (ADR-4-005/4-008).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class ActionId(StrEnum):
    PASS = "pass"
    RECOMMEND_ONLY = "recommend_only"
    WARN = "warn"
    STOP_BEFORE_GENERATION = "stop_before_generation"
    REJECT_OUTPUT = "reject_output"
    CONSTRAIN_GENERATION_CONFIG = "constrain_generation_config"


# Actions Phase 4 recognizes but never auto-executes (ADR-4-005/4-008):
# recommendation-only until a bounded Repair Loop exists (Phase 6).
NOT_EXECUTABLE_ACTION_IDS = frozenset(
    {"repair", "regenerate", "rebind", "reinitialize", "redact_secret", "redact_pii"}
)


class NotExecutedReason(StrEnum):
    MODE_NOT_ENFORCE = "mode_not_enforce"
    BINDING_UNAVAILABLE = "binding_unavailable"
    # Any of the Binding's embedded Capability/Authority/Policy/Budget/
    # Registry Digests no longer matches the *current* live Snapshot at
    # Resolve time — the Binding was valid when cached but the live State
    # moved on (architecture §9 "Stale Binding再利用禁止"). This is the
    # Resolver's own real capability/policy/budget re-check (P4-CODEX-006),
    # not a duplicate of `BINDING_UNAVAILABLE` (which covers a Binding
    # that was never Executable in the first place, e.g. zero Descriptors).
    BINDING_STALE = "binding_stale"
    ACTION_NOT_REGISTERED = "action_not_registered"
    ACTION_NOT_ALLOWED_AT_POINT = "action_not_allowed_at_point"
    AUTHORITY_MISSING = "authority_missing"
    CAPABILITY_MISSING = "capability_missing"
    BUDGET_EXCEEDED = "budget_exceeded"
    CONFLICT_UNRESOLVED = "conflict_unresolved"
    # A *different* Action ID, recommended in the same Invocation, takes
    # precedence over this one under the Phase 4 fixed Action precedence
    # order (e.g. `stop_before_generation` supersedes
    # `constrain_generation_config` at `pre` — once generation is Stopped,
    # Constraining its Config is moot). Distinct from `CONFLICT_UNRESOLVED`,
    # which is reserved for a genuinely undecidable same-priority conflict.
    SUPERSEDED_BY_HIGHER_PRIORITY_ACTION = "superseded_by_higher_priority_action"
    ADAPTER_FAILURE = "adapter_failure"
    NOT_EXECUTABLE_ACTION_CLASS = "not_executable_action_class"


class ActionRegistryEntry(ImmutableContract):
    action_id: ActionId
    allowed_points: tuple[str, ...] = Field(min_length=1, max_length=16)
    allowed_stages: tuple[str, ...] = Field(min_length=1, max_length=8)
    side_effect_class: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
