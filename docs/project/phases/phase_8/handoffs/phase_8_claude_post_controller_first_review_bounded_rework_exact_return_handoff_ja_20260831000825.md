# Phase 8 Claude Post-Controller First Review Bounded Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_20260831000825
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 00:08 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-CR0_through_P8-CR4
入力Handoff: phase_8_claude_post_controller_first_review_bounded_rework_exact_handoff_ja_20260830234754.md
入力Review: phase_8_codex_controller_p8_a_through_p8_f_first_independent_review_ja_20260830234754.md
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_claimed: false
phase_9_entered: false
git_mutation_executed: false
network_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
```

## 1. 結論

Codex Controller第1回Independent Reviewが指摘したFinding 3件（P8-CODEX-001〜003）を、Fresh Task化・Bootstrap再実行・P8-A〜F再実装なしで、Current Working Treeを継続したまま全件是正した。P8-CR0（Entry／Finding Freeze）からP8-CR4（Verification／Internal Review／Return）まで連結実行し、途中停止なし。

```yaml
p8_codex_001_disposition: RESOLVED
p8_codex_002_disposition: RESOLVED
p8_codex_003_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

詳細な経緯・Test構成・Rationaleは本Package付属の以下3文書を参照（本Handoffはその要約と正式なReturn）。

```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_correction_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_bounded_rework_complete_package_recovery_ja_20260831000825.md
```

## 2. P8-CODEX-001〜003 Disposition

### P8-CODEX-001（Concurrent advanceによる同一Tool二重実行）— RESOLVED

`DevAgentRunService`へRun単位`threading.Lock`を導入した（`_lock_for(run_id)`）。`advance`／`submit_approval`／`cancel_run`／`record_late_result`の4つのPublic Methodはいずれも対応する`_xxx_locked()`実装へLock越しに委譲する構造へ変更し、同一Run宛の呼び出し（Tool実行を含む）を全体としてAtomicに直列化する。別Run同士は互いのLockと無関係であり、不要なGlobal Serial化は発生しない。Cross-process／Distributed Lockは実装していない（単一Local Process内Guaranteeのみ、Handoff Non-goal通り）。

Lockを意図的に無効化した状態（`_lock_for`を毎回新規Lockへ差し替える再現実験）でRegression Testが実際に`tool_execute_count: 2`で失敗することを確認し、Testが名目的なものではなく実在するBugを検出できることを実証した。

### P8-CODEX-002（Frozen AuthorizationEnvelope未配線）— RESOLVED

`AuthorizationEnvelope`をSingle-Step-Scopeの装飾型からRun-Scopeの実配線契約へ全面差し替えた。`start_run()`がPlan／Approval Profile／Max Step／Retry Policy／Deadlineから実際にEnvelopeを構築し、`RunSnapshot.envelope`として永続化する。Caller（`DevAgentStartRunRequest`）にはEnvelopeを自由入力できるFieldが存在しない。`advance()`はStep実行直前にRun Identity／Allowed Step／Allowed Tool／Resource Scope／Expiryの5 Legを照合し、不一致は新設`RunCompletionOutcome`値`"authority_denied"`（Architecture§7が既に定義していたFailure語彙）へ収束、Tool Portを一切呼ばない。

新設`ApprovalEvidence`（Run/Step/Tool/Decision/Actor Class/Timestamp/Gate Reason）を`submit_approval()`が承認・却下いずれの決定でも記録し、`RunSnapshot.approvals`として永続化する。Gate判定の真の正本はこのTyped Evidenceであり、既存`StepRecord.approved: bool`はBackward-Compatible Cacheとして残した。Evidenceは`(run_id, step_id, tool_id)`の厳密一致でしか成立しないため、別Step・別Tool・別Runへの再利用は構造的に不可能であることを、Cross-Step・Cross-Run双方のTestで実証した。既存Run Store File（`envelope`/`approvals`キー無し）はCorrupt扱いにならない（両Fieldとも安全なDefault値）。

### P8-CODEX-003（Acceptance集計とUser Manual Gateの誤分類）— RESOLVED

Acceptance集計を次に統一した。

```text
PASS             38
PARTIAL           1  # P8-ACC-038（GD相関、構造的制約により据え置き — 不変）
USER MANUAL GATE  1  # P8-ACC-040（User実画面確認待ち）
TOTAL             40
```

Real MCP／Real Modelは40件のいずれにも数えず、「Authority不足によりNOT RUN」というScope外Boundaryとして別記した。Claude localhost Browser実演はAutomated Candidate EvidenceでありUser Manual Acceptance（P8-ACC-040）の代替にならないことを明記した。Historical P8-D/E/F Recoveryは無改変のまま、Append-only Correction Addendumで訂正内容を記録した。

## 3. Changed Paths

```text
# Backend Source（既存File改修、新規0）
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
src/margpa_runtime_llm/web/dev_agent_contracts.py

# Backend Test（既存File改修4、新規File1）
tests/unit/dev_agent/test_dev_agent_contracts.py
tests/unit/dev_agent/test_run_service.py
tests/unit/dev_agent/test_json_file_run_store.py
tests/integration/dev_agent/test_dev_agent_web_app.py
tests/unit/dev_agent/test_run_service_concurrency.py  # 新規

# Constitution（既存File改修、Manifest Digestは非依存 — 検証済み）
constitution/rules/external-write-requires-human-gate.md

# Docs（新規、Append-only）
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_correction_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_bounded_rework_complete_package_recovery_ja_20260831000825.md
docs/project/phases/phase_8/handoffs/phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_ja_20260831000825.md（本文書）
```

