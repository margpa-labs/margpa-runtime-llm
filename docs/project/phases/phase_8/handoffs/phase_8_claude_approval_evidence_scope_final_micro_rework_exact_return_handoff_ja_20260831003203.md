# Phase 8 Claude Approval Evidence Scope Final Micro Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_approval_evidence_scope_final_micro_rework_exact_return_handoff_20260831003203
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 00:32 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-CR5_approval_evidence_scope_only
入力Handoff: phase_8_claude_approval_evidence_scope_final_micro_rework_exact_handoff_ja_20260831001957.md
入力Review: phase_8_codex_controller_post_first_rework_re_review_ja_20260831001957.md
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_claimed: false
phase_9_entered: false
git_mutation_executed: false
network_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
frontend_touched: false
```

## 1. 結論

Codex Controller最終再Reviewが指摘したP8-CODEX-004（Approval EvidenceのRun Scope不照合とCompatibility BoolによるGate迂回）を、Fresh Task化・P8-A〜F／P8-CR0〜CR4再実装なしで是正した。P8-CODEX-001〜003・Concurrency Lock・Acceptance集計・Frontendはいずれも無変更。

```yaml
p8_codex_004_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

詳細は本Package付属のRecovery Indexを参照。

```text
docs/project/phases/phase_8/history/index/phase_8_claude_approval_evidence_scope_final_micro_rework_complete_package_recovery_ja_20260831003203.md
```

## 2. P8-CODEX-004 Disposition

### 原因（Controller指摘のまま）

`_has_approval_evidence(run, step)`が`evidence.run_id == run.run_id`を照合していなかった。Gate条件も`not next_step.approved and not _has_approval_evidence(...)`というOR相当構造だったため、Envelope付き新規Runでも`StepRecord.approved=true`単独（Typed Evidence 0件）でGateを通過できた。Controller自身が実Probeで再現：同一Planを持つRun A／Bを作成しRun Aだけを承認、Run Aの型付きEvidenceをRun Bのapprovalsへ移してRun Bをadvance()した結果、`approval_gate_bypassed: true`、`tool_execution: occurred`。

### 是正内容

1. `_has_approval_evidence()`へ`evidence.run_id == run.run_id`の照合を追加。加えて対象ToolにImportant Gate Reasonがある場合、Evidenceの`gate_reason`が現在のDescriptorと一致することも要求する。
2. Gate判定を非対称化：`gate_satisfied = _has_approval_evidence(...)`を算出した上で、`run.envelope is None`（Pre-P8-CR2 Legacy Run）のときだけLegacy Bool`next_step.approved`をORで併用する。Envelope付きRun（P8-CR2以降の全Run）はTyped Evidenceのみで判定される。
3. `RunSnapshot`へ`model_validator`（`validate_approvals_belong_to_this_run`）を追加し、`approvals`内Evidenceの`run_id`が親Runと異なる場合は構築自体を`ValidationError`で拒否する。これはPersistence／REST境界（`__init__`／`model_validate()`）で発火する独立した第2層であり、既存`JsonFileDevAgentRunStore`の「Corrupt File Skip」動作にそのまま乗る（Store自体の変更は不要だった）。
4. `StepRecord.approved`のDocstringを、新しい狭いScope（Legacy Runにのみ効力を持つCompatibility Cache）を正直に反映するよう更新した。虚偽Actor／Timestamp／Gate Reasonを捏造するMigrationは行っていない。

Fix前の状態でController Probeと同一の操作を再現し、実際にGate Bypassが発生する（`counting_port.calls == 1`）ことを確認した上でFixし、Fix後は同一操作が`counting_port.calls == 0`へ収束することを確認した。Fix差し戻し検証後のSourceがdiff上Fix版と完全一致することも確認済み。

## 3. Changed Paths

```text
# Backend Source（既存File改修、新規0）
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py

# Backend Test（既存File改修、新規0）
tests/unit/dev_agent/test_run_service.py       # +6 tests
tests/unit/dev_agent/test_json_file_run_store.py  # +1 test
```

明示的に変更していないもの：`__init__.py`、`web/dev_agent_contracts.py`、`web/dev_agent_routes.py`、`bootstrap/dev_agent.py`、`adapters/dev_agent/*`、`entrypoints/web/main.py`、Concurrency Lock（P8-CR1）、Envelope基本発行・照合Logic（P8-CR2のうちP8-CODEX-004対象外部分）、Acceptance集計文書、Frontend全File。

## 4. Run A Evidence -> Run B Reuse Rejection Evidence

```yaml
runtime_layer:
  test: test_run_service.py::test_transplanted_evidence_from_another_run_is_rejected_and_never_executes
  result: "counting_port.calls == 0"
persistence_layer:
  test: test_json_file_run_store.py::test_a_run_file_whose_approval_evidence_belongs_to_a_different_run_is_skipped
  result: "tampered file skipped, other Runs recovered normally"
contract_layer:
  test: test_run_service.py::test_run_snapshot_rejects_approval_evidence_scoped_to_a_different_run
  result: "ValidationError on construction"
```

## 5. Envelope付きBool-only Bypass Rejection Evidence

```yaml
test: test_run_service.py::test_envelope_having_run_cannot_bypass_the_gate_with_bool_alone
result: "counting_port.calls == 0, re-converges to AWAITING_APPROVAL"
gate_reason_drift:
  test: test_run_service.py::test_gate_reason_drift_between_evidence_and_current_descriptor_is_denied
  result: "counting_port.calls == 0（Evidence自体の内容が現在Descriptorと食い違う場合も拒否）"
```

## 6. Normal Approval / Restart / Legacy Compatibility Evidence

```yaml
normal_approval_and_restart: "既存Test（unit + REST）が無改変でPASS継続"
different_step_or_tool_regression: "既存Testが無改変でPASS継続"
legacy_run_compatibility:
  read: "既存Test PASS継続"
  execute: "新規test_legacy_run_without_an_envelope_still_honors_the_bool_alone — approved=trueのみで実行できることを実証（Over-correctionしていないことの証拠）"
  rest: "既存Test PASS継続"
```

## 7. Focused／Canonical／Mypy／Ruff Results

```yaml
dev_agent_unit_and_integration:
  command: "uv run pytest tests/unit/dev_agent/ tests/integration/dev_agent/ -q"
  result: "84 passed"
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
```

## 8. Internal Review Finding / Rework

Handoff §4／Controller Review §3.3再読の上、実装Sourceと突き合わせ1 Cycle実施。自己発見1件を追加した：Evidenceの`gate_reason`が現在Descriptorと食い違う（Drift）Caseが未Testだった（`test_gate_reason_drift_between_evidence_and_current_descriptor_is_denied`を新規追加）。Major／Critical Findingは無し。実装の再修正は発生していない。

## 9. Process Action Inventory

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
p8_a_through_f_and_cr0_through_cr4_reimplemented: false
concurrency_lock_changed: false
acceptance_summary_changed: false
```

## 10. Acceptance（変更なし）

```text
PASS             38
PARTIAL           1  # P8-ACC-038
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

## 11. Exact Next Action

```text
Codex Controller Final Re-review待ちで停止する。
成立が確認され次第、User Manual Gate（P8-ACC-040）へ進む。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Phase 8 Closure、Roadmap、Git、Backup、Phase 9のいずれへも進んでいない。
```

Return後は本Handoffの通り停止する。
