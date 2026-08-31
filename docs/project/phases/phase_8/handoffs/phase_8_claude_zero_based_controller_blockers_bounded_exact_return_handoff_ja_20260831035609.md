# Phase 8 Claude ゼロベースController Blocker限定Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_zero_based_controller_blockers_bounded_exact_return_handoff_20260831035609
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 03:56 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-RW6-0_through_E
入力Handoff: phase_8_claude_zero_based_controller_blockers_bounded_exact_handoff_ja_20260831005304.md
入力Review: phase_8_codex_controller_zero_based_second_full_re_review_ja_20260831004652.md
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

Codex Controllerゼロベース第2回全体再Reviewが指摘した4 Major Finding（P8-CODEX-005〜008）を、Fresh Task化・P8-A〜F／P8-CR0〜5再実装なしで全て解消した。P8-CODEX-001〜004・Concurrency Lock・既存Acceptance成立範囲は無変更。Handoff §4で明示的に対象外とされたP8-CODEX-009／010・P8-ACC-038は本Packageでは修正していない。

```yaml
p8_codex_005_disposition: RESOLVED
p8_codex_006_disposition: RESOLVED
p8_codex_007_disposition: RESOLVED
p8_codex_008_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
```

詳細は本Package付属のRecovery Indexおよび4件のPackage別Recoveryを参照。

```text
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_zero_based_blockers_bounded_complete_package_recovery_ja_20260831035609.md
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_a_redirect_evidence_truthfulness_recovery_ja_20260831011018.md
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_b_deterministic_dev_agent_budget_recovery_ja_20260831011018.md
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_c_important_gate_runtime_completion_recovery_ja_20260831011018.md
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_d_constitution_mode_preview_recovery_ja_20260831011018.md
```

## 2. 4 Finding別Disposition

### P8-CODEX-005（RESOLVED）— Redirect後Canonical URLとSource Authorityが不一致

`_build_fetched_evidence()`の`source_authority`計算をRedirect前`url`からRedirect後`fetched.canonical_url`のHostへ修正。`WebEvidence`／`WebCitation`へ`requested_url`Fieldを新設し両URLを損失なく保持（`WEB_CITATION_EVIDENCE_SCHEMA_VERSION` 1→2）。Controller実Probeと同一の`.gov`→`.org`Redirectシナリオで、Fix前は`OFFICIAL`と誤判定・Fix後は正しく`GENERAL`と判定されることを実証。

### P8-CODEX-006（RESOLVED）— Budget未実装をMax Stepで代替

`ToolDescriptor.budget_cost`（Fixture比例Cost）、`RunSnapshot.budget_limit`／`budget_consumed`、実行直前Check、超過時`budget_exceeded`収束を実装。単一の高Cost StepがMax Step=10でも独立してBudget超過することをTestで実証し、Max Step代替ではないことを示した。

### P8-CODEX-007（RESOLVED）— Completion Gate未配線

`RunState.AWAITING_COMPLETION_APPROVAL`と構造的に独立した`CompletionApprovalEvidence`を実装。`important_gate_only`は全Step成功後もRun-level Completion Gateで停止する。Generic Gate Engineが8 Reason全て（Completion含む）を扱えることをParametrized Fixture Testで証明し、Step ApprovalとCompletion Approvalが相互流用不可であることを実証。Frontend Demo Run UIへCompletion Gate承認画面を追加（新規UI無しでは実画面Demo Runが行き詰まるため必須対応）。

### P8-CODEX-008（RESOLVED）— Constitution Mode比較がProduction不可能

`resolve_constitution_mode_preview()`と`GET /api/v2/constitution/preview`を新設。同一ManifestをOFF／OBSERVE／ENFORCE全てへPure Evaluationし、Production Active Mode（常にOFF）を一切変更しない。Responseに`active_production_mode`を明示し、FrontendへPreview／Active Mode混同防止のDisclaimer付き比較UIを追加。

## 3. Changed Paths

