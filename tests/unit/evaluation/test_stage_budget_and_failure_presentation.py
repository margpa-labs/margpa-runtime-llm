from pathlib import Path

from margpa_runtime_llm.modules.evaluation.application.failure_presentation import (
    EvaluationFailureCode,
    classify_evaluation_failure,
    present_evaluation_failure,
)
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    load_stage_budget_registry,
    resolve_local_macos_judge_budget,
)


def test_local_stage_budget_replaces_one_deadline_with_seven_named_stages() -> None:
    path = Path(__file__).parents[3] / "config/profiles/phase_6_role_stage_budgets.toml"
    registry = load_stage_budget_registry(path)
    profile = registry.resolve(
        role="judge",
        provider_id="judge.selene-1-mini-llama-3.1-8b-q5-k-m",
        hardware_profile="local.macos-arm64.metal",
    )
    assert profile is not None
    assert profile.verification_state == "configured_not_hardware_verified"
    assert profile.load_budget_ms == 180_000
    assert profile.prompt_build_budget_ms == 5_000
    assert profile.inference_budget_ms == 120_000
    assert profile.decode_budget_ms == 5_000
    assert profile.repair_generation_budget_ms == 180_000
    assert profile.rejudge_budget_ms == 120_000
    assert profile.cancel_grace_ms == 10_000
    assert len(profile.digest_sha512) == 128


def test_role_provider_hardware_tuple_must_match_exactly() -> None:
    path = Path(__file__).parents[3] / "config/profiles/phase_6_role_stage_budgets.toml"
    registry = load_stage_budget_registry(path)
    assert (
        registry.resolve(
            role="judge",
            provider_id="judge.selene-1-mini-llama-3.1-8b-q5-k-m",
            hardware_profile="unverified.other.hardware",
        )
        is None
    )


def test_built_in_judge_has_a_zero_model_call_stage_budget() -> None:
    profile = resolve_local_macos_judge_budget("built_in.deterministic")
    assert profile.verification_state == "deterministic_no_model_call"
    assert profile.inference_budget_ms == 0
    assert profile.enforce_pipeline_budget_ms == 0


def test_five_failure_reasons_have_distinct_ja_and_en_presentations() -> None:
    codes = tuple(EvaluationFailureCode)
    ja = tuple(
        present_evaluation_failure(reason_code=code, frozen_language="ja").message for code in codes
    )
    en = tuple(
        present_evaluation_failure(reason_code=code, frozen_language="en").message for code in codes
    )
    assert len(set(ja)) == len(codes)
    assert len(set(en)) == len(codes)
    timeout_ja = present_evaluation_failure(
        reason_code=EvaluationFailureCode.JUDGE_TIMEOUT, frozen_language="ja-JP"
    )
    timeout_en = present_evaluation_failure(
        reason_code=EvaluationFailureCode.JUDGE_TIMEOUT, frozen_language="en-US"
    )
    assert timeout_ja.language == "ja"
    assert "入力内容の問題ではありません" in timeout_ja.message
    assert timeout_en.language == "en"
    assert "not caused by your input" in timeout_en.message


def test_runtime_failure_codes_are_not_collapsed() -> None:
    assert classify_evaluation_failure("deadline_exceeded") is EvaluationFailureCode.JUDGE_TIMEOUT
    assert classify_evaluation_failure("malformed_output") is EvaluationFailureCode.MALFORMED_OUTPUT
    assert (
        classify_evaluation_failure("provider_unavailable")
        is EvaluationFailureCode.PROVIDER_UNAVAILABLE
    )
    assert (
        classify_evaluation_failure("evaluation_inconclusive")
        is EvaluationFailureCode.EVALUATION_INCONCLUSIVE
    )
    assert (
        classify_evaluation_failure("repair_budget_exceeded_before_rejudge")
        is EvaluationFailureCode.REPAIR_EXHAUSTED
    )


def test_stage_deadline_reasons_classify_as_timeout_not_inconclusive() -> None:
    """P6-RR-R20-WU-003 (resolves a gap found while proving S12/S13's Live
    Timeout presentation, part of P6-CODEX-085): R14's three real Stage
    Deadline failure reasons previously matched none of this function's
    checks (no `"timeout"` substring, not equal to the bare
    `"deadline_exceeded"` string) and silently fell through to the
    generic `EVALUATION_INCONCLUSIVE` presentation — a genuine
    Turn-facing regression, not just a missing test."""
    assert (
        classify_evaluation_failure("inference_stage_deadline_exceeded")
        is EvaluationFailureCode.JUDGE_TIMEOUT
    )
    assert (
        classify_evaluation_failure("repair_generation_stage_deadline_exceeded")
        is EvaluationFailureCode.JUDGE_TIMEOUT
    )
    assert (
        classify_evaluation_failure("rejudge_stage_deadline_exceeded")
        is EvaluationFailureCode.JUDGE_TIMEOUT
    )
