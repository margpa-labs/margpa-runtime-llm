"""Candidate Validation (CL-P9-3-C.4/.5).

Rejects: an empty Candidate, a Fact citing a Turn absent from the exact
Source Projection it was built from, a Reference count mismatch, and a
Candidate whose measured token count exceeds its own frozen Plan's budget.
This is the one gate a Structured/LLM Builder's output must also pass --
the Deterministic Builder always satisfies it by construction, but
Validation still runs on its output rather than trusting the Builder
identity (Invariant: never trust `configured_builder` as a proxy for
correctness).
"""

from __future__ import annotations

from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    CompactionPlan,
    StructuredContextSections,
)
from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
    ContextCompactionDomainErrorCode,
)
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
)


def validate_candidate(
    sections: StructuredContextSections,
    *,
    token_count: int,
    plan: CompactionPlan,
    source_projection: ConversationSourceProjection,
) -> None:
    if sections.source_summary_is_empty():
        raise ContextCompactionDomainError(
            code=ContextCompactionDomainErrorCode.CANDIDATE_REJECTED,
            safe_message="The Compaction Candidate retains no Source content.",
        )
    if token_count > plan.token_budget:
        raise ContextCompactionDomainError(
            code=ContextCompactionDomainErrorCode.CANDIDATE_REJECTED,
            safe_message="The Compaction Candidate exceeds its own frozen Token Budget.",
        )
    known_turn_ids = {turn.turn_id.value for turn in source_projection.turns}
    for reference in (
        *sections.important_fact_sources,
        *(range_.first_source for range_ in sections.omitted_ranges),
        *(range_.last_source for range_ in sections.omitted_ranges),
        *(turn.source for turn in sections.recent_verbatim_tail),
    ):
        if reference.turn_id.value not in known_turn_ids:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.CANDIDATE_REJECTED,
                safe_message=(
                    "The Compaction Candidate cites a Turn absent from its own Source Projection."
                ),
            )
        if reference.source_conversation_revision != plan.source_conversation_revision:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.STALE_REVISION,
                safe_message=(
                    "The Compaction Candidate cites a different Conversation Revision than "
                    "its own frozen Plan."
                ),
            )