```text
# Backend Source
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

# Backend Test
tests/unit/web_knowledge/test_web_knowledge_service.py
tests/integration/web/test_persistent_web_app.py
tests/integration/conversation/test_persistent_citation_evidence.py
tests/unit/dev_agent/test_run_service.py
tests/integration/dev_agent/test_dev_agent_web_app.py
tests/unit/dev_agent/test_json_file_run_store.py
tests/unit/constitution/test_constitution_contracts.py
tests/integration/web/test_constitution_web_app.py

# Frontend
frontend/src/types.ts
frontend/src/api/client.ts
frontend/src/components/WebSearchPanel.tsx (+.test.tsx)
frontend/src/components/WebCitationsSection.tsx (+.test.tsx)
frontend/src/components/DevAgentPanel.tsx (+.test.tsx)
frontend/src/components/ConstitutionPanel.tsx (+.test.tsx)
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

明示的に変更していないもの：`web/app.py`、`bootstrap/web_application.py`、`entrypoints/web/main.py`、`adapters/dev_agent/*`、`adapters/constitution/*`、P8-CODEX-001〜004解消済みSource、Concurrency Lock実装、無関係なFrontend機能。

## 4. Focused／Canonical Verification

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2124 passed, 7 deselected"
ruff:
  result: "All checks passed"
mypy:
  result: "Success: no issues found in 344 source files"
frontend_full_suite:
  command: "npm test -- --run"
  result: "302 passed (33 files)"
frontend_typecheck_lint_build:
  result: clean
regression_guard_verification:
  method: "各Packageの中核分岐を一時的に無効化し、新規Testが実際にFailすることを確認した上で復元（diff上Fix版と完全一致を都度確認）"
  confirmed_for: [P8-CODEX-005, P8-CODEX-006, P8-CODEX-007]
```

## 5. Corrected 40 Acceptance集計

```text
PASS                 37
  P8-ACC-012  FAIL -> PASS（P8-CODEX-005）
  P8-ACC-021  PARTIAL -> PASS（P8-CODEX-008）
  P8-ACC-034  PARTIAL -> PASS（P8-CODEX-007）
  P8-ACC-036  FAIL -> PASS（P8-CODEX-006）
PARTIAL               1  P8-ACC-038（GD相関、既知Foundation Boundary）
FAIL                   1  P8-ACC-039（P8-CODEX-010、Network-restricted環境で3 Testが非Hermetic、既知・PoC非Blocker）
USER MANUAL GATE       1  P8-ACC-040
TOTAL                 40
```

Handoff §5の期待上限と完全一致。P8-ACC-039をPASSへ捏造していない：本Session環境では全2124 Testが通過した事実と、該当3 TestがSafe DNS Stub対象外で実`socket.getaddrinfo()`へ到達する非Hermetic構成である事実の両方を確認・記録した（P8-CODEX-010自体は未修正、Handoff §4により対象外）。

## 6. Internal Review Finding（1 Cycle）

4 Findingの限定是正Checklistと実装Sourceを再突合し、自己発見2件を追加した：(1) Frontend `requested_url`表示のTest Assertion欠落 → Redirect表示有無双方のTest 4件追加、(2) `JsonFileDevAgentRunStore`のBackward Compatibility TestがP8-RW6-B/CのNew Fieldを未Cover → 専用Test 1件追加。Major／Critical Findingは無し。

## 7. 未解決として保持したもの

```text
P8-CODEX-009  Manual SheetとRun Completion Transitionの不一致 — Handoff §4により対象外、DEFERRED
P8-CODEX-010  Manual URL Conversation Testの実DNS依存 — Handoff §4により対象外、DEFERRED
P8-ACC-038    GD相関未実装 — 既知Foundation Boundary、PARTIAL継続
P8-ACC-040    User実画面確認 — USER_MANUAL_GATE継続
```

## 8. Process Action Inventory

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

## 9. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_p8_rw6_zero_based_blockers_bounded_complete_package_recovery_ja_20260831035609.md
```

## 10. Exact Next Action

```text
Codex ControllerのTargeted Re-review待ちで停止する。
成立が確認され次第、User Manual Gate（P8-ACC-040）へ進む。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Phase 8 Closure、Roadmap、Git、Backup、Phase 9のいずれへも進んでいない。
```

Return後は本Handoffの通り停止する。
