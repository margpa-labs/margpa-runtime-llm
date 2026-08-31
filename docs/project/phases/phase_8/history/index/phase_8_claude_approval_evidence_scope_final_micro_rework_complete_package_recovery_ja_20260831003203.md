# Phase 8 Claude Approval Evidence Scope Final Micro Rework — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-CR5
state: complete
provider: Claude
created_at: 2026-08-31 00:32 JST
handoff_source: phase_8_claude_approval_evidence_scope_final_micro_rework_exact_handoff_ja_20260831001957.md
review_source: phase_8_codex_controller_post_first_rework_re_review_ja_20260831001957.md
addendum_kind: append_only
```

## 結論

```yaml
p8_cr5_established: true
mvp_blocker_open: 0
critical_open: 0
codex_004_disposition: RESOLVED
```

Codex Controller最終再Reviewが指摘したP8-CODEX-004（Approval EvidenceのRun Scope不照合とCompatibility BoolによるGate迂回）だけを修正した。P8-CODEX-001〜003・Concurrency Lock・Envelope基本配線・Acceptance集計・Frontendは無変更。

## P8-CODEX-004 Disposition

```yaml
disposition: RESOLVED
severity: major
priority: P0
```

### Source上の原因（Controller指摘のまま）

- `_has_approval_evidence(run, step)`が`evidence.run_id == run.run_id`を照合していなかった。`RunSnapshot`にもRun ID相関Validatorが無く、永続化／復元される型付きStateとして構造保証されていなかった。
- Gate条件が`not next_step.approved and not _has_approval_evidence(...)`というOR相当の構造だったため、Envelope付き新規Runでも`StepRecord.approved=true`単独（Typed Evidence 0件）でGateを通過できた。

### 是正内容

1. **`_has_approval_evidence()`の照合強化**（`run_service.py`）：`evidence.run_id == run.run_id`を追加。さらに対象ToolがImportant Gate Reasonを持つ場合、Evidenceの`gate_reason`が現在のDescriptorと一致することも要求する（`expected_gate_reason = descriptor.important_gate_reason if descriptor is not None else None`との等価性照合）。
2. **Gate判定の非対称化**（`run_service.py` `_advance_locked()`）：`gate_satisfied = _has_approval_evidence(...)`を算出した上で、`run.envelope is None`（Pre-P8-CR2 Legacy Run）のときだけ`gate_satisfied = gate_satisfied or next_step.approved`とBoolをOR。Envelope付きRun（P8-CR2以降に生成された全Run）ではBoolを一切参照しない。
3. **Contract／Persistence Boundaryの独立した第2層**（`contracts.py`）：`RunSnapshot`へ`model_validator(mode="after")`（`validate_approvals_belong_to_this_run`）を追加。`approvals`内の各`ApprovalEvidence.run_id`が親`RunSnapshot.run_id`と一致しない場合は`ValidationError`。`model_copy()`は再Validationしないため通常のState遷移には影響せず、`__init__`／`model_validate()`（Run Store File読込・直接構築）だけで発火する。`JsonFileDevAgentRunStore._read_one()`の既存try/exceptにより、該当Fileは自動的に`DevAgentRunStoreCorrupt`として扱われる（Store側の変更は不要だった）。
4. **`StepRecord.approved`のDocstring更新**：新しいScope（Legacy Runにのみ効力を持つCompatibility Cache）を正直に反映。虚偽Actor／Timestamp／Gate Reasonの捏造は行っていない（LegacyへのMigrationは選択せず、Boolを素のままLegacy限定Fallbackとして残す設計を選択）。

### 実証（Before／After）

Controller実Probeと同一の操作を再現し、Fix前は実際にGateが迂回されることを確認した上でFixした。

```yaml
before_fix_reproduction:
  method: "_has_approval_evidence()を旧版（run_id照合なし）へ一時的に差し替え、Gate条件も旧OR構造へ一時的に差し戻して実行"
  test_transplanted_evidence: FAILED (counting_port.calls == 1, Gate Bypass再現)
  test_bool_only_bypass: FAILED (counting_port.calls == 1, Gate Bypass再現)
after_fix:
  test_transplanted_evidence: PASSED (counting_port.calls == 0)
  test_bool_only_bypass: PASSED (counting_port.calls == 0)
  restore_verified: "Fix差し戻し後のSourceがdiff上Fix版と完全一致することを確認済み"
```

## Run A Evidence -> Run B Reuse Rejection Evidence

```yaml
runtime_layer:
  test: tests/unit/dev_agent/test_run_service.py::test_transplanted_evidence_from_another_run_is_rejected_and_never_executes
  method: "Run Aで承認したApprovalEvidenceをRun Bのapprovalsへmodel_copyで直接移植（Contract Validatorをバイパスする経路）。Run Bをadvance()"
  result: "counting_port.calls == 0, Run BはAWAITING_APPROVALのまま"
persistence_layer:
  test: tests/unit/dev_agent/test_json_file_run_store.py::test_a_run_file_whose_approval_evidence_belongs_to_a_different_run_is_skipped
  method: "approvals[0].run_idが親Runと異なる、Schema上は妥当なJSONをRun Store Fileへ直接書込み"
  result: "load_all()がその1件だけをCorrupt扱いでSkip（他Runは正常回収）"
