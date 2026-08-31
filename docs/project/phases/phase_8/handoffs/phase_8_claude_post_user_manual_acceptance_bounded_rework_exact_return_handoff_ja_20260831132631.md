# Phase 8 Claude Post-User-Manual Acceptance Bounded Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_return_handoff_20260831132631
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 13:26 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-MR0_through_P8-MR6
入力Handoff: phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_handoff_ja_20260831122257.md
入力Handoff_sha512: 37c5bc5490533139f5c1d5413f7364382afdd5797aa3103ee56f82aeccda02bafe67c00d30986aabcf35aade214c9982a3ff18ca3c40e741d878b54d03d8a408
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
phase_8_closure_claimed: false
phase_9_entered: false
git_mutation_executed: false
git_read_executed: false
network_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
user_runtime_data_touched: false
```

## 1. 結論

2026-08-31 User Mac Manual AcceptanceのSegment 1〜5で再現した6件のFinding（P8-MANUAL-001〜006）を、
Fresh Task化・過去Package（P8-A〜F／P8-CR／P8-RW6／7）の再実装なしで全て解消した。Internal Review（1 Cycle、
Requirement／Negative Path／Security Boundary／Persistence／UI Truthfulness／Acceptanceの6観点）で新規に
1件のCritical/Major相当の欠陥（`FixtureWorkspaceToolPort`の未捕捉例外Risk）を発見し、同一Package内でReworkした。

```yaml
p8_manual_001_disposition: RESOLVED
p8_manual_002_disposition: RESOLVED
p8_manual_003_disposition: RESOLVED
p8_manual_004_disposition: RESOLVED
p8_manual_005_disposition: RESOLVED
p8_manual_006_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

## 2. Preserved Baseline and Regression Statement

Phase 7 Local Corpus／RAG／Citation／Data Controls／Conversation Persistence、Branch Data／API／既定非表示、
Direct URL OFF／SSRF／Redirect／Timeout／Size／Content-Type安全境界、`example.org`のFetch／Citation Digest／
Untrusted／Reload／Restart、Loopback／Private／Link-local／Metadata／Dangerous Port拒否、Constitution Manifest／
Revision／Digest／3-Mode Semantics／Production OFF、Dev Agent Stable Capability ID／Run／Step／Concurrency／
Budget／Envelope／Approval Evidence／Completion Gate／Cancel／Late Result拒否——いずれも未再実装・未Rollback。
Backend Full Suite（2167件）・Frontend Full Suite（315件）が全通過し、Regressionは検出されなかった。

## 3. Finding別Disposition

詳細はRecovery Index §3を参照。要約：

```text
P8-MANUAL-001  Manual URL Reliability／Fail-closed Grounding      RESOLVED
P8-MANUAL-002  Web Citation Required Metadata                     RESOLVED
P8-MANUAL-003  Archive Sidebar／Panel State Synchronization        RESOLVED
P8-MANUAL-004  Constitution Mode／Decision Layout                  RESOLVED
P8-MANUAL-005  Dev Agent Traceable Fixture／Informed Approval      RESOLVED
P8-MANUAL-006  Dev Agent Button Contrast                           RESOLVED
```

P8-MANUAL-001の中心修正（Fail-closed Grounding）は、User Manual Web Segment 1で再現した「阿部寛」バグ
（URL取得失敗にもかかわらずModelが未取得Pageに基づかない人物説明を生成した）を直接修正するものであり、
本Package最大の安全性修正である。P8-MANUAL-005の中心修正（Step Input REST投影）は、Blind Approval
（承認前にTarget Path／Write Contentが一切見えない）というUser指摘の直接修正である。

## 4. Changed Paths

Recovery Index §4を参照（Backend Source 15件、Backend Test 7件、Frontend 12件）。

## 5. Focused／Canonical Verification

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2167 passed, 7 deselected"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "本Packageの変更Fileは全てClean。Package外の既存5 Fileに手を付けていない旧来のFormat Driftが残るが、本Reworkの対象外（詳細はRecovery Index §5）。"
mypy:
  result: "Success: no issues found in 346 source files"
frontend_full_suite:
  command: "npm test -- --run"
  result: "315 passed (33 files)"
frontend_typecheck_lint_build:
  result: clean
