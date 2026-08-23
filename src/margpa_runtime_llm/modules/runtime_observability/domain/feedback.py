"""User Feedback (Architecture, Phase 6-F-WU-004).

No-auto-training is enforced by omission: this module has no training
pipeline hook, no export path, and no field that would let Feedback drive a
model-weight update. Rating alone must never trigger Retry/Regenerate/Repair
(Acceptance P6-ACC-044A): only an explicit `requested_action` can.
"""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

CATEGORY_PATTERN = r"^[a-z][a-z0-9_]*$"


class FeedbackRating(StrEnum):
    GOOD = "good"
    BAD = "bad"


class FeedbackRequestedAction(StrEnum):
    REGENERATE = "regenerate"
    CORRECT = "correct"


class UserFeedback(ImmutableContract):
    feedback_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    rating: FeedbackRating
    category: str = Field(min_length=1, pattern=CATEGORY_PATTERN)
    comment: str | None = Field(default=None, max_length=2000)
    requested_action: FeedbackRequestedAction | None = None
    created_at: str = Field(min_length=1)


def should_trigger_action(*, feedback: UserFeedback) -> bool:
    """Rating alone never triggers anything; only an explicit requested_action does."""
    return feedback.requested_action is not None
