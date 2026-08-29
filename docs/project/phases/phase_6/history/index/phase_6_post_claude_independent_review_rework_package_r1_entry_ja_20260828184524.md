# Phase 6 Post-Claude Independent Review Rework — Package R1 Entry（Atomic Provider／Mode／Lifecycle Transaction）

```yaml
document_id: phase_6_post_claude_independent_review_rework_package_r1_entry_20260828184524
package: P6-RR-R1
role: package_entry
created_at: 2026-08-28 18:45:24 JST
predecessor: phase_6_post_claude_independent_review_rework_package_r0_recovery_ja_20260828184118.md
git_action: 0
network_action: 0
```

## 1. 前提

Package R0を完了し、Preserved BaselineとOpen Finding Ledger（P6-CODEX-062〜068）を確定済み。本Packageは目標のP6-CODEX-062（Provider Selection／Mode／Lifecycleが非Atomic）を解消する。

## 2. Source調査結果（Mutation前の設計根拠）

本Task内のSource再読により、次を確認した。

```text
1. provider_selection_routes.py の apply_provider_selection() は、typed_role is ModelRole.MAIN
   の場合のみ _apply_main_provider_selection() へ分岐し、実Switch TransactionをMode／
   Lifecycleと同一Requestで扱う。JUDGE／GUARDは controller.select() のみを呼び、Mode／
   Lifecycleと一切連動しない。

2. feature_modes_routes.py の apply_judge() は、Mode≠OFF要求時に
   role_provider_lifecycle.activate(role=JUDGE) を先に呼び、state≠ACTIVEならMode Commit前に
   Error化する——Preflight-before-Commitは既に正しく実装済み。

3. bootstrap/configuration_control.py の _GuardrailGovernanceModeApplierAdapter.apply() も、
   Mode≠OFF要求時に role_provider_lifecycle.activate(role=GUARD) を先に呼び、同様に
   Preflight-before-Commitを既に正しく実装済み。

4. したがって、P6-CODEX-062／P6-GOV-018 Scenario Bの実際のGapは「Mode-Apply経路」ではなく、
   「Provider Selection（Configured変更）経路」が Mode／Lifecycle と非連動である点に限定される。
   ProviderSelectionController.select() 自体のDocstringが明示する通り「Selection never
   performs an implicit Load or fallback」——Selection経路でActivationを試みる設計は本来の
   Architecture Intentに反する。よって修正方針は「Selection変更時、対象RoleのModeが非OFFなら
   同一Requestで Mode を OFF へ強制Rollbackし、旧Adapterを Drain／Unload する」とする
   （Addendum M-WU-005の「旧Activeを維持するかMode OFFへRollback」のうちMode OFF Rollback側）。
```

## 3. Work Unit計画

```text
R1-WU-001: Judge／Guard Provider変更時のMode現在値Check（Preflightに相当する事前確認）
R1-WU-002: 既存Transition State Machine（RoleProviderLifecycleManager.activate()）の再確認・
           非破壊であることの確認（新規実装は不要、既存機構の適用範囲拡大のみ）
R1-WU-003/004: Selection変更をAtomicなMode-OFF-Rollback Transactionとして実装
               （provider_selection_routes.py 新規関数 _apply_role_provider_selection）
R1-WU-005: 旧Adapter Drain／Unload（role_provider_lifecycle.deactivate()の無条件呼び出し）
R1-WU-006: Judge／Guard両Roleへ同一Contractを適用（単一関数で両Role対応）
R1-WU-007: Package R1 Recovery Index作成
```

## 4. Changed File Inventory（計画時点、実施前）

```text
src/margpa_runtime_llm/web/provider_selection_routes.py（変更予定）
tests/integration/web/test_provider_selection_main_switch.py またはRole別新規Test（変更／新規予定）
```

## 5. Preserved Baseline再確認

R1はMAIN Role Switch Transaction（M-WU-002、Package M成果）を変更しない。JUDGE／GUARDの
Mode-Apply経路（feature_modes_routes.py、configuration_control.py）も変更しない——両者は
既にPreflight-before-Commitを正しく実装しており、Redoは不要。
