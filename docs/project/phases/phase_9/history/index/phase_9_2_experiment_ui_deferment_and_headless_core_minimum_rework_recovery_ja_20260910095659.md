# Phase 9-2 Experiment UI延期／Headless Core維持 最小Rework Recovery

```yaml
document_id: phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_recovery_20260910095659
document_state: full_recovery
language: ja
created_at: 2026-09-10T09:56:59+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

User Mac実画面テストで現行Minimal Experiment UIのCancel導線・Plan Reset・Details表示・State明示が通常利用に不十分と判明し（`phase_9_2_user_mac_original_manual_checklist_partial_result_and_strategy_change_input_ja_20260910093525.md`）、ユーザーはExperiment UIをMVP必須機能とせずPhase 11以降へ延期する方針を承認した（`phase_11_plus_experiment_workspace_ui_deferment_and_headless_core_preservation_reservation_ja_20260910093525.md`）。これを受け、Controllerが発行したQuota制約付き最小Rework Handoff（`phase_9_controller_experiment_ui_deferment_and_headless_core_minimum_rework_exact_handoff_ja_20260910093525.md`）に基づき、通常UIからExperiment入口だけを最小変更で除去した。Experiment Backend Coreと`ExperimentPanel.tsx`本体・専用Testは無変更で保持。Exact Returnを新規Pathへ提出、Codex Controller Independent Review待ち。

## 2. What Changed

- **Experiment入口の非表示化**: `TopBar.tsx`から`id="experiment-toggle"`Button（`onOpenExperiment`Callback含む）を削除。`App.tsx`から`ExperimentPanel`のImport、`experimentPanelOpen`State、`<ExperimentPanel>`のMountを削除。通常UIのState／Callback／Mount経路のいずれからもExperiment Panelを開けない。
- **Headless Core非変更**: `src/margpa_runtime_llm/modules/experiment/`、`adapters/experiment/`、`web/experiment_routes.py`、`bootstrap/experiment_*`、Experiment Store／API／Worker／Lease／Identity／Trace／Comparison／Case／Evidence契約、`ExperimentPanel.tsx`内部（Cancel／Reset／Details／Polling）のいずれも本Round`Read`以外のTool未使用。
- **Focused Test更新**: `App.test.tsx`のExperiment Button存在確認Testを非存在確認Testへ置換（`queryByRole`/`querySelector`双方で`null`確認）。Theme／Language／Settings／Chat関連の既存37件は無変更のままPASS。
- **検証**: Focused Test（`App.test.tsx`38件）・TypeScript Typecheckをmandatoryとして実施、両方PASS。Quotaに余力があったためLintも追加実施しPASS。Frontend Full Test／Buildは今回未実施（Quota節約のため意図的に停止）。Backend Full Suite／Real Model／Browserは元よりHandoff禁止のため未実施。

## 3. Files Created/Modified This Round

**新規ファイル**:
- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_ja_20260910095659.md`（本Roundの正本Return）
- 本File（Recovery Index）

**修正ファイル（Frontend、他File一切無変更）**:
- `frontend/src/components/TopBar.tsx`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_ja_20260910095659.md](../../handoffs/phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_ja_20260910095659.md)

Maximum Claim: `P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_CANDIDATE_FOR_CONTROLLER_REVIEW`

## 5. Verification Summary

- Focused Test（`App.test.tsx`）: `38 passed`。
- TypeScript Typecheck: Error 0件。
- Lint（余力による追加実施）: Error/Warning 0件。
- Frontend Full Test／Build: 未実施（Quota節約のため）。
- Backend Full Suite／Real Model／Browser: 未実施（Handoff禁止事項、対象外）。
- Git操作: 本Round中ゼロ回。

## 6. Open Items at This Point

- `frontend/src/i18n/translations.ts`の`experimentToggleLabel`Key（ja/en）は未使用のまま残置（Scope外Fileのため今回非対応）。
- Frontend Full TestとBuildは未実施——次回Quotaに余力がある回での実施候補。
- `ExperimentPanel.tsx`自体のCancel／Reset／Details／Polling修復は、Phase 11以降のExperiment Workspace再設計まで引き続き延期。

## 7. Next Step

Codex Controller Independent Reviewを待つ。追加Rework、User Manual、Phase Completion、Git操作、次Phaseへの着手のいずれも、本Returnの範囲では行わない。
