"""Phase 9-2 WU-B B1: EvaluationCaseManifest."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.experiment.domain.dataset import (
    EvaluationCaseManifest,
    ObservationOutcome,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)


def test_case_manifest_defaults_to_pass_only_acceptable_outcome_and_no_human_review() -> None:
    case = EvaluationCaseManifest(
        case_id="case-ALPHA-15",
        revision="rev-1",
        input="What is the confirmed value of ALPHA-15?",
    )
    assert case.acceptable_outcomes == (ObservationOutcome.PASS,)
    assert case.requires_human_review is False


def test_case_manifest_can_declare_no_single_correct_answer_and_require_human_review() -> None:
    case = EvaluationCaseManifest(
        case_id="case-ALPHA-open",
        revision="rev-1",
        input="Summarize the ALPHA project status in your own words.",
        acceptable_outcomes=(ObservationOutcome.PASS, ObservationOutcome.INCONCLUSIVE),
        requires_human_review=True,
    )
    assert case.requires_human_review is True
    assert ObservationOutcome.INCONCLUSIVE in case.acceptable_outcomes


def test_case_manifest_rejects_empty_case_id() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        EvaluationCaseManifest(case_id="", revision="rev-1", input="x")
    assert excinfo.value.code is ExperimentCoreErrorCode.EMPTY_IDENTIFIER


def test_case_manifest_rejects_empty_input() -> None:
    with pytest.raises(ValidationError):
        EvaluationCaseManifest(case_id="case-a", revision="rev-1", input="")
