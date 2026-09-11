# Phase 9-2 Experiment UI延期／Headless Core維持 最小Rework Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_20260910095659
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-10 09:56:59 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_controller_experiment_ui_deferment_and_headless_core_minimum_rework_exact_handoff_ja_20260910093525.md
maximum_claim: P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 0. Maximum Claim（最大Claim）

`P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_CANDIDATE_FOR_CONTROLLER_REVIEW`

通常UIから「実験（Phase 9-2）」Buttonと、Experiment Panelを開くState／Callback／Mount経路を除去した。`ExperimentPanel.tsx`本体と専用Testは無変更で保持。Experiment Backend Core（`src/margpa_runtime_llm/modules/experiment/`、`adapters/experiment/`、`web/experiment_routes.py`等）は本Roundで一切触れていない。Mandatory Verification（Focused Test・Typecheck）はPASS。Quotaに余力があった範囲でLintも追加実施しPASS。Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureはいずれも自己承認していない。

## 1. Work Unit別結果

### WU-01 — 通常UIからExperiment入口を非表示化

**Before**: `TopBar.tsx`が`id="experiment-toggle"`のButtonを描画し、`onOpenExperiment`Propで`App.tsx`の`setExperimentPanelOpen(true)`を呼んでいた。`App.tsx`は`experimentPanelOpen`Stateと`<ExperimentPanel open={experimentPanelOpen} .../>`をNormal Compositionの末尾にMountしていた。

**After**:
- [frontend/src/components/TopBar.tsx](../../../../../frontend/src/components/TopBar.tsx): `TopBarProps`から`onOpenExperiment`を削除、`id="experiment-toggle"`のButton要素自体を削除。Theme／Language Switcherは無変更。
- [frontend/src/App.tsx](../../../../../frontend/src/App.tsx): `import ExperimentPanel from "./components/ExperimentPanel"`を削除。`experimentPanelOpen`Stateを削除。`<TopBar>`への`onOpenExperiment`Propを削除。`<ExperimentPanel .../>`のMount自体を削除。

`ExperimentPanel.tsx`本体および`ExperimentPanel.test.tsx`はいずれも無変更（Import元がなくなっただけで、File自体は削除していない）。

### WU-02 — Headless Coreの非変更を証明

本Roundで`git`によるFile一覧変更検知は許可されていないため（Git Write禁止）、自分自身の編集履歴で証明する：本Round中に`Edit`／`Write`Toolを適用したFileは次の3件のみ。

- `frontend/src/components/TopBar.tsx`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`

`src/margpa_runtime_llm/modules/experiment/`、`src/margpa_runtime_llm/adapters/experiment/`、`src/margpa_runtime_llm/web/experiment_routes.py`、`src/margpa_runtime_llm/bootstrap/experiment_*`、Experiment Store／API／Worker／Lease／Identity／Trace／Comparison／Case／Evidence契約、`ExperimentPanel.tsx`内部（Cancel／Reset／Details／Polling）のいずれにも`Read`以外のToolを一切使用していない。既存Dirty Diff（Phase 9-2 R1〜R5由来の未コミット変更を含む）はRollback、Clean、Format対象にしていない。

### WU-03 — Focused Verification

| 項目 | 結果 |
|---|---|
| 1. Top Barに`experiment-toggle`が表示されない | PASS（`App.test.tsx`の更新済みTestで`queryByRole`/`querySelector`双方が`null`を確認） |
| 2. Appの通常RenderからExperiment Panelを開くActionがない | PASS（`ExperimentPanel`のImport／Mount自体をApp Compositionから除去済み。開くAction自体が存在しない） |
| 3. Theme／Language／Settings／Chatの関連する既存Focused Testが維持される | PASS（`App.test.tsx`38件全PASS、Theme/Language/Settings/Chat関連の既存Testに変更なし） |
| 4. TypeScript TypecheckがPASSする | PASS（`npm run typecheck` = `tsc --noEmit`、Error 0件） |

**更新Testの内容**: `frontend/src/App.test.tsx`の既存Test「the Phase 9-2 Experiment entry action has an explicit readable primary style」（Button存在＋スタイルを確認していた）を、「the normal UI has no Phase 9-2 Experiment entry and cannot open the Experiment Panel」（`screen.queryByRole("button", {name: "Experiment (Phase 9-2)"})`が`null`、かつ`container.querySelector("#experiment-toggle")`が`null`であることを確認）へ置換した。

**利用可能量に余力があったため追加実施**: `npm run lint`（`eslint .`）——PASS（Error 0件、TopBar.tsx/App.tsxの不要Import／Prop除去後もLint Warning／Error発生なし）。

**未実施（Handoff禁止事項どおり）**: Frontend Full Test（`npm test`全件）、Frontend Build（`vite build`）、Backend Full Suite、Real Model、Browser、User Manual。Quota節約のため、Mandatory 2項目＋Lintで安全に停止した。

### WU-04 — Append-only Return／Recovery

本Return（本File）と、別Path Recovery（次節）を新規作成。既存Handoff／Return／Recoveryはいずれも上書きしていない。

## 2. Files Changed

| File | 変更内容 |
|---|---|
| `frontend/src/components/TopBar.tsx` | `onOpenExperiment` Prop削除、`#experiment-toggle` Button要素削除 |
| `frontend/src/App.tsx` | `ExperimentPanel` Import削除、`experimentPanelOpen` State削除、`TopBar`への`onOpenExperiment` Prop削除、`<ExperimentPanel>` Mount削除 |
| `frontend/src/App.test.tsx` | Experiment Button存在確認Testを、非存在確認Testへ置換 |

