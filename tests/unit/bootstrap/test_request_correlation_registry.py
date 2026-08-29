"""P6-RR-R19-WU-001..004 (resolves P6-CODEX-082): `RequestCorrelationRegistry`
must make `current_request_id()` correct the instant a Turn starts —
never only after its Recording Hook fires — and must never let a late
update for a superseded Request silently become Current."""

from __future__ import annotations

from margpa_runtime_llm.bootstrap.request_correlation_registry import (
    RequestCorrelationRegistry,
)


def test_current_request_id_is_valid_immediately_at_begin() -> None:
    registry = RequestCorrelationRegistry()
    assert registry.current_request_id() is None
    registry.begin(request_id="req-1", started_at="2026-08-29T00:00:00Z")
    assert registry.current_request_id() == "req-1"
    entry = registry.entry_for("req-1")
    assert entry is not None
    assert entry.status == "pending"
    assert entry.completed_at is None


def test_a_new_turn_becomes_current_even_before_the_previous_ones_hooks_fire() -> None:
    """The exact regression this Registry exists to fix: Turn N+1 starting
    must move Current forward immediately, never waiting on Turn N's own
    late Recording/Judge completion."""
    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-1", started_at="t0")
    registry.begin(request_id="req-2", started_at="t1")
    assert registry.current_request_id() == "req-2"
    # req-1's own Terminal transition, arriving late, must not move
    # Current backward.
    registry.mark_terminal(request_id="req-1", status="completed", completed_at="t2")
    assert registry.current_request_id() == "req-2"
    entry_1 = registry.entry_for("req-1")
    assert entry_1 is not None
    assert entry_1.status == "completed"


def test_mark_terminal_updates_status_and_completed_at() -> None:
    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-1", started_at="t0")
    registry.mark_terminal(request_id="req-1", status="cancelled", completed_at="t1")
    entry = registry.entry_for("req-1")
    assert entry is not None
    assert entry.status == "cancelled"
    assert entry.completed_at == "t1"


def test_mark_terminal_for_an_unknown_request_id_is_a_silent_no_op() -> None:
    registry = RequestCorrelationRegistry()
    registry.mark_terminal(request_id="never-registered", status="failed", completed_at="t0")
    assert registry.entry_for("never-registered") is None


def test_retention_bound_evicts_the_oldest_entries_first() -> None:
    registry = RequestCorrelationRegistry(retain=2)
    registry.begin(request_id="req-1", started_at="t0")
    registry.begin(request_id="req-2", started_at="t1")
    registry.begin(request_id="req-3", started_at="t2")
    assert registry.entry_for("req-1") is None
    assert registry.entry_for("req-2") is not None
    assert registry.entry_for("req-3") is not None
    assert [entry.request_id for entry in registry.entries()] == ["req-2", "req-3"]
    assert registry.current_request_id() == "req-3"


def test_generation_increases_monotonically_across_begins() -> None:
    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-1", started_at="t0")
    registry.begin(request_id="req-2", started_at="t1")
    entry_1 = registry.entry_for("req-1")
    entry_2 = registry.entry_for("req-2")
    assert entry_1 is not None
    assert entry_2 is not None
    assert entry_2.generation > entry_1.generation
