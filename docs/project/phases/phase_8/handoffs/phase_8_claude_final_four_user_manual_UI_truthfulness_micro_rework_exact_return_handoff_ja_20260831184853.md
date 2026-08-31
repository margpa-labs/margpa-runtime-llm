# Phase 8 Final Four User Manual UI／Truthfulness Micro Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_final_four_user_manual_ui_truthfulness_micro_rework_exact_return_20260831184853
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 18:48 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-MR9-0_through_P8-MR9-4
入力Exact_Handoff: phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_exact_handoff_ja_20260831181553.md
入力Exact_Handoff_sha512: 949b2804f6070f41449386d1c3891bcc045e4ffce97d2b51e0d42b0ae5ecff4ccd83d16ec1c424ce5412ed33b67936377d802c4f6403be4461bc8a5f10bdfc57
maximum_claim: COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK
phase_8_closure_claimed: false
p8_acc_040_pass_claimed: false
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

User Mac Post-MR8実画面Evidence（2026-08-31 18:15:53 JST）が報告した最後の4件、
P8-MANUAL-FINAL-001（Completion Gate表示の虚偽）、P8-MANUAL-FINAL-002（過去Web Failure警告の
Composer残留）、P8-MANUAL-FINAL-003（Untrusted Label文字色不統一）、P8-MANUAL-FINAL-004（New Demo Run
Button色不統一）を、P8-MR0〜MR8・Manual URL・Archive・Citation・Constitution・Dev Agent Foundation・
Local Corpusの再実装なしで解消した。4件ともFrontend変更のみで完結し、Backend Sourceは無変更である。
Internal Reviewで新規のCritical／Major欠陥は見つからなかった。

```yaml
p8_manual_final_001_disposition: RESOLVED
p8_manual_final_002_disposition: RESOLVED
p8_manual_final_003_disposition: RESOLVED
p8_manual_final_004_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

## 2. Mandatory Differential Reading

指定4文書（User Mac Post-MR8 Evidence、Latest Exact Return、Latest Recovery、Current Unresolved
Registry）を指定順で全文読み、SHA-512を照合した。4文書とも一致し、Digest不一致はなかった。
Current Working TreeをCanonical Baselineとして、そのままP8-MR9-0からP8-MR9-4まで連結実行した。

## 3. Preserved Baseline

P8-MR0〜MR8のSource／Test／Persistence、Manual URL UTF-8 Public Fetch／Retry／Fail-closed Grounding、
HTML本文抽出／Final Prompt-aware Budget／Typed Failure、Web Citation Metadata／Reload／Restart、
Archive／Unarchive／Sidebar／Panel同期、Constitution 3-Mode Semantics／Production OFF、Dev Agent
Run／Step／Budget／Envelope／Approval Evidence／実File Fixture、Local Corpus削除／Current Citation
Freshness、General Keyword Search Fixture境界——いずれも未再実装・未Rollback。

## 4. Finding別Disposition

詳細はRecovery Index §3を参照。要約：

```text
P8-MANUAL-FINAL-001  Completion Gate Truthfulness（DevAgentPanel.tsx、Frontendのみ）        RESOLVED
P8-MANUAL-FINAL-002  Current Composer Web Failure Lifecycle（App.tsx、Frontendのみ）         RESOLVED
P8-MANUAL-FINAL-003  Untrusted External Content文字色統一（app.css、Frontendのみ）           RESOLVED
P8-MANUAL-FINAL-004  New Demo Run Button色統一（DevAgentPanel.tsx、Frontendのみ）            RESOLVED
```

P8-MANUAL-FINAL-001の中心修正は、Completion Gateの表示Sourceを`run.envelope.gate_reasons`（直前のTool
Gateの凍結値）から、Runtime Contract上常に`completion`固定の`COMPLETION_GATE_REASON`定数へ切り替えた
ことである。P8-MANUAL-FINAL-002は、3経路（Chat切替／新規Chat／成功した次Turン）のうち新規Chatと
成功した次Turンは既存実装で既に正しく、Chat切替（`selectPersistentConversation()`）だけにStatus Reset
漏れがあったことをTest-first（先にTestを書き、2件は最初からPASS、1件だけが実際にFailすることを
確認）で特定し、その1箇所だけを最小修正した。P8-MANUAL-FINAL-003／004はいずれもCSS Class／既存Token
の再利用による1行規模の修正である。

## 5. Changed Paths

Recovery Index §4を参照（Frontend Source 3件、Frontend Test 4件、配信用Static Artifact 2件、
Backend変更0件）。

## 6. Focused Frontend Test Result

```yaml
p8_manual_final_001:
  test: "DevAgentPanel > the full Gate -> Approve -> Complete flow works end to end from the screen"
  result: pass
