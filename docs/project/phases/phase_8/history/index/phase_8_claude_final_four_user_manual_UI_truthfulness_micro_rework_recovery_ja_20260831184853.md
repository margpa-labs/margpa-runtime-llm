# Phase 8 Final Four User Manual UI／Truthfulness Micro Rework — Recovery Index

```yaml
document_id: phase_8_claude_final_four_user_manual_ui_truthfulness_micro_rework_recovery_20260831184853
document_type: recovery_index
document_state: frozen
language: ja
created_at: 2026-08-31 18:48 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
execution_scope: P8-MR9-0_through_P8-MR9-4
入力Exact_Handoff: phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_exact_handoff_ja_20260831181553.md
入力Exact_Handoff_sha512: 949b2804f6070f41449386d1c3891bcc045e4ffce97d2b51e0d42b0ae5ecff4ccd83d16ec1c424ce5412ed33b67936377d802c4f6403be4461bc8a5f10bdfc57
対象Finding: P8_MANUAL_FINAL_001_through_004
```

## 1. 完了状態サマリ

```yaml
p8_manual_final_001_disposition: RESOLVED
p8_manual_final_002_disposition: RESOLVED
p8_manual_final_003_disposition: RESOLVED
p8_manual_final_004_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
major_open: 0
internal_review_rework_performed: 0
maximum_claim: COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK
```

## 2. Mandatory Differential Reading — Digest確認結果

```yaml
user_mac_post_mr8_evidence:
  path: docs/project/phases/phase_8/history/operations/phase_8_user_mac_post_mr8_full_manual_acceptance_and_behavior_evidence_ja_20260831181553.md
  sha512_match: true
latest_exact_return:
  path: docs/project/phases/phase_8/handoffs/phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_return_handoff_ja_20260831150330.md
  sha512_match: true
latest_recovery:
  path: docs/project/phases/phase_8/history/index/phase_8_claude_manual_url_final_two_blockers_micro_rework_recovery_ja_20260831150330.md
  sha512_match: true
current_unresolved_registry:
  path: docs/project/shared/未解決/current_unresolved_findings_registry_ja.md
  sha512_match: true
```

4文書とも指定Digestに一致。Digest不一致はなく、Current Working TreeをCanonical Baselineとしてそのまま
P8-MR9-0からP8-MR9-4まで連結実行した。

## 3. Finding別詳細

### 3.1 P8-MANUAL-FINAL-001 — Completion Gate Truthfulness（UF-P8-003／P8-CODEX-011）

根本原因：`DevAgentPanel.tsx`のCompletion Gate表示（`awaitingCompletion`分岐）が、Runtime Contract上
`CompletionApprovalEvidence.gate_reason: Literal[ImportantGateReason.COMPLETION]`で常に`completion`固定と
定義されているにもかかわらず、`run.envelope.gate_reasons`（直前の`write_note` Tool Gateの凍結Envelopeに
残った`external_write`）をそのまま参照・表示していた。User Mac実画面Evidence（§6.3）が実測した
`Gate Reason: external_write`という虚偽表示を再現した。

実装：Module定数`COMPLETION_GATE_REASON: DevAgentImportantGateReason = "completion"`を追加し、
Completion Gateの表示を`run.envelope.gate_reasons`から切り離して常にこの定数を表示するよう変更した。
Tool Gate（`awaitingStep`分岐）側は無変更——`external_write`表示、`external_write` Tool Gateの削除、
Approval Engine／Authorization Envelope／Completion Transition／Persistence Schemaの作り直しは一切行って
いない（Handoff §6.2 Non-goalどおり）。Backend変更は不要だった。

Regression Guard：修正を一時的に元へ戻し（Completion Gateが再び`run.envelope.gate_reasons`を参照する形へ）、
新規Testが実際にController／User Evidenceと同じ`external_write`誤表示でFailすることを確認してから復元、
diff一致を確認した。

### 3.2 P8-MANUAL-FINAL-002 — Current Composer Web Failure Lifecycle（UF-UI-011／P8-CODEX-011）

調査：Composer最下部の状態文言（`App.tsx`の単一`status`State、`Composer`の`#generation-status`）を
起点に、Chat切替・新規Chat・成功した次Turnの3経路を個別に検証した。

- 新規Chat（`createPersistentConversationAndSelect()`）：作成成功時に既に`setStatusKey("idle")`を
  呼んでおり、Composer警告は既に消えることをTestで確認した（Source変更不要）。
- 成功した次Turn（`handlePersistentEvent`の`completed`分岐）：Turn開始時の`setStatusKey("connecting")`
  →`"generating"`、成功終了時の`setStatusKey("completed", ...)`が既に無条件で古い警告を上書きすることを
  Testで確認した（Source変更不要）。
