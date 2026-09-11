# Phase 9-2 Whole Scope Independent Review 3 Acceptance Truth Rework Recovery

記録時刻: 2026-09-09 07:55:20 JST  
実行役: 設計者兼実装者役（Task `01a03b6c-2a68-7881-99bc-c788a600f632`）  
Controller: プロジェクト責任者兼設計統括者役（Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`）

## 1. Recovery State

- State: `P9_2_WHOLE_SCOPE_R3_ACCEPTANCE_TRUTH_REWORK_COMPLETE_CANDIDATE_FOR_CONTROLLER_REREVIEW`
- Scope: `IR-P9-2-WHOLE-R3-01`〜`03`と、直接必要な汎用Fixture／Evaluator／Comparison結線および回帰Testだけ。
- Phase 9-2 Complete／Closure、Real Model、Real Browser、User Manual、Phase 9-3／10、Git write／Commit／Push／Cleanは主張・実行していない。
- 先行R1／R2差分、既存Dirty Working Tree、Controller-owned anomaly EvidenceはRollback／Clean／意味変更せず保持した。

## 2. Finding Disposition

### IR-P9-2-WHOLE-R3-01 — FIXED CANDIDATE

- `CURRENT`を状態名だけでPASSにせず、回答本文が`current_source_value`を実際に含む場合だけ`CURRENT_FACT_USED`とするよう修正した。
- Historical Citation Digest改変の最悪判定、Updated／Deleted、Historical Claim反復の既存優先関係を維持した。
- Top-level Fixtureの同一Caseで、`baseline-all-off`の`"I am not sure."`は`INCONCLUSIVE`、Current Valueを返す`fixture-main-active`だけが`PASS`となることをPlan→Run→Raw Evidence→Comparison→Restart Readで確認した。

Evidence:

- `src/margpa_runtime_llm/modules/experiment/domain/freshness.py:47`
- `src/margpa_runtime_llm/modules/experiment/domain/freshness.py:62`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py:123`
- `tests/unit/experiment/test_freshness_case.py:35`
- `tests/integration/web/test_experiment_routes.py:1768`

### IR-P9-2-WHOLE-R3-02 — FIXED CANDIDATE

- Semantic Case Packをrev-2へ更新し、Current／Updated／Deleted、RAG Off／Relevant／Irrelevant／NO_HIT with Main Call／Strict NO_HIT Call 0、Belief Revision、False Improvement、Composition Matrixの全11 CaseをRevision付きManifestへ登録した。
- `SemanticEvaluatorRoute`をCase Digestへ含め、Case→Fixture Adapter→Deterministic EvaluatorのRoutingを明示した。
- `CaseSemanticEvidence(execution_mode="fixture")`をRaw EvidenceとComparison Rowへ永続化し、Case ID／Revision不一致をTyped Rejectする。
- `false_positive`、`false_grounding`、`correction_acceptance`は対応するFixture Evidenceが解決した場合だけboolを持ち、未観測は`None`のまま保持する。
- False Improvementは、明示的なFixture OracleとRuntime Repair AdoptionからFixture metricを導出する一方、Human Observationは`NOT_RUN / human_review_pending`のまま保持する。Human判定用`RepairSemanticOutcome`をFixture Oracleとして流用しない。
- Production RowへFixture Semantic Evidenceを注入せず、3つのSemantic metricは未観測`None`のまま保持する回帰を確認した。

Evidence:

- `src/margpa_runtime_llm/modules/experiment/domain/dataset.py:41`
- `src/margpa_runtime_llm/modules/experiment/domain/case_pack.py:20`
- `src/margpa_runtime_llm/modules/experiment/domain/case_pack.py:129`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py:27`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py:57`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:325`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py:145`
- `tests/integration/web/test_experiment_routes.py:1804`
- `tests/integration/web/test_experiment_routes.py:853`

### IR-P9-2-WHOLE-R3-03 — FIXED CANDIDATE

- 公開PresetのDeterministic Fixture経路へ、Main／Judge／Guard／Main Governance／Definition／RAG／Repair／Recording／Strict Buffer／ProgressiveとCall-0 Variantを接続した。
- `VariantComparisonDeclaration`をComparison artifactへ永続化し、保存前にPlan内の実Variantを使って単一要因差を再計算する。Baseline／Regression／Ablationを読み戻せ、複数要因差のGuard short-circuitは単一要因関係として宣言しない。
- Multiple DefinitionのMatch／Conflict／Suppression、Manual／Static／Dynamic Routing、Repair要求元を各RunのSemantic Evidenceへ接続した。
- Strict／Progressive状態列を実Fixture Runから生成した。
- Manual URL Fail-closed、Strict NO_HIT、Guard short-circuitのMain Call 0を、Raw Actor Invocationの`called=False`とExecution Traceの両方へ接続した。手作りProjectionだけをAcceptance Evidenceとしていない。
- Restart後のComparisonにRow、Semantic Evidence、Variant Relationshipが残ることをFresh Storeで確認した。

