# Phase 8 Claude Post-Controller First Review Bounded Rework — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-CR (P8-CR0 through P8-CR4)
state: complete
provider: Claude
created_at: 2026-08-31 00:08 JST
handoff_source: phase_8_claude_post_controller_first_review_bounded_rework_exact_handoff_ja_20260830234754.md
review_source: phase_8_codex_controller_p8_a_through_p8_f_first_independent_review_ja_20260830234754.md
```

## 結論

```yaml
p8_cr_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
codex_001_disposition: RESOLVED
codex_002_disposition: RESOLVED
codex_003_disposition: RESOLVED
```

Codex Controller第1回Independent Reviewが指摘したMajor／MVP Blocker 2件（P8-CODEX-001：Concurrent advance二重実行、P8-CODEX-002：AuthorizationEnvelope未配線）とEvidence／Traceability訂正1件（P8-CODEX-003：Acceptance集計とUser Manual Gateの誤分類）を、Fresh Task化・P8-A〜F再実装なしで、Current Working Treeを継続したまま是正した。

## Work Unit別Status

| Work Unit | Status | 備考 |
|---|---|---|
| P8-CR0（Entry／Finding Freeze） | COMPLETE | Handoff・Controller Review・Requirements・Architecture・Acceptance MatrixをSHA-512確認の上、指定順で全文読了。Source直接確認によりExact Changed Pathを決定 |
| P8-CR1（Concurrent Transition Atomicity） | COMPLETE | Run単位`threading.Lock`導入。Required Test 3種（実Thread+Blocking Tool、advance対cancel、Approval対cancel）＋REST Focused Test 1種を追加 |
| P8-CR2（Frozen Authorization Envelope／Approval Evidence） | COMPLETE | Envelope実配線・永続化・照合、Typed Approval Evidence実装。Envelope 5 Leg（Run/Step/Tool/Resource/Expiry）個別Test、Cross-Step／Cross-Run再利用拒否Test、Restart Evidence、Backward Compatibility Testを追加 |
| P8-CR3（Evidence／Current Prose Correction） | COMPLETE | Append-only Correction Addendum・Traceability Addendum作成。Historical P8-D/E/F Recoveryは無改変。Constitution Rule Prose更新（Digest非依存を確認済み） |
| P8-CR4（Verification／Internal Review／Return） | COMPLETE | Backend Canonical 2084 passed / Ruff clean / Mypy clean。Frontend無変更のため再実行省略。Internal Review 1 Cycleで自己発見4件（Cross-Run再利用Test欠落、Envelope 3 Leg — Run Identity／Resource／Expiry — の未Test分岐）をその場で追加 |

## P8-CODEX-001〜003 Disposition（要約）

詳細は本Package付属の`phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md`を参照。

- **P8-CODEX-001**：`DevAgentRunService`へRun単位Lock導入。同一Run宛の`advance`／`submit_approval`／`cancel_run`／`record_late_result`を直列化。別Run同士はGlobal Serial化しない。Cross-process Lockは実装しない（Non-goal通り）。Lock除去下での再現実験（`_lock_for`を毎回新規Lockへ差し替え）でTestが実際に`calls==2`で落ちることを確認済み — Regression Guardとして機能することを実証した。
- **P8-CODEX-002**：`AuthorizationEnvelope`をRun-Scope（Run Identity／Allowed Step IDs／Allowed Tool IDs／Resource Scope／Max Step・Attempt／Expiry／Gate Reasons）へ全面差し替え、`start_run()`内で実際に構築・永続化。`advance()`がStep実行直前にRun／Step／Tool／Resource／Expiryの5 Legを照合し、不一致は新設`RunCompletionOutcome`値`"authority_denied"`（Architecture§7の既存Failure語彙）へ収束、Tool実行0を保証。`ApprovalEvidence`（Run/Step/Tool/Decision/Actor Class/Timestamp/Gate Reason）を新設し、`submit_approval()`が承認・却下いずれもEvidence化。既存`StepRecord.approved: bool`はCompatibility Cacheとして残し、真の正本はEvidence（`_has_approval_evidence()`）とした。既存Run Store Fileは`envelope`/`approvals`未存在でも破損扱いにしない（両Field共にDefault値）。
- **P8-CODEX-003**：Acceptance集計を`38 PASS / 1 PARTIAL(P8-ACC-038) / 1 USER MANUAL GATE(P8-ACC-040) / TOTAL 40`へ統一。Real MCP／Real Modelは40件のいずれにも数えず、Scope外／NOT RUN Boundaryとして別記。Claude localhost Browser実演はAutomated Candidate EvidenceでありUser Manual PASSの代替にならないことを明記。

## Changed Paths

Backend Source（既存File改修、新規0）：
```text
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
src/margpa_runtime_llm/web/dev_agent_contracts.py
```

Backend Test（既存File改修3、新規File1）：
```text
tests/unit/dev_agent/test_dev_agent_contracts.py（改修）
tests/unit/dev_agent/test_run_service.py（改修）
tests/unit/dev_agent/test_json_file_run_store.py（改修）
tests/integration/dev_agent/test_dev_agent_web_app.py（改修）
tests/unit/dev_agent/test_run_service_concurrency.py（新規）
```

Constitution（既存File改修、Digest非依存を確認済み）：
```text
constitution/rules/external-write-requires-human-gate.md
```

Docs（新規、Append-only）：
```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_correction_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_bounded_rework_complete_package_recovery_ja_20260831000825.md（本文書）
docs/project/phases/phase_8/handoffs/phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_ja_20260831000825.md（Exact Return、本Package完了成果）
```

明示的に**変更していない**もの（Preserved COMPLETE、§3に基づく）：
```text
src/margpa_runtime_llm/bootstrap/dev_agent.py
src/margpa_runtime_llm/web/dev_agent_routes.py
src/margpa_runtime_llm/adapters/dev_agent/（fake_tool_adapter.py／json_file_run_store.py／mcp_fixture_adapter.py）
src/margpa_runtime_llm/entrypoints/web/main.py
frontend/（全File）
Historical P8-D/E/F Recovery・Traceability・User Manual Test Sheet・Exact Return Handoff（Append-onlyのみ、本文無改変）
```

## Concurrency Probe Results

```yaml
before_fix_reproduction:
  method: "_lock_for()を毎回新規threading.Lockへ差し替え、実Lock除去状態を再現"
  concurrent_advance_calls: 2
  tool_execute_count: 2
  note: "P8-CODEX-001のController実Probe（tool_execute_count: 2, stored_attempt_count: 1）と同型の不整合を再現。本Rework前のSourceが実際に脆弱であったことの直接確認"
