# Phase 8 Claude Constitution Preview Semantics Micro Rework — Exact Return Handoff

```yaml
document_id: phase_8_claude_constitution_preview_semantics_micro_rework_exact_return_handoff_20260831071113
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 07:11 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-RW7-0_through_C
入力Handoff: phase_8_claude_constitution_preview_semantics_micro_rework_exact_handoff_ja_20260831065824.md
入力Handoff_sha512: 362636aab3e496e482196314d2d878e1b68b3b0879580facc264db2e2355092df01f040c2100cdea866453ec9a8f5d4f10e8051373cd098df2a91d85587a68e1
入力Controller_Review: phase_8_codex_controller_rw6_two_cycle_targeted_re_review_ja_20260831065406.md
入力Controller_Review_sha512: 124db30e3185e8c1d550b7063263b21760b97aa805f20d1b2434977cf71bfe19920d0b05486a81c5ec67123dd647ae22c0dff9f01570837ac725187c21925c60
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_claimed: false
phase_9_entered: false
git_mutation_executed: false
git_read_executed: false
network_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
```

## 1. 結論

Codex Controller二段階Targeted Re-reviewが残した唯一のMajor Finding、P8-CODEX-012
（Constitution PreviewがDecision Outcomeだけを表示し、Action Permission／Violation Presentation比較を欠く）を解消した。
P8-CODEX-005〜007／P8-A〜F／P8-RW6-A〜Cは無変更。P8-CODEX-009／010／011、P8-ACC-038は本Packageでは修正していない。

```yaml
p8_codex_012_disposition: RESOLVED
p8_acc_021_disposition: PASS
mvp_blocker_open: 0
critical_open: 0
```

詳細はRecovery Index参照。

```text
docs/project/phases/phase_8/history/index/phase_8_claude_constitution_preview_semantics_micro_rework_recovery_ja_20260831071113.md
```

## 2. P8-CODEX-012 Disposition

`ConstitutionModePreviewEntry`（`src/margpa_runtime_llm/modules/constitution/contracts.py`）へ
`evaluation_disposition`／`action_permission`／`violation_presentation`の3軸を追加した。前2者はExact Handoff §4の
固定Table通りMode自体にのみ依存（`_EVALUATION_DISPOSITION_BY_MODE`／`_ACTION_PERMISSION_BY_MODE`）、後者
（`violation_presentation`）は実際の`ConstitutionDecision.outcome`から`_resolve_violation_presentation()`で正直に導出する
——Ruleが1件も適用されないViewは`not_evaluated`、適用されるが未対応（今日の実Manifest全Rule）なら`typed_unsupported`、
実際に`observed`／`enforced`された場合のみそれぞれの値へ収束する。未対応Ruleを`observed`／`enforced`へ捏造することはない。

`src/margpa_runtime_llm/web/constitution_contracts.py`の`ConstitutionModePreviewEntryResponse`／
`project_mode_previews()`が3軸を損失なく`/api/v2/constitution/preview`へProjectionする。
`frontend/src/components/ConstitutionPanel.tsx`が各View／Modeについて Decision／Evaluation／Action Permission／
Violation Presentationの4行を日本語／英語Label付きで表示する。Preview Disclaimerと`active_production_mode=off`表示は無変更。

Production Constitution Active ModeはOFF固定のまま。Preview呼出しはRuntime Activation、External Action、
Tool Authority、Model InjectionまたはNetworkを一切発生させない（Pure計算のみ、新規I/O導入なし）。

Regression Guard: Backend／Frontendそれぞれで一時的にPre-fix状態（3軸をMode非依存の固定値へ、またはFrontend描画を削除）
へ書き換え、新規Testが実際にFailすることを確認した上でScratchpadバックアップから復元し、diffで完全一致を確認した。

## 3. P8-ACC-021 Disposition and Exact Evidence

```yaml
before: PARTIAL
after: PASS
```

Source Evidence：
- `src/margpa_runtime_llm/modules/constitution/contracts.py` — `resolve_constitution_mode_preview()`がMode毎に3軸をPure／Deterministicに解決。
- `src/margpa_runtime_llm/web/constitution_contracts.py` — REST Responseへ損失なくProjection。

Test Evidence：
- `tests/unit/constitution/test_constitution_contracts.py` — 新規5 Testが固定値テーブルへの収束と、未対応Ruleの`typed_unsupported`保持を実証。
- `tests/integration/web/test_constitution_web_app.py` — 新規2 TestがREST Response経由でも同じ性質を実証。

UI Evidence：
- `frontend/src/components/ConstitutionPanel.tsx` — 3軸をja/en Label付きで表示。
- `frontend/src/components/ConstitutionPanel.test.tsx` — 新規2 Test（en/ja）が実際の表示文字列を検証、Regression Guardで実効性確認済み。

## 4. Changed Paths

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

明示的に変更していないもの：`constitution_routes.py`、`bootstrap/constitution.py`、`frontend/src/api/client.ts`、
P8-CODEX-005〜007解消済みSource、Dev Agent／Budget／Completion Gate、Manual URL、Archive、Branch関連。
`npm run build`によるFrontend静的再生成物（`src/margpa_runtime_llm/web/static/*`）はBuild Verificationの副産物であり、手動編集ではない。

## 5. Focused／Canonical Verification

```yaml
focused_backend:
  command: "uv run pytest -q tests/unit/constitution/ tests/integration/web/test_constitution_web_app.py"
  result: "39 passed"
backend_full_suite:
  command: "uv run pytest -q"
  result: "2131 passed, 7 deselected"
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
frontend_typecheck_lint_build:
  result: clean
```

## 6. Known P8-CODEX-010 Separation

Codex Network制限環境における既知3件のNon-hermetic Failure（`tests/unit/conversation/test_conversation_generation.py`の
3 Test）は、本Session環境（2131件全通過）でも構成上再現し得るが、本Packageの変更（Constitution Previewのみ）とは無関係であり、
Handoff §7の指示通り本Taskでは修正していない。P8-ACC-039は既知FAILのまま保持する。

## 7. Internal Review Finding Ledger（1 Cycle、6観点）

Requirement／Negative Path／Composition／Persistence非影響／UI Claim／Acceptanceの6観点で実施。
Critical／Major／MVP Blockerは0件。唯一の記録事項は理論的健全性の確認：`resolve_constitution_mode_preview()`は
`known_rule_ids`へ`capability_view.rule_ids`自身から構築したfrozensetを渡すため、Preview経路では`unknown_rule` outcomeが
構造的に発生し得ず、`violation_presentation`の`typed_unsupported`と混同されるリスクは無い（到達不能パスであり、Coverage漏れではない）。
詳細はRecovery Index §7を参照。ReworkはCycle内で発生していない。

## 8. Process Action Inventory

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
p8_codex_009_010_011_touched: false
p8_acc_038_touched: false
```

## 9. Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_constitution_preview_semantics_micro_rework_recovery_ja_20260831071113.md
```

## 10. Exact Next Action

```text
Codex ControllerのTargeted Re-review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL。
Final Acceptance、Phase 8 ClosureまたはPhase 9開始のいずれもClaimしていない。
```

Return後は本Handoffの通り停止する。
