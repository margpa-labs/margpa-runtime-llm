# Phase 8 Post-User-Manual Rework Controller Findings — Exact Return Handoff

```yaml
document_id: phase_8_claude_post_manual_rework_controller_findings_bounded_exact_return_handoff_20260831143355
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 14:33 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-MR7-0_through_P8-MR7-6
入力Controller_Review: phase_8_post_user_manual_rework_controller_independent_review_adjust_ja_20260831134826.md
入力Controller_Review_sha512: d00f8f9e27bae53dcb60ebc9eff2131a973a839c4dcc13aa312952d8602801bca8cf009998239cfdbb05830d8a6dfd5d895a80b2d3093dbdc8219659df5b221d
入力Handoff: phase_8_claude_post_manual_rework_controller_findings_bounded_exact_handoff_ja_20260831134826.md
入力Handoff_sha512: 2fe2c909f8b72f9a7156bbf1bb7a97f183bdde9bb086ed32da8924b380378d2697a5abd3ab7faa86a5dca9f2607a7e4cf504c406015fcbab07b1e393f9db9759
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

Codex Controller Independent Review（2026-08-31 13:48:26 JST、判定`ADJUST`）が検出したP8-CODEX-013〜018の
6件を、Fresh Task化・成立済みUI／Archive／Dev Agent Foundation（P8-MANUAL-003〜006、P8-CR系、P8-RW6／7）の
再実装なしで全て解消した。実装過程で2件の真のCritical/Major欠陥（`CommitConversation`のFAILED Turn拒否、
Truncation Notice未考慮のBudget超過）を発見し、同一Package内でReworkした。

```yaml
p8_codex_013_disposition: RESOLVED
p8_codex_014_disposition: RESOLVED
p8_codex_015_disposition: RESOLVED
p8_codex_016_disposition: RESOLVED
p8_codex_017_disposition: RESOLVED
p8_codex_018_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

## 2. Preserved Baseline and Regression Statement

P8-MANUAL-003〜006（Archive Sidebar／Panel同期、Constitution Layout、Dev Agent Traceable Fixture／Informed
Approval、Button Contrast）、P8-CR系Concurrency／Authorization Envelope／Approval Evidence／Budget／Completion
Gate、P8-RW6 Redirect Evidence Truthfulness、P8-RW7 Constitution Preview 3-axis Semantics——いずれも未再実装・
未Rollback。Backend Full Suite（2186件、Controller指摘4件含む）・Frontend Full Suite（315件）が全通過し、
本Package開始前からのRegressionは検出されなかった。

## 3. Finding別Disposition

詳細はRecovery Index §2を参照。要約：

```text
P8-CODEX-013  Resolver Injection／Test Hermeticity                    RESOLVED
P8-CODEX-014  ERROR-terminal Failure Web Evidence Persistence          RESOLVED
P8-CODEX-015  Web Citation Schema 1／2 Backward Compatibility          RESOLVED
P8-CODEX-016  Context-aware Web Evidence Budget／Raw Content Contract  RESOLVED
P8-CODEX-017  User Manual Recheck Sheet Reproducibility                RESOLVED
P8-CODEX-018  Acceptance Disposition Count／Claim Correction           RESOLVED
```

P8-CODEX-013の中心修正（Constructor-level Resolver Injection）は、Controllerが実測した4 Test Failureの
唯一の原因を解消するものであり、`tests/unit/web_knowledge/`の既存Autouse DNS遮断Fixtureが及んでいなかった
`tests/unit/conversation/`の Gapを埋めた。P8-CODEX-014の中心修正（`CommitConversation`のFAILED Turn許可）は、
実装過程で実際に`pydantic.ValidationError`を再現してから発見した真の欠陥であり、単なる引数配線漏れではなく
Domain Contract自体のGapだった。P8-CODEX-016の中心修正（実Token Counterによる二分探索Truncation）は、
User Manual Web Segment 1の「Hololive公式Page」再現（Large HTML Context Failure）と、CJK Content特有の
Token／Character比の高さの両方に対応する。

## 4. Changed Paths

Recovery Index §3を参照（Backend Source 13件、Backend Test 10件、Docs 3件）。

## 5. Focused／Canonical Verification

```yaml
controller_4_focused_tests:
  result: "4 passed in 0.21s"
backend_full_suite:
  command: "uv run pytest -q"
  result: "2186 passed, 7 deselected"
  deselected_reason: "model_smoke marker (addopts), intentional exclusion unrelated to this Package"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "563 files already formatted — the 5 Controller-flagged files are now clean, and no new drift was introduced"
mypy:
  result: "Success: no issues found in 346 source files"
frontend_typecheck_lint_build:
  result: clean
frontend_full_suite:
  result: "315 passed (33 files)"
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

新規Web関連Testは全て`httpx.MockTransport`／Injected `resolver`／`socket.getaddrinfo`をAssertion Errorへ
差し替えるMonkeypatch Guardのいずれかで完結し、実Networkに一切到達していない（Guard自体が「実DNSへ到達したら
Test失敗」という形でNetwork 0を機械的に証明する）。Persistence関連の新規Testは全て`tmp_path`ベースのTemp
SQLiteを使用し、Userの実際の`runtime_data/`には一切触れていない。

## 7. Internal Review Finding Ledger

Requirement／Negative Path／Persistence／Backward Compatibility／Context Budget／Acceptance Claimの6観点で
1 Cycle実施（詳細はRecovery Index §5）。

```yaml
critical_or_major_found_and_reworked: 2
finding_1: "CommitConversationのweb_citation_evidence InvariantがCOMPLETED Turn限定だったため、fail_generation()
  への配線だけではValidationErrorで実際にFailした（Persistence観点）。COMPLETEDまたはFAILEDへ限定的に緩和して修正。"
finding_2: "_bounded_truncate_web_evidence_to_token_budget()の二分探索がTRUNCATION_NOTICEのTokenコストを含めず
  候補をFitさせ、実際の戻り値がBudgetを超過し得た（Context Budget観点、Negative Path）。TRUNCATION_NOTICE込みで
  測定するよう修正。"
```

## 8. Acceptance Correction Addendum

```text
docs/project/phases/phase_8/operations/phase_8_post_manual_rework_controller_findings_acceptance_correction_addendum_ja_20260831143355.md
```

Frozen Acceptance Matrix（40項目）は書き換えていない。P8-ACC-001〜040の全40件を個別に再導出し、
`PASS 38 + PARTIAL 1（P8-ACC-038）+ USER MANUAL GATE 1（P8-ACC-040）= 40`という、Table行数・Frozen Matrix
行数と機械的に一致する集計を得た。

## 9. Corrected User Manual Recheck Sheet

```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_manual_rework_controller_findings_corrected_user_manual_recheck_sheet_ja_20260831143355.md
```

User実構成（`$PWD/runtime_data`／`mac-local-primary`）に合わせた起動Command（初回Migration付き／以後の通常）、
実Scopeに合わせたDev Agent確認Path、Public URL FetchのReal Network使用を正直に明記したSheet。

## 10. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_post_manual_rework_controller_findings_bounded_recovery_ja_20260831143355.md
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
Codex ControllerのReview完了後、Corrected User Manual Recheck Sheetを用いたUser実画面再確認が必要。
```

Return後は本Handoffの通り停止する。
