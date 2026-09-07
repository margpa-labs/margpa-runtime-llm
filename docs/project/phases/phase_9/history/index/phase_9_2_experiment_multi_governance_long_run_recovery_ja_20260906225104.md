# Phase 9-2 Experiment Multi-Governance Long Run Recovery

```yaml
document_id: phase_9_2_experiment_multi_governance_long_run_recovery_20260906225104
document_state: partial_recovery
language: ja
created_at: 2026-09-06T22:51:04+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller Exact Handoff(`phase_9_controller_phase_9_2_experiment_multi_governance_long_run_exact_handoff_ja_20260906212349.md`)およびExecution Design(`phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown_ja.md`)に基づき、P9-2-AからP9-2-Fまでを依存順で実装した。A〜Eは完全に実装・検証済み。Fは、Comparison Report・Fixture Matrix→Acceptance Mapping・Internal Review A/Bを完了したが、F3(実Model Gate)は意図的に今Round未実行のまま停止している。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ち。

## 2. What Changed

新規Module `src/margpa_runtime_llm/modules/experiment/` および `src/margpa_runtime_llm/adapters/experiment/` を追加し、Model/Provider/GD固有Schemaを一切Hard-codeしない汎用Experiment/Multi-Governance Research Coreを実装した。

- **Domain**: `identity.py`(ExperimentPlan/VariantDescriptor/ComponentSelection、Digest付き)、`config_snapshot.py`(EffectiveConfigurationSnapshot)、`run.py`(VariantRun一方向State Machine)、`dataset.py`/`evaluation.py`(Case Manifest、Evaluator Identity分離、Metric)、`comparison_declaration.py`(Baseline/Regression/Ablation単一要因検証)、`composition.py`(Actor Port、Governance Composition/Conflict/Routing/Repair Propagation)、`freshness.py`/`retrieval_case.py`/`belief_revision.py`/`false_improvement.py`(Semantic Research Case分類)、`case_pack.py`(Neutral Fixture Case Pack)、`trace.py`(Model Call 0 Trace)、`presentation.py`(Strict Buffer/Progressive)、`comparison_report.py`(Comparison Report)。
- **Application**: `experiment_service.py`(Plan作成/Run開始/状態取得/Cancel/結果取得のMinimal API)、`composition_runner.py`(Independence Matrix Runner)、`comparison_service.py`(Comparison Report Builder)。
- **Adapters**: `local_filesystem_experiment_store.py`(Restart可能Persistence)、`fixture_actor_adapters.py`(Fixture Actor/Routing Strategy)。
- **Web**: `experiment_routes.py`(`/api/v7/experiment`、Fixture限定Run)、`web_application.py`/`contracts.py`/`app.py`への小さな追加配線。
- **Frontend**: `ExperimentPanel.tsx`(最小Experiment画面)、TopBarへの切替Button、`types.ts`/`api/client.ts`/`i18n/translations.ts`/`app.css`への追加。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md`(本Roundの正本Return、Files Changedの完全な一覧を含む)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md](../../handoffs/phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md)

Maximum Claim: `P9_2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Focused Unit Test(`tests/unit/experiment/`): `149 passed`。
- Integration Route Test(`tests/integration/web/test_experiment_routes.py`): `5 passed`。
- Backend Non-model Full Suite: `2557 passed, 37 deselected`(82.24s)。
- Ruff(Whole Repo): `All checks passed!`。
- Canonical Mypy(Whole Repo): `43 errors/4 files`(既存Baseline完全一致、新規Error 0)。
- Frontend: `npm run test`(34 Files/330 Tests全Pass)、`typecheck`/`lint`/`build`いずれも成功。
- Sabotage-regression 7件、いずれも検出力を確認し復元後Byte一致を確認。

## 6. Open Items at This Point

- F3(実Model Gate)は今Round意図的に未実行(理由はExact Return §9参照)。
- `ComponentSelection.mode=None`の呼び出し判定が未Exercise(Blockerではない、Exact Return §8/§9参照)。
- Selene/DeepSeek Judgeとの比較Caseは今Round未実装(Scope外どおり)。
- `criteria_evaluated`のUnknown判定理由、Memory定量計測はPhase 9-1由来の既存Open Findingのまま。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closure、追加のUI大改造、F3実Model Gateの実行のいずれも、本Returnの範囲では行わない。次の指示を待つ。
