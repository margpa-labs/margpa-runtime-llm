# Phase 8 P8-RW7 Constitution Preview Semantics Micro Rework — Recovery Index

```yaml
document_id: phase_8_claude_constitution_preview_semantics_micro_rework_recovery_20260831071113
document_type: recovery_index
document_state: frozen
language: ja
created_at: 2026-08-31 07:11 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
execution_scope: P8-RW7-0_through_C
入力Handoff: phase_8_claude_constitution_preview_semantics_micro_rework_exact_handoff_ja_20260831065824.md
入力Handoff_sha512: 362636aab3e496e482196314d2d878e1b68b3b0879580facc264db2e2355092df01f040c2100cdea866453ec9a8f5d4f10e8051373cd098df2a91d85587a68e1
入力Controller_Review: phase_8_codex_controller_rw6_two_cycle_targeted_re_review_ja_20260831065406.md
対象Finding: P8-CODEX-012
```

## 1. 完了状態

P8-CODEX-012（Constitution PreviewがDecision以外の比較Contractを実装していない）を解消した。
`ConstitutionModePreviewEntry`へ`evaluation_disposition`／`action_permission`／`violation_presentation`の3軸を追加し、
Backend Contract・REST Projection・Frontend UIへ損失なく到達させた。Production Active Constitution ModeはOFF固定のまま無変更。

```yaml
p8_codex_012_disposition: RESOLVED
p8_acc_021_disposition: PASS
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

## 2. 3軸の固定意味論（Exact Handoff §4を実装値としてそのまま固定）

```text
OFF
  evaluation_disposition: not_evaluated
  action_permission: no_constitution_action
  violation_presentation: not_evaluated

OBSERVE
  evaluation_disposition: evaluate_record_only
  action_permission: no_block_no_authority_change
  violation_presentation: observation_only | typed_unsupported（実Decisionから正直に導出）

ENFORCE
  evaluation_disposition: evaluate_and_apply_supported_action
  action_permission: supported_actions_only_no_authority_expansion
  violation_presentation: enforced | typed_unsupported（実Decisionから正直に導出）
```

`evaluation_disposition`／`action_permission`はMode自体に固定（Ruleの`supported`状態に非依存）。
`violation_presentation`だけは実際の`ConstitutionDecision.outcome`から導出する：
Viewに適用Ruleが1件もない場合は`not_evaluated`（「未対応」の捏造ではなく「対象なし」を正直に表す）、
Ruleはあるが`supported_rule_ids`未包含（今日の実Manifest全Rule）の場合は`typed_unsupported`、
Ruleが実際に`observed`／`enforced`された場合のみそれぞれの値へ収束する。

## 3. Changed Paths（手動編集のみ、npm run buildによる静的再生成物は除く）

```text
# Backend Source
src/margpa_runtime_llm/modules/constitution/contracts.py
src/margpa_runtime_llm/modules/constitution/__init__.py
src/margpa_runtime_llm/web/constitution_contracts.py

# Backend Test
tests/unit/constitution/test_constitution_contracts.py
tests/integration/web/test_constitution_web_app.py

# Frontend
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/components/ConstitutionPanel.tsx
frontend/src/components/ConstitutionPanel.test.tsx
frontend/src/styles/app.css
```

`src/margpa_runtime_llm/web/constitution_routes.py`は無変更（Projection関数呼び出しのみで、
新規3軸FieldはProjection層で完結するため）。`frontend/src/api/client.ts`も無変更
（`fetchConstitutionModePreview()`はJSON Shapeを素通しするだけで、新規Fieldの追加はTypes側で表現される）。

`npm run build`実行によりFrontend Build成果物（`src/margpa_runtime_llm/web/static/app.js`／`app.css`／
`index.html`）が再生成されたが、これは手動編集ではなくBuild Verificationの副産物であり、
セッション開始時点で既にUncommitted状態だった先行Package（P8-RW6）分の差分を含む。

## 4. Focused／Canonical Verification

```yaml
focused_backend:
  command: "uv run pytest -q tests/unit/constitution/ tests/integration/web/test_constitution_web_app.py"
  result: "39 passed"
backend_full_suite:
  command: "uv run pytest -q"
  result: "2131 passed, 7 deselected"
  baseline_before_this_package: "2124 passed, 7 deselected"
  new_tests_this_package: 7
ruff:
  result: "All checks passed"
mypy:
  result: "Success: no issues found in 344 source files"
focused_frontend:
  command: "npx vitest run src/components/ConstitutionPanel.test.tsx"
  result: "7 passed"
frontend_full_suite:
  command: "npm test -- --run"
  result: "304 passed (33 files)"
  baseline_before_this_package: "302 passed (33 files)"
  new_tests_this_package: 2
frontend_typecheck:
  command: "npx tsc --noEmit"
  result: clean
frontend_lint:
  command: "npx eslint ."
  result: clean