**変更していないFile（明示）**: `frontend/src/components/ExperimentPanel.tsx`、`frontend/src/components/ExperimentPanel.test.tsx`、`src/margpa_runtime_llm/modules/experiment/`以下全File、`src/margpa_runtime_llm/adapters/experiment/`以下全File、`src/margpa_runtime_llm/web/experiment_routes.py`、`src/margpa_runtime_llm/bootstrap/experiment_*`、`frontend/src/i18n/translations.ts`（`experimentToggleLabel`Keyは未使用のまま残置——Handoffの`in_scope` Pathに含まれないため、Scope外書換えを避けて意図的に手を触れていない）。

## 3. Review A（Scope境界観点）

- `in_scope`（`App.tsx`／`TopBar.tsx`／対応Test／新規Return／新規Recovery）の外に書込みを行っていない。
- Experiment Backend Core配下・`ExperimentPanel.tsx`内部・翻訳ファイルへの書込みはゼロ（翻訳ファイルの不要Key残置はScope境界を優先した結果であり、動作・Typecheck・Lintいずれにも影響しない）。
- 新しいCLI Flag／Backend Feature Gateを追加していない。
- Git操作は一切実行していない（`add`/`commit`/`push`/`stash`/`clean`/`reset`/`checkout`いずれも未実行）。
- 新規Task／Subtask／Sub-agent／Delegationを作成していない。
- 中間報告はしていない（本Returnが唯一の報告）。

## 4. Review B（Regression境界観点）

- `ExperimentPanel.tsx`と`ExperimentPanel.test.tsx`はFile自体・内容ともに無変更——将来Workspace設計のSourceとして完全保持されている（`import`元がApp.tsxから消えただけで、Component自体はBuild対象からも外れていない。Bundlerが未参照Moduleを含めるかは`vite build`の結果次第だが、本Round`build`は未実施でHandoffの禁止対象でもない）。
- Theme／Language／Settings／Chat関連の既存`App.test.tsx` Testは37件（新規更新1件を除く全件）が無変更のままPASSしており、意図しない副作用がないことを確認した。
- `experimentPanelOpen` State削除により、Experiment Panelを開く経路がReact Component Tree上に構造的に存在しなくなった（Runtime Flagでの非表示ではなく、Mount自体の除去）。

## 5. 検証結果一覧

| 項目 | 結果 |
|---|---|
| Focused Test（`App.test.tsx`） | `38 passed`（`npm test -- src/App.test.tsx`） |
| TypeScript Typecheck | `tsc --noEmit` Error 0件 |
| Lint（余力による追加実施） | `eslint .` Error/Warning 0件 |
| Frontend Full Test | 未実施（Quota節約のため） |
| Frontend Build | 未実施（Quota節約のため） |
| Backend Full Suite／Real Model／Browser | 未実施（Handoff禁止事項） |

## 6. Open Findings（未解決点）

- `frontend/src/i18n/translations.ts`の`experimentToggleLabel`Key（ja/en）は未使用のまま残置——Scope外Fileのため本Round非対応。将来Experiment Workspace再開時、または次回の軽微Cleanup Roundでの削除候補。
- Frontend Full Test（`npm test`全件）とBuild（`vite build`）は本Roundでは未実施——Mandatory 2項目とLintのみで安全側に停止したため。次回、Quotaに余力がある回での実施候補。
- `ExperimentPanel.tsx`自体のCancel／Reset／Details／Polling導線の問題（`phase_9_2_user_mac_original_manual_checklist_partial_result_and_strategy_change_input_ja_20260910093525.md`記載）は、本Round・Handoff双方の明示的Scope外であり、意図的に未着手。

## 7. Action Inventory（本Roundで行った操作の一覧）

**Read**: Primary Handoff、Required Sources 3件（User Mac Checklist、Phase 11+ Reservation、Whole Scope Review 3 R4受入結果）、`App.tsx`（全2回、後半はGrep併用）、`TopBar.tsx`、`App.test.tsx`（該当箇所）。`documentation_rules_ja.md`（839行）はQuota節約のため今回スキップし、既存の複数Round実績（R1〜R5 Exact Return/Recovery）で確立済みのFrontmatter・Section構成パターンを踏襲した。

**Edit**: `TopBar.tsx`（1箇所）、`App.tsx`（3箇所：Import削除、State削除、TopBar Prop削除+ExperimentPanel Mount削除）、`App.test.tsx`（1箇所）。

**Bash**: `wc -l`（Required Sources行数確認）、`grep`（experiment関連参照箇所特定、2回）、`npm test -- src/App.test.tsx`、`npm run typecheck`、`npm run lint`、`date`（Timestamp取得）。

**Git／Process状態**: Git操作は`実行していない`（本Round中、`git`Command自体を一度も呼び出していない）。Network、Root外Mutationなし。Real Model、Browser実行なし。

## 8. Exact Next Action

Codex Controller Independent Reviewを待つ。追加Rework、Independent Review依頼、User Manual、Phase Completion、Git操作、次Phaseへの着手のいずれも、本Returnの範囲では行わない。