after_fix:
  test: tests/unit/dev_agent/test_run_service_concurrency.py::test_concurrent_advance_executes_tool_exactly_once
  concurrent_advance_calls: 2
  tool_execute_count: 1
  repeated_runs: 15
  flaky: false
rest_level_evidence:
  test: tests/integration/dev_agent/test_dev_agent_web_app.py::test_concurrent_advance_via_rest_executes_tool_exactly_once
  dispatch_path: "asyncio.gather(POST .../advance, POST .../advance) -> Route -> asyncio.to_thread(service.advance)"
  tool_execute_count: 1
  repeated_runs: 10
  flaky: false
representative_races:
  advance_vs_cancel: "final state always CANCELLED, tool executed at most once (test_concurrent_advance_vs_cancel_is_deterministic)"
  approval_vs_cancel: "final state always CANCELLED, loser always either no-op or InvalidRunTransitionError (test_concurrent_approval_vs_cancel_is_deterministic)"
```

## Authorization Envelope実配線Evidence

```yaml
issued_at: start_run()内 `_issue_envelope()`
persisted_with: RunSnapshot.envelope
caller_widenable: false  # DevAgentStartRunRequestにEnvelope-shaped Fieldなし
checked_at: "advance()内、_execute()呼び出し直前"
checked_legs: [run_identity, step_id, tool_id, resource_scope, expires_at]
violation_outcome: "authority_denied"
violation_tool_executions: 0
tests:
  - test_start_run_issues_a_frozen_envelope_matching_the_plan
  - test_step_outside_the_envelope_is_authority_denied_with_zero_executions
  - test_run_identity_mismatch_envelope_is_authority_denied
  - test_tool_not_authorized_by_envelope_is_authority_denied
  - test_unsupported_resource_scope_is_authority_denied
  - test_expired_envelope_is_authority_denied_even_without_a_run_level_deadline
  - test_start_run_issues_an_authorization_envelope_via_rest
