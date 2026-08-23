from margpa_runtime_llm.modules.runtime_observability.presentation.safe_refusal import (
    SafeRefusalLanguage,
    render_safe_refusal,
)


def test_japanese_safe_refusal_matches_the_frozen_architecture_text() -> None:
    text = render_safe_refusal(
        reject_code="guardrail_reject_input", language=SafeRefusalLanguage.JA
    )
    assert text == "その依頼には対応できません。別の安全な内容であればお手伝いできます。"


def test_english_safe_refusal_matches_the_frozen_architecture_text() -> None:
    text = render_safe_refusal(
        reject_code="guardrail_reject_input", language=SafeRefusalLanguage.EN
    )
    assert text == "I cannot help with that request. I can help with a safer alternative."


def test_the_raw_reject_code_never_appears_in_the_rendered_text() -> None:
    text = render_safe_refusal(
        reject_code="guardrail_reject_input", language=SafeRefusalLanguage.EN
    )
    assert "guardrail_reject_input" not in text


def test_different_reject_codes_produce_the_same_safe_text_not_leaked_detail() -> None:
    first = render_safe_refusal(
        reject_code="guardrail_reject_input", language=SafeRefusalLanguage.EN
    )
    second = render_safe_refusal(
        reject_code="guardrail_reject_output", language=SafeRefusalLanguage.EN
    )
    assert first == second
