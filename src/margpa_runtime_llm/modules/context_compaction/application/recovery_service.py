"""Recovery Index construction and Selective Rehydration (CL-P9-3-E.1/.2/.3).

Rehydration re-reads the Canonical Conversation through the SAME read-only
`ConversationSourceProjectionPort` every other Compaction operation uses --
it never reconstructs omitted content from the compacted Artifact itself,
so a stale/edited-since Structured Context can never mask a genuine
Conversation change (Invariant 10).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    RecoveryIndex,
    RecoveryIndexEntry,
    RehydratedTurn,
    RehydrationFailure,
    RehydrationFailureCode,
    SelectiveRehydrationRequest,
    SelectiveRehydrationResult,
    StructuredContextArtifact,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import RecoveryIndexId
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjectionPort,
)
from margpa_runtime_llm.modules.context_compaction.ports.model_context import (
    ModelContextCapacityPort,
)


def build_recovery_index(
    artifact: StructuredContextArtifact,
    *,
    recovery_index_id: RecoveryIndexId,
    model_context: ModelContextCapacityPort,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> RecoveryIndex:
    entries = []
    for position, omitted in enumerate(artifact.sections.omitted_ranges):
        estimate = model_context.count_text_tokens(
            f"{omitted.first_source.turn_id.value}:{omitted.last_source.turn_id.value}"
        )
        default_estimate = omitted.turn_count * 200
        entries.append(
            RecoveryIndexEntry(
                entry_id=f"{artifact.structured_context_id.value}-omitted-{position}",
                omitted_range=omitted,
                rehydration_token_estimate=default_estimate if estimate is None else estimate,
            )
        )
    return RecoveryIndex(
        recovery_index_id=recovery_index_id,
        structured_context_id=artifact.structured_context_id,
        conversation_id=artifact.conversation_id,
        branch_id=artifact.branch_id,
        source_conversation_revision=artifact.source_conversation_revision,
        entries=tuple(entries),
        created_at=clock(),
    )


class SelectiveRehydrationService:
    def __init__(
        self,
        *,
        source: ConversationSourceProjectionPort,
        model_context: ModelContextCapacityPort,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._source = source
        self._model_context = model_context
        self._clock = clock

    def rehydrate(
        self,
        request: SelectiveRehydrationRequest,
        *,
        index: RecoveryIndex,
    ) -> SelectiveRehydrationResult:
        now = self._clock()
        if index.recovery_index_id != request.recovery_index_id:
            return self._all_failed(request, RehydrationFailureCode.NOT_FOUND, now)
        projection = self._source.read(request.conversation_id)
        if projection is None:
            return self._all_failed(request, RehydrationFailureCode.NOT_FOUND, now)
        if projection.source_conversation_revision != index.source_conversation_revision:
            return self._all_failed(request, RehydrationFailureCode.STALE, now)

        entries_by_id = {entry.entry_id: entry for entry in index.entries}
        turns_by_id = {turn.turn_id.value: turn for turn in projection.turns}
        rehydrated: list[RehydratedTurn] = []
        failures: list[RehydrationFailure] = []
        total_tokens = 0
        for entry_id in request.requested_entry_ids:
            entry = entries_by_id.get(entry_id)
            if entry is None:
                failures.append(
                    RehydrationFailure(
                        entry_id=entry_id,
                        code=RehydrationFailureCode.NOT_FOUND,
                        safe_message="The requested Recovery Index entry does not exist.",
                    )
                )
                continue
            omitted = entry.omitted_range
            first_id = omitted.first_source.turn_id.value
            last_id = omitted.last_source.turn_id.value
            first_seq = turns_by_id[first_id].sequence if first_id in turns_by_id else None
            last_seq = turns_by_id[last_id].sequence if last_id in turns_by_id else None
            if first_seq is None or last_seq is None:
                failures.append(
                    RehydrationFailure(
                        entry_id=entry_id,
                        code=RehydrationFailureCode.CONFLICT,
                        safe_message=(
                            "The omitted Turn range is no longer present in the Conversation."
                        ),
                    )
                )
                continue
            range_entry_tokens = 0
            range_turns = []
            for turn in projection.turns:
                if first_seq <= turn.sequence <= last_seq:
                    for role, content, message_id in (
                        ("user", turn.user_content, turn.user_message_id),
                        ("assistant", turn.assistant_content, turn.assistant_message_id),
                    ):
                        if content is None or message_id is None:
                            continue
                        count = self._model_context.count_text_tokens(content)
                        if count is None:
                            count = len(content) // 4
                        range_entry_tokens += count
                        range_turns.append((turn, role, content, message_id))
            if total_tokens + range_entry_tokens > request.token_budget:
                failures.append(
                    RehydrationFailure(
                        entry_id=entry_id,
                        code=RehydrationFailureCode.BUDGET_EXCEEDED,
                        safe_message=(
                            "Rehydrating this entry would exceed the requested Token Budget."
                        ),
                    )
                )
                continue
            for turn, role, content, message_id in range_turns:
                rehydrated.append(
                    RehydratedTurn(
                        entry_id=entry_id,
                        source=type(omitted.first_source)(
                            turn_id=turn.turn_id,
                            message_id=message_id,
                            source_conversation_revision=projection.source_conversation_revision,
                        ),
                        role=role,
                        content=content,
                    )
                )
            total_tokens += range_entry_tokens

        return SelectiveRehydrationResult(
            request=request,
            rehydrated=tuple(rehydrated),
            failures=tuple(failures),
            total_tokens_used=total_tokens,
            resolved_at=now,
        )

    def _all_failed(
        self,
        request: SelectiveRehydrationRequest,
        code: RehydrationFailureCode,
        now: datetime,
    ) -> SelectiveRehydrationResult:
        return SelectiveRehydrationResult(
            request=request,
            rehydrated=(),
            failures=tuple(
                RehydrationFailure(
                    entry_id=entry_id,
                    code=code,
                    safe_message="The Recovery Index could not be resolved for this request.",
                )
                for entry_id in request.requested_entry_ids
            ),
            total_tokens_used=0,
            resolved_at=now,
        )
