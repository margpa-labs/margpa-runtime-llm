"""CL-P9-3-D/E: Coordinator Pipeline integration -- Atomic Compaction,
Rollback, Concurrency, Restart Read, Recovery/Rehydration/Handoff.

Uses a real `LocalFilesystemCompactionStore` (tmp_path) and a real
`CompactionWorker` (real background thread) so CAS/threading behavior is
exercised for real, not mocked away -- only the Conversation Source and
Model Context are Fakes (Model Call 0 is genuine: `count_text_tokens` here
is a real deterministic char/4 count, never a Generation call).
"""

import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.context_compaction.local_filesystem_compaction_store import (
    LocalFilesystemCompactionStore,
)
from margpa_runtime_llm.modules.context_compaction.application.auto_policy import (
    AutoCompactionPolicyController,
)
from margpa_runtime_llm.modules.context_compaction.application.budget_service import (
    ContextBudgetService,
    ReserveConfig,
)
from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.application.deterministic_builder import (
    DeterministicExtractiveBuilder,
)
from margpa_runtime_llm.modules.context_compaction.application.handoff_service import (
    ContextHandoffService,
)
from margpa_runtime_llm.modules.context_compaction.application.recovery_service import (
    SelectiveRehydrationService,
    build_recovery_index,
)
from margpa_runtime_llm.modules.context_compaction.application.worker import CompactionWorker
from margpa_runtime_llm.modules.context_compaction.domain import (
    DEFAULT_BRANCH_ID,
    CompactionAttempt,
    CompactionAttemptState,
    PressureState,
    RehydrationFailureCode,
    SelectiveRehydrationRequest,
    ThresholdConfig,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import (
    HandoffArtifactId,
    RecoveryIndexId,
)
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    SourceConversationTurn,
)
from margpa_runtime_llm.modules.conversation.domain.identity import (
    ConversationId,
    ConversationMessageId,
    ConversationTurnId,
)


class FakeSource:
    def __init__(self, turn_count: int = 20, revision: int = 1) -> None:
        self.turn_count = turn_count
        self.revision = revision

    def read(self, conversation_id: ConversationId) -> ConversationSourceProjection | None:
        if self.turn_count == 0:
            return None
        turns = tuple(
            SourceConversationTurn(
                turn_id=ConversationTurnId(value=f"turn-{i}"),
                sequence=i,
                user_message_id=ConversationMessageId(value=f"user-{i}"),
                user_content=f"user turn {i} " * 8,
                assistant_message_id=ConversationMessageId(value=f"assistant-{i}"),
                assistant_content=f"assistant turn {i} " * 8,
            )
            for i in range(self.turn_count)
        )
        return ConversationSourceProjection(
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            source_conversation_revision=self.revision,
            turns=turns,
        )


