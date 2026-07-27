"""Normalize and render raw thinking output without changing the Model Port."""

from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    NormalizedThinkingOutput,
    PresentedThinkingOutput,
    PresentedThinkingStreamDelta,
    PresentedThinkingStreamFinish,
    ResolvedThinkingPresentationPolicy,
    ThinkingContentKind,
    ThinkingParseStatus,
    ThinkingParseSummary,
    ThinkingPersistence,
    ThinkingSegmentDelta,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.presentation.ports.thinking_output_parser import (
    ThinkingOutputParser,
    ThinkingOutputParserSession,
)


class ThinkingPresentationRenderer:
    def __init__(self, policy: ResolvedThinkingPresentationPolicy) -> None:
        if policy.persistence is not ThinkingPersistence.DISABLED:
            raise ValueError("raw thinking persistence is not supported")
        self._policy = policy
        self._reasoning_started = False
        self._reasoning_closed = False

    def render(self, segments: tuple[ThinkingSegmentDelta, ...]) -> tuple[str, ...]:
        output: list[str] = []
        for segment in segments:
            if segment.kind is ThinkingContentKind.REASONING:
                if self._policy.visibility is ThinkingVisibility.HIDDEN:
                    continue
                if not self._reasoning_started:
                    output.append(f"<{self._policy.display_label}>")
                    self._reasoning_started = True
                if segment.text_delta:
                    output.append(segment.text_delta)
                continue

            if self._policy.visibility is ThinkingVisibility.VISIBLE:
                output.extend(self._close_reasoning())
            if segment.text_delta:
                output.append(segment.text_delta)
        return tuple(output)

    def finish(self, summary: ThinkingParseSummary) -> tuple[str, ...]:
        del summary
        if self._policy.visibility is ThinkingVisibility.VISIBLE:
            return self._close_reasoning()
        return ()

    def _close_reasoning(self) -> tuple[str, ...]:
        if not self._reasoning_started or self._reasoning_closed:
            return ()
        self._reasoning_closed = True
        return (f"</{self._policy.display_label}>",)


class ThinkingPresentationSession:
    def __init__(
        self,
        *,
        parser_session: ThinkingOutputParserSession,
        policy: ResolvedThinkingPresentationPolicy,
    ) -> None:
        self._parser_session = parser_session
        self._policy = policy
        self._renderer = ThinkingPresentationRenderer(policy)
        self._reasoning_parts: list[str] = []
        self._final_parts: list[str] = []
        self._display_parts: list[str] = []
        self._finished: PresentedThinkingStreamFinish | None = None

    def feed(self, text_delta: str) -> tuple[str, ...]:
        return self.feed_presentation(text_delta).display_deltas

    def feed_presentation(self, text_delta: str) -> PresentedThinkingStreamDelta:
        if self._finished is not None:
            raise RuntimeError("the presentation session has already finished")
        segments = self._parser_session.feed(text_delta)
        return PresentedThinkingStreamDelta(
            display_deltas=self._consume(segments),
            semantic_deltas=self._visible_semantic_deltas(segments),
        )

    def finish(self) -> PresentedThinkingStreamFinish:
        if self._finished is not None:
            return self._finished
        parser_finish = self._parser_session.finish()
        terminal_deltas = list(self._consume(parser_finish.segments))
        renderer_finish = self._renderer.finish(parser_finish.summary)
        terminal_deltas.extend(renderer_finish)
        self._display_parts.extend(renderer_finish)
        reasoning_content = (
            None
            if parser_finish.summary.status is ThinkingParseStatus.PLAIN_TEXT
            else "".join(self._reasoning_parts)
        )
        presented = PresentedThinkingOutput(
            display_content="".join(self._display_parts),
            normalized=NormalizedThinkingOutput(
                reasoning_content=reasoning_content,
                final_content="".join(self._final_parts),
                parse_status=parser_finish.summary.status,
                warnings=parser_finish.summary.warnings,
            ),
        )
        self._finished = PresentedThinkingStreamFinish(
            display_deltas=tuple(terminal_deltas),
            semantic_deltas=self._visible_semantic_deltas(parser_finish.segments),
            presented=presented,
        )
        return self._finished

    def _consume(self, segments: tuple[ThinkingSegmentDelta, ...]) -> tuple[str, ...]:
        for segment in segments:
            if segment.kind is ThinkingContentKind.REASONING:
                self._reasoning_parts.append(segment.text_delta)
            else:
                self._final_parts.append(segment.text_delta)
        display_deltas = self._renderer.render(segments)
        self._display_parts.extend(display_deltas)
        return display_deltas

    def _visible_semantic_deltas(
        self,
        segments: tuple[ThinkingSegmentDelta, ...],
    ) -> tuple[ThinkingSegmentDelta, ...]:
        if self._policy.visibility is ThinkingVisibility.VISIBLE:
            return tuple(segment for segment in segments if segment.text_delta)
        return tuple(
            segment
            for segment in segments
            if segment.kind is ThinkingContentKind.FINAL and segment.text_delta
        )


class ThinkingPresentationService:
    def __init__(self, parser: ThinkingOutputParser) -> None:
        self._parser = parser

    def present_text(
        self,
        raw_content: str,
        policy: ResolvedThinkingPresentationPolicy,
    ) -> PresentedThinkingOutput:
        session = self.start_stream(policy)
        session.feed(raw_content)
        return session.finish().presented

    def start_stream(
        self,
        policy: ResolvedThinkingPresentationPolicy,
    ) -> ThinkingPresentationSession:
        return ThinkingPresentationSession(
            parser_session=self._parser.start(),
            policy=policy,
        )
