# Phase 9-2 Experiment Truthful Variant Execution / Evidence R2 Recovery

```yaml
document_id: phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_recovery_20260907084839
document_state: partial_recovery
language: ja
created_at: 2026-09-07T08:48:39+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller Exact Handoff（`phase_9_controller_phase_9_2_experiment_
truthful_variant_execution_and_evidence_r2_exact_handoff_ja_20260907071729.md`）
に基づき、R1 Return（`phase_9_claude_phase_9_2_experiment_live_composition_
and_evidence_convergence_r1_exact_return_ja_20260907032749.md`）へのCHANGES_
REQUIRED判定（IR-P9-2-R1-01〜07）をR2-WU-01からWU-06まで依存順に対応した。
全WU resolved。Fixture/Integration収束確認後、Handoff R2 SS9.2が要求する
実Model Gate（Main Qwen only / Main Qwen+Gemma Judge/Repair / Main Qwen+
Qwen3Guard）を3/3成功させた。Exact Returnを新規Fileとして提出済み、Codex
Controller Independent Review待ち。

## 2. What Changed

- **Frozen Effective Configuration（WU-01）**: `BootstrapLiveConfigurationReader`
  新設（Live Judge/Guard/Main-Governance/Repair/Recording/Mainを読取り、
  Definition Set/RAG/Presentationは対応するLive Controllerが存在しないため
  対象外）。Plan作成時に1回Snapshotを凍結し全Variantへ同一Digestを付与。
  Production Run開始前に全体Digest一致＋宣言Slot個別一致の両方をCall 0で
  検証（`find_mismatched_slots()`新設）。Turn完了直後にPost-hoc再検証し、
  実行中の設定変更を`live_config_changed_during_run`として検出。
- **Actual Component Evidence（WU-02）**: `LiveProductionTurnAdapter.
  run_turn()`を全面改修。`main_called`をConversationEventType/codeの実測
  分岐（Pre-block確定Code/Post-block確定Code/曖昧Codeの保守的False化/
  NO_HIT短絡の`attempt_provenance`判定）から導出。`repair_adopted`を
  `repair_called`と分離し実`repair_accepted`から導出。Guard Evidenceは
  前後差分推定を廃止し`unavailable_correlation`を常時返す。未観測5
  Componentは`not_observed`（`_record()`ヘルパーの`outcome`強制上書き
  Bugも同時修正）。
- **Case Evaluation（WU-03）**: `case_evaluator.evaluate_case_outcome()`
  新設。既存Domain Classifier（`classify_freshness_answer`等）へcase_id
  ごとに分岐。「completed⇒PASS」Oracle全廃。`get_comparison()`を観測→
  永続化→Response生成の単一パスへ再構成しRestart可読性を保証。
  `ComparisonReport`にrubric_revision不一致Report-level検証を追加。
- **Async Worker（WU-04）**: Deadlineを`threading.Timer`で呼出し中も
  含め束縛。`submit()`をShutdown後も非例外化（自らFAILED Publish）。
  In-flight登録をExecutor Submitと同一Lockで順序固定しRace修正。
  Cancel冪等化（Worker側Cancel Hook勝利時に200を返す）。Restart孤立Run
  復旧（`reconcile_orphaned_running_runs()`新設、`VariantRun.execution_mode`
  Frozen Identity化）。
- **Frontend Truthfulness（WU-05）**: `execution_mode`を権威Fieldとして
  全面採用。Preset選択時にFrozen Config（Component=Mode一覧）を事前表示。
  Comparison取得失敗時にStale/Unavailable状態を明示表示（無言で古い表示を
  維持しない）。repair_called/repair_adopted区別表示、Raw Evidence
  Pointer表示追加。
- **Verification（WU-06）**: Fixture/Integration Hard Assert（新規Test
  約40件、既存含め全Pass）に加え、実Model Gate 3シナリオを新設・全実行・
  全成功（詳細はException Return §8）。実行中にTest Harness自身の実
  バグ（`model_runtime_info`未配線による`attempt_provenance`欠落）と
  Test側のExecutionState期待値誤りを発見・即修正。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_20260907084839.md`（本Roundの正本Return）
- 本File（Recovery Index）

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_20260907084839.md](../../handoffs/phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_20260907084839.md)

Maximum Claim: `P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Focused Unit（`tests/unit/experiment/` + `tests/unit/bootstrap/test_
  experiment_production_turn_adapter.py`）: 約210件、全Pass。
- Integration（`tests/integration/web/test_experiment_routes.py`）: 17件、全Pass。
- Backend Non-model Full Suite: `2627 passed, 40 deselected`（81.5秒）。
- Ruff（Whole Repo）: `All checks passed!`。
- Canonical Mypy（Whole Repo）: `43 errors/4 files`（既存Baseline完全一致）。
- Frontend: `npm test`（34 files/331 tests全Pass）、`tsc --noEmit`/
  `eslint .`/`npm run build`いずれも成功。
- 実Model Gate: **3/3成功**（Main Qwen only / Main Qwen+Gemma Judge・Repair
  / Main Qwen+Qwen3Guard、いずれも1回実行で最終的にPass。詳細な実測値・
  資源観測はExact Return §8）。

## 6. Open Items at This Point

- Definition Set/RAG/Presentation 3 Component SlotはLive Controllerが
  Codebaseに存在せず今Round対象外（`mode=None`固定、Adapter Evidence上も
  `not_observed`）。
- Guard Evidence相関は引き続き`unavailable_correlation`（真の相関ではない、
  実機で実Guard実行との整合を確認済み）。
- `repair_adopted=True`（Repair実採用）分岐は実Model Gateでは非発火
  （実Judge Trial 1回でDeviationなしのため）。Fake-based Unit Testでのみ
  実証済み。強制発火目的の再試行は方針上行っていない。
- main_called判定の曖昧Error Code（Pre/Post両方から到達し得る4種）は
  保守的にFalseへ倒す設計（Open Finding、Phase 9-1側の将来改修が必要）。
- 二Variant同時実行時のConfig非交差はCode Review/設計保証で確認、専用
  並行実行Testは未追加。
- Frozen Config Digest「1 byte改変」は`ExperimentPlan`自身の既存Plan
  Digest検証機構で間接的に捕捉（専用narrow Testの代わりに機能的に同等な
  Drift Testで検証）。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3
着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では
行わない。次の指示を待つ。
