# Phase 9-2 Whole Scope Independent Review 2 UI Identity／Persistence Rework Recovery

記録時刻: 2026-09-09 02:13:28 JST  
実行役: 設計者兼実装者役（Task `01a03b6c-2a68-7881-99bc-c788a600f632`）  
Controller: プロジェクト責任者兼設計統括者役（Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`）

## 1. Recovery State

- State: `COMPLETE_CANDIDATE_FOR_CONTROLLER_REREVIEW`
- Scope: Controller Independent Review 2でConfirmed MAJORとなった`IR-P9-2-WHOLE-R2-01`〜`03`と直接回帰Testだけ。
- Phase 9-2 Complete／User Manual PASS／Closure／Phase 9-3／Phase 10／Gitは主張・実行していない。
- Network、Real Browser、Real Model Artifact、User `runtime_data`、Project Root外Actionは実行していない。
- 既存Dirty Working TreeはRollback／Clean／Stashせず保持した。

## 2. Completed Findings

### IR-P9-2-WHOLE-R2-01 — FIXED

- `refreshRunList()`へ単調増加するRefresh generationを導入した。
- Run ListとComparisonを同じgenerationで並行取得し、両Responseが揃った時点で「最新generationかつ現在のExperiment ID」である場合だけUI stateへ反映する。
- 新しいPlan成功時とExperiment ID入力変更時に旧Refresh generationを無効化する。
- 遅い旧Comparisonが新しいTerminal Comparisonの後に到着する順序をDeferred Promiseで決定的に再現し、Terminal stateと`pass`が保持されることをHard Assertした。

Evidence:

- `frontend/src/components/ExperimentPanel.tsx:206`
- `frontend/src/components/ExperimentPanel.tsx:248`
- `frontend/src/components/ExperimentPanel.tsx:288`
- `frontend/src/components/ExperimentPanel.tsx:468`
- `frontend/src/components/ExperimentPanel.test.tsx:754`

### IR-P9-2-WHOLE-R2-02 — FIXED

- Detail取得ごとにgeneration、要求時Experiment ID、要求時Run IDを固定した。
- Responseは3条件すべてが現在選択と一致する場合だけInvocation／Execution Modeを更新する。
- A選択後にBを選択し、Aが遅着する順序を決定的Test化した。BのGuard EvidenceとProduction Disclaimerだけが残り、AのFixture表示へ逆戻りしないことをHard Assertした。
- 現在選択中Detailの取得失敗を捕捉し、旧Invocationを消去して誤表示を残さないことも同Testで確認した。

Evidence:

- `frontend/src/components/ExperimentPanel.tsx:406`
- `frontend/src/components/ExperimentPanel.test.tsx:839`

### IR-P9-2-WHOLE-R2-03 — FIXED

- `ExperimentService.create_plan_with_desired_configurations()`をApplication境界として追加した。
- 既存Planの重複確認をSnapshot書込みより前に行い、既に公開済みのPlanへ紐づくSnapshotを上書きしない。
- Plan参照Variant集合とDesired Snapshot集合の完全一致、各Digest一致を全書込み前に検証する。
- 全Desired Snapshotを先に保存し、Planを最後の可視Commit pointとして保存する。
- Routeの従来のPlan先行保存＋後続Snapshot保存を、上記単一Application操作へ置換した。
- 2件目のSnapshot保存で一度だけ例外を注入し、HTTP 500後にPlanが不可視、同一ID再試行で201、全Digest／Variant相関、既存Planへの重複要求がSnapshot非上書き、Fresh StoreでRestart Read成立を確認した。

Evidence:

- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:84`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:89`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:104`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:133`
- `src/margpa_runtime_llm/web/experiment_routes.py:620`
- `src/margpa_runtime_llm/web/experiment_routes.py:654`
- `tests/integration/web/test_experiment_routes.py:152`
- `tests/integration/web/test_experiment_routes.py:285`

## 3. Sabotage-regression

各Findingの核心Guardを一時的に修正前相当へ戻し、新規TestがFAILすることを確認した後、`apply_patch`で即時復元した。Git Stash／Backupは使用していない。

| Finding | 一時Sabotage | 検出結果 |
|---|---|---|
| R2-01 | Refreshのgeneration一致条件を除去 | 遅着した旧Empty Comparisonが新Terminal Comparisonを上書きし、`pass`消失でFAIL（1 failed／10 skipped） |
| R2-02 | Detailのgeneration一致条件を除去 | 遅着したAがBを上書きし、Bの`guard`消失でFAIL（1 failed／10 skipped） |
| R2-03 | Plan保存をSnapshot保存前へ移動 | 2件目Snapshot失敗後もPlanが読め、`Plan is None` AssertでFAIL（1 failed） |

復元後:

- Frontend `ExperimentPanel.test.tsx`: `11 passed`
- Backend Service＋atomic persistence: `18 passed`

## 4. Validation

| Validation | Result |
|---|---|
| Finding-focused Frontend | `1 file / 11 tests` PASS |
| Finding-focused Backend | `18 passed in 0.61s` |
| Phase 9-2 Backend scope | `272 passed in 5.99s` |
| Frontend Full | `34 files / 339 tests` PASS |
| Frontend typecheck | PASS |
| Frontend lint | PASS |
| Frontend build | PASS、60 modules transformed、canonical static asset生成 |
| Changed Python paths Ruff | `All checks passed!` |
| Changed Python paths Mypy | `Success: no issues found in 3 source files` |
| `git diff --check` | PASS |

非Model Backend Full Suiteは今回再実行していない。直前R1 Recoveryで`2680 passed, 43 deselected`が成立済みであり、今回は変更範囲を含むPhase 9-2 Backend 272件、Frontend Full 339件、直接Focused／Staticで差分を検証したため、Handoffの「費用対効果上必要な場合のみ」に従った。

## 5. Current Changed Paths for This Rework

Product:

- `frontend/src/components/ExperimentPanel.tsx`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`

Tests:

- `frontend/src/components/ExperimentPanel.test.tsx`
- `tests/integration/web/test_experiment_routes.py`

Generated validation artifact:

- `src/margpa_runtime_llm/web/static/app.js`

先行R1／UI Rework差分とController-owned anomaly EvidenceはExpected Dirtyとして保持し、本R2の変更理由へ混入させていない。

## 6. Two-perspective Self Review

1. UI Identity／Async Order観点: Refresh、Plan、Detailの各ResponseがgenerationとExperiment／Run identityへ相関し、旧Responseが現在表示のRun／Comparison／Evidence／Disclaimerを上書きできないことをSourceと逆順Testで確認した。Blocker／Major残件なし。
2. Persistence／Failure／Restart観点: 公開済みPlanを唯一の可視Commit pointとし、pre-commit Snapshot失敗、同一ID retry、duplicate non-overwrite、Digest／Variant相関、Fresh Store Restart Readを確認した。Blocker／Major残件なし。

Minor UX候補（Cancel失敗時表示改善）はHandoffどおりScope外であり、今回のComplete Candidateを妨げるFindingではない。

## 7. Exact Resume / Next Action

このTaskの追加Actionはない。Controllerは対になるExact Returnと本Recoveryを用いて`IR-P9-2-WHOLE-R2-01`〜`03`だけをIndependent Re-reviewする。Phase 9-2 Complete／User Manual／Phase 9-3／Phase 10／Closure／Gitは別Authorityまで開始しない。
