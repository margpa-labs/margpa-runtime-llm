"""Reason-specific, turn-language-frozen Judge/Repair failure messages."""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract


class EvaluationFailureCode(StrEnum):
    DEADLINE_EXCEEDED = "deadline_exceeded"
    JUDGE_TIMEOUT = "deadline_exceeded"
    MALFORMED_OUTPUT = "malformed_output"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    ACTIVATION_FAILED = "activation_failed"
    CANCELLED = "cancelled"
    REPAIR_FAILED = "repair_failed"
    EVALUATION_INCONCLUSIVE = "evaluation_inconclusive"
    REPAIR_EXHAUSTED = "repair_exhausted"


class EvaluationFailurePresentation(ImmutableContract):
    reason_code: EvaluationFailureCode
    language: str = Field(pattern=r"^(ja|en)$")
    message: str = Field(min_length=1, max_length=512)


_MESSAGES: dict[str, dict[EvaluationFailureCode, str]] = {
    "ja": {
        EvaluationFailureCode.DEADLINE_EXCEEDED: (
            "判定が設定時間内に完了しませんでした。入力内容の問題ではありません。"
        ),
        EvaluationFailureCode.MALFORMED_OUTPUT: (
            "Judgeの応答を解釈できなかったため、判定結果を使用していません。"
        ),
        EvaluationFailureCode.PROVIDER_UNAVAILABLE: (
            "選択したProviderをLoadまたは使用できませんでした。"
        ),
        EvaluationFailureCode.ACTIVATION_FAILED: (
            "選択したProviderの有効化に失敗したため、判定を実行していません。"
        ),
        EvaluationFailureCode.CANCELLED: "判定は安全に中止されました。",
        EvaluationFailureCode.REPAIR_FAILED: (
            "修復または再判定を完了できなかったため、修復結果を使用していません。"
        ),
        EvaluationFailureCode.EVALUATION_INCONCLUSIVE: "判定結果を確定できませんでした。",
        EvaluationFailureCode.REPAIR_EXHAUSTED: "Repair Budgetを使い切りました。",
    },
    "en": {
        EvaluationFailureCode.DEADLINE_EXCEEDED: (
            "Evaluation did not finish within its configured time; "
            "this was not caused by your input."
        ),
        EvaluationFailureCode.MALFORMED_OUTPUT: (
            "The Judge response could not be interpreted, so its result was not used."
        ),
        EvaluationFailureCode.PROVIDER_UNAVAILABLE: (
            "The selected provider could not be loaded or used."
        ),
        EvaluationFailureCode.ACTIVATION_FAILED: (
            "The selected provider could not be activated, so evaluation was not run."
        ),
        EvaluationFailureCode.CANCELLED: "The evaluation was cancelled safely.",
        EvaluationFailureCode.REPAIR_FAILED: (
            "Repair or re-evaluation did not finish, so its result was not used."
        ),
        EvaluationFailureCode.EVALUATION_INCONCLUSIVE: "The evaluation result was inconclusive.",
        EvaluationFailureCode.REPAIR_EXHAUSTED: "The Repair budget was exhausted.",
    },
}


def present_evaluation_failure(
    *, reason_code: EvaluationFailureCode, frozen_language: str
) -> EvaluationFailurePresentation:
    language = "ja" if frozen_language.lower().startswith("ja") else "en"
    return EvaluationFailurePresentation(
        reason_code=reason_code,
        language=language,
        message=_MESSAGES[language][reason_code],
    )


def classify_evaluation_failure(reason: str | None) -> EvaluationFailureCode | None:
    if reason is None:
        return None
    # P6-RR-R20-WU-003 (Post-Claude Independent Review Rework, resolves a
    # gap found while proving S12/S13's Live Timeout presentation, part
    # of P6-CODEX-085): R14's real Stage Deadlines
    # (`inference_stage_deadline_exceeded`, `repair_generation_stage_
    # deadline_exceeded`, `rejudge_stage_deadline_exceeded`) never
    # actually matched here — none contains the substring "timeout", and
    # none equals the bare `"deadline_exceeded"` this set checked for
    # exact equality against. They silently fell through to the generic
    # `EVALUATION_INCONCLUSIVE` presentation ("the evaluation result was
    # inconclusive") instead of the correct, more informative Timeout
    # message ("did not finish within its configured time; this was not
    # caused by your input") — a genuine Turn-facing regression this
    # Package's own new Test caught. The `"deadline_exceeded" in reason`
    # substring check now catches all three, and must stay ordered
    # *before* the `"repair"`/`"rejudge"` substring check below, since
    # two of those three Reasons also contain "repair"/"rejudge" and a
    # Stage Deadline is a more specific, more useful classification than
    # a generic Repair failure.
    if (
        reason in {"timeout", "deadline_exceeded", "judge_timeout"}
        or "timeout" in reason
        or "deadline_exceeded" in reason
    ):
        return EvaluationFailureCode.DEADLINE_EXCEEDED
    if reason in {"malformed_output", "malformed_response"}:
        return EvaluationFailureCode.MALFORMED_OUTPUT
    if reason in {"unknown", "evaluation_inconclusive"}:
        return EvaluationFailureCode.EVALUATION_INCONCLUSIVE
    if "cancel" in reason or "preempt" in reason:
        return EvaluationFailureCode.CANCELLED
    if "activation" in reason:
        return EvaluationFailureCode.ACTIVATION_FAILED
    if "budget" in reason or "exhausted" in reason:
        return EvaluationFailureCode.REPAIR_EXHAUSTED
    if "repair" in reason or "rejudge" in reason:
        return EvaluationFailureCode.REPAIR_FAILED
    if "unavailable" in reason or "model_busy" in reason or "model_call_error" in reason:
        return EvaluationFailureCode.PROVIDER_UNAVAILABLE
    return None
