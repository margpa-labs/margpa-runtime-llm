"""Phase 4 Governance Evidence: Restart Readback and Raw-Content
Redaction (P4-EVD-001/002, P4-CODEX-003 Rework, P4-G-WU-002).

Restart Readback: a fresh `LocalJsonlEvidenceStore` instance pointed at
the same on-disk directory — simulating a process restart — must recover
every Governance Point Start/Terminal Event a prior instance wrote.

Redaction: the actual Model Output text that triggered an Enforce Reject
must never appear anywhere in the persisted Evidence, even though that
exact text is what the Governance Point evaluated — only Typed, Safe
scalar summary fields (P4-EVD-002/P4-STS-002) are ever written.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from margpa_runtime_llm.adapters.audit_evidence.evidence_governance_observer import (
    EvidenceGovernanceObserver,
)
from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import LocalJsonlEvidenceStore
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
)
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventKind,
    AuditRunId,
    SafeExecutedActionRecord,
    SafeRecommendedActionRecord,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    EvaluationMethod,
    ExecutionDescriptor,
    RuntimeCapabilitySnapshot,
)

_SECRET_LOOKING_OUTPUT_MARKER = "sk-live-should-never-be-persisted-anywhere-in-evidence-0042"


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor() -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def test_governance_evidence_survives_a_simulated_process_restart(tmp_path: Path) -> None:
    run_id = AuditRunId(value=str(uuid4()))

    def _store_factory() -> LocalJsonlEvidenceStore:
        return LocalJsonlEvidenceStore(
            anchor=tmp_path, relative_root="evidence", scope="runtime_governance"
        )

    observer = EvidenceGovernanceObserver(
        store_factory=_store_factory,
        run_id=run_id,
        source_component="test.runtime_governance",
        mode_provider=lambda: "enforce",
    )
    observer.observe_point_started(
        invocation_id="inv-restart-1", point_id="main_model.post", stage="post", mode="enforce"
    )
    observer.observe_point_terminal(
        invocation_id="inv-restart-1",
        point_id="main_model.post",
        stage="post",
        mode="enforce",
        execution_state="evaluated",
        severity="high",
        selected_descriptor_ids=("argd.rule-1",),
        observations=(),
        recommended_actions=(
            SafeRecommendedActionRecord(
                action_id="reject_output", reason_descriptor_id="argd.rule-1", severity="high"
            ),
        ),
        executed_actions=(
            SafeExecutedActionRecord(
                action_id="reject_output",
                executed=True,
                intervening=True,
                not_executed_reason_code=None,
            ),
        ),
        unavailable_reason_code=None,
        degraded_reason_code=None,
        binding_digest_sha512="b" * 128,
        source_plan_id="plan-restart-test",
        source_plan_digest_sha512="c" * 128,
        capability_snapshot_digest_sha512="d" * 128,
        authority_snapshot_digest_sha512="e" * 128,
        policy_snapshot_digest_sha512="f" * 128,
        budget_snapshot_digest_sha512="a" * 128,
        action_registry_digest_sha512="1" + "0" * 127,
        latency_ms=3,
        call_count=0,
    )
    assert observer.status().degraded is False

    # A brand new Store instance, same on-disk directory — simulates a
    # fresh process reading what a prior process wrote (P4-G-WU-002
    # "Restart").
    restarted_store = LocalJsonlEvidenceStore(
        anchor=tmp_path, relative_root="evidence", scope="runtime_governance"
    )
    recovered = restarted_store.read_all(run_id)
    assert [event.envelope.event_kind for event in recovered] == [
        AuditEventKind.GOVERNANCE_POINT_STARTED,
        AuditEventKind.GOVERNANCE_POINT_TERMINAL,
    ]
    terminal_payload = recovered[1].envelope.safe_payload
    # P4-CODEX-007: Restart Readback must recover the actual
    # Recommendation/Execution Identity and Reason — not merely a
    # matching count — plus the Binding/Source Plan/Snapshot Digests
    # this Result traces back to.
    assert terminal_payload.execution_state == "evaluated"  # type: ignore[union-attr]
    assert terminal_payload.executed_actions[0].action_id == "reject_output"  # type: ignore[union-attr]
    assert terminal_payload.executed_actions[0].executed is True  # type: ignore[union-attr]
    assert terminal_payload.executed_actions[0].intervening is True  # type: ignore[union-attr]
    assert terminal_payload.recommended_actions[0].action_id == "reject_output"  # type: ignore[union-attr]
    assert (
        terminal_payload.recommended_actions[0].reason_descriptor_id  # type: ignore[union-attr]
        == "argd.rule-1"
    )
    assert terminal_payload.recommended_actions[0].severity == "high"  # type: ignore[union-attr]
    assert terminal_payload.selected_descriptor_ids == ("argd.rule-1",)  # type: ignore[union-attr]
    assert terminal_payload.binding_digest_sha512 == "b" * 128  # type: ignore[union-attr]
    assert terminal_payload.source_plan_id == "plan-restart-test"  # type: ignore[union-attr]
    assert terminal_payload.source_plan_digest_sha512 == "c" * 128  # type: ignore[union-attr]


def test_the_raw_rejected_output_never_appears_anywhere_in_persisted_evidence(
    tmp_path: Path,
) -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    # Small enough that the marker-bearing output below exceeds it,
    # genuinely routing the real content through `reject_output` —
    # the point of this test is that *this exact text*, which the
    # Evaluator genuinely inspected, never reaches persisted Evidence.
    composition.budget = composition.budget.model_copy(update={"max_snapshot_chars": 10})
    run_id = AuditRunId(value=str(uuid4()))

    def _store_factory() -> LocalJsonlEvidenceStore:
        return LocalJsonlEvidenceStore(
            anchor=tmp_path, relative_root="evidence", scope="runtime_governance"
        )

    observer = EvidenceGovernanceObserver(
        store_factory=_store_factory,
        run_id=run_id,
        source_component="test.runtime_governance",
        mode_provider=lambda: "enforce",
    )
    _, post_hook = build_main_model_governance_hooks(
        composition=composition,
        mode_provider=lambda: "enforce",
        governance_observer=observer,
    )

    # Exceeds the tiny Budget above -> genuinely routes through
    # `output_exceeds_budget` -> `reject_output`, with this exact
    # marker-bearing string as the Snapshot the Evaluator inspected.
    should_reject, reason = post_hook(_SECRET_LOOKING_OUTPUT_MARKER)
    assert should_reject is True
    assert reason == "governance_reject_output"

    segment_files = list((tmp_path / "evidence").rglob("*.jsonl"))
    assert segment_files, "expected at least one Evidence segment file to exist"
    for segment in segment_files:
        raw_text = segment.read_text(encoding="utf-8")
        assert _SECRET_LOOKING_OUTPUT_MARKER not in raw_text
        # No raw Model Output field of any kind — only Typed scalar
        # summary fields belong in a Governance Point Evidence payload
        # (P4-EVD-002).
        assert "content" not in raw_text
