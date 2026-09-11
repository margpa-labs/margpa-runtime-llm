"""Implements `conversation.application.generation_context_mapper.
ActiveContextProjectionPort` (CL-P9-3-E.5) -- the one point Compacted
Projections actually reach a real Generation Request.

Renders a `StructuredContextArtifact`'s Sections into a valid, alternating
`ConversationMessage` sequence: the rendered Sections become a preamble on
the FIRST retained message, `recent_verbatim_tail` supplies the following
alternating Turns verbatim, and the caller's own trailing (pending) messages
are appended unchanged -- the Deterministic Builder always produces a
`recent_verbatim_tail` starting with `user` and ending with `assistant`
(Invariant: only completed Turns are ever included), so this join is always
alternation-safe.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    StructuredContextSections,
)
from margpa_runtime_llm.modules.conversation.contracts import ConversationMessage, ConversationRole
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId


def render_structured_context_preamble(sections: StructuredContextSections) -> str:
    lines = [
        "[Phase 9-3 Compacted Context -- older Turns summarized/omitted below]",
        f"Current objective (verbatim first Turn): {sections.current_objective}",
        f"Current position (verbatim latest Turn): {sections.current_position}",
    ]
    if sections.omitted_ranges:
        lines.append(
            f"{len(sections.omitted_ranges)} omitted Turn range(s) exist and are recoverable "
            "via Selective Rehydration."
        )
    lines.append(sections.exact_next_route)
    return "\n".join(lines)


class CompactionActiveContextProjectionAdapter:
    def __init__(self, *, coordinator: CompactionCoordinator) -> None:
        self._coordinator = coordinator

    def resolve_messages(
        self,
        *,
        conversation_id: ConversationId,
        current_source_revision: int,
        original_messages: tuple[ConversationMessage, ...],
    ) -> tuple[ConversationMessage, ...]:
        projection = self._coordinator.active_projection_for_generation(
            conversation_id, current_source_revision=current_source_revision
        )
        if projection is None or projection.structured_context_id is None:
            return original_messages
        artifact = self._coordinator.load_structured_context(
            projection.structured_context_id.value
        )
        if artifact is None:
            return original_messages

        tail = artifact.sections.recent_verbatim_tail
        if not tail:
            return original_messages

        preamble = render_structured_context_preamble(artifact.sections)
        rendered: list[ConversationMessage] = [
            ConversationMessage(
                role=ConversationRole.USER,
                content=f"{preamble}\n\n---\n\n{tail[0].content}",
            )
        ]
        for turn in tail[1:]:
            rendered.append(
                ConversationMessage(
                    role=(
                        ConversationRole.USER
                        if turn.role == "user"
                        else ConversationRole.ASSISTANT
                    ),
                    content=turn.content,
                )
            )
        return tuple(rendered) + original_messages[-1:]
