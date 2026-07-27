"""Port for model-declared thinking output protocols."""

from typing import Protocol

from ..contracts.thinking import ThinkingParserFinish, ThinkingSegmentDelta


class ThinkingOutputParserSession(Protocol):
    def feed(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]: ...

    def finish(self) -> ThinkingParserFinish: ...


class ThinkingOutputParser(Protocol):
    def start(self) -> ThinkingOutputParserSession: ...