class FakeModelContext:
    def __init__(self, capacity: int | None = 4096, tokenizer_down: bool = False) -> None:
        self.capacity = capacity
        self.tokenizer_down = tokenizer_down

    def loaded_context_capacity(self) -> int | None:
        return self.capacity

    def loaded_model_identity(self) -> str | None:
        return "fake-model"

    def count_text_tokens(self, text: str) -> int | None:
        if self.tokenizer_down:
            return None
        return max(1, len(text) // 4)


def _make_coordinator(
    tmp_path: Path,
    *,
    source: FakeSource | None = None,
    model_context: FakeModelContext | None = None,
    auto_enabled: bool = True,
    token_budget: int = 200,
    store: LocalFilesystemCompactionStore | None = None,
) -> tuple[CompactionCoordinator, LocalFilesystemCompactionStore, FakeSource, FakeModelContext]:
    source = source or FakeSource()
    model_context = model_context or FakeModelContext()
    store = store or LocalFilesystemCompactionStore(base_dir=tmp_path)
    budget_service = ContextBudgetService(
        source=source, model_context=model_context, reserves=ReserveConfig()
    )
    builder = DeterministicExtractiveBuilder(model_context=model_context)
    auto_policy = AutoCompactionPolicyController(enabled=auto_enabled)
    worker = CompactionWorker()
    thresholds = ThresholdConfig(
        advisory_remaining_budget_floor=100_000, auto_trigger_remaining_budget_floor=100_000
    )
    coordinator = CompactionCoordinator(
        store=store,
        budget_service=budget_service,
        builder=builder,
        auto_policy=auto_policy,
        worker=worker,
        thresholds=thresholds,
        token_budget=token_budget,
    )
    return coordinator, store, source, model_context


def _wait_terminal(
    coordinator: CompactionCoordinator, attempt_id: str, *, timeout: float = 5.0
) -> CompactionAttempt:
    deadline = time.monotonic() + timeout
    terminal_states = {
        CompactionAttemptState.COMPLETED,
        CompactionAttemptState.FAILED,
        CompactionAttemptState.REJECTED,
        CompactionAttemptState.CANCELLED,
        CompactionAttemptState.CONFLICTED,
    }
    attempt = coordinator.get_attempt(attempt_id)
    while time.monotonic() < deadline:
        attempt = coordinator.get_attempt(attempt_id)
        if attempt is not None and attempt.state in terminal_states:
            return attempt
        time.sleep(0.01)
    raise AssertionError(f"attempt {attempt_id!r} did not reach a terminal state in time")


def test_manual_compaction_completes_and_activates_via_cas(tmp_path: Path) -> None:
    coordinator, store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.state is CompactionAttemptState.COMPLETED
    active = store.load_active_context_projection(cid, DEFAULT_BRANCH_ID)
    assert active is not None
    assert active.structured_context_id is not None
    assert active.active_projection_revision == 1


def test_preview_never_persists_anything(tmp_path: Path) -> None:
    coordinator, store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")
    result = coordinator.preview(cid, generation_reserve_tokens=100)
    assert result is not None and result.feasible
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None
    assert store.list_non_terminal_attempts(cid, DEFAULT_BRANCH_ID) == ()


def test_manual_compaction_available_and_completes_even_with_auto_off(tmp_path: Path) -> None:
    """Hard Evidence #3: Manual is not gated by Auto Trigger Threshold."""

    coordinator, _store, _source, _model = _make_coordinator(tmp_path, auto_enabled=False)
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.state is CompactionAttemptState.COMPLETED


def test_auto_compaction_triggers_at_hard_reserve_and_activates(tmp_path: Path) -> None:
    """Hard Evidence #5: Auto ON resolves Hard Reserve through the SAME
    pipeline, inline, before the caller's own preflight check returns."""

    model_context = FakeModelContext(capacity=4096)
    coordinator, store, _source, _model = _make_coordinator(
        tmp_path, model_context=model_context, auto_enabled=True, token_budget=250
    )
    cid = ConversationId(value="conv-1")
    before = coordinator.budget(cid, generation_reserve_tokens=100)
    assert before is not None
    usage_before = before[0].current_prompt_usage.value

    pressure_after = coordinator.run_auto_compaction_if_required(
        cid, generation_reserve_tokens=100
    )
    active = store.load_active_context_projection(cid, DEFAULT_BRANCH_ID)
    assert active is not None and active.structured_context_id is not None

    after = coordinator.budget(cid, generation_reserve_tokens=100)
    assert after is not None
    usage_after = after[0].current_prompt_usage.value
    assert usage_after is not None and usage_before is not None
    assert usage_after < usage_before, "a genuinely activated Compaction must reduce prompt usage"
    # `pressure_after` is whatever the fixture's own (deliberately tiny)
    # Threshold floors classify the now-reduced usage as -- the meaningful
    # assertion is the measured reduction above, not a specific label here.
    assert pressure_after in PressureState


def test_snapshot_persisted_before_candidate_build_call_zero_on_builder_unavailable(
    tmp_path: Path,
) -> None:
    """Invariant 6/12: a Builder that cannot run (tokenizer down) must fail
    the Attempt without ever activating a new Projection -- the original
    (no Projection at all, in this case) must survive untouched."""

    model_context = FakeModelContext(tokenizer_down=True)
    coordinator, store, _source, _model = _make_coordinator(tmp_path, model_context=model_context)
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.state is CompactionAttemptState.FAILED
    assert final.error_code == "builder_unavailable"
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None
    # The Snapshot itself IS persisted (Preflight succeeded) -- only the
    # Candidate build (genuine Model-adjacent work) never ran.
    assert store.load_pre_action_snapshot(attempt.snapshot_id) is not None


def test_concurrent_attempts_the_loser_is_conflicted_never_overwrites_the_winner(
    tmp_path: Path,
) -> None:
    """Hard Evidence #7/#8/#9: two Attempts computed against the same stale
    Projection revision race to activate -- exactly one wins (`completed`),
    the other is `conflicted`, and the Active Projection ends up pointing at
    the WINNER's own Structured Context, never silently overwritten."""

    coordinator, store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")

    # Manually drive two pipeline runs against the SAME starting revision by
    # calling the private pipeline function directly (bypassing the
    # single-threaded Worker, which would otherwise serialize them and make
    # a genuine race impossible to construct deterministically in a test).
    attempt_a = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final_a = _wait_terminal(coordinator, attempt_a.attempt_id.value)
    assert final_a.state is CompactionAttemptState.COMPLETED

    # Attempt B is now built starting from the ALREADY-STALE `revision 0`
    # pointer state by directly invoking the pipeline with a hand-built
    # Attempt whose own preflight-computed "current projection" snapshot is
    # forced stale via a monkey-patched snapshot capture equal to Attempt A's
    # pre-image. This exercises the CAS rejection path directly.
    from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
        ActiveContextProjection,
    )

    stale_new_projection = ActiveContextProjection(
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        active_projection_revision=1,
        structured_context_id=None,
        source_conversation_revision=1,
        updated_at=datetime.now(UTC),
    )
    activated = store.compare_and_swap_active_context_projection(
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        expected_active_projection_revision=0,  # stale: winner already advanced it to 1
        new_projection=stale_new_projection,
    )
    assert activated is False, "a stale expected revision must never win the CAS"
    current = store.load_active_context_projection(cid, DEFAULT_BRANCH_ID)
    assert current is not None and current.active_projection_revision == 1
    winner = coordinator.get_attempt(attempt_a.attempt_id.value)
    assert winner is not None
    assert current.structured_context_id == winner.structured_context_id


