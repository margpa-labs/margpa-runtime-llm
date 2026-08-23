import pydantic
import pytest

from margpa_runtime_llm.modules.runtime_observability.domain.event import RuntimeEvent


def _event(**overrides: object) -> RuntimeEvent:
    base: dict[str, object] = {
        "event_id": "evt-1",
        "request_id": "req-1",
        "component_role": "guardrail",
        "point_id": "guardrail.input",
        "state": "evaluated",
        "timestamp": "2026-08-23T00:00:00+00:00",
    }
    base.update(overrides)
    return RuntimeEvent.model_validate(base)


def test_event_allows_all_correlation_ids_to_be_absent_with_typed_reasoning_elsewhere() -> None:
    event = _event()
    assert event.conversation_id is None
    assert event.evaluation_run_id is None
    assert event.repair_attempt_id is None


def test_event_rejects_a_malformed_point_id() -> None:
    with pytest.raises(pydantic.ValidationError):
        _event(point_id="Guardrail Input!!")


def test_event_safe_payload_only_accepts_flat_primitive_values() -> None:
    event = _event(safe_payload={"match_count": 1, "action_taken": False, "reason": "policy"})
    assert event.safe_payload["match_count"] == 1
    assert event.safe_payload["action_taken"] is False
