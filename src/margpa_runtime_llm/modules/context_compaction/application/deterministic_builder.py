"""Deterministic Extractive Builder (Canonical Design SS10.1, CL-P9-3-C).

Model Call 0: uses only `ModelContextCapacityPort.count_text_tokens`
(tokenizer measurement, not Generation) to fit the most recent Turns
verbatim into `token_budget`. It never guesses semantic importance for
older Turns -- guessing without genuine NLU would either be trivial or
overclaim understanding the project does not have here, so older Turns
become one honestly-labeled `OmittedRange` (always `rehydratable=True`,
since the Original Conversation is untouched and Selective Rehydration can
always recover them) rather than a fabricated "important fact".

`current_objective`/`current_position` are therefore the literal (verbatim,
length-capped) content of the first/last User Turn respectively -- real,
Source-backed proxies, never a generated paraphrase.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    ContextSourceTurnReference,
    OmittedRange,
    RecentVerbatimTurn,
    StructuredContextSections,
)
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    SourceConversationTurn,
)
from margpa_runtime_llm.modules.context_compaction.ports.model_context import (
    ModelContextCapacityPort,
)

_PROXY_TEXT_MAX_CHARACTERS = 2000
_EXACT_NEXT_ROUTE = (
    "Deterministic Extractive Builder performed no semantic next-step inference. "
    "See Recent Verbatim Tail for the latest exchange and the Recovery Index for "
    "full access to every omitted Turn."
)


def _turn_source(turn: SourceConversationTurn, revision: int) -> ContextSourceTurnReference:
    return ContextSourceTurnReference(
        turn_id=turn.turn_id,
        message_id=turn.user_message_id,
        source_conversation_revision=revision,
    )


class DeterministicExtractiveBuilderUnavailable(Exception):
    """Raised only when the loaded Backend cannot count tokens right now --
    the caller falls back to rejecting the Attempt rather than fabricating
    a Candidate with an unmeasured token count."""


class DeterministicExtractiveBuilder:
    def __init__(self, *, model_context: ModelContextCapacityPort) -> None:
        self._model_context = model_context

    def build(
        self,
        projection: ConversationSourceProjection,
        *,
        token_budget: int,
    ) -> tuple[StructuredContextSections, int]:
        """Returns the built Sections and their measured total token count.

        Raises `DeterministicExtractiveBuilderUnavailable` if the loaded
        Backend's tokenizer is not answering right now (never silently
        proceeds with an unmeasured/estimated token count for a Candidate
        that must later be Token-budget-validated exactly).
        """

        turns = projection.turns
        if not turns:
            raise DeterministicExtractiveBuilderUnavailable(
                "no completed turn is available to build a Candidate from"
            )

        fixed_overhead = self._count(_EXACT_NEXT_ROUTE)
        first_turn_proxy = self._truncate(turns[0].user_content)
        last_turn_proxy = self._truncate(turns[-1].user_content)
        fixed_overhead += self._count(first_turn_proxy) + self._count(last_turn_proxy)

        remaining_budget = token_budget - fixed_overhead
        if remaining_budget <= 0:
            raise DeterministicExtractiveBuilderUnavailable(
                "token_budget is too small for the fixed Section overhead"
            )

        recent: list[RecentVerbatimTurn] = []
        used = 0
        cutoff_index = len(turns)
        for index in range(len(turns) - 1, -1, -1):
            turn = turns[index]
            turn_cost = self._count(turn.user_content) + (
                self._count(turn.assistant_content) if turn.assistant_content else 0
            )
            if used + turn_cost > remaining_budget and recent:
                cutoff_index = index + 1
                break
            used += turn_cost
            cutoff_index = index
            # Each Turn's own (user, assistant) pair is built in chronological
            # order and prepended as a whole unit -- reversing the flattened
            # list here (as opposed to reversing whole-Turn groups) would
            # flip user/assistant order WITHIN a Turn too, corrupting the
            # dialogue sequence the Recent Verbatim Tail must preserve.
            turn_group = [
                RecentVerbatimTurn(
                    source=_turn_source(turn, projection.source_conversation_revision),
                    role="user",
                    content=turn.user_content,
                )
            ]
            if turn.assistant_content is not None:
                turn_group.append(
                    RecentVerbatimTurn(
                        source=_turn_source(turn, projection.source_conversation_revision),
                        role="assistant",
                        content=turn.assistant_content,
                    )
                )
            recent = turn_group + recent

        omitted_ranges: tuple[OmittedRange, ...] = ()
        if cutoff_index > 0:
            omitted_turns = turns[:cutoff_index]
            omitted_ranges = (
                OmittedRange(
                    first_source=_turn_source(
                        omitted_turns[0], projection.source_conversation_revision
                    ),
                    last_source=_turn_source(
                        omitted_turns[-1], projection.source_conversation_revision
                    ),
                    turn_count=len(omitted_turns),
                    rehydratable=True,
                    reason=(
                        "deterministic_extractive_baseline_omits_older_turns_verbatim_content"
                    ),
                ),
            )

        sections = StructuredContextSections(
            current_objective=first_turn_proxy,
            current_position=last_turn_proxy,
            exact_next_route=_EXACT_NEXT_ROUTE,
            recent_verbatim_tail=tuple(recent),
            omitted_ranges=omitted_ranges,
        )
        total_tokens = fixed_overhead + used
        return sections, total_tokens

    def _count(self, text: str) -> int:
        count = self._model_context.count_text_tokens(text)
        if count is None:
            raise DeterministicExtractiveBuilderUnavailable(
                "the loaded backend's tokenizer is not available right now"
            )
        return count

    @staticmethod
    def _truncate(text: str) -> str:
        if len(text) <= _PROXY_TEXT_MAX_CHARACTERS:
            return text
        return text[:_PROXY_TEXT_MAX_CHARACTERS]
