"""CL-P9-3-C: Deterministic Extractive Builder (Model Call 0) + Validation."""

from datetime import UTC, datetime

import pytest

from margpa_runtime_llm.modules.context_compaction.application.deterministic_builder import (
    DeterministicExtractiveBuilder,
    DeterministicExtractiveBuilderUnavailable,
)
from margpa_runtime_llm.modules.context_compaction.application.validation import validate_candidate
from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    CompactionPlan,
    CompactionStrategy,
    ContextSourceTurnReference,
    OmittedRange,
)
from margpa_runtime_llm.modules.context_compaction.domain.budget import ContextBudgetSnapshot
from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
    ContextCompactionDomainErrorCode,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import (
    DEFAULT_BRANCH_ID,
    CompactionPlanId,
    ContextActionId,
    SnapshotId,
)
from margpa_runtime_llm.modules.context_compaction.domain.measurement import (
    MeasuredTokens,
    MeasurementClass,
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

_NOW = datetime.now(UTC)


class _FakeModelContext:
    """Real, deterministic char/4 tokenizer -- Model Call 0 (no Generation)."""

    def loaded_context_capacity(self) -> int | None:
        return 4096

    def loaded_model_identity(self) -> str | None:
        return "fake-model"

    def count_text_tokens(self, text: str) -> int | None:
        return max(1, len(text) // 4)


class _UnavailableModelContext(_FakeModelContext):
    def count_text_tokens(self, text: str) -> int | None:
        return None


def _turns(n: int) -> tuple[SourceConversationTurn, ...]:
    return tuple(
        SourceConversationTurn(
            turn_id=ConversationTurnId(value=f"turn-{i}"),
            sequence=i,
            user_message_id=ConversationMessageId(value=f"user-{i}"),
            user_content=f"user content number {i} " * 10,
            assistant_message_id=ConversationMessageId(value=f"assistant-{i}"),
            assistant_content=f"assistant content number {i} " * 10,
        )
        for i in range(n)
    )


def _projection(n: int, revision: int = 1) -> ConversationSourceProjection:
    return ConversationSourceProjection(
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        source_conversation_revision=revision,
        turns=_turns(n),
    )


def _budget(revision: int = 1) -> ContextBudgetSnapshot:
    def _m(value: int, cls: MeasurementClass = MeasurementClass.ESTIMATED) -> MeasuredTokens:
        return MeasuredTokens(value=value, measurement_class=cls, source="test", observed_at=_NOW)

    return ContextBudgetSnapshot(
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        source_conversation_revision=revision,
        model_context_capacity=_m(4096, MeasurementClass.PROVIDER_REPORTED),
        current_prompt_usage=_m(1000, MeasurementClass.RUNTIME_CALCULATED),
        generation_reserve=_m(100),
        system_governance_reserve=_m(100),
        rag_tool_reserve=_m(0),
        compaction_working_reserve=_m(100),
        safety_margin=_m(100),
        computed_at=_NOW,
    )


def _plan(*, token_budget: int, revision: int = 1) -> CompactionPlan:
    return CompactionPlan(
        plan_id=CompactionPlanId(value="plan-1"),
        action_id=ContextActionId(value="action-1"),
        snapshot_id=SnapshotId(value="snapshot-1"),
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        source_conversation_revision=revision,
        budget=_budget(revision),
        configured_builder=CompactionStrategy.DETERMINISTIC_EXTRACTIVE,
        token_budget=token_budget,
        deadline_at=_NOW,
        max_model_calls=0,
        frozen_at=_NOW,
    )


def test_builder_keeps_recent_turns_verbatim_and_omits_the_rest() -> None:
    builder = DeterministicExtractiveBuilder(model_context=_FakeModelContext())
    projection = _projection(20)
    sections, token_count = builder.build(projection, token_budget=200)
    assert sections.recent_verbatim_tail
    assert sections.omitted_ranges
    assert sections.omitted_ranges[0].rehydratable is True
    assert token_count > 0
    # The most recent turn's content must be the LAST entry kept.
    assert sections.recent_verbatim_tail[-1].content.startswith("assistant content number 19")


def test_builder_never_fabricates_facts_beyond_verbatim_source() -> None:
    builder = DeterministicExtractiveBuilder(model_context=_FakeModelContext())
    sections, _ = builder.build(_projection(5), token_budget=2048)
    assert sections.important_facts == ()
    assert sections.fixed_decisions == ()


def test_builder_raises_when_no_completed_turn_exists() -> None:
    builder = DeterministicExtractiveBuilder(model_context=_FakeModelContext())
    empty = ConversationSourceProjection(
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        source_conversation_revision=1,
        turns=(),
    )
    with pytest.raises(DeterministicExtractiveBuilderUnavailable):
        builder.build(empty, token_budget=2048)


def test_builder_is_unavailable_never_silent_when_tokenizer_is_down() -> None:
    """Model Call 0 discipline: a Backend that cannot count tokens right now
    must never let the Builder silently proceed with a fabricated/estimated
    count -- the Attempt must fail, not persist an unmeasured Candidate."""

    builder = DeterministicExtractiveBuilder(model_context=_UnavailableModelContext())
    with pytest.raises(DeterministicExtractiveBuilderUnavailable):
        builder.build(_projection(5), token_budget=2048)


def test_validate_candidate_rejects_a_candidate_exceeding_its_own_token_budget() -> None:
    builder = DeterministicExtractiveBuilder(model_context=_FakeModelContext())
    projection = _projection(20)
    sections, token_count = builder.build(projection, token_budget=2048)
    tiny_plan = _plan(token_budget=1)
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        validate_candidate(
            sections, token_count=token_count, plan=tiny_plan, source_projection=projection
        )
    assert excinfo.value.code is ContextCompactionDomainErrorCode.CANDIDATE_REJECTED


def test_validate_candidate_rejects_a_reference_to_an_unknown_turn() -> None:
    projection = _projection(5)
    sections, token_count = DeterministicExtractiveBuilder(
        model_context=_FakeModelContext()
    ).build(projection, token_budget=2048)
    forged = sections.model_copy(
        update={
            "omitted_ranges": (
                OmittedRange(
                    first_source=ContextSourceTurnReference(
                        turn_id=ConversationTurnId(value="turn-does-not-exist"),
                        message_id=ConversationMessageId(value="user-does-not-exist"),
                        source_conversation_revision=1,
                    ),
                    last_source=ContextSourceTurnReference(
                        turn_id=ConversationTurnId(value="turn-does-not-exist"),
                        message_id=ConversationMessageId(value="user-does-not-exist"),
                        source_conversation_revision=1,
                    ),
                    turn_count=1,
                    rehydratable=True,
                    reason="forged",
                ),
            )
        }
    )
    plan = _plan(token_budget=2048)
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        validate_candidate(
            forged, token_count=token_count, plan=plan, source_projection=projection
        )
    assert excinfo.value.code is ContextCompactionDomainErrorCode.CANDIDATE_REJECTED


def test_validate_candidate_rejects_a_stale_revision_reference() -> None:
    projection = _projection(5, revision=2)
    sections, token_count = DeterministicExtractiveBuilder(
        model_context=_FakeModelContext()
    ).build(projection, token_budget=2048)
    plan = _plan(token_budget=2048, revision=1)  # frozen at an older revision
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        validate_candidate(
            sections, token_count=token_count, plan=plan, source_projection=projection
        )
    assert excinfo.value.code is ContextCompactionDomainErrorCode.STALE_REVISION


def test_validate_candidate_rejects_an_empty_candidate() -> None:
    projection = _projection(1)
    empty_sections = DeterministicExtractiveBuilder(model_context=_FakeModelContext()).build(
        projection, token_budget=2048
    )[0].model_copy(update={"recent_verbatim_tail": (), "important_facts": ()})
    plan = _plan(token_budget=2048)
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        validate_candidate(
            empty_sections, token_count=0, plan=plan, source_projection=projection
        )
    assert excinfo.value.code is ContextCompactionDomainErrorCode.CANDIDATE_REJECTED