- Chat切替（`selectPersistentConversation()`）：他の2経路と異なり、Status Resetを一切呼んでいなかった。
  別Conversationへ切り替えても直前のTurnの`serverWarning` Statusがそのまま残留する——User Mac実画面
  Evidence（§8）が報告した実際の不具合の根本原因はここだった。

実装：`selectPersistentConversation()`へ`terminalWarningRef.current = null`と`setStatusKey("idle")`を
追加した。`openArchivedChat()`は内部で本Functionを呼ぶため同じ修正が自動的に適用される。Historical
Failure Turn自体は`messages`/`turns`（`loadPersistentDetail`によるServer Canonical Reload）が保持する
別の状態であり、この修正では一切変更していない——Chat切替後に同じ失敗Conversationへ戻っても、
Historical Bubbleは元のまま表示され、Composer警告だけが再表示されないことをTestで確認した。

Regression Guard：新規Test 3件（Chat切替／新規Chat／成功した次Turン）をまず実装した状態で実行し、
Chat切替のTestだけが実際に古い警告文言を含んだままFailすることを確認した（新規Chatと成功した次Turンは
Source変更前から最初からPASSした——既存実装が既に正しかったことの直接証拠）。`selectPersistentConversation()`
の修正後、3件全てPASSすることを確認した。

### 3.3 P8-MANUAL-FINAL-003 — Untrusted External Content文字色統一（UF-UI-012）

根本原因：`.web-search-panel-untrusted-label`（`WebCitationsSection.tsx`のChat Citation Cardと
`WebSearchPanel.tsx`のSettings Direct URL Previewが共有するClass）に対応するCSS Ruleがapp.css内に
一件も存在せず、周囲のAmbient Text Color（祖先要素依存）をそのまま継承していた。Citation Card内の他の
全FieldはToken化された`--citation-label`／`--citation-text`（緑系）を明示指定しているため、Untrusted
Labelだけが視覚的に浮いて見えていた。

実装：`--citation-label`／`--citation-accent`（緑、Citation Cardの"正当な証拠"を示す配色）を転用せず、
既にApp全体でCaution／Warning Semanticsとして再利用されている既存Token`--gauge-warn`
（`.dev-agent-run-error`／`.dev-agent-run-step-error`と同じToken）を採用した。Untrusted＝注意喚起という
意味を緑（Trusted相当の配色）へ寄せることなく、かつ新しいAd-hoc Colorも作らずLight／Dark両Themeで
可読な色へ統一した。文言・意味は無変更。

Test：`WebCitationsSection.test.tsx`／`WebSearchPanel.test.tsx`の既存Testを拡張し、Untrusted Label要素が
`web-search-panel-untrusted-label` Classを持つことを明示Assertした（jsdom環境はCSS Custom Propertyの
解決値を検証できないため、本Repository内の既存慣例——Button Contrast等も同様にClass名Assertionで
検証している——に倣った）。

### 3.4 P8-MANUAL-FINAL-004 — New Demo Run Button色統一（UF-UI-013）

根本原因：`#dev-agent-reset`（Completed／Cancelled後の「新しいDemo Runを開始」Button）だけが
`className="secondary"`を使用しており、同じ動作を行う初期の「Start Run」Button（`#dev-agent-start-run`、
`className="primary"`）と視覚的に不統一だった。

実装：`#dev-agent-reset`のClassを`"secondary"`から`"primary"`へ変更した。新しいButton Design Systemまたは
専用Hard-code Colorは作らず、既存の`.primary` Classをそのまま再利用した。

Regression Guard：一時的にClassを`"secondary"`へ戻し、既存2 Test（Complete経路／Cancel経路）が実際に
`toHaveClass("primary")`でFailすることを確認してから復元、diff一致を確認した。

## 4. Changed Paths

```text
# Frontend Source
frontend/src/App.tsx
frontend/src/components/DevAgentPanel.tsx
frontend/src/styles/app.css

# Frontend Test
frontend/src/App.test.tsx
frontend/src/components/DevAgentPanel.test.tsx
frontend/src/components/WebCitationsSection.test.tsx
frontend/src/components/WebSearchPanel.test.tsx

# 配信用Static Artifact（`npm run build`再生成）
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
```

Backend Source／Testは本Package内で一切変更していない。P8-CODEX-013〜020、P8-MANUAL-002〜006、
既存UI（Archive／Citation本体構造／Constitution Preview／Dev Agent Foundation）、Local Corpusのいずれも
再実装・Rollbackしていない。

## 5. Focused／Canonical Verification

