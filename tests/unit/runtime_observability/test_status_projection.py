from margpa_runtime_llm.modules.runtime_observability.domain.event import RuntimeEvent
from margpa_runtime_llm.modules.runtime_observability.projection.status_projection import (
    NOT_INVOKED_CURRENT_REQUEST,
    project_current_request_status,
    project_historical_latest,
)

_KNOWN_POINTS = ("input", "context_source", "stream_candidate", "output_candidate")


def _event(*, point_id: str, state: str, timestamp: str = "t0") -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"evt-{point_id}",
        request_id="req-1",
        component_role="guardrail",
        point_id=point_id,
        state=state,
        timestamp=timestamp,
    )


def test_current_request_projection_shows_not_invoked_for_points_with_no_current_event() -> None:
    projection = project_current_request_status(
        current_request_events={"input": _event(point_id="input", state="evaluated")},
        known_points=_KNOWN_POINTS,
    )
    assert projection["input"] == "evaluated"
    assert projection["context_source"] == NOT_INVOKED_CURRENT_REQUEST
    assert projection["stream_candidate"] == NOT_INVOKED_CURRENT_REQUEST
    assert projection["output_candidate"] == NOT_INVOKED_CURRENT_REQUEST


def test_current_request_projection_cannot_be_given_historical_events_by_construction() -> None:
    # The function signature has no parameter for prior-request events at all,
    # so there is nothing to pass here that could leak a stale result in.
    import inspect

    signature = inspect.signature(project_current_request_status)
    assert set(signature.parameters) == {"current_request_events", "known_points"}


def test_current_request_projection_surfaces_a_failed_state_verbatim_not_coerced() -> None:
    # A failure at one Point must not be masked as success, nor silently
    # dropped back to not_invoked, alongside an unrelated Point that did
    # succeed in the same request.
    projection = project_current_request_status(
        current_request_events={
            "input": _event(point_id="input", state="evaluated"),
            "context_source": _event(point_id="context_source", state="failed"),
        },
        known_points=_KNOWN_POINTS,
    )
    assert projection["context_source"] == "failed"
    assert projection["input"] == "evaluated"


def test_historical_projection_keeps_the_most_recent_event_per_point() -> None:
    events = [
        _event(point_id="input", state="evaluated", timestamp="t0"),
        _event(point_id="input", state="rejected", timestamp="t1"),
    ]
    projection = project_historical_latest(events_oldest_first=events, known_points=_KNOWN_POINTS)
    assert projection["input"] is not None
    assert projection["input"].state == "rejected"
    assert projection["context_source"] is None
