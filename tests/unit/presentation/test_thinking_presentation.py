"""Deterministic parser, renderer, and presentation-service tests."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.bootstrap.output_parser_registry import build_output_parser
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationResult,
    GenerationTiming,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeReference
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ThinkingOutputProtocolDefinition,
)
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    PresentedThinkingOutput,
    ResolvedThinkingPresentationPolicy,
    ThinkingParseStatus,
    ThinkingPersistence,
    ThinkingPresentationConfig,
    ThinkingPresentationSource,
    ThinkingVisibility,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITION = load_model_definition(PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml")
TAGGED_PROTOCOL = DEFINITION.output_protocol.thinking


def policy(
    visibility: ThinkingVisibility,
    label: str = "推論過程",
) -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=visibility,
        display_label=label,
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.EXPLICIT,
        display_label_source=ThinkingPresentationSource.EXPLICIT,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def tagged_service() -> ThinkingPresentationService:
    return ThinkingPresentationService(build_output_parser(TAGGED_PROTOCOL))


def present(
    raw: str,
    visibility: ThinkingVisibility,
    label: str = "推論過程",
) -> PresentedThinkingOutput:
    return tagged_service().present_text(raw, policy(visibility, label))


def test_plain_text_is_final_for_hidden_and_visible() -> None:
    raw = "Final <think>user-authored text"

    hidden = present(raw, ThinkingVisibility.HIDDEN)
    visible = present(raw, ThinkingVisibility.VISIBLE)

    for output in (hidden, visible):
        assert output.display_content == raw
        assert output.normalized.reasoning_content is None
        assert output.normalized.final_content == raw
        assert output.normalized.parse_status is ThinkingParseStatus.PLAIN_TEXT
        assert not output.normalized.warnings


def test_complete_tagged_output_is_normalized_and_rendered() -> None:
    raw = " \n<think>reasoning</think>final"

    hidden = present(raw, ThinkingVisibility.HIDDEN)
    visible = present(raw, ThinkingVisibility.VISIBLE)
    custom = present(raw, ThinkingVisibility.VISIBLE, "思考過程")

    assert hidden.display_content == "final"
    assert visible.display_content == "<推論過程>reasoning</推論過程>final"
    assert custom.display_content == "<思考過程>reasoning</思考過程>final"
    assert visible.normalized.reasoning_content == "reasoning"
    assert visible.normalized.final_content == "final"
    assert visible.normalized.parse_status is ThinkingParseStatus.COMPLETE


def test_unclosed_reasoning_has_warning_and_visible_container_is_closed() -> None:
    raw = "<think>unfinished"

    hidden = present(raw, ThinkingVisibility.HIDDEN)
    visible = present(raw, ThinkingVisibility.VISIBLE)

    assert hidden.display_content == ""
    assert visible.display_content == "<推論過程>unfinished</推論過程>"
    assert visible.normalized.reasoning_content == "unfinished"
    assert visible.normalized.final_content == ""
    assert visible.normalized.parse_status is ThinkingParseStatus.UNCLOSED_REASONING
    assert [warning.code for warning in visible.normalized.warnings] == ["unclosed_reasoning"]


def test_extra_delimiter_is_preserved_and_reported_as_malformed() -> None:
    raw = "<think>reasoning</think>final</think>"

    hidden = present(raw, ThinkingVisibility.HIDDEN)
    visible = present(raw, ThinkingVisibility.VISIBLE)

    assert hidden.display_content == "final</think>"
    assert visible.display_content == "<推論過程>reasoning</推論過程>final</think>"
    assert visible.normalized.final_content == "final</think>"
    assert visible.normalized.parse_status is ThinkingParseStatus.MALFORMED_PROTOCOL
    assert [warning.code for warning in visible.normalized.warnings] == [
        "unexpected_extra_delimiter"
    ]


def test_extra_opening_delimiter_inside_reasoning_is_preserved_and_reported() -> None:
    raw = "<think>one<think>two</think>final"

    visible = present(raw, ThinkingVisibility.VISIBLE)

    assert visible.display_content == "<推論過程>one<think>two</推論過程>final"
    assert visible.normalized.reasoning_content == "one<think>two"
    assert visible.normalized.parse_status is ThinkingParseStatus.MALFORMED_PROTOCOL
    assert [warning.code for warning in visible.normalized.warnings] == [
        "unexpected_extra_delimiter"
    ]


@pytest.mark.parametrize("split", range(1, len("<think>reasoning</think>final")))
def test_every_single_split_matches_non_streaming(split: int) -> None:
    raw = "<think>reasoning</think>final"
    expected = present(raw, ThinkingVisibility.VISIBLE)
    session = tagged_service().start_stream(policy(ThinkingVisibility.VISIBLE))

    display_deltas = [
        *session.feed(raw[:split]),
        *session.feed(raw[split:]),
    ]
    terminal = session.finish()
    display_deltas.extend(terminal.display_deltas)

    assert "".join(display_deltas) == expected.display_content
    assert terminal.presented == expected


def test_one_character_chunks_and_empty_deltas_match_non_streaming() -> None:
    raw = "<think>reasoning</think>final"
    expected = present(raw, ThinkingVisibility.VISIBLE)
    session = tagged_service().start_stream(policy(ThinkingVisibility.VISIBLE))
    display_deltas: list[str] = []

    display_deltas.extend(session.feed(""))
    for character in raw:
        display_deltas.extend(session.feed(character))
        display_deltas.extend(session.feed(""))
    terminal = session.finish()
    display_deltas.extend(terminal.display_deltas)

    assert "".join(display_deltas) == expected.display_content
    assert terminal.presented == expected


def test_hidden_stream_never_flashes_reasoning_or_canonical_tags() -> None:
    session = tagged_service().start_stream(policy(ThinkingVisibility.HIDDEN))

    before_final = [
        *session.feed("<thi"),
        *session.feed("nk>secret reasoning"),
        *session.feed("</thi"),
        *session.feed("nk>"),
    ]
    final_deltas = session.feed("safe final")
    terminal = session.finish()

    assert before_final == []
    assert "".join(final_deltas) == "safe final"
    assert terminal.display_deltas == ()
    assert terminal.presented.display_content == "safe final"


def test_raw_generation_contracts_remain_unchanged() -> None:
    raw = "<think>reasoning</think>final"
    result = GenerationResult(
        request_id="request",
        model_key="main.model",
        content=raw,
        finish_reason=FinishReason.STOP,
        timing=GenerationTiming(total_generation_seconds=0.1),
        runtime_info=ModelRuntimeReference(
            load_instance_id="load",
            model_key="main.model",
            backend_key="fake",
            backend_version="1",
            definition_file_sha512="a" * 128,
        ),
    )
    chunk = GenerationChunk(
        request_id="request",
        sequence=0,
        text_delta="<thi",
        is_final=False,
    )

    presented = present(result.content, ThinkingVisibility.HIDDEN)

    assert presented.display_content == "final"
    assert result.content == raw
    assert chunk.text_delta == "<thi"


def test_plain_parser_and_unknown_parser_registry_behavior() -> None:
    plain = ThinkingOutputProtocolDefinition(parser_key="plain_text_v1")
    plain_output = ThinkingPresentationService(build_output_parser(plain)).present_text(
        "<think>literal</think>",
        policy(ThinkingVisibility.HIDDEN),
    )
    unknown = ThinkingOutputProtocolDefinition(parser_key="future_parser_v1")

    assert plain_output.display_content == "<think>literal</think>"
    assert plain_output.normalized.parse_status is ThinkingParseStatus.PLAIN_TEXT
    with pytest.raises(InferenceError) as captured:
        build_output_parser(unknown)
    assert captured.value.code == "invalid_model_definition"


@pytest.mark.parametrize(
    "data",
    [
        {
            "parser_key": "plain_text_v1",
            "opening_delimiter": "<think>",
        },
        {"parser_key": "tagged_thinking_v1"},
        {
            "parser_key": "tagged_thinking_v1",
            "opening_delimiter": "<think>",
            "closing_delimiter": "<think>",
        },
        {
            "parser_key": "tagged_thinking_v1",
            "opening_delimiter": "<think>\n",
            "closing_delimiter": "</think>",
        },
    ],
)
def test_invalid_output_protocol_definition_is_rejected(data: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        ThinkingOutputProtocolDefinition.model_validate(data)


@pytest.mark.parametrize(
    "label",
    [
        "",
        " ",
        " leading",
        "trailing ",
        "a" * 65,
        "<reasoning>",
        "reason/ing",
        "line\nbreak",
        "control\x00",
    ],
)
def test_invalid_display_label_is_rejected(label: str) -> None:
    with pytest.raises(ValidationError):
        ThinkingPresentationConfig(display_label=label)
