"""Compaction Coordinator (CL-P9-3-D): the one Pipeline Manual and Auto both
use (Canonical Design SS7/SS9).

Phase order, each persisted before the next begins:

    requested -> preflight -> snapshot_persisted -> planned
    -> candidate_building -> validating -> candidate_persisted
    -> activating -> completed | conflicted | failed | cancelled

Invariant 6 ("Snapshot永続化成功前はCandidate生成Call 0"): `_run_pipeline`
never calls the Builder before `save_pre_action_snapshot` has returned.
Invariant 9 ("遅延結果...がActive Pointerを巻き戻す禁止"): every Activation
goes through `CompactionStorePort.compare_and_swap_active_context_projection`,
so a stale Attempt can only ever fail to activate, never overwrite a newer
Pointer.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import UTC, datetime

from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

from ..domain.artifacts import (
    ActivationRecord,
    ActivationResult,
    ActiveContextProjection,
    CompactionAttempt,
    CompactionAttemptState,
    CompactionPlan,
    CompactionStrategy,
    ContextHandoffArtifact,
    PreActionSnapshot,
    StructuredContextArtifact,
)
from ..domain.budget import (
    ContextBudgetSnapshot,
    PressureState,
    ThresholdConfig,
    compute_pressure_state,
)
from ..domain.errors import ContextCompactionDomainError, ContextCompactionDomainErrorCode
from ..domain.identity import DEFAULT_BRANCH_ID, ContextBranchId, HandoffArtifactId
from ..domain.measurement import MeasuredTokens, MeasurementClass
from ..ports.store import CompactionStorePort
from .auto_policy import AutoCompactionPolicyController
from .budget_service import ContextBudgetService
from .deterministic_builder import (
    DeterministicExtractiveBuilder,
    DeterministicExtractiveBuilderUnavailable,
)
from .id_factory import CompactionIdFactory
from .validation import validate_candidate
from .worker import CompactionWorker

DEFAULT_TOKEN_BUDGET = 2048
DEFAULT_DEADLINE_SECONDS = 30.0


class PreviewResult:
    def __init__(
        self,
        *,
        budget: ContextBudgetSnapshot,
        pressure: PressureState,
        feasible: bool,
        reason: str | None,
        estimated_token_reduction: int | None,
        sections_preview: object | None,
    ) -> None:
        self.budget = budget
        self.pressure = pressure
        self.feasible = feasible
        self.reason = reason
        self.estimated_token_reduction = estimated_token_reduction
        self.sections_preview = sections_preview


class CompactionCoordinator:
    def __init__(
        self,
        *,
        store: CompactionStorePort,
        budget_service: ContextBudgetService,
        builder: DeterministicExtractiveBuilder,
        auto_policy: AutoCompactionPolicyController,
        worker: CompactionWorker,
        thresholds: ThresholdConfig,
        id_factory: CompactionIdFactory | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        deadline_seconds: float = DEFAULT_DEADLINE_SECONDS,
    ) -> None:
        self._store = store
        self._budget_service = budget_service
        self._builder = builder
        self._auto_policy = auto_policy
        self._worker = worker
        self._thresholds = thresholds
        self._ids = id_factory or CompactionIdFactory()
        self._clock = clock
        self._token_budget = token_budget
        self._deadline_seconds = deadline_seconds
        self._cancel_events: dict[str, threading.Event] = {}
        self._cancel_lock = threading.Lock()
        self._restart_read_done: set[str] = set()

    # -- Restart Read ---------------------------------------------------------

    def ensure_restart_read(
        self, conversation_id: ConversationId, branch_id: ContextBranchId = DEFAULT_BRANCH_ID
    ) -> tuple[CompactionAttempt, ...]:
        """Idempotent: the first call for a given (conversation, branch) in
        this process marks every non-terminal Attempt found
        `interrupted_by_restart`; every later call for the same key is a
        cheap no-op (nothing non-terminal can remain after the first call
        marks it terminal)."""

        key = f"{conversation_id.value}::{branch_id.value}"
        if key in self._restart_read_done:
            return ()
        self._restart_read_done.add(key)
        stale = self._store.list_non_terminal_attempts(conversation_id, branch_id)
        now = self._clock()
        marked = []
        for attempt in stale:
            terminal = attempt.transitioned(
                target=CompactionAttemptState.INTERRUPTED_BY_RESTART,
                updated_at=now,
                terminal_reason="a prior process instance left this Attempt non-terminal",
            )
            self._store.save_compaction_attempt(terminal)
            marked.append(terminal)
        return tuple(marked)

    # -- Budget / Preview -------------------------------------------------------

    def budget(
        self, conversation_id: ConversationId, *, generation_reserve_tokens: int
    ) -> tuple[ContextBudgetSnapshot, PressureState] | None:
        self.ensure_restart_read(conversation_id)
        snapshot = self._budget_service.compute(
            conversation_id, generation_reserve_tokens=generation_reserve_tokens
        )
        if snapshot is None:
            return None
        snapshot = self._substitute_active_projection_usage(snapshot)
        pressure = compute_pressure_state(
            snapshot, self._thresholds, auto_compaction_enabled=self._auto_policy.is_enabled()
        )
        return snapshot, pressure

    def _substitute_active_projection_usage(
        self, snapshot: ContextBudgetSnapshot
    ) -> ContextBudgetSnapshot:
        """Pressure must reflect what will actually be sent to the Model.
        `ContextBudgetService.compute()` always measures the ORIGINAL
        Conversation Projection (it has no Store dependency); when a
        Structured Context is genuinely active for the current Conversation
        Revision, its own already-measured `token_count` replaces
        `current_prompt_usage` here -- otherwise Auto Compaction could never
        relieve the very Pressure it was triggered by, since the raw
        Original keeps growing regardless of any Compaction performed
        against it."""

        projection = self.active_projection_for_generation(
            snapshot.conversation_id,
            current_source_revision=snapshot.source_conversation_revision,
        )
        if projection is None or projection.structured_context_id is None:
            return snapshot
        artifact = self._store.load_structured_context_artifact(projection.structured_context_id)
        if artifact is None:
            return snapshot
        active_usage = MeasuredTokens(
            value=artifact.token_count,
            measurement_class=MeasurementClass.RUNTIME_CALCULATED,
            source="active_structured_context_artifact",
            observed_at=snapshot.computed_at,
        )
        return snapshot.model_copy(update={"current_prompt_usage": active_usage})

    def preview(
        self, conversation_id: ConversationId, *, generation_reserve_tokens: int
    ) -> PreviewResult | None:
        """Mutation 0: no Snapshot/Plan/Attempt is created or persisted."""

        result = self.budget(conversation_id, generation_reserve_tokens=generation_reserve_tokens)
        if result is None:
            return None
        snapshot, pressure = result
        projection = self._budget_service.source.read(conversation_id)
        if projection is None:
            return None
        try:
            sections, token_count = self._builder.build(
                projection, token_budget=self._token_budget
            )
        except DeterministicExtractiveBuilderUnavailable as exc:
            return PreviewResult(
                budget=snapshot,
                pressure=pressure,
                feasible=False,
                reason=str(exc),
                estimated_token_reduction=None,
                sections_preview=None,
            )
        current_usage = snapshot.current_prompt_usage.value or 0
        return PreviewResult(
            budget=snapshot,
            pressure=pressure,
            feasible=True,
            reason=None,
            estimated_token_reduction=max(0, current_usage - token_count),
            sections_preview=sections,
        )

    # -- Manual / Auto entry points -----------------------------------------------

    def request_manual_compaction(
        self, conversation_id: ConversationId, *, generation_reserve_tokens: int
    ) -> CompactionAttempt:
        """Manual Compaction never checks Auto Trigger Threshold or the Auto
        Policy flag (SS5.3/Invariant 3) -- it only needs a completed Turn
        to build from."""

        self.ensure_restart_read(conversation_id)
        action_id = self._ids.action_id()
        attempt_id = self._ids.attempt_id()
        now = self._clock()
        attempt = CompactionAttempt(
            attempt_id=attempt_id,
            plan_id=self._ids.plan_id(),
            action_id=action_id,
            snapshot_id=self._ids.snapshot_id(),
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            state=CompactionAttemptState.REQUESTED,
            requested_at=now,
            updated_at=now,
        )
        self._store.save_compaction_attempt(attempt)
        with self._cancel_lock:
            self._cancel_events[attempt_id.value] = threading.Event()
        submitted = self._worker.submit(
            attempt_id.value,
            lambda: self._run_pipeline(
                attempt, generation_reserve_tokens=generation_reserve_tokens
            ),
        )
        if not submitted:
            attempt = attempt.transitioned(
                target=CompactionAttemptState.FAILED,
                updated_at=self._clock(),
                terminal_reason="the Compaction Worker has already shut down",
                error_code="worker_shutdown",
            )
            self._store.save_compaction_attempt(attempt)
        return attempt

    def run_auto_compaction_if_required(
        self, conversation_id: ConversationId, *, generation_reserve_tokens: int
    ) -> PressureState:
        """Called from the Generation preflight (Invariant 5: never switches
        Pointer mid-Generation, only before a new Attempt starts). Runs the
        pipeline INLINE (blocking) so the caller's own Turn only proceeds
        once the outcome -- success or failure -- is known; a `failed`/
        `cancelled` outcome here still allows the caller to fall back to
        `manual_compaction_required` semantics."""

        result = self.budget(conversation_id, generation_reserve_tokens=generation_reserve_tokens)
        if result is None:
            return PressureState.UNKNOWN
        _snapshot, pressure = result
        # `hard_reserve_protected` is included here, not only
        # `auto_compaction_required`: both mean "Auto is ON and this
        # Conversation has already reached (or passed) the point Auto is
        # meant to resolve" -- the two states differ only in how much margin
        # remained when Pressure was computed, never in whether Auto should
        # act (SS6.4).
        if pressure not in (
            PressureState.AUTO_COMPACTION_REQUIRED,
            PressureState.HARD_RESERVE_PROTECTED,
        ):
            return pressure
        action_id = self._ids.action_id()
        attempt_id = self._ids.attempt_id()
        now = self._clock()
        attempt = CompactionAttempt(
            attempt_id=attempt_id,
            plan_id=self._ids.plan_id(),
            action_id=action_id,
            snapshot_id=self._ids.snapshot_id(),
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            state=CompactionAttemptState.REQUESTED,
            requested_at=now,
            updated_at=now,
        )
        self._store.save_compaction_attempt(attempt)
        with self._cancel_lock:
            self._cancel_events[attempt_id.value] = threading.Event()
        self._run_pipeline(attempt, generation_reserve_tokens=generation_reserve_tokens)
        recheck = self.budget(conversation_id, generation_reserve_tokens=generation_reserve_tokens)
        return recheck[1] if recheck is not None else PressureState.UNKNOWN

    def get_attempt(self, attempt_id_value: str) -> CompactionAttempt | None:
        from ..domain.identity import CompactionAttemptId

        return self._store.load_compaction_attempt(CompactionAttemptId(value=attempt_id_value))

    def request_cancel(self, attempt_id_value: str) -> bool:
        with self._cancel_lock:
            event = self._cancel_events.get(attempt_id_value)
        if event is not None:
            event.set()
        return self._worker.request_cancel(attempt_id_value) or event is not None

    # -- Handoff (CL-P9-3-E.4, Active Context Mutation 0) --------------------------

    def build_handoff(
        self, conversation_id: ConversationId, *, handoff_artifact_id_value: str
    ) -> ContextHandoffArtifact | None:
        """Read-only: never touches `ActiveContextProjection`/`CompactionAttempt`
        state. Reuses this same Coordinator's own Source/Builder rather than
        requiring a caller to reach into private fields to construct a
        separate `ContextHandoffService`."""

        projection = self._budget_service.source.read(conversation_id)
        if projection is None:
            return None
        try:
            sections, _token_count = self._builder.build(
                projection, token_budget=self._token_budget
            )
        except DeterministicExtractiveBuilderUnavailable:
            return None
        return ContextHandoffArtifact(
            handoff_artifact_id=HandoffArtifactId(value=handoff_artifact_id_value),
            conversation_id=conversation_id,
            branch_id=projection.branch_id,
            source_conversation_revision=projection.source_conversation_revision,
            sections=sections,
            created_at=self._clock(),
        )

    # -- Rollback -----------------------------------------------------------------

    def rollback(self, attempt_id_value: str) -> ActivationRecord:
        from ..domain.identity import CompactionAttemptId

        attempt_id = CompactionAttemptId(value=attempt_id_value)
        attempt = self._store.load_compaction_attempt(attempt_id)
        if attempt is None or attempt.state is not CompactionAttemptState.COMPLETED:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ATTEMPT_NOT_FOUND,
                safe_message="Only a Completed Compaction Attempt can be rolled back.",
            )
        snapshot = self._store.load_pre_action_snapshot(attempt.snapshot_id)
        if snapshot is None:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_NOT_FOUND,
                safe_message="The Pre-action Snapshot for this Attempt is missing.",
            )
        current = self._store.load_active_context_projection(
            attempt.conversation_id, attempt.branch_id
        )
        current_revision = current.active_projection_revision if current is not None else 0
        now = self._clock()
        restored = ActiveContextProjection(
            conversation_id=attempt.conversation_id,
            branch_id=attempt.branch_id,
            active_projection_revision=current_revision + 1,
            structured_context_id=snapshot.previous_structured_context_id,
            source_conversation_revision=snapshot.source_conversation_revision,
            updated_at=now,
        )
        succeeded = self._store.compare_and_swap_active_context_projection(
            conversation_id=attempt.conversation_id,
            branch_id=attempt.branch_id,
            expected_active_projection_revision=current_revision,
            new_projection=restored,
        )
        record = ActivationRecord(
            attempt_id=attempt_id,
            conversation_id=attempt.conversation_id,
            branch_id=attempt.branch_id,
            expected_source_conversation_revision=snapshot.source_conversation_revision,
            observed_source_conversation_revision=snapshot.source_conversation_revision,
            expected_active_projection_revision=current_revision,
            observed_active_projection_revision=current_revision,
            result=(
                ActivationResult.ROLLED_BACK if succeeded else ActivationResult.REJECTED_CONFLICT
            ),
            new_active_projection_revision=(current_revision + 1 if succeeded else None),
            recorded_at=now,
        )
        self._store.save_activation_record(record)
        if not succeeded:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.REVISION_CONFLICT,
                safe_message="Rollback lost a race with a concurrent Activation.",
            )
        rolled_back_attempt = attempt.transitioned(
            target=CompactionAttemptState.ROLLED_BACK,
            updated_at=now,
            terminal_reason="rolled back by explicit request",
        )
        self._store.save_compaction_attempt(rolled_back_attempt)
        return record

    # -- Generation-time read ------------------------------------------------------

    def active_projection_for_generation(
        self, conversation_id: ConversationId, *, current_source_revision: int
    ) -> ActiveContextProjection | None:
        """`None` means "use the original projection" -- either no Active
        Context Projection has ever been written, it points at no
        Structured Context (explicit original), or it was computed against
        a Conversation Revision that is no longer current (a newer Turn
        landed since) -- a safety net against ever serving a stale
        Compacted Projection for a Conversation that has since moved on."""

        projection = self._store.load_active_context_projection(
            conversation_id, DEFAULT_BRANCH_ID
        )
        if projection is None or projection.structured_context_id is None:
            return None
        if projection.source_conversation_revision != current_source_revision:
            return None
        return projection

    def load_structured_context(
        self, structured_context_id_value: str
    ) -> StructuredContextArtifact | None:
        from ..domain.identity import StructuredContextId

        return self._store.load_structured_context_artifact(
            StructuredContextId(value=structured_context_id_value)
        )

    # -- Pipeline (runs on the Worker thread for Manual; inline for Auto) --------------

    def _cancelled(self, attempt_id_value: str) -> bool:
        with self._cancel_lock:
            event = self._cancel_events.get(attempt_id_value)
        return event is not None and event.is_set()

    def _run_pipeline(
        self, attempt: CompactionAttempt, *, generation_reserve_tokens: int
    ) -> None:
        try:
            self._run_pipeline_inner(attempt, generation_reserve_tokens=generation_reserve_tokens)
        finally:
            with self._cancel_lock:
                self._cancel_events.pop(attempt.attempt_id.value, None)

    def _terminal(
        self,
        attempt: CompactionAttempt,
        *,
        target: CompactionAttemptState,
        reason: str,
        error_code: str | None = None,
    ) -> None:
        updated = attempt.transitioned(
            target=target, updated_at=self._clock(), terminal_reason=reason, error_code=error_code
        )
        self._store.save_compaction_attempt(updated)

    def _run_pipeline_inner(
        self, attempt: CompactionAttempt, *, generation_reserve_tokens: int
    ) -> None:
        attempt_id_value = attempt.attempt_id.value
        conversation_id = attempt.conversation_id
        branch_id = attempt.branch_id

        if self._cancelled(attempt_id_value):
            self._terminal(attempt, target=CompactionAttemptState.CANCELLED, reason="cancelled")
            return

        # -- preflight: budget + current pointer -----------------------------
        preflight_result = self.budget(
            conversation_id, generation_reserve_tokens=generation_reserve_tokens
        )
        if preflight_result is None:
            self._terminal(
                attempt,
                target=CompactionAttemptState.REJECTED,
                reason="no completed turn is available to compact",
                error_code=ContextCompactionDomainErrorCode.CORE_UNAVAILABLE.value,
            )
            return
        budget_snapshot, _pressure = preflight_result
        attempt = attempt.transitioned(
            target=CompactionAttemptState.PREFLIGHT, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)

        current_projection = self._store.load_active_context_projection(conversation_id, branch_id)
        current_projection_revision = (
            current_projection.active_projection_revision if current_projection is not None else 0
        )
        current_structured_context_id = (
            current_projection.structured_context_id if current_projection is not None else None
        )

        # -- snapshot: persisted BEFORE any Candidate work (Invariant 6) ------
        snapshot = PreActionSnapshot(
            snapshot_id=attempt.snapshot_id,
            action_id=attempt.action_id,
            conversation_id=conversation_id,
            branch_id=branch_id,
            source_conversation_revision=budget_snapshot.source_conversation_revision,
            previous_active_projection_revision=current_projection_revision,
            previous_structured_context_id=current_structured_context_id,
            captured_at=self._clock(),
        )
        try:
            self._store.save_pre_action_snapshot(snapshot)
        except Exception:
            self._terminal(
                attempt,
                target=CompactionAttemptState.FAILED,
                reason="the Pre-action Snapshot could not be persisted",
                error_code=ContextCompactionDomainErrorCode.SNAPSHOT_FAILED.value,
            )
            return
        attempt = attempt.transitioned(
            target=CompactionAttemptState.SNAPSHOT_PERSISTED, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)

        if self._cancelled(attempt_id_value):
            self._terminal(attempt, target=CompactionAttemptState.CANCELLED, reason="cancelled")
            return

        # -- plan: frozen -------------------------------------------------------
        plan = CompactionPlan(
            plan_id=attempt.plan_id,
            action_id=attempt.action_id,
            snapshot_id=attempt.snapshot_id,
            conversation_id=conversation_id,
            branch_id=branch_id,
            source_conversation_revision=budget_snapshot.source_conversation_revision,
            budget=budget_snapshot,
            configured_builder=CompactionStrategy.DETERMINISTIC_EXTRACTIVE,
            token_budget=self._token_budget,
            deadline_at=datetime.fromtimestamp(
                self._clock().timestamp() + self._deadline_seconds, tz=UTC
            ),
            max_model_calls=0,
            frozen_at=self._clock(),
        )
        self._store.save_compaction_plan(plan)
        attempt = attempt.transitioned(
            target=CompactionAttemptState.PLANNED, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)

        if self._clock() > plan.deadline_at:
            self._terminal(
                attempt,
                target=CompactionAttemptState.FAILED,
                reason="the Compaction Plan deadline was already exceeded",
                error_code="deadline_exceeded",
            )
            return

        # -- candidate build: Model Call 0 ---------------------------------------
        attempt = attempt.transitioned(
            target=CompactionAttemptState.CANDIDATE_BUILDING, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)
        projection = self._budget_service.source.read(conversation_id)
        if projection is None:
            self._terminal(
                attempt,
                target=CompactionAttemptState.FAILED,
                reason="the source conversation projection disappeared mid-attempt",
            )
            return
        try:
            sections, token_count = self._builder.build(projection, token_budget=self._token_budget)
            executed_builder = CompactionStrategy.DETERMINISTIC_EXTRACTIVE
        except DeterministicExtractiveBuilderUnavailable as exc:
            self._terminal(
                attempt,
                target=CompactionAttemptState.FAILED,
                reason=str(exc),
                error_code="builder_unavailable",
            )
            return

        if self._cancelled(attempt_id_value):
            self._terminal(attempt, target=CompactionAttemptState.CANCELLED, reason="cancelled")
            return

        # -- validate -------------------------------------------------------------
        attempt = attempt.transitioned(
            target=CompactionAttemptState.VALIDATING, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)
        structured_context_id = self._ids.structured_context_id()
        artifact = StructuredContextArtifact(
            structured_context_id=structured_context_id,
            conversation_id=conversation_id,
            branch_id=branch_id,
            source_conversation_revision=budget_snapshot.source_conversation_revision,
            configured_builder=plan.configured_builder,
            executed_builder=executed_builder,
            token_count=token_count,
            sections=sections,
            created_at=self._clock(),
        )
        try:
            validate_candidate(
                sections, token_count=token_count, plan=plan, source_projection=projection
            )
        except ContextCompactionDomainError as exc:
            self._terminal(
                attempt,
                target=CompactionAttemptState.REJECTED,
                reason=exc.safe_message,
                error_code=exc.code.value,
            )
            return

        # -- persist candidate ------------------------------------------------------
        self._store.save_structured_context_artifact(artifact)
        attempt = attempt.transitioned(
            target=CompactionAttemptState.CANDIDATE_PERSISTED,
            updated_at=self._clock(),
            structured_context_id=structured_context_id,
        )
        self._store.save_compaction_attempt(attempt)

        if self._cancelled(attempt_id_value):
            self._terminal(attempt, target=CompactionAttemptState.CANCELLED, reason="cancelled")
            return

        # -- activate via CAS -----------------------------------------------------------
        attempt = attempt.transitioned(
            target=CompactionAttemptState.ACTIVATING, updated_at=self._clock()
        )
        self._store.save_compaction_attempt(attempt)
        new_projection = ActiveContextProjection(
            conversation_id=conversation_id,
            branch_id=branch_id,
            active_projection_revision=current_projection_revision + 1,
            structured_context_id=structured_context_id,
            source_conversation_revision=budget_snapshot.source_conversation_revision,
            updated_at=self._clock(),
        )
        activated = self._store.compare_and_swap_active_context_projection(
            conversation_id=conversation_id,
            branch_id=branch_id,
            expected_active_projection_revision=current_projection_revision,
            new_projection=new_projection,
        )
        record = ActivationRecord(
            attempt_id=attempt.attempt_id,
            conversation_id=conversation_id,
            branch_id=branch_id,
            expected_source_conversation_revision=budget_snapshot.source_conversation_revision,
            observed_source_conversation_revision=budget_snapshot.source_conversation_revision,
            expected_active_projection_revision=current_projection_revision,
            observed_active_projection_revision=current_projection_revision,
            result=(
                ActivationResult.ACTIVATED
                if activated
                else ActivationResult.REJECTED_STALE_PROJECTION_REVISION
            ),
            new_active_projection_revision=(
                current_projection_revision + 1 if activated else None
            ),
            recorded_at=self._clock(),
        )
        self._store.save_activation_record(record)
        if not activated:
            self._terminal(
                attempt,
                target=CompactionAttemptState.CONFLICTED,
                reason="a concurrent Attempt already advanced the Active Context Projection",
                error_code=ActivationResult.REJECTED_STALE_PROJECTION_REVISION.value,
            )
            return
        self._terminal(
            attempt, target=CompactionAttemptState.COMPLETED, reason="activated successfully"
        )
