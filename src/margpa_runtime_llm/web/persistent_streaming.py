"""Thread-affine SSE bridge for durable persistent conversation events."""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator, Generator, Iterator
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import cast

from fastapi import Request

from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationTurn,
    ConversationTurnId,
    ConversationTurnState,
)

from .generation_observation import GenerationObservationTracker

PERSISTENT_SSE_QUEUE_CAPACITY = 32
PERSISTENT_SSE_KEEPALIVE_SECONDS = 15.0
PERSISTENT_DISCONNECT_POLL_SECONDS = 0.1
PERSISTENT_QUEUE_PUT_POLL_SECONDS = 0.05
PERSISTENT_PRODUCER_CLEANUP_TIMEOUT_SECONDS = 10.0
PERSISTENT_SSE_KEEPALIVE = ": keepalive\n\n"

type PersistentQueueItem = tuple[str, dict[str, object]] | None


def encode_persistent_sse(event: str, data: dict[str, object]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"


def project_persistent_event(
    *,
    service: PersistentConversationService,
    conversation_id: ConversationId,
    turn_id: ConversationTurnId,
    event: ConversationEvent,
) -> tuple[str, dict[str, object]]:
    data = event.data
    if event.event is ConversationEventType.START:
        stored = service.get_conversation(conversation_id)
        turn = _turn(stored.conversation.turns, turn_id)
        request_id = data.get("request_id")
        if (
            turn.state is not ConversationTurnState.GENERATING
            or not isinstance(request_id, str)
            or turn.request_id != request_id
        ):
            raise RuntimeError("persistent start projection is not durable")
        return (
            "start",
            {
                "conversation_id": conversation_id.value,
                "turn_id": turn_id.value,
                "request_id": request_id,
                "state": data.get("state", "generating"),
                "durable_revision": stored.storage_revision,
            },
        )
    if event.event is ConversationEventType.RETRIEVAL:
        citations = []
        raw_citations = data.get("citations")
        if isinstance(raw_citations, list):
            for item in raw_citations:
                if not isinstance(item, dict):
                    continue
                citations.append(
                    {
                        "source_class": item.get("source_class"),
                        "project_relative_path": item.get("project_relative_path"),
                        "heading_breadcrumb": item.get("heading_breadcrumb"),
                        "chunk_id": item.get("chunk_id"),
                        "document_sha512": item.get("document_sha512"),
                        "retrieval_score": item.get("retrieval_score"),
                        "selected_order": item.get("selected_order"),
                        "truncated": item.get("truncated", False),
                        # P7-RW5-B/C: `None` for Project Docs - carried
                        # through the same allowlist as every other Citation
                        # field so the Persistent Live `retrieval` event
                        # shows the same Local Corpus Title/Path the REST
                        # Detail projection (`PersistentCitationResponse`)
                        # already carries.
                        "document_title": item.get("document_title"),
                        "storage_display_path": item.get("storage_display_path"),
                    }
                )
        return (
            "retrieval",
            {
                "state": data.get("state"),
                "citations": citations,
                "warnings": _safe_warnings(data.get("warnings")),
            },
        )
    if event.event is ConversationEventType.WEB_EVIDENCE:
        citations = []
        raw_citations = data.get("citations")
        if isinstance(raw_citations, list):
            for item in raw_citations:
                if not isinstance(item, dict):
                    continue
                citations.append(
                    {
                        "requested_url": item.get("requested_url"),
                        "canonical_url": item.get("canonical_url"),
                        "title": item.get("title"),
                        "provider_key": item.get("provider_key"),
                        "source_authority": item.get("source_authority"),
                        "fetched_at": item.get("fetched_at"),
                        "content_type": item.get("content_type"),
                        "transformation": item.get("transformation"),
                        "content_sha512": item.get("content_sha512"),
                        "source_class": item.get("source_class"),
                        "selected_order": item.get("selected_order"),
                    }
                )
        return (
            "web_evidence",
            {
                "citations": citations,
                "failure_reason": data.get("failure_reason"),
                "specific_failure_reason": data.get("specific_failure_reason"),
            },
        )
    if event.event is ConversationEventType.DELTA:
        return (
            "delta",
            {
                "channel": data.get("channel"),
                "text": data.get("text"),
            },
        )
    if event.event is ConversationEventType.STATUS:
        return ("status", {"state": data.get("state")})
    if event.event is ConversationEventType.WARNING:
        return (
            "warning",
            {"code": data.get("code"), "message": data.get("message")},
        )
    if event.event in {
        ConversationEventType.COMPLETED,
        ConversationEventType.CANCELLED,
        ConversationEventType.ERROR,
    }:
        stored = service.get_conversation(conversation_id)
        turn = _turn(stored.conversation.turns, turn_id)
        terminal = {
            ConversationEventType.COMPLETED: ConversationTurnState.COMPLETED,
            ConversationEventType.CANCELLED: ConversationTurnState.CANCELLED,
            ConversationEventType.ERROR: ConversationTurnState.FAILED,
        }[event.event]
        if turn.state is not terminal:
            raise RuntimeError("persistent terminal projection is not durable")
        common: dict[str, object] = {
            "conversation_id": conversation_id.value,
            "turn_id": turn_id.value,
            "request_id": turn.request_id,
            "durable_revision": stored.storage_revision,
        }
        if event.event is ConversationEventType.COMPLETED:
            assistant = next(
                (
                    message
                    for message in stored.conversation.messages
                    if message.message_id == turn.assistant_message_id
                ),
                None,
            )
            if assistant is None:
                raise RuntimeError("persistent assistant projection is unavailable")
            common.update(
                {
                    "assistant_message": {
                        "role": "assistant",
                        "content": assistant.content,
                    },
                    "finish_reason": data.get("finish_reason", "unknown"),
                    "head_turn_id": (
                        stored.conversation.head_turn_id.value
                        if stored.conversation.head_turn_id is not None
                        else None
                    ),
                    "context_usage": data.get("context_usage"),
                }
            )
        elif event.event is ConversationEventType.ERROR:
            common.update(
                {
                    "code": data.get("code", "generation_failed"),
                    "message": data.get("message", "The generation failed."),
                    "retryable": bool(data.get("retryable", False)),
                }
            )
        return (event.event.value, common)
    raise RuntimeError("unsupported persistent stream event")


class PersistentSseBridge:
    """Own a sync generation iterator on one worker from first step through close."""

    def __init__(
        self,
        *,
        events: Iterator[ConversationEvent],
        service: PersistentConversationService,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        observation_tracker: GenerationObservationTracker | None = None,
    ) -> None:
        self._events = cast(Generator[ConversationEvent, None, None], events)
        self._service = service
        self._conversation_id = conversation_id
        self._turn_id = turn_id
        self._observation_tracker = observation_tracker
        self._queue: asyncio.Queue[PersistentQueueItem] = asyncio.Queue(
            maxsize=PERSISTENT_SSE_QUEUE_CAPACITY
        )
        self._consumer_stopped = threading.Event()
        self._producer: asyncio.Task[None] | None = None
        self._ready: asyncio.Future[None] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def prepare(self) -> None:
        """Start the sole producer and surface pre-stream lifecycle failures as HTTP."""

        if self._producer is not None:
            raise RuntimeError("persistent SSE bridge is already prepared")
        self._loop = asyncio.get_running_loop()
        self._ready = self._loop.create_future()
        self._producer = asyncio.create_task(
            asyncio.to_thread(self._produce),
            name="margpa-persistent-sse",
        )
        try:
            await self._ready
        except BaseException:
            self._consumer_stopped.set()
            await self._await_producer()
            raise

    async def stream(self, request: Request) -> AsyncIterator[str]:
        if self._producer is None or self._loop is None:
            raise RuntimeError("persistent SSE bridge is not prepared")
        last_activity = self._loop.time()
        try:
            while True:
                remaining = max(
                    0.0,
                    PERSISTENT_SSE_KEEPALIVE_SECONDS - (self._loop.time() - last_activity),
                )
                try:
                    item = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=min(PERSISTENT_DISCONNECT_POLL_SECONDS, remaining),
                    )
                except TimeoutError:
                    if await request.is_disconnected():
                        break
                    if self._loop.time() - last_activity >= PERSISTENT_SSE_KEEPALIVE_SECONDS:
                        last_activity = self._loop.time()
                        yield PERSISTENT_SSE_KEEPALIVE
                    continue
                if item is None:
                    break
                last_activity = self._loop.time()
                yield encode_persistent_sse(*item)
                if await request.is_disconnected():
                    break
        finally:
            self._consumer_stopped.set()
            _drain(self._queue)
            await self._await_producer()
            _drain(self._queue)

    def _produce(self) -> None:
        ready = False
        try:
            for event in self._events:
                if self._observation_tracker is not None:
                    self._observation_tracker.observe(event)
                projected = project_persistent_event(
                    service=self._service,
                    conversation_id=self._conversation_id,
                    turn_id=self._turn_id,
                    event=event,
                )
                if not self._put(projected):
                    return
                if not ready:
                    ready = True
                    self._resolve_ready(None)
        except BaseException as exc:
            if not ready:
                self._resolve_ready(exc)
        finally:
            self._events.close()
            if not ready:
                self._resolve_ready(RuntimeError("persistent stream produced no start event"))
            self._put(None)

    def _put(self, item: PersistentQueueItem) -> bool:
        if self._consumer_stopped.is_set() or self._loop is None:
            return False
        try:
            pending = asyncio.run_coroutine_threadsafe(self._queue.put(item), self._loop)
        except RuntimeError:
            return False
        while True:
            try:
                pending.result(timeout=PERSISTENT_QUEUE_PUT_POLL_SECONDS)
                return True
            except FutureTimeoutError:
                if self._consumer_stopped.is_set():
                    pending.cancel()
                    return False
            except FutureCancelledError:
                return False

    def _resolve_ready(self, error: BaseException | None) -> None:
        if self._loop is None or self._ready is None:
            return

        def resolve() -> None:
            if self._ready is None or self._ready.done():
                return
            if error is None:
                self._ready.set_result(None)
            else:
                self._ready.set_exception(error)

        self._loop.call_soon_threadsafe(resolve)

    async def _await_producer(self) -> None:
        if self._producer is None:
            return
        try:
            await asyncio.wait_for(
                asyncio.shield(self._producer),
                timeout=PERSISTENT_PRODUCER_CLEANUP_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise RuntimeError("The persistent SSE producer did not stop safely.") from exc


def _turn(
    turns: tuple[ConversationTurn, ...],
    turn_id: ConversationTurnId,
) -> ConversationTurn:
    value = next((item for item in turns if getattr(item, "turn_id", None) == turn_id), None)
    if value is None:
        raise RuntimeError("persistent turn projection is unavailable")
    return value


def _safe_warnings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [
        {"code": item.get("code"), "message": item.get("message")}
        for item in value
        if isinstance(item, dict)
    ]


def _drain(queue: asyncio.Queue[PersistentQueueItem]) -> None:
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            return
