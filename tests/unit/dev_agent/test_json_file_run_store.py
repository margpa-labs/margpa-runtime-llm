"""Unit tests for Phase 8 (P8-E/P8-CR2) JsonFileDevAgentRunStore (Restart
Recovery, and — since P8-CR2 — Authorization Envelope/Approval Evidence
persistence and pre-P8-CR2 Backward Compatibility)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.dev_agent import (
    DevAgentRunStoreUnsafePath,
    JsonFileDevAgentRunStore,
)
from margpa_runtime_llm.modules.dev_agent import (
    ApprovalDecision,
    ApprovalEvidence,
    ApprovalProfile,
    AuthorizationEnvelope,
    CapabilityId,
    ImportantGateReason,
    Plan,
    PlanStep,
    RetryPolicy,
    RunSnapshot,
    RunState,
    StepRecord,
    StepState,
)


def _run(run_id: str = "run-one") -> RunSnapshot:
    return RunSnapshot(
        run_id=run_id,
        capability_id=CapabilityId.DEV_AGENT,
        plan=Plan(steps=(PlanStep(step_id="only", tool_id="list_files", input={}),)),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        retry_policy=RetryPolicy(),
        max_steps=5,
        state=RunState.RUNNING,
        steps=(StepRecord(step_id="only", tool_id="list_files", state=StepState.PENDING),),
        created_at="2026-08-30T00:00:00+00:00",
    )


def test_save_and_load_all_round_trips(tmp_path: Path) -> None:
    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    store.save(_run("run-one"))
    store.save(_run("run-two"))

    loaded = store.load_all()
    assert {run.run_id for run in loaded} == {"run-one", "run-two"}


def test_load_all_on_empty_store_is_empty(tmp_path: Path) -> None:
    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    assert store.load_all() == ()


def test_a_new_store_instance_recovers_persisted_runs(tmp_path: Path) -> None:
    """Models a process Restart: a fresh Store object over the same
    directory must see everything the previous process instance saved."""

    first = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    first.save(_run("run-one"))

    second = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    loaded = second.load_all()
    assert len(loaded) == 1
    assert loaded[0].run_id == "run-one"


def test_a_corrupt_run_file_is_skipped_not_fatal(tmp_path: Path) -> None:
    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    store.save(_run("run-good"))
    corrupt_path = tmp_path / "persistent" / "default" / "dev_agent" / "runs" / "run-bad.json"
    corrupt_path.write_text("not valid json{{{", encoding="utf-8")

    loaded = store.load_all()
    assert {run.run_id for run in loaded} == {"run-good"}


def test_unsafe_run_id_is_rejected(tmp_path: Path) -> None:
    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    with pytest.raises(DevAgentRunStoreUnsafePath):
        store.save(_run("../escape"))


def test_unsafe_scope_key_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="scope_key"):
        JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="../escape")


# -- P8-CR2: Authorization Envelope / Approval Evidence persistence ---------


def _run_with_envelope_and_approval(run_id: str = "run-with-envelope") -> RunSnapshot:
    envelope = AuthorizationEnvelope(
        run_id=run_id,
        allowed_step_ids=("only",),
        allowed_tool_ids=("write_note",),
        resource_scope="fixture_only",
        max_steps=5,
        max_attempts=1,
        expires_at=None,
        gate_reasons=(ImportantGateReason.EXTERNAL_WRITE,),
        issued_at="2026-08-30T00:00:00+00:00",
    )
    evidence = ApprovalEvidence(
        run_id=run_id,
        step_id="only",
        tool_id="write_note",
        decision=ApprovalDecision.APPROVED,
        actor_class="human_reviewer",
        decided_at="2026-08-30T00:01:00+00:00",
        gate_reason=ImportantGateReason.EXTERNAL_WRITE,
    )
    return RunSnapshot(
        run_id=run_id,
        capability_id=CapabilityId.DEV_AGENT,
        plan=Plan(steps=(PlanStep(step_id="only", tool_id="write_note", input={}),)),
        approval_profile=ApprovalProfile.IMPORTANT_GATE_ONLY,
        retry_policy=RetryPolicy(),
        max_steps=5,
        state=RunState.RUNNING,
        steps=(
            StepRecord(
                step_id="only", tool_id="write_note", state=StepState.PENDING, approved=True
            ),
        ),
        created_at="2026-08-30T00:00:00+00:00",
        envelope=envelope,
        approvals=(evidence,),
    )


def test_envelope_and_approval_evidence_round_trip_through_the_file(tmp_path: Path) -> None:
    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    store.save(_run_with_envelope_and_approval())

    second = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    loaded = second.load_all()
    assert len(loaded) == 1
    run = loaded[0]

    assert run.envelope is not None
    assert run.envelope.run_id == "run-with-envelope"
    assert run.envelope.allowed_step_ids == ("only",)
    assert run.envelope.allowed_tool_ids == ("write_note",)
    assert run.envelope.resource_scope == "fixture_only"
    assert run.envelope.gate_reasons == (ImportantGateReason.EXTERNAL_WRITE,)

    assert len(run.approvals) == 1
    assert run.approvals[0].step_id == "only"
    assert run.approvals[0].decision is ApprovalDecision.APPROVED
    assert run.approvals[0].actor_class == "human_reviewer"


def test_a_pre_p8_cr2_run_file_without_envelope_or_approvals_is_not_corrupt(
    tmp_path: Path,
) -> None:
    """Backward Compatibility: a Run Store file written before P8-CR2
    existed has no `envelope`/`approvals` keys in its `run` payload at all
    — `load_all()` must still recover it (defaulted to `None`/`()`), never
    treat it as `DevAgentRunStoreCorrupt`."""

    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    legacy_run = _run("legacy-run").model_dump(mode="json", exclude={"envelope", "approvals"})
    payload = {"schema_version": 1, "run": legacy_run}
    run_dir = tmp_path / "persistent" / "default" / "dev_agent" / "runs"
    run_dir.mkdir(parents=True)
    (run_dir / "legacy-run.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = store.load_all()
    assert len(loaded) == 1
    assert loaded[0].envelope is None
    assert loaded[0].approvals == ()


def test_a_run_file_predating_budget_and_completion_gate_is_not_corrupt(tmp_path: Path) -> None:
    """P8-RW6-B/P8-RW6-C Backward Compatibility: a Run Store file written
    before Budget (`budget_limit`/`budget_consumed`) or the Completion Gate
    (`completion_approvals`) existed has none of those keys at all —
    `load_all()` must still recover it with safe defaults, never treat it
    as `DevAgentRunStoreCorrupt`."""

    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    legacy_run = _run("legacy-run").model_dump(
        mode="json",
        exclude={
            "envelope",
            "approvals",
            "budget_limit",
            "budget_consumed",
            "completion_approvals",
        },
    )
    payload = {"schema_version": 1, "run": legacy_run}
    run_dir = tmp_path / "persistent" / "default" / "dev_agent" / "runs"
    run_dir.mkdir(parents=True)
    (run_dir / "legacy-run.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = store.load_all()
    assert len(loaded) == 1
    assert loaded[0].budget_limit is None
    assert loaded[0].budget_consumed == 0
    assert loaded[0].completion_approvals == ()


# -- P8-CR5 (P8-CODEX-004): persistence-boundary rejection -------------------


def test_a_run_file_whose_approval_evidence_belongs_to_a_different_run_is_skipped(
    tmp_path: Path,
) -> None:
    """The persistence-boundary layer of the P8-CODEX-004 fix: a Run Store
    file that is otherwise schema-valid JSON, but whose `approvals[].run_id`
    does not match the outer Run's own `run_id` (the on-disk shape a
    transplanted-Evidence tamper would actually take), must fail
    `RunSnapshot.model_validate()` and be treated exactly like any other
    corrupt file — skipped and logged, never silently accepted — via
    `RunSnapshot.validate_approvals_belong_to_this_run()`."""

    store = JsonFileDevAgentRunStore(runtime_data_root=tmp_path, scope_key="default")
    store.save(_run_with_envelope_and_approval("run-good"))

    tampered = _run_with_envelope_and_approval("run-tampered").model_dump(mode="json")
    tampered["approvals"][0]["run_id"] = "some-other-run"
    payload = {"schema_version": 1, "run": tampered}
    run_dir = tmp_path / "persistent" / "default" / "dev_agent" / "runs"
    (run_dir / "run-tampered.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = store.load_all()
    assert {run.run_id for run in loaded} == {"run-good"}