```

## Approval Evidence Persistence／Restart Evidence

```yaml
evidence_fields: [run_id, step_id, tool_id, decision, actor_class, decided_at, gate_reason]
recorded_for: [APPROVED, DENIED]
source_of_truth: ApprovalEvidence  # StepRecord.approved は Compatibility Cache
cross_step_reuse: rejected  # test_approval_evidence_for_one_step_never_authorizes_a_different_step
cross_run_reuse: rejected  # test_approval_evidence_and_envelope_never_cross_runs
restart_survival:
  unit_level: test_approval_evidence_persists_and_survives_restart
  rest_level: test_approval_evidence_is_returned_via_rest_and_survives_restart
```

## Backward Compatibility Evidence

```yaml
legacy_run_snapshot_missing_envelope_and_approvals:
  validates: true
  test: test_a_run_persisted_before_p8_cr2_has_no_envelope_and_is_not_corrupt
legacy_json_store_file_missing_envelope_and_approvals_keys:
  treated_as_corrupt: false
  test: test_a_pre_p8_cr2_run_file_without_envelope_or_approvals_is_not_corrupt
legacy_run_still_advanceable_via_rest:
  test: test_a_legacy_run_without_an_envelope_is_still_advanceable_via_rest
constitution_manifest_digest:
  affected_by_rule_prose_edit: false
  verified_by: "tests/unit/constitution/, tests/integration (constitution-tagged) — 24 passed"
```

## Focused／Canonical Validation

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2084 passed, 7 deselected"
ruff:
  command: "uv run ruff check ."
  result: "All checks passed"
mypy:
  command: "uv run mypy src/"
  result: "Success: no issues found in 344 source files"
frontend:
  changed: false
  reexecuted: false
  reason: "P8-CR0-CR4はBackend Source／Testのみを変更対象とした。Frontend Sourceに変更が無いためP8-CR4の指示通り再実行を省略した"
```

## Internal Review 1 Cycle — Finding／Rework

Handoff §5-§7の要件を再度読み直し、実装Sourceと突き合わせた結果、次の4件のTest Coverage Gapを自己発見しその場で追加した（先送りしていない）：

1. `test_approval_evidence_and_envelope_never_cross_runs`：Codex Finding原文の「別Run...への再利用を拒否する」を、Step単位のTestだけでなくRun単位でも明示的に実証するTestが欠けていた。
2. `test_run_identity_mismatch_envelope_is_authority_denied`：`_envelope_violation()`のRun Identity Legが未Test（構造的に到達しない分岐であり、Envelope Field自体の存在証明にしかならない懸念があったため追加）。
3. `test_tool_not_authorized_by_envelope_is_authority_denied`：Tool LegをStep Legから独立してTestするCaseが欠けていた（元のTestはStep/Tool両方を同時に落とすため、どちらのCheckが実際に発火したか厳密には未分離だった）。
4. `test_unsupported_resource_scope_is_authority_denied`：Resource Scope Legが未Test（`SUPPORTED_RESOURCE_SCOPES`が閉じた1値集合であるため通常経路では到達しないが、Architecture・Handoffが明示的にResourceを検証対象へ含めているため、分岐自体の動作を実証する必要があると判断）。

Major／Critical Findingは無し。上記4件はいずれもTest Coverage Gap（実装自体は当初から正しく動作していた）であり、実装の再修正は発生していない。

## Acceptance（本Package完了時点、40件中）

```text
PASS             38
PARTIAL           1  # P8-ACC-038（GD相関、Phase 8 Foundationの構造的制約により据え置き — 不変）
USER MANUAL GATE  1  # P8-ACC-040（User実画面確認待ち）
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
phase_8_closure_claimed: false
phase_9_entered: false
roadmap_touched: false
```

## Exact Next Action

```text
Codex Controller Re-review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Phase 8 Closure、Roadmap、Git、Backup、Phase 9のいずれへも進んでいない。
```
