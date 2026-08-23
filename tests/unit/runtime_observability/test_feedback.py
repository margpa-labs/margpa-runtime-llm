import pydantic
import pytest

from margpa_runtime_llm.modules.runtime_observability.domain.feedback import (
    FeedbackRating,
    FeedbackRequestedAction,
    UserFeedback,
    should_trigger_action,
)


def _feedback(**overrides: object) -> UserFeedback:
    base: dict[str, object] = {
        "feedback_id": "fb-1",
        "request_id": "req-1",
        "turn_id": "turn-1",
        "rating": FeedbackRating.BAD,
        "category": "accuracy",
        "created_at": "2026-08-23T00:00:00+00:00",
    }
    base.update(overrides)
    return UserFeedback.model_validate(base)


def test_bad_rating_alone_never_triggers_an_action() -> None:
    feedback = _feedback(rating=FeedbackRating.BAD)
    assert should_trigger_action(feedback=feedback) is False


def test_good_rating_alone_never_triggers_an_action() -> None:
    feedback = _feedback(rating=FeedbackRating.GOOD)
    assert should_trigger_action(feedback=feedback) is False


def test_explicit_requested_action_does_trigger() -> None:
    feedback = _feedback(
        rating=FeedbackRating.BAD, requested_action=FeedbackRequestedAction.REGENERATE
    )
    assert should_trigger_action(feedback=feedback) is True


def test_category_must_be_a_lowercase_snake_case_token() -> None:
    with pytest.raises(pydantic.ValidationError):
        _feedback(category="Not Valid!")


def test_comment_is_optional() -> None:
    feedback = _feedback(comment=None)
    assert feedback.comment is None
