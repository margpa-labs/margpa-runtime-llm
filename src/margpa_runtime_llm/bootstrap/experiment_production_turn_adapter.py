"""Live `ProductionTurnPort` Adapter (Phase 9-2 R1 WU-03; R2-WU-02 convergence).

Wraps the real, already-composed Phase 9-1 `ConversationGenerationService`
(Main/Judge/Guard/Governance/RAG/Repair/Recording, already fully wired by
`bootstrap.web_application.build_phase1_web_runtime`) as ONE real Production
Turn per `run_turn()` call -- never re-implementing any of Main/Judge/Guard/
Repair dispatch itself (Handoff R1 6.1). This module is the one place that
actually touches `modules.conversation`/`bootstrap.judge_live_integration`/
`bootstrap.guardrail_governance` for the Experiment feature; the pure
projection logic (`modules.experiment.application.production_turn_runner`)
never imports any of them.

Config Isolation (Handoff R1 6.2, Option 2): this Adapter NEVER calls
`ProviderSelectionController`/`JudgeModeController`/`GuardrailModeController`
to force a different Main/Judge/Guard selection for one Run -- it only reads
back whatever the live Runtime's config actually was during this one real
Turn. A genuinely separate Experiment-scoped Runtime instance (Option 1) was
judged too large a lift to build this Round; `bootstrap.
experiment_live_configuration.BootstrapLiveConfigurationReader` (R2-WU-01)
is the bounded Frozen-vs-Live comparison `web/experiment_routes.py` performs
instead, around this Adapter's own `run_turn()` call.

R2-WU-02 (IR-P9-2-R1-02 fix) rewrites `run_turn()`'s own Evidence
projection -- R1's version unconditionally set `main_called=True` and
`final_disposition="candidate_accepted"` regardless of what actually
happened. This version instead:

- Derives `main_called` from the real `ConversationEventType`/`code`
  reached, using the confirmed pre-Main-call vs. post-Main-call `code`
  vocabulary (`_PRE_MAIN_CALL_ERROR_CODES`/`_POST_MAIN_CALL_ERROR_CODES`
  below) -- an unrecognized/ambiguous `code` (a real, confirmed blind spot:
  some Guard/Governance `*_mode_unavailable`/`*_enforce_evaluation_failed`
  codes are emitted from BOTH the pre- and post-check paths with the
  identical string, see the Exact Return's Open Findings) is conservatively
  treated as `main_called=False` -- never a confirmed `True` this Adapter
  cannot actually back up.
- Distinguishes a genuine Main Attempt from `ConversationGenerationSession`'s
  own NO_HIT short-circuit (`_identifier_no_hit_denied_event()`, which
  yields `COMPLETED` without ever calling Main) via the presence of
  `data["attempt_provenance"]` -- the same signal `persistent_conversation_
  service.py` already relies on for an equivalent purpose.
- Reads `JudgeGovernanceComposition.last_result().final_disposition`
  (request_id-correlated) for the real Turn disposition -- `"observed_
  candidate"`/`"candidate_accepted"`/`"repair_accepted"`/`"safe_fallback"`
  -- instead of always assuming `"candidate_accepted"`.
- Splits `repair_adopted` (from `last_result.repair_accepted`) from
  `repair_called` (from `last_result.repair_outcome is not None`) -- a
  Called-but-rejected Repair is never credited as Adopted.
- Reports Guard Evidence honestly as `unavailable_correlation`
  (`guard_called=None` -- R3-WU-02 upgrade from R2's own `guard_called=
  False`, the Controller's confirmed IR-P9-2-R2-04 finding: a genuinely
  UNOBSERVED Component must never be reported as a confirmed `False`)
  rather than inferring it from a before/after `invocation_id` diff -- the
  Controller's Independent Review confirmed that diff is not a genuine
  request-scoped correlation (no `request_id` field exists anywhere in
  the Guard result chain, confirmed by direct research) and must not be
  presented as confirmed Evidence.

R3-WU-02 (IR-P9-2-R2-04 MAJOR fix) additionally changes the ambiguous-
`code` branch below from a conservative `main_called=False` to the
honest `main_called=None`: R2 could not actually back up a confirmed
`False` there either (the whole reason it called that branch an Open
Finding) -- with the tri-state `ActorInvocationRecord` contract this
Round adds, "genuinely cannot tell" now has its own correct
representation instead of being forced into one of the two confirmed
states."""

from __future__ import annotations

from collections.abc import Callable

