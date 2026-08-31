# Phase 8 Claude ゼロベースController Blocker限定Rework（P8-RW6-0〜E）— Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-RW6-0_through_E
state: complete
provider: Claude
created_at: 2026-08-31 03:56 JST
handoff_source: phase_8_claude_zero_based_controller_blockers_bounded_exact_handoff_ja_20260831005304.md
review_source: phase_8_codex_controller_zero_based_second_full_re_review_ja_20260831004652.md
```

## 結論

```yaml
p8_rw6_established: true
mvp_blocker_open: 0
critical_open: 0
codex_005_disposition: RESOLVED
codex_006_disposition: RESOLVED
codex_007_disposition: RESOLVED
codex_008_disposition: RESOLVED
codex_009_disposition: DEFERRED_PER_HANDOFF_SCOPE
codex_010_disposition: DEFERRED_PER_HANDOFF_SCOPE
```

Codex Controllerゼロベース第2回全体再Reviewが指摘した4 Major Findingを全て解消した。P8-CODEX-001〜004・Concurrency Lock・既存Acceptance成立範囲は無変更。P8-CODEX-009／010・P8-ACC-038はHandoff §4の明示指示どおり本Packageでは修正していない（既存未解決課題として保持）。

Package別詳細は次の個別Recoveryを参照。

```text
phase_8_claude_p8_rw6_a_redirect_evidence_truthfulness_recovery_ja_20260831011018.md      (P8-CODEX-005)
phase_8_claude_p8_rw6_b_deterministic_dev_agent_budget_recovery_ja_20260831011018.md       (P8-CODEX-006)
phase_8_claude_p8_rw6_c_important_gate_runtime_completion_recovery_ja_20260831011018.md    (P8-CODEX-007)
phase_8_claude_p8_rw6_d_constitution_mode_preview_recovery_ja_20260831011018.md            (P8-CODEX-008)
```

## 4 Finding別Disposition（要約）

### P8-CODEX-005 — Redirect後Canonical URLとSource Authorityが不一致 → RESOLVED

`_build_fetched_evidence()`が`source_authority`をRedirect前`url`ではなく`fetched.canonical_url`のHostから再計算するよう修正。`WebEvidence`／`WebCitation`へ`requested_url`Fieldを新設し、Requested／Canonical両URLをEvidence／Citation／Persistence（`WEB_CITATION_EVIDENCE_SCHEMA_VERSION` 1→2）／REST／SSE／UIで損失なく保持。`.gov`→`.org`Redirect（Controller実Probeと同一シナリオ）でSource Authorityが`OFFICIAL`ではなく`GENERAL`に正しく収束することをFix前後で実証。Acceptance Target `P8-ACC-012`：PASS。

### P8-CODEX-006 — Budget未実装をMax Stepで代替してPASS Claim → RESOLVED

`ToolDescriptor.budget_cost`（Fixture比例、write_note=5／list_files・read_file=1）、`RunSnapshot.budget_limit`／`budget_consumed`、Tool実行直前Check、超過時`budget_exceeded`収束（Architecture§7既存語彙）を実装。単一の高Cost StepがMax Step=10でもBudget超過するTestでMax Stepとの非同義性を実証。Reload／Restart後もLimit／Usage保持。Acceptance Target `P8-ACC-036`：PASS。

### P8-CODEX-007 — Completion Gate未配線／重要Gate分類の実動Evidence不足 → RESOLVED

`RunState.AWAITING_COMPLETION_APPROVAL`（新設）、`CompletionApprovalEvidence`（Step用`ApprovalEvidence`とは構造的に別Type）、`submit_completion_approval()`を実装。`important_gate_only`は全Step成功後もRun-level Completion Gateで停止し、明示Approvalなしに自動`completed`へ収束しない。Generic Gate Engineが8 Reason全て（Completion含む）を扱えることをParametrized Fixture Testで証明。Step ApprovalとCompletion Approvalの相互不流用を実証。Frontend Demo Run UIへCompletion Gate承認画面を追加（新規UI無しではUser実画面Demo Runが行き詰まるため必須）。Acceptance Target `P8-ACC-034`：PASS。

### P8-CODEX-008 — Constitution Mode比較がProductionではOFF固定 → RESOLVED

`resolve_constitution_mode_preview()`と`GET /api/v2/constitution/preview`を新設。同一ManifestをOFF／OBSERVE／ENFORCE全てへPure Evaluation、Production Active Mode（常にOFF）は一切変更しない。Responseへ`active_production_mode`を明示的に含め、FrontendのConstitutionPanelへ「PreviewでありActive Runtime Modeではない」旨のDisclaimer付き3-Mode比較Sectionを追加。Acceptance Target `P8-ACC-021`：PASS。

## Changed Paths（全体、P8-RW6-0〜E合算）

Backend Source：
```text
src/margpa_runtime_llm/modules/web_knowledge/contracts.py
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py
src/margpa_runtime_llm/web/web_search_contracts.py
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/web/persistent_streaming.py
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/bootstrap/dev_agent.py
src/margpa_runtime_llm/web/dev_agent_contracts.py
src/margpa_runtime_llm/web/dev_agent_routes.py
src/margpa_runtime_llm/modules/constitution/contracts.py
src/margpa_runtime_llm/modules/constitution/__init__.py
src/margpa_runtime_llm/web/constitution_contracts.py
src/margpa_runtime_llm/web/constitution_routes.py
```

Backend Test：
```text
tests/unit/web_knowledge/test_web_knowledge_service.py
tests/integration/web/test_persistent_web_app.py
tests/integration/conversation/test_persistent_citation_evidence.py
tests/unit/dev_agent/test_run_service.py
tests/integration/dev_agent/test_dev_agent_web_app.py
tests/unit/dev_agent/test_json_file_run_store.py
tests/unit/constitution/test_constitution_contracts.py
tests/integration/web/test_constitution_web_app.py
```

Frontend：
```text
frontend/src/types.ts
frontend/src/api/client.ts
frontend/src/components/WebSearchPanel.tsx（+.test.tsx）
frontend/src/components/WebCitationsSection.tsx（+.test.tsx）
frontend/src/components/DevAgentPanel.tsx（+.test.tsx）
frontend/src/components/ConstitutionPanel.tsx（+.test.tsx）
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

