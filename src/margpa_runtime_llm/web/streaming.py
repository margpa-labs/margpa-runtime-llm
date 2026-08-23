"""Bridge a blocking Model Port iterator to an asynchronous SSE response."""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator, Generator
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import cast

from fastapi import Request

from margpa_runtime_llm.modules.conversation.public import (
    ConversationEvent,
    ConversationGenerationSession,
)

from .generation_observation import GenerationObservationTracker

type QueueItem = ConversationEvent | None

SSE_QUEUE_CAPACITY = 32
SSE_KEEPALIVE_INTERVAL_SECONDS = 15.0
SSE_KEEPALIVE_COMMENT = ": keepalive\n\n"
DISCONNECT_POLL_SECONDS = 0.1
QUEUE_PUT_POLL_SECONDS = 0.05
PRODUCER_CLEANUP_TIMEOUT_SECONDS = 10.0


def encode_sse(event: ConversationEvent) -> str:
    payload = json.dumps(event.data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event.event.value}\ndata: {payload}\n\n"


async def stream_session_as_sse(
    request: Request,
    session: ConversationGenerationSession,
    observation_tracker: GenerationObservationTracker | None = None,
) -> AsyncIterator[str]:
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[QueueItem] = asyncio.Queue(maxsize=SSE_QUEUE_CAPACITY)
    consumer_stopped = threading.Event()

    def put_unless_stopped(item: QueueItem) -> bool:
        if consumer_stopped.is_set():
            return False
        try:
            pending = asyncio.run_coroutine_threadsafe(queue.put(item), loop)
        except RuntimeError:
            return False
        while True:
            try:
                pending.result(timeout=QUEUE_PUT_POLL_SECONDS)
                return True
            except FutureTimeoutError:
                if consumer_stopped.is_set():
                    pending.cancel()
                    return False
            except FutureCancelledError:
                return False

    def produce() -> None:
        events = cast(Generator[ConversationEvent, None, None], session.events())
        try:
            for event in events:
                if observation_tracker is not None:
                    observation_tracker.observe(event)
                if not put_unless_stopped(event):
                    break
        finally:
            events.close()
            put_unless_stopped(None)

    producer = asyncio.create_task(
        asyncio.to_thread(produce),
        name=f"margpa-sse-producer-{session.request_id}",
    )
    producer_finished = False
    last_wire_activity = loop.time()
    try:
        while True:
            keepalive_remaining = max(
                0.0,
                SSE_KEEPALIVE_INTERVAL_SECONDS - (loop.time() - last_wire_activity),
            )
            try:
                item = await asyncio.wait_for(
                    queue.get(),
                    timeout=min(DISCONNECT_POLL_SECONDS, keepalive_remaining),
                )
            except TimeoutError:
                if await request.is_disconnected():
                    break
                if loop.time() - last_wire_activity >= SSE_KEEPALIVE_INTERVAL_SECONDS:
                    last_wire_activity = loop.time()
                    yield SSE_KEEPALIVE_COMMENT
                continue
            if item is None:
                producer_finished = True
                break
            last_wire_activity = loop.time()
            yield encode_sse(item)
            if await request.is_disconnected():
                break
    finally:
        consumer_stopped.set()
        if not producer_finished:
            session.request_cancel()
        _drain_queue(queue)
        try:
            await asyncio.wait_for(
                asyncio.shield(producer),
                timeout=PRODUCER_CLEANUP_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise RuntimeError("The SSE producer did not stop during cleanup.") from exc


def _drain_queue(queue: asyncio.Queue[QueueItem]) -> None:
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            return