from margpa_runtime_llm.modules.conversation.public import (
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.experiment.application.production_turn_runner import (
    ProductionTurnObservation,
)
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

from .guardrail_governance import GuardrailGovernanceComposition
from .judge_live_integration import JudgeGovernanceComposition

_PRE_MAIN_CALL_ERROR_CODES = frozenset(
    {
        "guardrail_reject_input",
        "guardrail_context_source_rejected",
        "governance_stop_before_generation",
        "web_evidence_fetch_failed",
    }
)
"""`code` values confirmed (by direct source research) to be reachable
ONLY from a pre-check path that returns BEFORE `ConversationGenerationSession`
ever calls Main's own `self._inference.stream(request)` -- Main Call 0."""

_POST_MAIN_CALL_ERROR_CODES = frozenset(
    {"guardrail_reject_output", "governance_reject_output", "guardrail_stream_rejected"}
)
"""`code` values confirmed reachable only AFTER Main's own model call
already ran -- Main WAS called, even though the Turn still ended in
`ConversationEventType.ERROR`."""


class LiveProductionTurnAdapter:
    """Real `ProductionTurnPort` implementation. Constructed once by
    `bootstrap.web_application.build_phase1_web_runtime` and threaded onto
    `WebRuntime.production_turn_adapter` -- absent (`None`) unless that
    Bootstrap wiring provides it, exactly like every other Optional
    `WebRuntime` feature."""

    def __init__(
        self,
        *,
        conversation: ConversationGenerationService,
        response_language: ResponseLanguage,
        max_new_tokens: int,
        thinking_visibility: ThinkingVisibility,
        judge_governance_composition: JudgeGovernanceComposition | None = None,
        guardrail_governance_composition: GuardrailGovernanceComposition | None = None,
    ) -> None:
        self._conversation = conversation
        self._response_language = response_language
        self._max_new_tokens = max_new_tokens
        self._thinking_visibility = thinking_visibility
        self._judge_governance_composition = judge_governance_composition
        # R2-WU-02: retained on the instance only so a future Round with a
        # genuine Guard/request_id correlation can extend this Adapter --
        # `run_turn()` itself no longer reads it to infer `guard_called`/
        # `guard_outcome` (see the module docstring's IR-P9-2-R1-05 fix).
        self._guardrail_governance_composition = guardrail_governance_composition

    def run_turn(
        self, *, user_input: str, on_request_id: Callable[[str], None] | None = None
    ) -> ProductionTurnObservation:
        value = ConversationGenerationInput(
            messages=(ConversationMessage(role=ConversationRole.USER, content=user_input),),
            settings=ConversationSettings(
                response_language=self._response_language,
                max_new_tokens=self._max_new_tokens,
                thinking_mode=ThinkingMode.DISABLED,
                thinking_visibility=self._thinking_visibility,
                summary_mode=SummaryMode.OFF,
            ),
        )
        session = self._conversation.start(value)
        real_request_id = session.request_id
        if on_request_id is not None:
            on_request_id(real_request_id)

        main_called: bool | None = False
        main_outcome = "not_observed"
        final_disposition = "unknown"
        assistant_content: str | None = None
        failure_reason: str | None = None
        for event in session.events():
            if event.event is ConversationEventType.COMPLETED:
                # R2-WU-02: `COMPLETED` alone does not prove Main ran --
                # `_identifier_no_hit_denied_event()` also yields
                # `COMPLETED` without ever calling Main. A real Main
                # Attempt always carries `attempt_provenance` in its
                # event data (the same signal `persistent_conversation_
                # service.py` already relies on for an equivalent check).
                main_called = "attempt_provenance" in event.data
                main_outcome = "completed" if main_called else "no_hit_denied"
                final_disposition = "candidate_accepted" if main_called else "no_hit_denied"
                message = event.data.get("assistant_message")
                if isinstance(message, dict):
                    content = message.get("content")
                    assistant_content = content if isinstance(content, str) else None
            elif event.event is ConversationEventType.CANCELLED:
                # A Cancel can only land once a real Attempt is in flight
                # (there is nothing to cancel before Main is ever called).
                main_called = True
                main_outcome = "cancelled"
                final_disposition = "cancelled"
            elif event.event is ConversationEventType.ERROR:
                message = event.data.get("message")
                code = message if isinstance(message, str) else None
                if code in _POST_MAIN_CALL_ERROR_CODES:
                    main_called = True
                elif code in _PRE_MAIN_CALL_ERROR_CODES:
                    main_called = False
                else:
                    # R3-WU-02 (IR-P9-2-R2-04 fix): an unrecognized or
                    # genuinely ambiguous `code` (e.g. a `*_mode_
                    # unavailable`/`*_enforce_evaluation_failed` string
                    # reachable from BOTH the pre- and post-check paths,
                    # confirmed by direct research) is never resolved by
                    # guessing -- and, with the tri-state Evidence
                    # contract this Round adds, it is no longer forced
                    # into R2's conservative `main_called=False` either
                    # (a confirmed negative this Adapter could not
                    # actually back up). `None` is the honest value: this
                    # Round's Evidence source genuinely cannot tell.
                    main_called = None
                main_outcome = "failed"
                final_disposition = "failed"
                failure_reason = code or "production_turn_error"

        judge_called = False
        judge_outcome = "off"
        repair_called = False
        repair_outcome = "off"
        repair_adopted: bool | None = None
        if self._judge_governance_composition is not None:
            last_result = self._judge_governance_composition.last_result()
            if last_result is not None and last_result.request_id == real_request_id:
                judge_called = True
                judge_outcome = last_result.judge_outcome or last_result.execution_state
                if last_result.repair_outcome is not None:
                    repair_called = True
                    repair_outcome = last_result.repair_outcome
                    repair_adopted = bool(last_result.repair_accepted)
                # `final_disposition` and `presentation_outcome` are kept
                # in sync by `judge_live_integration.py` (both set
                # together, from the same value) -- read defensively
                # through either, rather than assuming both are always
                # populated identically forever.
                real_disposition = last_result.final_disposition or last_result.presentation_outcome
                if real_disposition is not None:
                    final_disposition = real_disposition

        return ProductionTurnObservation(
            request_id=real_request_id,
            main_called=main_called,
            main_outcome=main_outcome,
            judge_called=judge_called,
            judge_outcome=judge_outcome,
            # R2-WU-02 (IR-P9-2-R1-05 fix): no genuine request-scoped
            # correlation exists for Guard anywhere in this codebase
            # (confirmed by direct research: `GuardrailResult` carries no
            # `request_id` field, and `RequestCorrelationRegistry` does
            # not track Guard invocations either) -- reported honestly as
            # `unavailable_correlation`, never inferred from a before/
            # after `invocation_id` diff the way R1 did.
            guard_called=None,
            guard_outcome="unavailable_correlation",
            repair_called=repair_called,
            repair_outcome=repair_outcome,
            repair_adopted=repair_adopted,
            final_disposition=final_disposition,
            assistant_content=assistant_content,
            failure_reason=failure_reason,
        )
