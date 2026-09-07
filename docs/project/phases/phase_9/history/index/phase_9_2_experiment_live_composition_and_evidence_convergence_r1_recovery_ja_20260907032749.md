# Phase 9-2 Experiment Live Composition／Evidence Convergence R1 Recovery

```yaml
document_id: phase_9_2_experiment_live_composition_and_evidence_convergence_r1_recovery_20260907032749
document_state: partial_recovery
language: ja
created_at: 2026-09-07T03:27:49+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller Exact Handoff(`phase_9_controller_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_handoff_ja_20260907002521.md`)に基づき、Long Run Return(`phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md`)へのCHANGES_REQUIRED判定7件(IR-P9-2-01〜07)をR1-WU-01からWU-06まで依存順に対応した。WU-01〜05は解決、WU-06はFixture/Integration Hard Assertまで解決、実Model 3-Run Gateは計測Evidence(空きMemory不足)に基づきTrue Stop(Partial)として停止した。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ち。

## 2. What Changed

- **Identity/Case/Config相関(WU-01)**: `ExperimentPlan`に`case_id`/`case_digest_sha512`/`VariantConfigurationRef`を追加し、Plan Digestの再計算対象に含めた。`VariantRun.request_id`を必須化。
- **Frozen Plan強制実行(WU-02)**: Web Routeの`start_run`が`_PRESET_VARIANTS`ではなく永続化済み`ExperimentPlan.variant()`のみを参照するよう修正。`composition_runner.py`の`mode=None`判定Bug(IR-P9-2-07)を修正。`ExperimentPlanBudget`の`max_variant_runs`/`stop_policy`(Execution Order)を`ExperimentService.start_run()`でRuntime強制。
- **Production Turn Variant Adapter(WU-03)**: `modules/experiment/application/production_turn_runner.py`(純粋Port/Projection、Fakeで単体検証)と`bootstrap/experiment_production_turn_adapter.py`(実`ConversationGenerationService`/`JudgeGovernanceComposition`/`GuardrailGovernanceComposition`を包む実装)を新設。Config Isolationは「別Instanceを作らずLive Configを読み取るのみ、強制しない」方式(Handoff §6.2 Option 2)を採用。
- **Case Evaluation/Comparison結線(WU-04)**: `_resolve_frozen_case()`でCase Pack実ContentからDigest再検証しつつ`case.input`を取得。`GET .../comparison`を新設し`build_comparison_report()`を実際に呼ぶ。Human Review未実施のCaseはPASSへ格上げしない決定論的Metric Oracleを追加。
- **Async Lifecycle(WU-05)**: `ExperimentRunWorker`(単一Thread、Deadline Call 0判定、Actor例外→FAILED、Cancel Hook)を新設。`POST /runs`を202 Async化。実装過程で`ExperimentService.publish_result()`の書き込み順序Race Bugを発見・修正(State保存がRaw Evidence保存より先行していたため、非同期化後に限って観測可能になっていた)。
- **Verification(WU-06)**: R1 9.1 Hard Assert 10項目の consolidated Test File を新設。実装中に`ComparisonRow`のRun/Case不一致未Rejectという別の実Gapを発見・修正。Sabotage-regression 3件実施、全て検出力確認・復元確認済み。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md](../../handoffs/phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md)

Maximum Claim: `P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Focused Unit(`tests/unit/experiment/`): `185 passed`。
- Integration(`tests/integration/web/test_experiment_routes.py`): `12 passed`。
- Backend Non-model Full Suite: `2588 passed, 37 deselected`(81.4s)。
- Ruff(Whole Repo): `All checks passed!`。
- Canonical Mypy(Whole Repo): `43 errors/4 files`(既存Baseline完全一致)。
- Frontend: `npm test`(34 files/331 tests全Pass)、`tsc --noEmit`/`eslint .`/`npm run build`いずれも成功。
- Sabotage-regression 3件、いずれも検出力を確認し復元後Byte一致を確認。
- 実Model Run: 0回(True Stop、理由はExact Return §9.1)。

## 6. Open Items at This Point

- 実Model 3-Run Gate(Handoff R1 9.2)は今Round意図的に未実行(理由: 実行直前のSystem Memory計測で16GiB中約14GiBが既にUser自身の作業により使用中、空き容量約1.3GiBのみと判明。Exact Return §9.1参照)。
- Config Digest不一致のRuntime再検証は、Effective Configuration Snapshotの実配線自体が今Roundの対象外のため未実施(Exact Return §9.2)。
- Guard Evidence相関はrequest_id非依存の近似Signal(Invocation ID変化検知)であり、真のRequest単位相関ではない(Exact Return §9.3)。
- `rubric_revision`に`case.revision`を代用する簡略化(Exact Return §9.4)。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closure、実Model Gateの実行のいずれも、本Returnの範囲では行わない。次の指示を待つ。