Evidence:

- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:84`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:119`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:171`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:231`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py:119`
- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py:79`
- `src/margpa_runtime_llm/web/experiment_routes.py:1109`
- `src/margpa_runtime_llm/web/experiment_routes.py:1257`
- `tests/integration/web/test_experiment_routes.py:1945`

## 3. Top-level Acceptance Matrix

単体Classifier／型生成だけを成立根拠にせず、Web APIのPlan→Run→Raw Evidence→ComparisonとFresh Store Restart Readを中心Evidenceとした。FixtureがLive Model／Artifactを持つようには偽装していない。

| Requirement／Acceptance | Top-level Disposition | Decisive Evidence／Boundary |
|---|---|---|
| P9-REQ-201／P9-ACC-039 | FIXTURE PATH PASS、LIVE ARTIFACTは既存Production Adapter境界 | 共通Fixture helperがExperiment／Case／Plan Digest、Run／Request／Variant、Case Revisionを相関し、Fixture Desired/Frozen Config Digestは正しく`None`。Live Config／Model Provider／Frozen Digest相関はFake Productionの既存Top-level Testで維持。Real Model ArtifactはNOT RUN。`tests/integration/web/test_experiment_routes.py:198`、`:808`、`:1188` |
| P9-REQ-202／P9-ACC-040 | PASS | 同一Versioned Composition CaseでMain／Judge／Guard／Main Governance／Definition／RAG／Repair／Recording／Presentationの実Fixture Invocationを比較。`tests/integration/web/test_experiment_routes.py:1945` |
| P9-REQ-203／P9-ACC-045 | PASS（Human結果自体はNOT RUN） | False ImprovementのFixture metricとHuman `NOT_RUN`を分離し、Baseline／Regression／Ablationを同じComparisonへ永続化。`tests/integration/web/test_experiment_routes.py:1804`、`:1945` |
| P9-REQ-204／P9-ACC-041 | PASS | Match／Conflict／Suppression、Manual／Static／Dynamic、Repair originを比較RowのEvidenceからHard Assert。`tests/integration/web/test_experiment_routes.py:2018` |
| P9-REQ-205／P9-ACC-042 | PASS | Current無関係回答非PASS、Updated／Deletedを個別Versioned Caseで実行・比較・Restart Read。`tests/integration/web/test_experiment_routes.py:1768`、`:1804` |
| P9-REQ-206／P9-ACC-042 | PASS | RAG Off／Relevant／Irrelevant／NO_HIT with call／Strict NO_HIT Call 0を実行し、False Grounding metricとMain Call Evidenceを比較。`tests/integration/web/test_experiment_routes.py:1804` |
| P9-REQ-207／P9-ACC-043 | PASS（Human ReviewはNOT RUN） | Belief RevisionのCorrection Acceptance true/falseを実Run Evidenceから導出。False ImprovementはFixture Oracleで明示しHuman Observationを代用しない。`tests/integration/web/test_experiment_routes.py:1804` |
| P9-REQ-208／P9-ACC-044 | PASS | Strict BufferのFinal-onlyとProgressiveのStarted→Generating→Evaluating→Finalizedを比較Evidenceへ永続化。`tests/integration/web/test_experiment_routes.py:2035` |
| P9-REQ-209／P9-ACC-044 | PASS | Manual URL Fail-closed／Strict NO_HIT／Guard short-circuitのCall 0をRaw InvocationとTraceの両方でHard Assert。`tests/integration/web/test_experiment_routes.py:1904`、`:2052` |
| P9-ACC-045横断 | PASS（Controller再判定待ち） | ReportがCase／Run／Rubric／Semantic metric truthをTyped検証し、Variant Relationshipの単一要因差をPlanから再検算して永続化。Production semantic未観測は`None`。`src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py:36`、`src/margpa_runtime_llm/modules/experiment/application/comparison_service.py:93` |

## 4. Sabotage-regression

各Findingの主要Oracleを一時的に修正前相当へ戻し、新規Top-level TestがFAILすることを確認した直後に`apply_patch`で完全復元した。Stash／Backupは使用していない。