```yaml
p8_manual_final_001_regression:
  test: "DevAgentPanel > the full Gate -> Approve -> Complete flow works end to end from the screen"
  assertion: "completion-gate textContent contains 'completion', not 'external_write'"
  result: pass
p8_manual_final_002_regression:
  tests:
    - "switching to another Chat clears a stale Web Failure warning... (App.test.tsx)"
    - "starting a New Chat clears a stale Web Failure warning... (App.test.tsx)"
    - "a successful next Turn clears a stale Web Failure warning... (App.test.tsx)"
  result: all 3 pass
p8_manual_final_003_regression:
  tests:
    - "WebCitationsSection: renders the Canonical URL, Public Web Source label, and Untrusted label"
    - "WebSearchPanel: fetched Search evidence is explicitly labelled Untrusted External Content"
  result: both pass (Class Assertion — jsdomはComputed CSS Custom Propertyを検証できないためCode
    Inspectionと併用)
p8_manual_final_004_regression:
  tests:
    - "DevAgentPanel: the full Gate -> Approve -> Complete flow works end to end from the screen"
    - "DevAgentPanel: Cancel finalizes the Run from the screen"
  result: both pass
frontend_typecheck:
  command: "npx tsc --noEmit"
  result: clean
frontend_lint:
  command: "npx eslint ."
  result: clean
frontend_full_test:
  command: "NODE_OPTIONS=--no-webstorage npx vitest run"
  result: "318 passed (33 test files)"
frontend_build:
  command: "npm run build"
  result: "built in 88ms — app.css 22.38kB, app.js 366.57kB, index.html 1.14kB"
static_artifact_updated: true
backend_full_suite: not_rerun_no_backend_source_changed
mypy: not_rerun_no_backend_source_changed
ruff_check: not_rerun_no_backend_source_changed
ruff_format_check: not_rerun_no_backend_source_changed
regression_guard_verification:
  method: >-
    4件全てについて、実際にFail-fastする状態（修正の一時的Revert）を再現し、新規／拡張Testが
    Controller／User Evidenceと同じ症状で実際にFailすることを確認してから復元し、diffで完全一致を
    確認した。
```

## 6. Internal Review Finding Ledger

Requirement／State Lifecycle／UI Truthfulness／Regressionの4観点で1 Cycle実施。

```yaml
requirement:
  finding: none
  note: >-
    P8-MANUAL-FINAL-001〜004の4件だけをHandoff §6〜§8のRequired Behaviorどおりに解消したことを
    本Index §3で確認した。それ以外の未解決（Model Call 0 Observability、Shift_JIS、Settings結果残留、
    Manual URL Card整理、通常Composer本文URL、Archive Modal、False-positive RAG、Semantic Governance、
    General Search、Full Web Hardening）には一切着手していない。
negative_path:
  finding: none
  note: >-
    Completion GateはTool Gate（`external_write`表示）を無変更のまま維持し、Completion Gate自体だけを
    修正した。Composer Warning Lifecycleは、同一Turn内の警告（Ephemeral経路の`terminalWarningRef`）と
    Persistent経路のCompleted上書きロジックを無変更のまま、Chat切替時のReset漏れだけを追加した——
    「同じCurrent AttemptがFailureへ到達した直後は警告を表示」という保持すべき挙動を壊していないことを
    既存Test（token-limit warning Test）が引き続きPASSすることで確認した。
ui_truthfulness:
  finding: none
  note: >-
    Completion Gateはもう`external_write`を偽って表示しない。Composer警告はもう別Conversation／新規
    Attemptの状態として誤って居座らない。Untrusted LabelはUntrustedという意味を保持したまま可読色へ
    統一され、Trusted相当の配色（Citation Cardの緑）へは寄せていない。New Demo Run Buttonは同じ動作を
    行うStart Run Buttonと同格のPrimary表示になり、劣った操作であるかのような誤った視覚的示唆を
    解消した。
regression:
  finding: none
  note: >-
    Frontend Full Test 318件全PASS（Typecheck／Lint Clean、Build成功、配信用Static Artifact更新済み）。
    Backend Sourceは無変更のためBackend Full／Mypy／Ruffは未実行（Handoff §9.4指示どおり）。
critical_or_major_found_and_reworked: 0
minor_optimization_applied: none
```

## 7. Process Action Inventory

```yaml
git_read_or_write_executed: false
network_used: false
install_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
backup_used: false
project_root_外_access_executed: 0
runtime_data_read_or_written: false
phase_8_closure_claimed: false
roadmap_touched: false
phase_9_entered: false
p8_codex_013_through_020_reimplemented: false
p8_manual_002_through_006_reimplemented: false
acceptance_matrix_touched: false
```

## 8. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK。
Phase 8 Closure、Acceptance Matrix再集計、Roadmap、Phase 9開始のいずれもClaimしていない。
Controller Review完了後、User実画面での最終再確認（4件のUI Truthfulness）が必要。
```
