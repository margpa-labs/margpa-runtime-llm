"""Stateful parser for a leading tagged thinking section."""

from enum import StrEnum

from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ThinkingContentKind,
    ThinkingParserFinish,
    ThinkingParseStatus,
    ThinkingParseSummary,
    ThinkingParseWarning,
    ThinkingSegmentDelta,
)


class _ParserState(StrEnum):
    DETECTING_PREFIX = "detecting_prefix"
    INSIDE_REASONING = "inside_reasoning"
    AFTER_REASONING = "after_reasoning"
    PLAIN_TEXT = "plain_text"


class TaggedThinkingOutputParser:
    def __init__(self, *, opening_delimiter: str, closing_delimiter: str) -> None:
        self._opening_delimiter = opening_delimiter
        self._closing_delimiter = closing_delimiter

    def start(self) -> "TaggedThinkingOutputParserSession":
        return TaggedThinkingOutputParserSession(
            opening_delimiter=self._opening_delimiter,
            closing_delimiter=self._closing_delimiter,
        )


class TaggedThinkingOutputParserSession:
    def __init__(self, *, opening_delimiter: str, closing_delimiter: str) -> None:
        self._opening_delimiter = opening_delimiter
        self._closing_delimiter = closing_delimiter
        self._state = _ParserState.DETECTING_PREFIX
        self._buffer = ""
        self._reasoning_scan_tail = ""
        self._final_scan_tail = ""
        self._extra_delimiter_detected = False
        self._finished: ThinkingParserFinish | None = None

    def feed(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]:
        if self._finished is not None:
            raise RuntimeError("the parser session has already finished")
        if not text_delta:
            return ()
        if self._state is _ParserState.DETECTING_PREFIX:
            return self._feed_detecting(text_delta)
        if self._state is _ParserState.INSIDE_REASONING:
            return self._feed_reasoning(text_delta)
        if self._state is _ParserState.AFTER_REASONING:
            return self._feed_final(text_delta)
        return (
            ThinkingSegmentDelta(
                kind=ThinkingContentKind.FINAL,
                text_delta=text_delta,
            ),
        )

    def finish(self) -> ThinkingParserFinish:
        if self._finished is not None:
            return self._finished

        terminal_segments: tuple[ThinkingSegmentDelta, ...] = ()
        warnings: tuple[ThinkingParseWarning, ...] = ()
        if self._state is _ParserState.DETECTING_PREFIX:
            if self._buffer:
                terminal_segments = (
                    ThinkingSegmentDelta(
                        kind=ThinkingContentKind.FINAL,
                        text_delta=self._buffer,
                    ),
                )
            status = ThinkingParseStatus.PLAIN_TEXT
        elif self._state is _ParserState.PLAIN_TEXT:
            status = ThinkingParseStatus.PLAIN_TEXT
        elif self._state is _ParserState.INSIDE_REASONING:
            if self._buffer:
                self._scan_reasoning_for_extra(self._buffer)
                terminal_segments = (
                    ThinkingSegmentDelta(
                        kind=ThinkingContentKind.REASONING,
                        text_delta=self._buffer,
                    ),
                )
            status = ThinkingParseStatus.UNCLOSED_REASONING
            warning_values = [
                ThinkingParseWarning(
                    code="unclosed_reasoning",
                    safe_message="The leading thinking section was not closed.",
                )
            ]
            if self._extra_delimiter_detected:
                warning_values.append(_extra_delimiter_warning())
            warnings = tuple(warning_values)
        elif self._extra_delimiter_detected:
            status = ThinkingParseStatus.MALFORMED_PROTOCOL
            warnings = (_extra_delimiter_warning(),)
        else:
            status = ThinkingParseStatus.COMPLETE

        self._buffer = ""
        self._finished = ThinkingParserFinish(
            segments=terminal_segments,
            summary=ThinkingParseSummary(status=status, warnings=warnings),
        )
        return self._finished

    def _feed_detecting(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]:
        self._buffer += text_delta
        first_non_whitespace = 0
        while (
            first_non_whitespace < len(self._buffer)
            and self._buffer[first_non_whitespace].isspace()
        ):
            first_non_whitespace += 1
        if first_non_whitespace == len(self._buffer):
            return ()

        candidate = self._buffer[first_non_whitespace:]
        if candidate.startswith(self._opening_delimiter):
            remainder = candidate[len(self._opening_delimiter) :]
            self._buffer = ""
            self._state = _ParserState.INSIDE_REASONING
            opening_signal = ThinkingSegmentDelta(
                kind=ThinkingContentKind.REASONING,
                text_delta="",
            )
            return (opening_signal, *self._feed_reasoning(remainder))
        if self._opening_delimiter.startswith(candidate):
            return ()

        plain_text = self._buffer
        self._buffer = ""
        self._state = _ParserState.PLAIN_TEXT
        return (
            ThinkingSegmentDelta(
                kind=ThinkingContentKind.FINAL,
                text_delta=plain_text,
            ),
        )

    def _feed_reasoning(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]:
        self._buffer += text_delta
        closing_index = self._buffer.find(self._closing_delimiter)
        if closing_index >= 0:
            reasoning = self._buffer[:closing_index]
            self._scan_reasoning_for_extra(reasoning)
            remainder = self._buffer[closing_index + len(self._closing_delimiter) :]
            self._buffer = ""
            self._state = _ParserState.AFTER_REASONING
            segments: list[ThinkingSegmentDelta] = []
            if reasoning:
                segments.append(
                    ThinkingSegmentDelta(
                        kind=ThinkingContentKind.REASONING,
                        text_delta=reasoning,
                    )
                )
            segments.append(
                ThinkingSegmentDelta(
                    kind=ThinkingContentKind.FINAL,
                    text_delta="",
                )
            )
            segments.extend(self._feed_final(remainder))
            return tuple(segments)

        suffix_length = _longest_suffix_prefix(self._buffer, self._closing_delimiter)
        safe_length = len(self._buffer) - suffix_length
        if safe_length == 0:
            return ()
        reasoning = self._buffer[:safe_length]
        self._scan_reasoning_for_extra(reasoning)
        self._buffer = self._buffer[safe_length:]
        return (
            ThinkingSegmentDelta(
                kind=ThinkingContentKind.REASONING,
                text_delta=reasoning,
            ),
        )

    def _scan_reasoning_for_extra(self, text_delta: str) -> None:
        scan_value = self._reasoning_scan_tail + text_delta
        if self._opening_delimiter in scan_value:
            self._extra_delimiter_detected = True
        tail_length = len(self._opening_delimiter) - 1
        self._reasoning_scan_tail = scan_value[-tail_length:] if tail_length else ""

    def _feed_final(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]:
        if not text_delta:
            return ()
        scan_value = self._final_scan_tail + text_delta
        if self._opening_delimiter in scan_value or self._closing_delimiter in scan_value:
            self._extra_delimiter_detected = True
        tail_length = (
            max(
                len(self._opening_delimiter),
                len(self._closing_delimiter),
            )
            - 1
        )
        self._final_scan_tail = scan_value[-tail_length:] if tail_length else ""
        return (
            ThinkingSegmentDelta(
                kind=ThinkingContentKind.FINAL,
                text_delta=text_delta,
            ),
        )


def _longest_suffix_prefix(value: str, delimiter: str) -> int:
    maximum = min(len(value), len(delimiter) - 1)
    for length in range(maximum, 0, -1):
        if value.endswith(delimiter[:length]):
            return length
    return 0


def _extra_delimiter_warning() -> ThinkingParseWarning:
    return ThinkingParseWarning(
        code="unexpected_extra_delimiter",
        safe_message="An extra thinking delimiter was found in model output.",
    )
