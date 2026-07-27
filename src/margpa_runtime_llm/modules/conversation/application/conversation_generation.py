"""Coordinate one cancellable conversation generation without storing chat history."""

from __future__ import annotations

import threading
from collections.abc import Callable, Generator, Iterator
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResolvedResponseLanguagePolicy,
    ResponseLanguage,
    ResponseLanguageSource,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
    ThinkingPresentationSession,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingContentKind,
    ThinkingParseStatus,
    ThinkingParseWarning,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.orchestration.response_language import (
    compose_conversation_generation_messages,
)
from margpa_runtime_llm.orchestration.summarization import compose_summary_messages

from ..contracts import (
    ConversationDeltaChannel,
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
)

TOKEN_LIMIT_WARNING = "最終回答を生成する前にToken上限へ到達しました。"
SUMMARY_FALLBACK_WARNING = (
    "The summary could not be completed safely. The original answer is shown."
)


class ConversationInference(Protocol):
    def stream(self, request: GenerationRequest) -> GenerationStream: ...


@dataclass(frozen=True, slots=True)
class _StageResult:
    finish_reason: FinishReason | None = None
    usage: TokenUsage | None = None
    final_content: str = ""
    display_content: str = ""
    parse_status: ThinkingParseStatus | None = None
    warnings: tuple[ThinkingParseWarning, ...] = ()
    cancelled: bool = False