明示的に変更していないもの：`bootstrap/dev_agent.py`／`web/dev_agent_routes.py`／`adapters/dev_agent/*`／`entrypoints/web/main.py`／Frontend全File／Historical P8-D・E・F Recovery本文。

## 4. Concurrency Probe Results

```yaml
regression_reproduction_without_lock:
  tool_execute_count: 2  # Controller実Probeと同型の不整合を再現
after_fix:
  unit_test: test_run_service_concurrency.py::test_concurrent_advance_executes_tool_exactly_once
  tool_execute_count: 1
  repeated_15_runs: all_passed
rest_level:
  test: test_dev_agent_web_app.py::test_concurrent_advance_via_rest_executes_tool_exactly_once
  dispatch: "asyncio.gather(POST advance, POST advance) -> asyncio.to_thread(service.advance) — Production Routeと同一経路"
  tool_execute_count: 1
  repeated_10_runs: all_passed
races:
  advance_vs_cancel: "final state always cancelled, exactly-once execution"
  approval_vs_cancel: "final state always cancelled, loser is no-op or InvalidRunTransitionError"
```

## 5. Authorization Envelope実配線Evidence

`start_run()`が`_issue_envelope()`でRun Identity／Allowed Step IDs／Allowed Tool IDs／Resource Scope（`fixture_only`固定）／Max Step・Attempt／Expiry／Gate Reasonsを実際に構築し`RunSnapshot.envelope`へ永続化。`advance()`が実行直前にRun／Step／Tool／Resource／Expiryの5 Legすべてを照合し、各Legの違反を個別Testで実証（`test_run_identity_mismatch_envelope_is_authority_denied`／`test_step_outside_the_envelope_is_authority_denied_with_zero_executions`／`test_tool_not_authorized_by_envelope_is_authority_denied`／`test_unsupported_resource_scope_is_authority_denied`／`test_expired_envelope_is_authority_denied_even_without_a_run_level_deadline`）。いずれもTool実行0件、`RunCompletionOutcome`は`"authority_denied"`。REST越しにも`envelope`Fieldとして実在を確認できる（`test_start_run_issues_an_authorization_envelope_via_rest`）。

## 6. Approval Evidence Persistence／Restart Evidence

`ApprovalEvidence`（Run/Step/Tool/Decision/Actor Class/Timestamp/Gate Reason）を承認・却下いずれの決定でも記録。Restart後もUnit・REST両Levelで保持を確認（`test_approval_evidence_persists_and_survives_restart`／`test_approval_evidence_is_returned_via_rest_and_survives_restart`）。Cross-Step再利用不可（`test_approval_evidence_for_one_step_never_authorizes_a_different_step`）、Cross-Run再利用不可（`test_approval_evidence_and_envelope_never_cross_runs`）を個別に実証。

## 7. Backward Compatibility Evidence

`envelope: AuthorizationEnvelope | None = None`／`approvals: tuple[ApprovalEvidence, ...] = ()`はいずれも安全なDefault値のため、Pre-P8-CR2のRunSnapshot／Run Store Fileは検証エラーにもCorrupt扱いにもならない。Unit Level（`test_a_run_persisted_before_p8_cr2_has_no_envelope_and_is_not_corrupt`／`test_a_pre_p8_cr2_run_file_without_envelope_or_approvals_is_not_corrupt`）とREST Level（`test_a_legacy_run_without_an_envelope_is_still_advanceable_via_rest`）の双方で、Legacy Runが引き続きAdvance可能であることを確認した。Constitution Rule Prose更新はManifest Digestに影響しないことをConstitution Test Suite（24 passed）で確認した。

## 8. Focused／Canonical Validation

```yaml
backend:
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
```

## 9. Internal Review 1 Cycle — Finding／Rework

Handoff §5〜§7を再読の上、実装Sourceと突き合わせる形で1 Cycle実施し、Test Coverage Gap 4件を自己発見しその場で追加した（先送りなし）：Cross-Run Approval/Envelope再利用拒否のTest欠落、`_envelope_violation()`のRun Identity／Tool（Step Legから分離した形）／Resource Scope各Legの個別Test欠落。実装自体の再修正は発生していない（当初から正しく動作していたが、証拠として不足していた分岐）。Major／Critical Findingは無し。

## 10. Acceptance（本Package完了時点）

```text
PASS             38
PARTIAL           1  # P8-ACC-038（GD相関、Real LLM/Tool Execution段階まで正直にPARTIAL据え置き）
USER MANUAL GATE  1  # P8-ACC-040（User実画面確認待ち）
TOTAL             40
```

## 11. Process Action Inventory

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
p8_a_through_f_reimplemented: false
```

Controller Reviewが既に記録済みのReal Browser／`/tmp` Process Nonconformance（Disposition: RECORDED / NON-BLOCKING）は、本Rework内で再調査していない。本Rework自体はReal Browser・Real Network・Real Model・Real MCPのいずれも使用していない。

## 12. Exact Next Action

```text
Codex Controller Re-review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Phase 8 Closure、Roadmap、Git、Backup、Phase 9のいずれへも進んでいない。
```

Return後は本Handoffの通り停止する。
