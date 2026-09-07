"""Freshness / Source Revision Governance (Phase 9-2, WU-D D1).

Design §8.1: "過去TurnのCitation/Revision/Digestは永久に固定し、新Turn
だけCurrent Sourceを再評価する" -- `classify_freshness_answer()` is the
one function deciding whether a NEW Turn's answer genuinely used Current
Source content, repeated a now-stale historical claim, or (the worst
case) coincided with the PAST Turn's own citation record being rewritten."""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identity import require_safe_identifier


class SourceRevisionState(StrEnum):
    CURRENT = "current"
    UPDATED = "updated"
    DELETED = "deleted"
    UNKNOWN = "unknown"


class FreshnessOutcome(StrEnum):
    CURRENT_FACT_USED = "current_fact_used"
    STALE_FACT_REPEATED = "stale_fact_repeated"
    HISTORICAL_CITATION_ALTERED = "historical_citation_altered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class FreshnessCase(ImmutableContract):
    case_id: str
    historical_claim: str
    historical_citation_digest_sha512: str
    source_revision_state: SourceRevisionState
    current_source_value: str | None = None

    @model_validator(mode="after")
    def _validate_id(self) -> FreshnessCase:
        require_safe_identifier(self.case_id, field_name="case_id")
        return self


def classify_freshness_answer(
    *,
    case: FreshnessCase,
    new_turn_answer: str,
    historical_turn_citation_digest_after_answer: str,
) -> FreshnessOutcome:
    """`historical_turn_citation_digest_after_answer` is the PAST Turn's
    own citation digest, re-read AFTER the new Turn's answer was
    produced -- if it no longer matches `case.historical_citation_
    digest_sha512`, the past Turn's own record was mutated. That is
    classified as the single worst outcome regardless of what the new
    answer itself said, independent of every other check below."""

    if historical_turn_citation_digest_after_answer != case.historical_citation_digest_sha512:
        return FreshnessOutcome.HISTORICAL_CITATION_ALTERED
    if case.source_revision_state in (SourceRevisionState.UPDATED, SourceRevisionState.DELETED):
        if case.current_source_value is not None and case.current_source_value in new_turn_answer:
            return FreshnessOutcome.CURRENT_FACT_USED
        if case.historical_claim in new_turn_answer:
            return FreshnessOutcome.STALE_FACT_REPEATED
        return FreshnessOutcome.INSUFFICIENT_EVIDENCE
    return FreshnessOutcome.CURRENT_FACT_USED