class ConversationGenerationSession:
    def __init__(
        self,
        *,
        request: GenerationRequest,
        inference: ConversationInference,
        presentation: ThinkingPresentationService,
        presentation_policy: ResolvedThinkingPresentationPolicy,
        summarization: SummarizationConfig,
        summary_mode: SummaryMode,
        response_language: ResponseLanguage,
        release: Callable[[], None],
    ) -> None:
        self._request = request
        self._inference = inference
        self._presentation = presentation
        self._presentation_policy = presentation_policy
        self._summarization = summarization
        self._summary_mode = summary_mode
        self._response_language = response_language
        self._release = release
        self._cancel_requested = threading.Event()
        self._finished = threading.Event()
        self._consumption_lock = threading.Lock()
        self._stream_lock = threading.Lock()
        self._active_stream: GenerationStream | None = None

    @property
    def request_id(self) -> str:
        return self._request.request_id

    @property
    def finished(self) -> bool:
        return self._finished.is_set()

    def request_cancel(self) -> None:
        self._cancel_requested.set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._finished.wait(timeout)

    def force_cancel(self) -> None:
        """Legacy emergency hook; normal callers use cooperative request_cancel()."""

        self._cancel_requested.set()
        with self._stream_lock:
            stream = self._active_stream
        if stream is not None:
            stream.cancel()

    def events(self) -> Iterator[ConversationEvent]:
        if not self._consumption_lock.acquire(blocking=False):
            raise RuntimeError("a conversation generation session can only be consumed once")

        try:
            if self._summary_mode is SummaryMode.OFF:
                yield from self._events_without_summary()
            else:
                yield from self._events_with_summary()
        except InferenceError as exc:
            yield self._error_event(
                code=exc.code.value,
                message=exc.safe_message,
                retryable=exc.retryable,
            )
        except Exception:
            yield self._error_event(
                code="unexpected_error",
                message="The generation failed unexpectedly.",
                retryable=False,
            )
        finally:
            self._finished.set()
            self._release()

    def _events_without_summary(self) -> Generator[ConversationEvent, None, None]:
        yield self._start_event(state="generating")
        result = yield from self._run_stage(
            request=self._request,
            presentation=self._presentation.start_stream(self._presentation_policy),
            emit_deltas=True,
        )
        if result.cancelled:
            yield self._cancelled_event()
            return
        yield from self._warning_events(result.warnings)
        yield self._completed_event(
            presented=result,
            original=result,
            summary=None,
            include_summary_metadata=False,
        )

    def _events_with_summary(self) -> Generator[ConversationEvent, None, None]:
        yield self._start_event(state="generating_answer")
        hidden_policy = self._presentation_policy.model_copy(
            update={"visibility": ThinkingVisibility.HIDDEN}
        )
        original = yield from self._run_stage(
            request=self._request,
            presentation=self._presentation.start_stream(hidden_policy),
            emit_deltas=False,
        )
        if original.cancelled or self._cancel_requested.is_set():
            yield self._cancelled_event()
            return

        yield ConversationEvent(
            event=ConversationEventType.STATUS,
            data={"request_id": self.request_id, "state": "summarizing_answer"},
        )
        if not original.final_content.strip():
            yield from self._summary_fallback_events(original)
            return
        if self._cancel_requested.is_set():
            yield self._cancelled_event()
            return

        summary: _StageResult | None = None
        try:
            summary = yield from self._run_stage(
                request=self._build_summary_request(original.final_content),
                presentation=self._presentation.start_stream(hidden_policy),
                emit_deltas=False,
            )
        except Exception:
            summary = None

        if self._cancel_requested.is_set() or (summary is not None and summary.cancelled):
            yield self._cancelled_event()
            return
        if not self._valid_summary(summary):
            yield from self._summary_fallback_events(original)
            return

        assert summary is not None
        yield self._delta_event(
            summary.final_content,
            channel=ConversationDeltaChannel.FINAL,
        )
        yield from self._warning_events(original.warnings)
        yield self._completed_event(
            presented=summary,
            original=original,
            summary=summary,
            include_summary_metadata=True,
        )

    def _run_stage(
        self,
        *,
        request: GenerationRequest,
        presentation: ThinkingPresentationSession,
        emit_deltas: bool,
    ) -> Generator[ConversationEvent, None, _StageResult]:
        if self._cancel_requested.is_set():
            return _StageResult(cancelled=True)

        finish_reason: FinishReason | None = None
        usage: TokenUsage | None = None
        stream = self._inference.stream(request)
        with self._stream_lock:
            self._active_stream = stream
        try:
            with stream:
                for chunk in stream:
                    if self._cancel_requested.is_set():
                        stream.cancel()
                        return _StageResult(cancelled=True)
                    if chunk.is_final:
                        finish_reason = chunk.finish_reason
                        usage = chunk.usage
                    presentation_delta = presentation.feed_presentation(chunk.text_delta)
                    for segment in presentation_delta.semantic_deltas:
                        if emit_deltas:
                            yield self._segment_delta_event(segment.kind, segment.text_delta)

                if self._cancel_requested.is_set() or finish_reason is FinishReason.CANCELLED:
                    stream.cancel()
                    return _StageResult(cancelled=True)

                terminal = presentation.finish()
                if emit_deltas:
                    for segment in terminal.semantic_deltas:
                        yield self._segment_delta_event(segment.kind, segment.text_delta)
                normalized = terminal.presented.normalized
                warnings = list(normalized.warnings)
                if finish_reason is FinishReason.LENGTH and not normalized.final_content.strip():
                    warnings.append(
                        ThinkingParseWarning(
                            code="final_answer_token_limit",
                            safe_message=TOKEN_LIMIT_WARNING,
                        )
                    )
                return _StageResult(
                    finish_reason=finish_reason,
                    usage=usage,
                    final_content=normalized.final_content,
                    display_content=terminal.presented.display_content,
                    parse_status=normalized.parse_status,
                    warnings=tuple(warnings),
                )
        finally:
            with self._stream_lock:
                if self._active_stream is stream:
                    self._active_stream = None

    def _build_summary_request(self, original_answer: str) -> GenerationRequest:
        return GenerationRequest(
            request_id=f"{self.request_id}:summary",
            model_key=self._request.model_key,
            messages=compose_summary_messages(
                original_answer=original_answer,
                response_language=self._response_language,
            ),
            parameters=self._request.parameters.model_copy(
                update={
                    "max_new_tokens": self._summarization.max_new_tokens,
                    "thinking_mode": ThinkingMode.DISABLED,
                }
            ),
        )

    @staticmethod
    def _valid_summary(summary: _StageResult | None) -> bool:
        return bool(
            summary is not None
            and summary.finish_reason is FinishReason.STOP
            and summary.parse_status
            in {ThinkingParseStatus.PLAIN_TEXT, ThinkingParseStatus.COMPLETE}
            and summary.final_content.strip()
        )

    def _summary_fallback_events(
        self,
        original: _StageResult,
    ) -> Generator[ConversationEvent, None, None]:
        if original.final_content:
            yield self._delta_event(
                original.final_content,
                channel=ConversationDeltaChannel.FINAL,
            )
        yield from self._warning_events(original.warnings)
        yield ConversationEvent(
            event=ConversationEventType.WARNING,
            data={
                "request_id": self.request_id,
                "code": "summary_fallback_original",
                "message": SUMMARY_FALLBACK_WARNING,
            },
        )
        yield self._completed_event(
            presented=original,
            original=original,
            summary=None,
            include_summary_metadata=True,
        )

    def _start_event(self, *, state: str) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": state},
        )

    def _segment_delta_event(
        self,
        kind: ThinkingContentKind,
        text: str,
    ) -> ConversationEvent:
        channel = (
            ConversationDeltaChannel.REASONING
            if kind is ThinkingContentKind.REASONING
            else ConversationDeltaChannel.FINAL
        )
        return self._delta_event(text, channel=channel)

    def _delta_event(
        self,
        text: str,
        *,
        channel: ConversationDeltaChannel,
    ) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.DELTA,
            data={
                "request_id": self.request_id,
                "channel": channel.value,
                "text": text,
            },
        )

    def _warning_events(
        self,
        warnings: tuple[ThinkingParseWarning, ...],
    ) -> Generator[ConversationEvent, None, None]:
        for warning in warnings:
            yield ConversationEvent(
                event=ConversationEventType.WARNING,
                data={
                    "request_id": self.request_id,
                    "code": warning.code,
                    "message": warning.safe_message,
                },
            )

    def _completed_event(
        self,
        *,
        presented: _StageResult,
        original: _StageResult,
        summary: _StageResult | None,
        include_summary_metadata: bool,
    ) -> ConversationEvent:
        data: dict[str, object] = {
            "request_id": self.request_id,
            "finish_reason": (
                presented.finish_reason.value if presented.finish_reason is not None else "unknown"
            ),
            "assistant_message": {
                "role": "assistant",
                "content": presented.final_content,
            },
            "usage": (
                presented.usage.model_dump(mode="json") if presented.usage is not None else None
            ),
        }
        if include_summary_metadata:
            data.update(
                {
                    "transformation": {
                        "summary_mode": SummaryMode.POST_GENERATION.value,
                        "summary_applied": summary is not None,
                        "fallback_used": summary is None,
                        "original_finish_reason": (
                            original.finish_reason.value
                            if original.finish_reason is not None
                            else None
                        ),
                        "summary_finish_reason": (
                            summary.finish_reason.value
                            if summary is not None and summary.finish_reason is not None
                            else None
                        ),
                    },
                }
            )
        return ConversationEvent(event=ConversationEventType.COMPLETED, data=data)

    def _cancelled_event(self) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.CANCELLED,
            data={"request_id": self.request_id, "state": "cancelled"},
        )

    def _error_event(self, *, code: str, message: str, retryable: bool) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.ERROR,
            data={
                "request_id": self.request_id,
                "code": code,
                "message": message,
                "retryable": retryable,
            },
        )


