# Phase 9-2 Whole Scope Independent Review 1 Major Rework Recovery

記録時刻: 2026-09-08 21:08:53 JST  
実行役: 設計者兼実装者役（Task `01a03b6c-2a68-7881-99bc-c788a600f632`）  
Controller: プロジェクト責任者兼設計統括者役（Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`）

## 1. Recovery State

- State: `COMPLETE_CANDIDATE_FOR_CONTROLLER_REREVIEW`
- Scope: Controller Independent Review 1でConfirmed MAJORとなった4件だけ。
- Phase 9-2 Complete／User Manual PASS／Closure／Phase 9-3／Gitは主張・実行していない。
- Network、Real Browser、Real Model Artifact、User `runtime_data`、Project Root外Actionは実行していない。
- 既存Dirty Working TreeはRollback／Clean／Stashせず保持した。

## 2. Completed Finding

### IR-P9-2-WHOLE-R1-01

- `ExperimentService.start_run()`からcaller-supplied `execution_mode`を除去。
- Run modeは永続化済み`ExperimentPlan.execution_mode`だけから導出。
- Runtime／Test callerを新しい単一Authority APIへ更新。
- fixture／production双方でPlan/Run mode一致とRestart Read一致を回帰Test化。

Evidence:
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:92`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py:154`
- `tests/unit/experiment/test_experiment_service.py:78`

### IR-P9-2-WHOLE-R1-02

- invoke起点`ExperimentCoreError`を`FAILED`へ収束。
- `failure_reason=actor_domain_error:<typed-code>`だけを保存し、safe messageを含めない。
- Late／Terminal publish競合は、既知Codeかつ永続Runが既Terminalの場合だけ無害化。
- Lease待機中のCancel／Deadline／Shutdown後にActorへ進まない再確認を追加。
- Success／Failed outcome／Cancel race／Deadline／Actor例外／ShutdownでLease releaseとin-flight cleanupを確認。

Evidence:
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:90`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:235`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:262`
- `tests/unit/experiment/test_run_worker.py:135`
- `tests/unit/experiment/test_run_worker.py:171`
- `tests/unit/experiment/test_run_worker.py:691`

### IR-P9-2-WHOLE-R1-03

- `ComparisonRow`でMetric stateとauthoritative Row stateの不一致をTyped Reject。
- stale／partial Raw EvidenceのMetric stateがRun stateと異なるApplication readではMetricを正直に`None`化。
- `ComparisonReport`へ`case_id`を追加。
- Metricおよび全Observationの`case_id`をReport caseへ照合し、metric不在時のwrong-caseもReject。
- Builderはcaller-supplied revisionを廃止し、永続Planの`case_id`／`case_revision`を唯一のAuthorityとして使用。
- Persisted JSONのRestart Readを`ComparisonReport.model_validate()`で確認。