明示的に変更していないもの：`web/app.py`（Router登録は既存のまま）、`bootstrap/web_application.py`・`entrypoints/web/main.py`（新規Composition不要）、`adapters/dev_agent/*`・`adapters/constitution/*`、P8-CODEX-001〜004解消済みSource、Concurrency Lock実装、Frontend Chat／Archive／SettingsPanel等の無関係機能。

## Focused／Canonical Verification

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2124 passed, 7 deselected"
ruff:
  command: "uv run ruff check ."
  result: "All checks passed"
mypy:
  command: "uv run mypy src/"
  result: "Success: no issues found in 344 source files"
frontend_full_suite:
  command: "npm test -- --run"
  result: "302 passed (33 files)"
frontend_typecheck:
  command: "npx tsc --noEmit -p ."
  result: clean
frontend_lint:
  command: "npx eslint ."
  result: clean
frontend_build:
  command: "npm run build"
  result: "built in ~90ms, no errors"
regression_guard_verification:
  method: "各Packageの中核分岐を一時的に無効化し、新規Regression Testが実際にFailすることを確認した上で復元（diff上Fix版と完全一致を都度確認）"
  p8_codex_005: confirmed
  p8_codex_006: confirmed
  p8_codex_007: confirmed
```

## Corrected 40 Acceptance集計

```text
PASS                 37
  内訳（前回33 PASSからの純増4件）：
  P8-ACC-012  FAIL -> PASS（P8-CODEX-005是正）
  P8-ACC-021  PARTIAL -> PASS（P8-CODEX-008是正）
  P8-ACC-034  PARTIAL -> PASS（P8-CODEX-007是正）
  P8-ACC-036  FAIL -> PASS（P8-CODEX-006是正）