frontend_build:
  command: "npm run build"
  result: succeeded
regression_guard_verification:
  method: >-
    contracts.py と ConstitutionPanel.tsx をそれぞれ一時的に Codex の指摘した
    Pre-fix 状態（3軸を Mode に依存しない固定値へ、または Frontend 描画を削除）へ書き換え、
    新規 Test が実際に Fail することを確認した上で Scratchpad バックアップから復元し、
    diff で復元後ファイルが Fix 版と完全一致することを確認した。
  confirmed_for:
    - "backend: src/margpa_runtime_llm/modules/constitution/contracts.py"
    - "frontend: frontend/src/components/ConstitutionPanel.tsx"
```

## 5. P8-ACC-021 再導出（Source／Test／UI Evidence）

```yaml
before: PARTIAL  # P8-RW6 Cycle2 Controller Reviewによる差し戻し
after: PASS
evidence:
  source:
    - "src/margpa_runtime_llm/modules/constitution/contracts.py: ConstitutionModePreviewEntry に evaluation_disposition/action_permission/violation_presentation を追加し、resolve_constitution_mode_preview() が Mode ごとに Pure/Deterministic に解決する。"
    - "src/margpa_runtime_llm/web/constitution_contracts.py: project_mode_previews() が3軸を損失なく /api/v2/constitution/preview Response へ Projection する。"
  test:
    - "tests/unit/constitution/test_constitution_contracts.py: test_mode_preview_entries_carry_the_frozen_per_mode_semantics ほか5件が Exact Handoff の固定値テーブルへの収束と、未対応 Rule の typed_unsupported 保持を実証する。"
    - "tests/integration/web/test_constitution_web_app.py: test_preview_entries_expose_the_three_axis_comparison / test_preview_violation_presentation_is_honest_for_the_real_manifest が REST Response 経由でも同じ性質を実証する。"
  ui:
    - "frontend/src/components/ConstitutionPanel.tsx: 各 View／Mode に Decision／Evaluation／Action Permission／Violation Presentation の4行を ja/en Label 付きで表示する。"
    - "frontend/src/components/ConstitutionPanel.test.tsx: 新規2 Test（en/ja）が実際の表示文字列を検証し、Revert 状態で Fail することを確認済み（Regression Guard）。"
```

## 6. Known P8-CODEX-010 分離

Backend Full Suiteは本Session環境で2131件全通過。Codex Controller自身のNetwork制限環境では次3件のみが
既知の非Hermetic構成（実`socket.getaddrinfo()`到達）によりFailすることが、入力Controller Reviewで確認済み。

```text
tests/unit/conversation/test_conversation_generation.py
  test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
  test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
  test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

本Package（P8-RW7）はConstitution Previewのみを変更しており、この3件とは無関係。修正もしていない
（Handoff §7により対象外・DEFERRED継続）。

## 7. Internal Review Finding Ledger（1 Cycle、6観点）

```yaml
requirement:
  finding: none
  note: "P8-REQ-016（OFFをallow allと解釈しない）はOFF Entryの action_permission=no_constitution_action / violation_presentation=not_evaluated で構造的に維持。"
negative_path:
  finding: reviewed_no_change_needed
  note: >-
    resolve_constitution_mode_preview() は known_rule_ids に capability_view.rule_ids 自身の
    frozenset を渡すため、Preview経路では unknown_rule outcome が原理的に発生しない
    （every rule_id in capability_view.rule_ids is trivially in known_rule_ids by construction）。
    したがって violation_presentation の "typed_unsupported" と "unknown_rule" 由来のケースが
    混同されるリスクは、このPathでは到達不能であり、Coverage漏れではない。理論的な健全性として記録する。
composition:
  finding: none
  note: "constitution_routes.py・bootstrap/constitution.py は無変更。Projection層のみで完結し、既存Route/Bootstrap配線を壊していない。"
persistence_non_impact:
  finding: none
  note: "Constitution Previewは Persistence を持たない Pure 計算であり、本Packageは Run Store・SQLite・JSON Fileいずれにも触れていない。"
ui_claim:
  finding: none
  note: "ConstitutionPanel.tsx はPreview Disclaimerとactive_production_modeの表示を無変更のまま維持し、新規3軸行のみ追加。既存5 Test + 新規2 Testが両立して通過。"
acceptance:
  finding: none
  note: "P8-ACC-021のPASS再導出は本Index §5の通り。他Acceptance項目への副作用なし（Backend Full Suite 2131件全通過で確認）。"
critical_or_major_found: 0
rework_performed_in_this_cycle: none
```

## 8. Process Action Inventory

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
p8_codex_009_010_011_touched: false
p8_acc_038_touched: false
```

## 9. Exact Next Action

```text
Codex ControllerのTargeted Re-review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Final Acceptance、Phase 8 ClosureまたはPhase 9開始はClaimしていない。
```
