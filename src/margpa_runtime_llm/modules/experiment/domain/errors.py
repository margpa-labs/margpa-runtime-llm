"""Typed errors for the Experiment Core Domain (Phase 9-2, WU-A)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExperimentCoreErrorCode(StrEnum):
    EMPTY_IDENTIFIER = "empty_identifier"
    DUPLICATE_IDENTIFIER = "duplicate_identifier"
    UNKNOWN_VARIANT = "unknown_variant"
    PLAN_DIGEST_MISMATCH = "plan_digest_mismatch"
    INVALID_STATE_TRANSITION = "invalid_state_transition"
    TERMINAL_ALREADY_PUBLISHED = "terminal_already_published"
    LATE_RESULT_REJECTED = "late_result_rejected"
    NOT_FOUND = "not_found"
    UNSAFE_IDENTIFIER = "unsafe_identifier"
    COMPONENT_SLOT_MISMATCH = "component_slot_mismatch"
    CONFIGURATION_DIGEST_MISMATCH = "configuration_digest_mismatch"
    HUMAN_KIND_REQUIRES_HUMAN_FACTORY = "human_kind_requires_human_factory"
    MULTI_FACTOR_DIFFERENCE = "multi_factor_difference"
    DECLARED_DIFF_MISMATCH = "declared_diff_mismatch"
    UNREGISTERED_REPAIR_ACTOR = "unregistered_repair_actor"
    CALL_ZERO_REASON_MISSING = "call_zero_reason_missing"
    CALL_ZERO_REASON_ON_NONZERO_CALL = "call_zero_reason_on_nonzero_call"
    STRICT_BUFFER_EMITTED_NON_FINAL_EVENT = "strict_buffer_emitted_non_final_event"
    UNVERIFIED_CONTENT_MARKED_VERIFIED = "unverified_content_marked_verified"
    PROGRESSIVE_STATE_NOT_MONOTONIC = "progressive_state_not_monotonic"
    PROGRESSIVE_SEQUENCE_MISSING_FINAL = "progressive_sequence_missing_final"
    CASE_ID_MISMATCH = "case_id_mismatch"
    CASE_DIGEST_MISMATCH = "case_digest_mismatch"
    CONFIG_DIGEST_UNKNOWN_VARIANT = "config_digest_unknown_variant"
    MAX_VARIANT_RUNS_EXCEEDED = "max_variant_runs_exceeded"
    EXECUTION_ORDER_VIOLATION = "execution_order_violation"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    PRODUCTION_ADAPTER_UNAVAILABLE = "production_adapter_unavailable"
    OBSERVATION_RUN_OR_CASE_MISMATCH = "observation_run_or_case_mismatch"
    LIVE_CONFIG_MISMATCH = "live_config_mismatch"
    LIVE_CONFIG_UNAVAILABLE = "live_config_unavailable"
    CONFIGURATION_LEASE_UNAVAILABLE = "configuration_lease_unavailable"
    RUBRIC_REVISION_MISMATCH = "rubric_revision_mismatch"


@dataclass(frozen=True, slots=True)
class ExperimentCoreError(Exception):
    """Fail-closed Typed error for every Experiment Core rejection (WU-A
    A1: "重複ID、空ID、未知Variant、Plan Digest不一致をTyped Rejectする").
    Never a bare `ValueError`/`KeyError` a caller could mistake for an
    unrelated bug. Matches the established
    `@dataclass(frozen=True, slots=True) class *Error(Exception)`
    convention already used across this codebase (e.g. `modules.
    configuration_control.contracts.ConfigurationControlError`) rather
    than inventing a one-off shape for this module alone."""

    code: ExperimentCoreErrorCode
    safe_message: str