PARTIAL               1
  P8-ACC-038  GD相関未実装（既知Foundation Boundary、Phase 6/9 Semantic Governance Debtとして保持、本Rework対象外）
FAIL                   1
  P8-ACC-039  Manual URL Conversation Test 3件がNetwork-restricted環境で非Hermetic（P8-CODEX-010、既知・PoC非Blocker、本Rework対象外）
USER MANUAL GATE       1
  P8-ACC-040  User実画面確認待ち
TOTAL                 40
```

Handoff §5の期待上限（`37 PASS / 1 PARTIAL / 1 FAIL / 1 USER MANUAL GATE / 40`）と完全一致。

P8-ACC-039について：本Session環境では`test_manual_web_evidence_is_injected_as_an_untrusted_tool_message`等3 Testを含む全2124 Testが通過した事実を確認した。同時に、これら3 Testは`tests/unit/web_knowledge/conftest.py`が持つSafe DNS Stub Fixtureの対象外であり、`validate_url_before_connect()`経由で実`socket.getaddrinfo()`へ到達する非Hermetic構成であることも確認した（P8-CODEX-010の指摘どおり）。これはSource Runtime Regressionではなく既存のTest Isolation Gapであり、Handoff §4により本Rework対象外と明示されているため、是正は行っていない。本Session内での`pytest`実行はProject Root内の既存Test Suiteを対象Fixture付きで実行するCanonical Verificationであり、新規のReal Network Actionを追加で行ったものではない。

## Internal Review Finding／Rework（1 Cycle）

Handoff §5「4 Blockerに直接関係するCritical／Majorだけをrework」の指示に基づき、実装Sourceと4 Findingの限定是正Checklistを再突合。自己発見2件をその場で追加した（先送りなし）：

1. Frontend `WebSearchPanel.tsx`／`WebCitationsSection.tsx`へ`requested_url`表示を追加した際、対応するTest Assertionが無かった（既存Fixtureの型合わせのみ）。Redirect表示の有無双方をTestする4件を追加。
2. Backend `JsonFileDevAgentRunStore`のBackward Compatibility Testが`envelope`/`approvals`欠落のみをCoverし、P8-RW6-B/CのNew Field（`budget_limit`/`budget_consumed`/`completion_approvals`）欠落は未Coverだった。専用Test 1件を追加。

Major／Critical Findingは無し。4 Blocker以外のMinor／Hardening／別Phase範囲（P8-CODEX-009／010、P8-ACC-038、WebCitationsSectionのsource_authority非表示という既存UI Gap等）は本Rework対象外として未解決へ送った。

## 未解決として保持したもの

```yaml
P8-CODEX-009:
  content: "User Manual SheetとRun Completion Transitionの不一致（write成功後さらに1回Advanceが必要）"
  disposition: DEFERRED
  reason: "Handoff §4で明示的に本Rework対象外"
P8-CODEX-010:
  content: "Manual URL Conversation Test 3件の実DNS依存"
  disposition: DEFERRED
  reason: "Handoff §4で明示的に本Rework対象外"
P8-ACC-038:
  content: "GD（Guardrail）相関、Dev Agent Runとの相関未実装"
  disposition: PARTIAL（既知）
  reason: "Fake ToolはModel出力を生成せずEvaluate対象が構造的に存在しない。Phase 6/9 Semantic Governance Debtとして保持"
P8-ACC-040:
  content: "User実画面でManual URL、Archive管理、Chat/Agent切替、Gate/Stopを確認"
  disposition: USER_MANUAL_GATE
  reason: "実User操作が必須。Claude Browser実演はAutomated Candidate Evidenceでありその代替ではない（先行Reworkで既に開示済み）"
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
p8_codex_009_010_touched: false
```

## Exact Next Action

```text
Codex ControllerのTargeted Re-review待ちで停止する。
成立が確認され次第、User Manual Gate（P8-ACC-040）へ進む。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Phase 8 Closure、Roadmap、Git、Backup、Phase 9のいずれへも進んでいない。
```
