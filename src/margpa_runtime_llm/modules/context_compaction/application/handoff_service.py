"""Context Handoff Artifact construction (CL-P9-3-E.4).

Active Context Mutation 0: reads the Canonical Conversation through the same
read-only `ConversationSourceProjectionPort`, runs the Deterministic
Extractive Builder (Model Call 0) and returns a `ContextHandoffArtifact` --
it never touches `ActiveContextProjection`, `CompactionAttempt` or any
other Compaction lifecycle state.

The higher-level Sections (`fixed_decisions`/`constraints`/`authority`/
`completed`/... ) stay empty here, exactly as they do for a Deterministic
Compaction Candidate (see `deterministic_builder.py`'s own docstring) --
producing plausible-looking values for those fields without genuine
semantic extraction would itself be the kind of fabricated Fact Invariant 13
forbids. This is a known, documented MVP limitation (an Optional
Structured/LLM Builder, SS10.2, could fill them later), not silently
hidden from the Handoff's own Reader.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from margpa_runtime_llm.modules.context_compaction.domain.artifacts import ContextHandoffArtifact
from margpa_runtime_llm.modules.context_compaction.domain.identity import HandoffArtifactId
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjectionPort,
)
from margpa_runtime_llm.modules.context_compaction.ports.model_context import (
    ModelContextCapacityPort,
)
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

from .deterministic_builder import DeterministicExtractiveBuilder

HANDOFF_TOKEN_BUDGET = 4096


class ContextHandoffService:
    def __init__(
        self,
        *,
        source: ConversationSourceProjectionPort,
        model_context: ModelContextCapacityPort,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._source = source
        self._builder = DeterministicExtractiveBuilder(model_context=model_context)
        self._clock = clock

    def build(
        self,
        conversation_id: ConversationId,
        *,
        handoff_artifact_id: HandoffArtifactId,
    ) -> ContextHandoffArtifact | None:
        """`None` when the Conversation has no completed Turn to build from."""

        projection = self._source.read(conversation_id)
        if projection is None:
            return None
        sections, _ = self._builder.build(projection, token_budget=HANDOFF_TOKEN_BUDGET)
        return ContextHandoffArtifact(
            handoff_artifact_id=handoff_artifact_id,
            conversation_id=conversation_id,
            branch_id=projection.branch_id,
            source_conversation_revision=projection.source_conversation_revision,
            sections=sections,
            created_at=self._clock(),
        )
