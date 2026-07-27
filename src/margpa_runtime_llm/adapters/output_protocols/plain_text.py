"""Plain-text output parser."""

from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ThinkingContentKind,
    ThinkingParserFinish,
    ThinkingParseStatus,
    ThinkingParseSummary,
    ThinkingSegmentDelta,
)


class PlainTextOutputParser:
    def start(self) -> "PlainTextOutputParserSession":
        return PlainTextOutputParserSession()


class PlainTextOutputParserSession:
    def __init__(self) -> None:
        self._finished: ThinkingParserFinish | None = None

    def feed(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]:
        if self._finished is not None:
            raise RuntimeError("the parser session has already finished")
        if not text_delta:
            return ()
        return (
            ThinkingSegmentDelta(
                kind=ThinkingContentKind.FINAL,
                text_delta=text_delta,
            ),
        )

    def finish(self) -> ThinkingParserFinish:
        if self._finished is None:
            self._finished = ThinkingParserFinish(
                summary=ThinkingParseSummary(status=ThinkingParseStatus.PLAIN_TEXT)
            )
        return self._finished
