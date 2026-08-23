"""Current Request Status Projection (Architecture 9.2, Phase 6-F-WU-002).

The two functions below are deliberately separate and never merged: Current
Request Projection's signature makes it structurally impossible to pass
historical events into it (there is no parameter for them), guaranteeing
Acceptance P6-ACC-036 "Current Requestへ過去Point結果混在0" by construction
rather than by caller discipline alone.
"""

from collections.abc import Mapping, Sequence

from ..domain.event import RuntimeEvent

NOT_INVOKED_CURRENT_REQUEST = "not_invoked_current_request"


def project_current_request_status(
    *, current_request_events: Mapping[str, RuntimeEvent], known_points: tuple[str, ...]
) -> dict[str, str]:
    """Only Events that actually occurred in the current request may appear here."""
    return {
        point_id: (
            current_request_events[point_id].state
            if point_id in current_request_events
            else NOT_INVOKED_CURRENT_REQUEST
        )
        for point_id in known_points
    }


def project_historical_latest(
    *, events_oldest_first: Sequence[RuntimeEvent], known_points: tuple[str, ...]
) -> dict[str, RuntimeEvent | None]:
    """A separate, explicitly-historical view; never substituted into Current Request Status."""
    latest_by_point: dict[str, RuntimeEvent] = {}
    for event in events_oldest_first:
        latest_by_point[event.point_id] = event
    return {point_id: latest_by_point.get(point_id) for point_id in known_points}