| Finding | 一時Sabotage | 検出結果 |
|---|---|---|
| R3-01 | CURRENTで本文を見ず無条件`CURRENT_FACT_USED`へ戻す | `"I am not sure."`が`pass`となり、期待`inconclusive`との差でTop-level Test FAIL |
| R3-02 | Fixture metric生成時にSemantic Evidenceを渡さない | Persist対象metricの未観測tupleとSemantic Evidence truthが不一致になり、Top-level Semantic MatrixがFAIL／Comparisonがfail-closed |
| R3-03 | ComparisonへVariant Relationshipを渡さない | 永続ComparisonのBaseline／Ablation AssertでTop-level Composition Test FAIL |

復元後の主要Top-level 3件: `3 passed`。最終Phase 9-2 Backend scopeでも全件PASSした。

## 5. Validation

| Validation | Result |
|---|---|
| Finding-focused Unit／Integration | `99 passed in 3.09s` |
| R3主要Top-level 3件（最終補強後） | `3 passed, 26 deselected in 1.19s` |
| Phase 9-2 Backend scope（最終） | `279 passed in 4.23s` |
| Frontend Full | `34 files / 339 tests` PASS |
| Frontend typecheck | PASS |
| Frontend lint | PASS |
| Frontend build | PASS、60 modules transformed、canonical static asset生成 |
| Changed Python paths Ruff（最終） | `All checks passed!` |
| Changed Python paths Mypy（最終） | `Success: no issues found in 9 source files` |
| `git diff --check`（最終） | PASS |

非Model Backend Full Suiteは本R3で再実行していない。先行R1の`2680 passed, 43 deselected`を保持し、本R3変更範囲はFocused、Phase 9-2 Backend 279件、Frontend Full 339件、Staticで検証した。

Tooling note: 最終Staticを`uv run`で包む最初の試行は、`uv`既定CacheがProject Root外の`/Users/yukitakagi/.cache/uv`を開こうとしてSandboxで実行前に拒否された。Root外Mutationは成立していない。以後はProject内`.venv/bin/ruff`／`mypy`を直接実行してPASSを確定し、同試行を反復していない。

## 6. Changed Paths for This R3 Rework

Product:

- `src/margpa_runtime_llm/modules/experiment/domain/freshness.py`
- `src/margpa_runtime_llm/modules/experiment/domain/dataset.py`
- `src/margpa_runtime_llm/modules/experiment/domain/case_pack.py`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py`（new）
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py`（new）
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py`
- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`
- `frontend/src/types.ts`
- `src/margpa_runtime_llm/web/static/app.js`（Frontend canonical build artifact）

Tests:

- `tests/unit/experiment/test_freshness_case.py`
- `tests/unit/experiment/test_case_evaluator.py`
- `tests/unit/experiment/test_case_pack.py`
- `tests/unit/experiment/test_comparison_report.py`
- `tests/integration/web/test_experiment_routes.py`

Docs（Append-only）:

- 本Recovery
- 対になるR3 Exact Return

## 7. Two-perspective Self Review

1. Acceptance truth／Provenance観点: Case Manifest revisionとEvaluator routeをPlan Digestへ固定し、Fixture Semantic EvidenceだけをFixture Rowへ運び、未観測metricを`None`、Human Reviewを`NOT_RUN`として維持した。自己Review中、Human専用`RepairSemanticOutcome`をFixture Oracleへ流用していた混同を検出し、Runtime Adoption＋明示Fixture Outcomeからの独立導出へ修正した。Fixture Config Digestを非`None`と誤期待した補強TestもFAILで検出し、FixtureはLive Snapshotを読まない正しい`None` Assertへ修正した。修正後にBlocker／Major残件を検出していない。
2. Persistence／Adversarial false-success観点: Metric対Semantic Evidence、Run／Case／Rubric identity、単一要因DeclarationをTyped validatorでfail-closedにし、Restart後も同一Artifactを再検証した。Call 0はTraceだけでなくActor Invocation Counterでも確認し、ProductionへFixture Oracleが漏れないことを回帰した。修正後にBlocker／Major残件を検出していない。

## 8. Open Boundary

- Real Model／Real Browser／User Manual: `NOT RUN`（Authorityで禁止）。
- False ImprovementのHuman評価: `NOT RUN / human_review_pending`。Fixture metricはHuman PASS／FAILの代替ではない。
- ProductionのSemantic metric: 対応する実Evidenceが未観測のため`None`。Fixture結果をReal Model結果として表示しない。
- Phase 9-2 Complete／Closure: `NOT CLAIMED`。最終DispositionはController Independent Re-review所有。
- R2で記録済みのCancel失敗時表示改善Minor候補はScope外のまま。

## 9. Exact Next Action

Controller Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`が`IR-P9-2-WHOLE-R3-01`〜`03`と上記Top-level Acceptance MatrixをIndependent Re-reviewする。本TaskはExact Return後に停止し、追加修正、Phase 9-2完了承認、User Manual、Phase 9-3／10、Closure、Gitへ進まない。
