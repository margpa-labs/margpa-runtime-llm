"""P8-A: `project_persistent_event()` must handle
`ConversationEventType.WEB_EVIDENCE` without raising.

Before this Task, `project_persistent_event()` raised
`RuntimeError("unsupported persistent stream event")` for any Event Type it
did not explicitly branch on - adding a new Type to `ConversationEventType`
without also adding a branch here would have crashed every Persistent (v2)
SSE stream for a Turn that requested Manual Web Evidence. This is a direct,
minimal regression test for that specific failure mode - it does not
exercise `service`/`conversation_id`/`turn_id` at all (the WEB_EVIDENCE
branch, like RETRIEVAL/DELTA/STATUS/WARNING, never calls back into the
Service), so a placeholder `service` is safe to pass.
"""

from __future__ import annotations

from typing import cast

from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationId, ConversationTurnId
from margpa_runtime_llm.web.persistent_streaming import project_persistent_event

_SERVICE = cast(PersistentConversationService, object())
_CONVERSATION_ID = ConversationId(value="conv-1")
_TURN_ID = ConversationTurnId(value="turn-1")


def test_web_evidence_event_projects_without_raising() -> None:
    event = ConversationEvent(
        event=ConversationEventType.WEB_EVIDENCE,
        data={
            "request_id": "req-1",
            "activation": "manual",
            "citations": [
                {
                    "citation_id": "web-citation-1",
                    "canonical_url": "https://example.org/article",
                    "title": "https://example.org/article",
                    "provider_key": "direct_url",
                    "source_authority": "general",
                    "fetched_at": "2026-08-30T00:00:00Z",
                    "content_type": "text/html",
                    "content_sha512": "a" * 128,
                    "source_class": "public_web",
                    "selected_order": 1,
                }
            ],
            "failure_reason": None,
            "network_calls_made": 1,
        },
    )

    name, projected = project_persistent_event(
        service=_SERVICE,
        conversation_id=_CONVERSATION_ID,
        turn_id=_TURN_ID,
        event=event,
    )

    assert name == "web_evidence"
    assert projected["failure_reason"] is None
    citations = projected["citations"]
    assert isinstance(citations, list)
    assert citations[0]["canonical_url"] == "https://example.org/article"
    assert citations[0]["source_class"] == "public_web"
    assert citations[0]["content_sha512"] == "a" * 128


def test_web_evidence_event_with_failure_and_zero_citations_projects_cleanly() -> None:
    event = ConversationEvent(
        event=ConversationEventType.WEB_EVIDENCE,
        data={
            "request_id": "req-1",
            "activation": "manual",
            "citations": [],
            "failure_reason": "url_rejected",
            "network_calls_made": 0,
        },
    )

    name, projected = project_persistent_event(
        service=_SERVICE,
        conversation_id=_CONVERSATION_ID,
        turn_id=_TURN_ID,
        event=event,
    )

    assert name == "web_evidence"
    assert projected["citations"] == []
    assert projected["failure_reason"] == "url_rejected"