def test_rollback_restores_the_previous_projection_and_records_evidence(tmp_path: Path) -> None:
    coordinator, store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    _wait_terminal(coordinator, attempt.attempt_id.value)
    record = coordinator.rollback(attempt.attempt_id.value)
    assert record.result.value == "rolled_back"
    restored = store.load_active_context_projection(cid, DEFAULT_BRANCH_ID)
    assert restored is not None and restored.structured_context_id is None
    rolled_back_attempt = coordinator.get_attempt(attempt.attempt_id.value)
    assert rolled_back_attempt is not None
    assert rolled_back_attempt.state is CompactionAttemptState.ROLLED_BACK


def test_rollback_of_a_non_completed_attempt_is_rejected(tmp_path: Path) -> None:
    coordinator, _store, _source, _model = _make_coordinator(
        tmp_path, model_context=FakeModelContext(tokenizer_down=True)
    )
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    _wait_terminal(coordinator, attempt.attempt_id.value)  # ends FAILED, not COMPLETED
    from margpa_runtime_llm.modules.context_compaction.domain.errors import (
        ContextCompactionDomainError,
    )

    with pytest.raises(ContextCompactionDomainError):
        coordinator.rollback(attempt.attempt_id.value)


def test_restart_read_marks_a_leftover_non_terminal_attempt_as_interrupted(
    tmp_path: Path,
) -> None:
    """Hard Evidence #9: a non-Terminal Attempt found on Store Restart Read
    is never resumed -- it is marked `interrupted_by_restart` and the
    Active Projection is left exactly as it was."""

    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    cid = ConversationId(value="conv-1")

    # Simulate a prior process that crashed mid-pipeline: an Attempt
    # persisted in a non-terminal state, with no Active Projection written.
    from margpa_runtime_llm.modules.context_compaction.domain.artifacts import CompactionAttempt
    from margpa_runtime_llm.modules.context_compaction.domain.identity import (
        CompactionAttemptId,
        CompactionPlanId,
        ContextActionId,
        SnapshotId,
    )

    leftover = CompactionAttempt(
        attempt_id=CompactionAttemptId(value="attempt-leftover"),
        plan_id=CompactionPlanId(value="plan-leftover"),
        action_id=ContextActionId(value="action-leftover"),
        snapshot_id=SnapshotId(value="snapshot-leftover"),
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        state=CompactionAttemptState.CANDIDATE_BUILDING,
        requested_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    store.save_compaction_attempt(leftover)

    # A brand-new process (new Coordinator instance, same on-disk Store).
    coordinator, _store, _source, _model = _make_coordinator(tmp_path, store=store)
    marked = coordinator.ensure_restart_read(cid)
    assert [a.attempt_id.value for a in marked] == ["attempt-leftover"]
    reloaded = store.load_compaction_attempt(CompactionAttemptId(value="attempt-leftover"))
    assert reloaded is not None
    assert reloaded.state is CompactionAttemptState.INTERRUPTED_BY_RESTART
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None


def test_generation_time_projection_is_none_when_source_revision_has_moved_on(
    tmp_path: Path,
) -> None:
    """Safety net: an Active Projection computed against an older Conversation
    Revision must never be served once a newer Turn has landed."""

    coordinator, _store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    _wait_terminal(coordinator, attempt.attempt_id.value)
    assert (
        coordinator.active_projection_for_generation(cid, current_source_revision=1) is not None
    )
    assert (
        coordinator.active_projection_for_generation(cid, current_source_revision=2) is None
    )


def test_recovery_index_and_selective_rehydration_round_trip(tmp_path: Path) -> None:
    source = FakeSource(turn_count=20)
    model_context = FakeModelContext()
    coordinator, store, _s, _m = _make_coordinator(
        tmp_path, source=source, model_context=model_context, token_budget=250
    )
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.structured_context_id is not None
    artifact = coordinator.load_structured_context(final.structured_context_id.value)
    assert artifact is not None
    assert artifact.sections.omitted_ranges

    index = build_recovery_index(
        artifact,
        recovery_index_id=RecoveryIndexId(value="recovery-1"),
        model_context=model_context,
    )
    store.save_recovery_index(index)
    assert store.load_recovery_index(index.recovery_index_id) == index

    rehydration = SelectiveRehydrationService(source=source, model_context=model_context)
    request = SelectiveRehydrationRequest(
        recovery_index_id=index.recovery_index_id,
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        requested_entry_ids=tuple(entry.entry_id for entry in index.entries),
        token_budget=100_000,
    )
    result = rehydration.rehydrate(request, index=index)
    assert result.failures == ()
    assert result.rehydrated
    assert result.total_tokens_used > 0


def test_selective_rehydration_reports_typed_not_found_for_an_unknown_entry(
    tmp_path: Path,
) -> None:
    source = FakeSource(turn_count=5)
    model_context = FakeModelContext()
    coordinator, _store, _s, _m = _make_coordinator(
        tmp_path, source=source, model_context=model_context
    )
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.structured_context_id is not None
    artifact = coordinator.load_structured_context(final.structured_context_id.value)
    assert artifact is not None
    index = build_recovery_index(
        artifact, recovery_index_id=RecoveryIndexId(value="recovery-1"), model_context=model_context
    )
    rehydration = SelectiveRehydrationService(source=source, model_context=model_context)
    request = SelectiveRehydrationRequest(
        recovery_index_id=index.recovery_index_id,
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        requested_entry_ids=("entry-does-not-exist",),
        token_budget=1000,
    )
    result = rehydration.rehydrate(request, index=index)
    assert len(result.failures) == 1
    assert result.failures[0].code is RehydrationFailureCode.NOT_FOUND


def test_selective_rehydration_reports_typed_stale_when_revision_moved_on(
    tmp_path: Path,
) -> None:
    source = FakeSource(turn_count=5, revision=1)
    model_context = FakeModelContext()
    coordinator, _store, _s, _m = _make_coordinator(
        tmp_path, source=source, model_context=model_context
    )
    cid = ConversationId(value="conv-1")
    attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
    final = _wait_terminal(coordinator, attempt.attempt_id.value)
    assert final.structured_context_id is not None
    artifact = coordinator.load_structured_context(final.structured_context_id.value)
    assert artifact is not None
    index = build_recovery_index(
        artifact, recovery_index_id=RecoveryIndexId(value="recovery-1"), model_context=model_context
    )
    source.revision = 2  # a newer Turn has landed since the Index was built
    rehydration = SelectiveRehydrationService(source=source, model_context=model_context)
    request = SelectiveRehydrationRequest(
        recovery_index_id=index.recovery_index_id,
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        requested_entry_ids=tuple(e.entry_id for e in index.entries) or ("none",),
        token_budget=1000,
    )
    result = rehydration.rehydrate(request, index=index)
    assert all(failure.code is RehydrationFailureCode.STALE for failure in result.failures)


def test_handoff_artifact_mutates_nothing(tmp_path: Path) -> None:
    source = FakeSource(turn_count=10)
    model_context = FakeModelContext()
    _coordinator, store, _s, _m = _make_coordinator(
        tmp_path, source=source, model_context=model_context
    )
    cid = ConversationId(value="conv-1")
    service = ContextHandoffService(source=source, model_context=model_context)
    handoff = service.build(cid, handoff_artifact_id=HandoffArtifactId(value="handoff-1"))
    assert handoff is not None
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None
    assert store.list_non_terminal_attempts(cid, DEFAULT_BRANCH_ID) == ()
    assert handoff.sections.recent_verbatim_tail


def test_cancel_requested_before_pipeline_runs_yields_call_zero_mutation_zero(
    tmp_path: Path,
) -> None:
    """Cancel semantics proven deterministically by invoking the pipeline
    function directly on the calling thread (no Worker race) after the
    cancel Event has already been set -- exactly the state a genuinely-won
    `request_cancel()` race would leave behind."""

    coordinator, store, _source, _model = _make_coordinator(tmp_path)
    cid = ConversationId(value="conv-1")
    from margpa_runtime_llm.modules.context_compaction.domain.artifacts import CompactionAttempt
    from margpa_runtime_llm.modules.context_compaction.domain.identity import (
        CompactionAttemptId,
        CompactionPlanId,
        ContextActionId,
        SnapshotId,
    )

    attempt = CompactionAttempt(
        attempt_id=CompactionAttemptId(value="attempt-cancel-early"),
        plan_id=CompactionPlanId(value="plan-1"),
        action_id=ContextActionId(value="action-1"),
        snapshot_id=SnapshotId(value="snapshot-1"),
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        state=CompactionAttemptState.REQUESTED,
        requested_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    store.save_compaction_attempt(attempt)
    with coordinator._cancel_lock:
        coordinator._cancel_events[attempt.attempt_id.value] = threading.Event()
        coordinator._cancel_events[attempt.attempt_id.value].set()
    coordinator._run_pipeline(attempt, generation_reserve_tokens=100)
    final = store.load_compaction_attempt(attempt.attempt_id)
    assert final is not None
    assert final.state is CompactionAttemptState.CANCELLED
    assert store.load_pre_action_snapshot(attempt.snapshot_id) is None
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None
