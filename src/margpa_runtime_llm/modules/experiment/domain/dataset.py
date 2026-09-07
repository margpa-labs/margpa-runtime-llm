"""Evaluation Case Manifest (Phase 9-2, WU-B B1).

Deliberately NOT a reuse or subclass of `modules.evaluation.domain.
dataset.EvaluationCase` (Phase 6's own Contract): that type's
`criteria: tuple[str, ...]` field is shaped for Phase 6's Deterministic
Rubric Evaluator specifically, and carries no Evidence/Expected-
Observation/Human-Review-necessity fields -- forcing this Phase 9-2
shape onto it would either bloat an already-live Phase 6 Contract with
unrelated fields or silently misuse `criteria` for something it was
never designed to hold. This is Experiment Core's own, independent
Manifest type instead (WU-A A2's same "Adapter, not force-reuse"
reasoning as `config_snapshot.py`)."""

from __future__ import annotations

import hashlib
from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .canonical import canonical_json_bytes
from .identity import require_safe_identifier


class ObservationOutcome(StrEnum):
    """WU-B B1/B3, and project-wide P9-REQ-003: `NOT_RUN`/`UNAVAILABLE`/
    `UNSUPPORTED` are real, distinct, first-class outcomes here -- never
    silently coerced into `FAIL` or `PASS` by a caller with nothing else
    to report."""

    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"
    NOT_APPLICABLE = "not_applicable"
    NOT_RUN = "not_run"
    UNAVAILABLE = "unavailable"


class EvaluationCaseManifest(ImmutableContract):
    """WU-B B1: `case_id`/`revision` are independently versioned (a Case
    can be revised without changing its `case_id`, and an `ExperimentPlan`
    freezes one exact `case_revision`, `identity.py`'s `ExperimentPlan.
    case_revision`). `requires_human_review=True` marks a Case whose
    `acceptable_outcomes` alone cannot resolve success (WU-B B1: "正解を
    一つへ固定できないCaseは、許容範囲とHuman Review必要性を明示する") --
    an LLM-only Evaluation of such a Case is never presented as
    equivalent to a completed Human Review (see `evaluation.py`'s
    `build_human_observation`/`build_automated_observation` split)."""

    case_id: str
    revision: str
    input: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()
    expected_observations: tuple[str, ...] = ()
    acceptable_outcomes: tuple[ObservationOutcome, ...] = (ObservationOutcome.PASS,)
    requires_human_review: bool = False

    @model_validator(mode="after")
    def _validate_ids(self) -> EvaluationCaseManifest:
        require_safe_identifier(self.case_id, field_name="case_id")
        require_safe_identifier(self.revision, field_name="revision")
        return self


def compute_case_digest_sha512(case: EvaluationCaseManifest) -> str:
    """R1-WU-01: a content Digest of the actual Case Manifest a Plan
    freezes -- `case_revision` alone (Design's original Canonical Domain
    Candidate) is shared across every Case in a Case Pack revision
    (`case_pack.CASE_PACK_REVISION`), so it cannot answer "which Case did
    this persisted Plan choose". `ExperimentPlan.case_digest_sha512`
    (`identity.py`) is this function's output, letting a Run-start re-
    derive the same Case by `case_id` from the live Case Pack and detect
    -- rather than silently ignore -- a Case Pack content change since
    the Plan was frozen."""

    payload: dict[str, object] = {
        "case_id": case.case_id,
        "revision": case.revision,
        "input": case.input,
        "evidence_refs": list(case.evidence_refs),
        "expected_observations": list(case.expected_observations),
        "acceptable_outcomes": [item.value for item in case.acceptable_outcomes],
        "requires_human_review": case.requires_human_review,
    }
    return hashlib.sha512(canonical_json_bytes(payload)).hexdigest()