contract_layer:
  test: tests/unit/dev_agent/test_run_service.py::test_run_snapshot_rejects_approval_evidence_scoped_to_a_different_run
  method: "RunSnapshot(...)を別RunのApprovalEvidenceを含めて直接構築"
  result: "ValidationErrorで構築自体が失敗"
```

## Envelope付きBool-only Bypass Rejection Evidence

```yaml
test: tests/unit/dev_agent/test_run_service.py::test_envelope_having_run_cannot_bypass_the_gate_with_bool_alone
method: "submit_approval()を経由せず、StepRecord.approved=True・state=PENDINGへ直接改変（Typed Evidenceは0件のまま）"
result: "counting_port.calls == 0, RunはAWAITING_APPROVALへ再度収束"
gate_reason_drift_evidence:
  test: tests/unit/dev_agent/test_run_service.py::test_gate_reason_drift_between_evidence_and_current_descriptor_is_denied
  method: "正規Evidenceのgate_reasonを承認後に別値へ改変"
  result: "counting_port.calls == 0, Gateへ再収束（Evidenceの内容自体が現在Descriptorと食い違う場合も拒否されることを確認）"
```

## Normal Approval / Restart / Legacy Compatibility Evidence

```yaml
normal_approval_and_restart:
  unit: tests/unit/dev_agent/test_run_service.py::test_approval_evidence_persists_and_survives_restart（既存、Fix後も無改変でPASS）
  rest: tests/integration/dev_agent/test_dev_agent_web_app.py::test_approval_evidence_is_returned_via_rest_and_survives_restart（既存、Fix後も無改変でPASS）
different_step_or_tool_regression_preserved:
  test: tests/unit/dev_agent/test_run_service.py::test_approval_evidence_for_one_step_never_authorizes_a_different_step（既存、Fix後も無改変でPASS）
legacy_run_compatibility:
  read_and_default: tests/unit/dev_agent/test_run_service.py::test_a_run_persisted_before_p8_cr2_has_no_envelope_and_is_not_corrupt（既存）
  execute_via_bool: tests/unit/dev_agent/test_run_service.py::test_legacy_run_without_an_envelope_still_honors_the_bool_alone（新規 — Legacy Runがapproved=trueだけで実行できることを明示的に実証、Over-correctionしていないことの証拠）
  rest: tests/integration/dev_agent/test_dev_agent_web_app.py::test_a_legacy_run_without_an_envelope_is_still_advanceable_via_rest（既存、Fix後も無改変でPASS）
```

## Changed Paths

```text
# Backend Source（既存File改修、新規0）
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py

# Backend Test（既存File改修、新規0）
tests/unit/dev_agent/test_run_service.py
tests/unit/dev_agent/test_json_file_run_store.py
```

明示的に変更していないもの：`__init__.py`（Export対象に変更無し）、`web/dev_agent_contracts.py`／`web/dev_agent_routes.py`（Response Schema・Route自体は無変更、既存Test 17件がそのままPASS）、`bootstrap/dev_agent.py`、`adapters/dev_agent/*`、`entrypoints/web/main.py`、Concurrency Lock（P8-CR1成果）、Envelope基本発行・照合Logic（P8-CR2成果のうちP8-CODEX-004対象外部分）、Frontend全File、Acceptance集計文書。

## Focused／Canonical／Mypy／Ruff Results

```yaml
dev_agent_unit_and_integration:
  command: "uv run pytest tests/unit/dev_agent/ tests/integration/dev_agent/ -q"
  result: "84 passed"
  new_in_this_package: 6  # test_run_service.py +5, test_json_file_run_store.py +1
backend_full_suite:
  command: "uv run pytest -q"
  result: "2090 passed, 7 deselected"
ruff:
  command: "uv run ruff check ."
  result: "All checks passed"
mypy:
  command: "uv run mypy src/"
  result: "Success: no issues found in 344 source files"
frontend:
  changed: false
  reexecuted: false
  reason: "Handoff §1により明示的に禁止"
```

## Internal Review 1 Cycle — Finding／Rework

Handoff §4／Controller Review §3.3を再読の上、実装Sourceと突き合わせて1 Cycle実施。自己発見1件をその場で追加した：Evidenceの`gate_reason`が現在Descriptorと食い違う（Drift）Caseが未Testだった（`test_gate_reason_drift_between_evidence_and_current_descriptor_is_denied`を追加）。Major／Critical Findingは無し。実装自体の再修正は発生していない。

## Acceptance（本Package完了時点、変更なし）

```text
PASS             38
PARTIAL           1  # P8-ACC-038
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

## Process Action Inventory

```yaml
network_authority_used: false
install_authority_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
git_mutation_used: false
backup_used: false
project_root_外_access_executed: 0
runtime_data_read_or_written: false
frontend_touched: false
phase_8_closure_claimed: false
phase_9_entered: false
roadmap_touched: false
```

## Exact Next Action

```text
Codex Controller Final Re-review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
成立が確認され次第、User Manual Gate（P8-ACC-040）へ進む。
```
