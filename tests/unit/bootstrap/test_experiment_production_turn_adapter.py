"""Phase 9-2 R2-WU-02: `LiveProductionTurnAdapter.run_turn()` Evidence
projection -- the IR-P9-2-R1-02 BLOCKER fix.

A duck-typed `_FakeSession`/`_FakeConversation` stands in for the real
`ConversationGenerationService`/`ConversationGenerationSession` -- this
module's own `run_turn()` orchestration logic (event-code dispatch, Judge
correlation, Guard honesty) is what R2-WU-02 actually changed; Phase 9-1's
own pre/post-check emission behavior is unchanged and already covered by
its own existing test suite. Testing the Adapter's interpretation of an
already-emitted event stream, in isolation, is the correct boundary here."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from margpa_runtime_llm.bootstrap.experiment_production_turn_adapter import (
    LiveProductionTurnAdapter,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    LiveJudgeResult,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility


@dataclass
class _FakeSession:
    request_id: str
    _events: list[ConversationEvent]

    def events(self) -> Iterator[ConversationEvent]:
        yield from self._events


@dataclass
class _FakeConversation:
    """Duck-types the one method `run_turn()` calls on `conversation` --
    never a real `ConversationGenerationService` (see module docstring)."""

    session: _FakeSession
    cancel_calls: list[str] = field(default_factory=list)

    def start(self, value: Any) -> _FakeSession:
        return self.session

    def cancel(self, request_id: str) -> None:
        self.cancel_calls.append(request_id)


def _build_adapter(
    *,
    session: _FakeSession,
    judge_governance_composition: JudgeGovernanceComposition | None = None,
) -> LiveProductionTurnAdapter:
    return LiveProductionTurnAdapter(
        conversation=_FakeConversation(session=session),  # type: ignore[arg-type]
        response_language=ResponseLanguage.EN,
        max_new_tokens=256,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        judge_governance_composition=judge_governance_composition,
    )


def _judge_result(**overrides: object) -> LiveJudgeResult:
    base: dict[str, object] = {
        "request_id": "real-req-1",
        "judge_role": JudgeIndependenceClass.MAIN_SELF,
        "recommendation": "accept",
        "confidence": 1.0,
        "execution_state": "completed",
        "failure_reason": None,
    }
    base.update(overrides)
    return LiveJudgeResult(**base)  # type: ignore[arg-type]


def _completed_event_with_attempt(content: str = "Paris.") -> ConversationEvent:
    return ConversationEvent(
        event=ConversationEventType.COMPLETED,
        data={
            "assistant_message": {"content": content},
            "attempt_provenance": {"model_key": "main.qwen3-4b-q4-k-m"},
        },
    )


def test_guard_pre_block_reports_main_call_zero() -> None:
    """R2-WU-02 Hard Assert #1 (IR-P9-2-R1-02): a Guard Input pre-block
    ends the Turn in `ERROR` with `code="guardrail_reject_input"` -- BEFORE
    Main's own model call. The Adapter must report `main_called=False`,
    never the R1 hard-coded `True`."""

    session = _FakeSession(
        request_id="real-req-1",
        _events=[
            ConversationEvent(
                event=ConversationEventType.ERROR,
                data={"message": "guardrail_reject_input"},
            )
        ],
    )
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.main_called is False
    assert observation.main_outcome == "failed"
    assert observation.failure_reason == "guardrail_reject_input"


def test_a_post_main_call_rejection_reports_main_called_true() -> None:
    """A rejection code confirmed reachable only AFTER Main's own call
    (`guardrail_reject_output`) must not be conflated with a pre-block."""

    session = _FakeSession(
        request_id="real-req-2",
        _events=[
            ConversationEvent(
                event=ConversationEventType.ERROR,
                data={"message": "guardrail_reject_output"},
            )
        ],
    )
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.main_called is True


def test_an_ambiguous_error_code_is_conservatively_reported_as_main_call_unknown() -> None:
    """R2-WU-02 (documented Open Finding) / R3-WU-02 (IR-P9-2-R2-04 fix):
    `guardrail_mode_unavailable` is confirmed reachable from BOTH the pre-
    and post-check paths with the identical string -- the Adapter must
    never guess `True`, and (R3 upgrade) must not guess a confirmed
    `False` either, since it genuinely cannot tell; the honest tri-state
    value is `None`."""

    session = _FakeSession(
        request_id="real-req-3",
        _events=[
            ConversationEvent(
                event=ConversationEventType.ERROR,
                data={"message": "guardrail_mode_unavailable"},
            )
        ],
    )
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.main_called is None


def test_no_hit_short_circuit_completed_without_attempt_provenance_is_not_a_main_call() -> None:
    """R2-WU-02: `ConversationGenerationSession._identifier_no_hit_denied_
    event()` yields `COMPLETED` without ever calling Main -- distinguished
    from a genuine Main Attempt by the absence of `attempt_provenance`."""

    session = _FakeSession(
        request_id="real-req-4",
        _events=[
            ConversationEvent(
                event=ConversationEventType.COMPLETED,
                data={"assistant_message": {"content": "insufficient evidence"}},
            )
        ],
    )
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.main_called is False
    assert observation.main_outcome == "no_hit_denied"
    assert observation.final_disposition == "no_hit_denied"


def test_a_genuine_completion_with_attempt_provenance_reports_main_called_true() -> None:
    session = _FakeSession(request_id="real-req-5", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.main_called is True
    assert observation.main_outcome == "completed"
    assert observation.assistant_content == "Paris."


def test_repair_called_but_not_adopted_reports_repair_adopted_false() -> None:
    """R2-WU-02 Hard Assert #2 (IR-P9-2-R1-02): a Called-but-rejected
    Repair is never credited as Adopted."""

    composition = JudgeGovernanceComposition()
    composition._last_result = _judge_result(
        repair_outcome="rejected", repair_accepted=False, presentation_outcome="safe_fallback"
    )
    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(
        session=session, judge_governance_composition=composition
    ).run_turn(user_input="x")
    assert observation.repair_called is True
    assert observation.repair_adopted is False


def test_repair_called_and_adopted_reports_repair_adopted_true() -> None:
    """R2-WU-02 Hard Assert #3: a Called AND Adopted Repair reports True."""

    composition = JudgeGovernanceComposition()
    composition._last_result = _judge_result(
        repair_outcome="accepted", repair_accepted=True, presentation_outcome="repair_accepted"
    )
    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(
        session=session, judge_governance_composition=composition
    ).run_turn(user_input="x")
    assert observation.repair_called is True
    assert observation.repair_adopted is True
    assert observation.final_disposition == "repair_accepted"