p8_manual_final_002:
  tests:
    - "App > switching to another Chat clears a stale Web Failure warning from the Composer, and switching back does not revive it"
    - "App > starting a New Chat clears a stale Web Failure warning from the Composer"
    - "App > a successful next Turn clears a stale Web Failure warning from the Composer"
  result: all pass
p8_manual_final_003:
  tests:
    - "WebCitationsSection > renders the Canonical URL, Public Web Source label, and Untrusted label"
    - "WebSearchPanel > fetched Search evidence is explicitly labelled Untrusted External Content"
  result: both pass
p8_manual_final_004:
  tests:
    - "DevAgentPanel > the full Gate -> Approve -> Complete flow works end to end from the screen"
    - "DevAgentPanel > Cancel finalizes the Run from the screen"
  result: both pass
regression_guard_verification:
  method: >-
    4件全てについて、実際にFail-fastする状態（修正の一時的Revert）を再現し、新規／拡張Testが
    User Mac Evidenceと同じ症状で実際にFailすることを確認してから復元し、diffで完全一致を確認した。
```

## 7. Frontend Typecheck／Full Test／Lint／Build Result

```yaml
typecheck:
  command: "npx tsc --noEmit"
  result: clean
lint:
  command: "npx eslint ."
  result: clean
full_test:
  command: "NODE_OPTIONS=--no-webstorage npx vitest run"
  result: "318 passed (33 test files), 0 failed"
build:
  command: "npm run build"
  result: "built in 88ms — app.css 22.38kB, app.js 366.57kB, index.html 1.14kB"
```

## 8. Backend変更有無

```yaml
backend_source_changed: false
backend_test_changed: false
backend_full_suite_rerun: not_required_per_handoff_section_9_4
mypy_rerun: not_required_per_handoff_section_9_4
ruff_check_rerun: not_required_per_handoff_section_9_4
ruff_format_check_rerun: not_required_per_handoff_section_9_4
```

Handoff §11「許可」欄が想定していたBackend Typed Contractの最小投影も、4件ともFrontendだけで解決
できたため不要だった。

## 9. Static Artifact更新

```yaml
updated: true
paths:
  - src/margpa_runtime_llm/web/static/app.css
  - src/margpa_runtime_llm/web/static/app.js
build_command: "npm run build (vite build, outDir=../src/margpa_runtime_llm/web/static)"
```

## 10. Internal Review Result

Requirement／State Lifecycle／UI Truthfulness／Regressionの4観点で1 Cycle実施し、新規のCritical／Major
欠陥は発見されなかった（詳細はRecovery Index §6）。Minor最適化の追加適用はなかった。

## 11. Network／Install／Git／Browser／Model／User runtime_data Action Count

```yaml
network_authority_used: false
real_network_calls_made: 0
install_authority_used: false
git_commands_executed: 0
real_browser_used: false
real_model_used: false
real_mcp_used: false
user_runtime_data_read: 0
user_runtime_data_written: 0
```

新規／拡張Testは全て`vi.stubGlobal("fetch", ...)`によるMock Fetchのみで完結し、実Network・実Browser・
実Model・実MCP・User `runtime_data/`のいずれにも一切到達していない。

## 12. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_recovery_ja_20260831184853.md
```

## 13. Exact Return Handoff Path

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_exact_return_handoff_ja_20260831184853.md
```

本ファイル確定後のSHA-512は、Task完了報告の本文（本文外）でCodex Controllerへ提示する。

## 14. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK。
Phase 8 Closure、P8-ACC-040 PASS、Roadmap、Phase 9 READYのいずれも主張していない。
Acceptance Matrixは変更していない——Handoff §9.7の指示どおり据え置いた。
Codex ControllerのReview完了後、User実画面での最終再確認（4件のUI Truthfulness）が必要。
```

Return後は本Handoffの通り停止する。
