"""Context Budget computation (CL-P9-3-A) -- pure orchestration over Ports.

Never calls a Generation/Inference Model: `count_text_tokens` is a
tokenizer-only measurement, the same "Call 0" category every other Governance
component in this project already treats token counting as (Invariant 12's
"LLM Callなしで動作でき" applies here too, one level below Candidate
building).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from margpa_runtime_llm.modules.context_compaction.domain.budget import ContextBudgetSnapshot
from margpa_runtime_llm.modules.context_compaction.domain.measurement import (
    MeasuredTokens,
    MeasurementClass,
)
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    ConversationSourceProjectionPort,
)
from margpa_runtime_llm.modules.context_compaction.ports.model_context import (
    ModelContextCapacityPort,
)
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId


@dataclass(frozen=True, slots=True)
class ReserveConfig:
    """SS6.1's remaining fixed Reserves. `generation_reserve_tokens` is not
    here -- it comes from the caller's own `ConversationSettings.
    max_new_tokens` for the pending Turn, which this Service does not own."""

    system_governance_reserve_tokens: int = 256
    rag_tool_reserve_tokens: int = 0
    compaction_working_reserve_tokens: int = 512
    safety_margin_tokens: int = 128


@dataclass(slots=True)
class ContextBudgetService:
    source: ConversationSourceProjectionPort
    model_context: ModelContextCapacityPort
    reserves: ReserveConfig = field(default_factory=ReserveConfig)
    clock: Callable[[], datetime] = field(default=lambda: datetime.now(UTC))

    def compute(
        self,
        conversation_id: ConversationId,
        *,
        generation_reserve_tokens: int,
    ) -> ContextBudgetSnapshot | None:
        """`None` when the Conversation has no completed Turn yet -- there is
        nothing to budget/compact against."""

        projection = self.source.read(conversation_id)
        if projection is None:
            return None
        now = self.clock()
        capacity = self.model_context.loaded_context_capacity()
        model_identity = self.model_context.loaded_model_identity()

        if capacity is None:
            capacity_measured = MeasuredTokens.unknown(
                source="loaded_context_capacity", observed_at=now
            )
        else:
            capacity_measured = MeasuredTokens(
                value=capacity,
                measurement_class=MeasurementClass.PROVIDER_REPORTED,
                source="loaded_context_capacity",
                observed_at=now,
                model_identity=model_identity,
            )

        usage_measured = self._current_prompt_usage(
            projection, now=now, model_identity=model_identity
        )

        def _reserve(value: int, source: str) -> MeasuredTokens:
            return MeasuredTokens(
                value=value,
                measurement_class=MeasurementClass.ESTIMATED,
                source=source,
                observed_at=now,
            )

        return ContextBudgetSnapshot(
            conversation_id=conversation_id,
            branch_id=projection.branch_id,
            source_conversation_revision=projection.source_conversation_revision,
            model_context_capacity=capacity_measured,
            current_prompt_usage=usage_measured,
            generation_reserve=_reserve(
                generation_reserve_tokens, "conversation_settings.max_new_tokens"
            ),
            system_governance_reserve=_reserve(
                self.reserves.system_governance_reserve_tokens, "config"
            ),
            rag_tool_reserve=_reserve(self.reserves.rag_tool_reserve_tokens, "config"),
            compaction_working_reserve=_reserve(
                self.reserves.compaction_working_reserve_tokens, "config"
            ),
            safety_margin=_reserve(self.reserves.safety_margin_tokens, "config"),
            computed_at=now,
        )

    def _current_prompt_usage(
        self,
        projection: ConversationSourceProjection,
        *,
        now: datetime,
        model_identity: str | None,
    ) -> MeasuredTokens:
        total = 0
        for turn in projection.turns:
            for text in (turn.user_content, turn.assistant_content):
                if text is None:
                    continue
                count = self.model_context.count_text_tokens(text)
                if count is None:
                    return MeasuredTokens.unknown(source="count_text_tokens", observed_at=now)
                total += count
        return MeasuredTokens(
            value=total,
            measurement_class=MeasurementClass.RUNTIME_CALCULATED,
            source="count_text_tokens",
            observed_at=now,
            model_identity=model_identity,
        )