def test_judge_safe_fallback_is_never_converted_to_candidate_accepted() -> None:
    """R2-WU-02 Hard Assert #4: a Judge `safe_fallback` disposition
    (ENFORCE, candidate withheld, canned failure substituted) must never
    be reported as `candidate_accepted` the way R1's version always did."""

    composition = JudgeGovernanceComposition()
    composition._last_result = _judge_result(
        repair_outcome=None, repair_accepted=None, presentation_outcome="safe_fallback"
    )
    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(
        session=session, judge_governance_composition=composition
    ).run_turn(user_input="x")
    assert observation.final_disposition == "safe_fallback"
    assert observation.repair_called is False
    assert observation.repair_adopted is None


def test_guard_evidence_is_always_reported_as_unavailable_correlation() -> None:
    """R2-WU-02 (IR-P9-2-R1-05 fix) / R3-WU-02 (IR-P9-2-R2-04 fix): no
    genuine request-scoped correlation exists for Guard -- the Adapter
    never infers `called`/`outcome` from a before/after `invocation_id`
    diff the way R1 did; it is always reported honestly, regardless of
    whether a Guardrail Governance Composition happens to be wired. R3
    upgrades `guard_called` itself from R2's confirmed `False` to the
    honest tri-state `None`: a genuinely UNOBSERVED Component is never a
    confirmed negative."""

    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(session=session).run_turn(user_input="x")
    assert observation.guard_called is None
    assert observation.guard_outcome == "unavailable_correlation"


def test_a_judge_result_for_a_different_request_id_is_never_attributed_to_this_turn() -> None:
    """A stale `last_result()` from an unrelated, concurrent ordinary Chat
    Turn must never be mistaken for this Experiment Run's own outcome."""

    composition = JudgeGovernanceComposition()
    composition._last_result = _judge_result(
        request_id="some-other-concurrent-chat-request",
        repair_outcome="accepted",
        repair_accepted=True,
    )
    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    observation = _build_adapter(
        session=session, judge_governance_composition=composition
    ).run_turn(user_input="x")
    assert observation.judge_called is False
    assert observation.repair_called is False
    assert observation.repair_adopted is None


def test_on_request_id_is_forwarded_before_the_turn_finishes() -> None:
    observed: list[str] = []
    session = _FakeSession(request_id="real-req-1", _events=[_completed_event_with_attempt()])
    _build_adapter(session=session).run_turn(
        user_input="x", on_request_id=observed.append
    )
    assert observed == ["real-req-1"]
