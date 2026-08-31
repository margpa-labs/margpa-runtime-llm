# Phase 8 Manual URL Final Two Blockers Micro Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_return_handoff_20260831150330
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 15:03 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-MR8-0_through_P8-MR8-3
入力Controller_Single_Review: phase_8_post_mr7_controller_single_review_adjust_ja_20260831144455.md
入力Controller_Single_Review_sha512: 24ef29271a91193e1570ded7635bb18c06a91f5d86f2431796c589bb98d779eac9bc6961e46b367b1eb5a125b71ec3a75186c298a44d21c27a041892bc39bf01
入力Handoff: phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_handoff_ja_20260831144455.md
入力Handoff_sha512: 1a684c5d3df63f7df5b0a841533ea6d043def9fae9bd25c29c9d1fd5158afad53789964b7d7a6b72ed33123f6ab7abcd23671f71d18b42af5c50b45d51d96cfa
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

Codex Controller Single Review（2026-08-31 14:44:55 JST、判定`ADJUST`）がProduction Composition上で
実再現した2件の最終Blocker、P8-CODEX-019（Final Prompt全体でのWeb Evidence Token Budget未成立）と
P8-CODEX-020（Service PreflightのTransient DNS FailureがProvider Retryへ到達しない）を、
P8-CODEX-013〜018・P8-MANUAL-002〜006・Archive／Citation／Constitution Preview／Dev Agent Foundationの
再実装なしで解消した。両方とも、Controllerが実測した失敗の形（`context_limit_exceeded`／
`url_rejected, resolver_calls: 1, fetch_calls: 0`）を実際に再現してから修正し、専用Regression Testで
証明した。Internal Reviewで新規のCritical／Major欠陥は見つからなかった。

```yaml
p8_codex_019_disposition: RESOLVED
p8_codex_020_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

## 2. Preserved Baseline and Regression Statement

P8-CODEX-013〜018（Resolver Injection、ERROR-terminal Persistence、Schema 1/2 Backward Compatibility、
Raw Fetch Contract、Recheck Sheet、Acceptance集計）、P8-MANUAL-002〜006、P8-CR系、P8-RW6／7——いずれも
未再実装・未Rollback。Acceptance集計（38 PASS／1 PARTIAL／1 USER MANUAL GATE = 40）も根拠なく再集計して
いない。Backend Full Suite（2191件）が全通過し、本Package開始前からのRegressionは検出されなかった。

## 3. Finding別Disposition

詳細はRecovery Index §2を参照。要約：

```text
P8-CODEX-019  Final Prompt-aware Web Evidence Budget（Expressive／Context Usage Notice考慮） RESOLVED
P8-CODEX-020  End-to-end Transient DNS Retry（Service Preflight -> Provider Retry）           RESOLVED
```

P8-CODEX-019の中心修正は、Web Evidence注入前に後置Notice分のToken数を実Counterで先読みしてReserveする
`_reserved_tokens_for_post_evidence_notices()`であり、既存の`content_budget_exceeded`分岐（P8-MR7-4）を
そのまま再利用する形で組み込んだ——新しいRaise分岐は不要だった。P8-CODEX-020の中心修正は、
`HttpxWebFetchProvider`と対称的なBounded Retry LoopをService自身のPreflight Validation呼び出しへ追加した
`_validate_url_with_retry()`であり、`search_and_fetch()`と`fetch_direct_url()`の両方の呼び出し箇所を
統一的に置き換えた。

## 4. Changed Paths

Recovery Index §3を参照（Backend Source 2件、Backend Test 2件）。

## 5. Mandatory Regression Result

```yaml
p8_codex_019:
  test: test_manual_web_evidence_cjk_content_fits_8192_with_notices_enabled
  condition: "effective_context_size=8192, max_new_tokens=128, Long CJK Web Content, ExpressiveMode=ENABLED, ContextUsagePromptInjectionMode=ENABLED"
  result: "Terminal=COMPLETED, Final Prompt Tokens + Max New Tokens <= 8192, context_limit_exceeded ERROR count = 0"
  zero_room_test: test_manual_web_evidence_content_budget_exceeded_when_notices_leave_zero_room
  zero_room_result: "content_budget_exceeded, Model Call 0 (inference.requests == [])"
p8_codex_020:
  test: test_fetch_direct_url_retries_a_transient_preflight_dns_failure_end_to_end
  result: "Resolver 1st call = socket.gaierror, subsequent call = Public IP, Result = successful Citation, real socket.getaddrinfo never called"
  permanent_test: test_fetch_direct_url_permanent_private_address_rejection_makes_zero_provider_calls
  permanent_result: "Provider Call 0, resolver_calls == 1"
```

## 6. MR7 Focused Regression Result

Controllerの6 Test（MR7 Context Budget 4経路、Httpx Provider Transient DNS Retry、Service Resolver
Injection）はBackend Full Suiteに含まれ、全通過を確認した。

## 7. Backend Full／Mypy／Ruff Result

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2191 passed, 7 deselected"
  deselected_reason: "model_smoke marker, intentional, unrelated to this Package"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "563 files already formatted"
mypy:
  result: "Success: no issues found in 346 source files"
frontend:
  note: "Frontend Source変更0のため、Frontend Full再実行は行っていない（Handoff §8.5どおり）。"
```

## 8. Network／User runtime_data／Real Browser／Real Model Action Count

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

新規Testは全て`socket.getaddrinfo`をAssertion Errorへ差し替えるMonkeypatch Guard、または`FakeInference`
経由で完結し、実Networkに一切到達していない。`sleep_fn`のInjectionにより、Retry Testも実待機なしで
即座に完了する。

## 9. Internal Review Result

Requirement／Negative Path／Composition／Regressionの4観点で1 Cycle実施し、新規のCritical／Major欠陥は
発見されなかった（詳細はRecovery Index §5）。実装中に見つけた1件のMinor最適化（Web Evidence未使用Turnでの
無駄なToken Counter呼び出しSkip）は同Package内で反映した。

## 10. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_manual_url_final_two_blockers_micro_rework_recovery_ja_20260831150330.md
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
p8_codex_013_through_018_reimplemented: false
p8_manual_002_through_006_reimplemented: false
acceptance_recount_performed: false
```

## 12. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK。
User Manual PASS、Phase 8 Closure、Phase 9 Readyのいずれも主張していない。
Codex ControllerのReview完了後、User実画面再確認（Corrected User Manual Recheck Sheet、P8-MR7成果物）が
必要。
```

Return後は本Handoffの通り停止する。