```

## 6. Network／User runtime_data／Real Browser／Real Model Action Count

```yaml
network_authority_used: false
real_network_calls_made: 0
user_runtime_data_read: 0
user_runtime_data_written: 0
real_browser_used: false
real_model_used: false
real_mcp_used: false
git_commands_executed: 0
```

Web関連の全新規Testは`httpx.MockTransport`／`socket.getaddrinfo`のMonkeypatch／Injected `sleep_fn`で完結し、
実Networkに一切到達していない。Dev Agent関連の全新規Testは`tmp_path`（pytest標準Fixture）を`runtime_data_root`
として使用し、User実際の`runtime_data/`には一切触れていない。

## 7. Internal Review Finding Ledger

Requirement／Negative Path／Security Boundary／Persistence／UI Truthfulness／Acceptanceの6観点で1 Cycle実施。

```yaml
requirement:
  finding: none
  note: "P8-REQ-024の「Fake／Deterministic Toolまたは安全な限定Local Tool」という選択的文言により、FixtureWorkspaceToolPortへの移行は要件逸脱ではないことを確認した。"
negative_path:
  finding: 1
  severity: major
  summary: "FixtureWorkspaceToolPort.execute()が、既存Directoryと衝突するWrite Pathで発生するIsADirectoryErrorを無防備に伝播し、DevAgentRunService.advance()（Tool呼出し箇所に元々try/exceptなし）を経由して未捕捉例外がRESTへ到達し得た。"
  disposition: fixed_in_this_package
  fix: "execute()全体をtry/except OSErrorで覆い、ToolExecutionFailed(reason=\"workspace_io_error\")へ収束するよう修正。実際に例外を再現してから修正後にFailしないことを確認し、専用Regression Testを追加した。"
security_boundary:
  finding: none
  note: "Fixture Workspace Adapterの Absolute Path／..／Symlink／Root Escape拒否、Owner-only 0700/0600、Atomic Writeを既存JsonFileDevAgentRunStoreと同水準で確認した。Manual URL Security Boundary（validate_url_before_connect）は無変更、Retryは安全検査後の許可されたURLに対してのみ適用される。"
persistence:
  finding: none
  note: "Dev Agent側はStepRecord.input/outputという既存Field(Backend Contract無変更)をREST投影しただけであり、Persistence Schemaへの影響は0。Web CitationはSchema Version 2->3のBumpのみで、既存のCorrupt-record Fallbackが後方互換性をカバーする。"
ui_truthfulness:
  finding: 1
  severity: minor_editorial
  summary: "devAgentNoteの文言（「実File・実Networkには一切触れない」）が、実File Adapterへの移行後は虚偽になる状態だった。"
  disposition: fixed_in_this_package
  fix: "「Fixture Workspace限定の実Fileを扱うが、Project SourceとNetworkには一切触れない」へ訂正した。"
acceptance:
  finding: none
  note: "Acceptance Disposition Addendumで36項目を再導出し、Regressionは検出されなかった。P8-ACC-038はPreserved BaselineとしてPARTIALのまま維持、P8-ACC-040はUser Manual Gateのまま維持。"
critical_or_major_found_and_reworked: 1
rework_performed_in_this_cycle: "FixtureWorkspaceToolPort.execute()のOSError安全網、devAgentNote文言訂正"
```

## 8. Acceptance Disposition Addendum

```text
docs/project/phases/phase_8/operations/phase_8_post_manual_acceptance_bounded_rework_acceptance_disposition_addendum_ja_20260831132631.md
```

Frozen Acceptance Matrix（40項目）は書き換えていない。Addendum内で36項目（Handoff §11指定Scope）を再導出し、
PASS 34／PARTIAL 1（P8-ACC-038、Preserved Baseline）／USER MANUAL GATE 1（P8-ACC-040）という結果を得た。

## 9. User Manual Recheck Sheet

```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_user_manual_acceptance_recheck_sheet_ja_20260831132631.md
```

6件のFindingだけを対象にした差分Recheck手順書。Phase 7既存経路やP8-A〜Fの成立済み経路の再確認は不要な設計。

## 10. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_user_manual_acceptance_bounded_rework_recovery_ja_20260831132631.md
```

## 11. Process Action Inventory

```yaml
network_authority_used: false
install_authority_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
git_read_or_write_used: false
backup_used: false
project_root_外_access_executed: 0
runtime_data_read_or_written: false
phase_8_closure_claimed: false
phase_9_entered: false
roadmap_touched: false
archive_full_delete_or_bulk_or_export_implemented: false
real_dev_agent_project_file_tool_implemented: false
general_search_provider_implemented: false
production_constitution_activation_touched: false
```

## 12. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK。
User Manual PASS、Phase 8 Closure、General Web Search、Formal Dev Agent Level 1、Phase 9 Readyの
いずれもClaimしていない。
Codex ControllerのReview完了後、User Manual Recheck Sheetを用いたUser実画面再確認が必要。
```

Return後は本Handoffの通り停止する。