class ConversationGenerationService:
    def __init__(
        self,
        *,
        inference: ConversationInference,
        presentation: ThinkingPresentationService,
        model_key: str,
        generation_defaults: GenerationParameters,
        response_language_default: ResponseLanguage,
        presentation_default: ResolvedThinkingPresentationPolicy,
        summarization: SummarizationConfig | None = None,
        thinking_control_available: bool = True,
    ) -> None:
        self._inference = inference
        self._presentation = presentation
        self._model_key = model_key
        self._generation_defaults = generation_defaults
        self._response_language_default = response_language_default
        self._presentation_default = presentation_default
        self._summarization = summarization or SummarizationConfig()
        self._thinking_control_available = thinking_control_available
        self._generation_gate = threading.Lock()
        self._active_lock = threading.Lock()
        self._active: ConversationGenerationSession | None = None

    @property
    def active_request_id(self) -> str | None:
        with self._active_lock:
            return self._active.request_id if self._active is not None else None

    def start(self, value: ConversationGenerationInput) -> ConversationGenerationSession:
        if (
            value.settings.thinking_mode is ThinkingMode.ENABLED
            and not self._thinking_control_available
        ):
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="Thinking generation control is unavailable for this model.",
            )
        if not self._generation_gate.acquire(blocking=False):
            raise InferenceError(
                code=InferenceErrorCode.MODEL_BUSY,
                safe_message="The model is already processing another request.",
                retryable=True,
            )
        try:
            request = self._build_request(value)
            policy = self._presentation_default.model_copy(
                update={
                    "visibility": (
                        value.settings.thinking_visibility
                        if value.settings.thinking_mode is ThinkingMode.ENABLED
                        else ThinkingVisibility.HIDDEN
                    )
                }
            )
            session = ConversationGenerationSession(
                request=request,
                inference=self._inference,
                presentation=self._presentation,
                presentation_policy=policy,
                summarization=self._summarization,
                summary_mode=value.settings.summary_mode,
                response_language=value.settings.response_language,
                release=lambda: self._release(request.request_id),
            )
            with self._active_lock:
                self._active = session
            return session
        except BaseException:
            self._generation_gate.release()
            raise

    def cancel(self, request_id: str) -> bool:
        with self._active_lock:
            session = self._active
            if session is None or session.request_id != request_id:
                return False
            session.request_cancel()
            return True

    def shutdown(self, timeout: float = 10.0) -> bool:
        with self._active_lock:
            session = self._active
        if session is None:
            return True
        session.request_cancel()
        return session.wait(timeout)

    def _build_request(self, value: ConversationGenerationInput) -> GenerationRequest:
        response_policy = ResolvedResponseLanguagePolicy(
            language=value.settings.response_language,
            source=ResponseLanguageSource.EXPLICIT,
        )
        messages = compose_conversation_generation_messages(
            messages=value.messages,
            policy=response_policy,
        )
        parameters = self._generation_defaults.model_copy(
            update={
                "max_new_tokens": value.settings.max_new_tokens,
                "thinking_mode": value.settings.thinking_mode,
            }
        )
        return GenerationRequest(
            request_id=str(uuid4()),
            model_key=self._model_key,
            messages=messages,
            parameters=parameters,
        )

    def _release(self, request_id: str) -> None:
        with self._active_lock:
            if self._active is not None and self._active.request_id == request_id:
                self._active = None
        if self._generation_gate.locked():
            self._generation_gate.release()