Evidence:
- `src/margpa_runtime_llm/modules/experiment/domain/errors.py:39`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py:56`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py:98`
- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py:42`
- `tests/unit/experiment/test_comparison_report.py:200`
- `tests/unit/experiment/test_comparison_report.py:226`

### IR-P9-2-WHOLE-R1-04

- bool一回読取を廃止し、ConditionベースのExperiment／Mutation共有Arbitrationへ変更。
- Mutation先着時はHTTP handler全区間をmutation-side leaseで保持し、Experimentは完了まで待機。
- Experiment held／waiting時の新規対象Mutationは409 Call 0。
- Middlewareのresponse／413／exception全経路でmutation leaseを`finally`解放。
- Barrierを使う実HTTP両順序Testで、Experiment先着409とMutation先着Actor待機を決定的に確認。

Evidence:
- `src/margpa_runtime_llm/modules/experiment/application/configuration_lease.py:29`
- `src/margpa_runtime_llm/modules/experiment/application/configuration_lease.py:54`
- `src/margpa_runtime_llm/web/app.py:350`
- `src/margpa_runtime_llm/web/app.py:405`
- `tests/integration/web/test_experiment_routes.py:1429`
- `tests/integration/web/test_experiment_routes.py:1502`

## 3. Sabotage-regression

各Findingの修正を一時的に外して指定TestがFAILすることを確認し、`apply_patch`で即時復元した。Git Stash／Backupは使用していない。

| Finding | 一時Sabotage | 検出結果 |
|---|---|---|
| R1-01 | Run modeを固定`fixture`へ戻す | production param caseがPlan/Run不一致でFAIL（1 failed, 1 passed） |
| R1-02 | invoke-domain-errorのFAILED publishを除去 | deadlineなしRunが`running`に残りtimeout FAIL（1 failed） |
| R1-03A | stale Metricのstate照合／UNAVAILABLE化を除去 | Failed RowへCompleted Metricが到達してFAIL（1 failed） |
| R1-03B | metricなしObservationのReport case照合を除去 | wrong-caseがRejectされずFAIL（1 failed） |
| R1-04 | mutation-side lease counter取得を除去 | Mutation処理中にActorが進入してBarrier Assert FAIL（1 failed） |

復元後Focused suite: `88 passed`。

## 4. Validation

| Validation | Result |
|---|---|
| Focused 6 files | `88 passed in 3.31s` |
| Phase 9-2 Backend scope | `271 passed in 3.41s` |
| Backend non-model Full | `2680 passed, 43 deselected in 84.15s` |
| Ruff whole repo | `All checks passed!` |
| Canonical Mypy (`pyproject.toml` scope, 650 files) | 既知Baselineと一致する`43 errors / 4 files`; 今回変更Fileは0 issue |
| Changed Python test files targeted Mypy | `Success: no issues found in 6 source files` |
| Frontend Full | `34 files / 337 tests` PASS |
| Frontend typecheck | PASS |
| Frontend lint | PASS |
| Frontend build | PASS、60 modules transformed、canonical static asset生成 |
| `git diff --check` | PASS |

Canonical Mypy既知Baseline 4 files:

- `tests/unit/guardrail_governance/test_stream_guard.py`
- `tests/unit/guardrail_governance/test_point_runtime.py`
- `tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py`
- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py:631`

## 5. Current Changed Paths for This Rework

Product:

- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py`
- `src/margpa_runtime_llm/modules/experiment/application/configuration_lease.py`
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py`
- `src/margpa_runtime_llm/modules/experiment/domain/errors.py`
- `src/margpa_runtime_llm/web/app.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`

Tests:

- `tests/integration/web/test_experiment_routes.py`
- `tests/unit/experiment/test_acceptance_mapping_p9_2.py`
- `tests/unit/experiment/test_comparison_report.py`
- `tests/unit/experiment/test_experiment_service.py`
- `tests/unit/experiment/test_r1_hard_assert_mapping.py`
- `tests/unit/experiment/test_run_worker.py`

Validation output:

- `src/margpa_runtime_llm/web/static/app.js`（既存Frontend差分を保持した状態でcanonical buildにより再生成）

Pre-existing UI Rework paths／Controller-owned anomaly Evidenceは変更理由へ混入させず、Expected Dirtyとして保持した。

## 6. Two-perspective Self Review

1. Authority／Architecture観点: Plan mode、Report case、Run state、Configuration arbitrationの各Authorityがcaller input／stale Evidence／TOCTOUへ分散していないことを確認。Blocker／Major残件なし。
2. Failure／Concurrency／Restart観点: domain error、publish競合、cancel、deadline、shutdown、partial write、Restart Read、Experiment先着／Mutation先着を確認。Blocker／Major残件なし。

## 7. Exact Resume / Next Action

このTaskの追加Actionはない。Controllerは本Recoveryと対になるExact Returnを使い、4 FindingだけをIndependent Re-reviewする。Phase 9-2 Complete／User Manual／Phase 9-3／Closure／Gitは別Authorityまで開始しない。
