# P9-1-B Semantic 109／Built-in Evaluation — Package Recovery

```yaml
document_id: phase_9_1_p9_1_b_semantic_109_recovery_20260901010000
document_type: compact_recovery_index
language: ja
created_at: 2026-09-01 01:00 JST
phase: phase_9
program: phase_9_1
package: P9-1-B
disposition: COMPLETE
```

## 1. 中心的Finding（WU-001／WU-002／WU-003の実態）

`semantic_criterion_adapter.py`の`_ARGD_MAP`／`_mapping_for()`を実読した結果、109件の
Canonical Descriptorは**全件**`SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE`／
`ABSOLUTE_SCORING`／`CLASSIFICATION`のいずれかへ写像される――3種いずれも「決定的Checkでは
誠実に解決できない質的判断」である。既存Test
`test_canonical_corpus_compiles_all_109_descriptors_without_silent_drop`が109/109の無欠落
Compileを既に証明している。

`_run_built_in_semantic_judge()`（`judge_live_integration.py`）自身のDocstringも同じ結論を
明記しており、既存Test（`test_built_in_judge_reports_every_semantic_criterion_as_not_
applicable`／`test_built_in_judge_reports_not_applicable_never_as_evaluated_or_unknown`）が
Built-in Judgeが**109件中0件**しか実評価できないことを既に証明している。これはBugでは
なくPhase 6 P6-RR-N-WU-001／P6-RR-R3-WU-005で審査済みのArchitecture上の結論である。

**結論**: WU-001（Inventory）／WU-002（Normalized IR -> Semantic Criterion変換Registry拡張）
／WU-003（Built-in対応Criterionの実評価）は、いずれも**追加実装ではなく検証**で完結した。
Built-inの「対応Criterion」集合は空集合であり、これは正しい。109 Deferred／evaluated 0から
脱却する唯一のAuthority非依存経路は、Built-inの改善ではなく**Main-shared自己Judge**
（MainのRoleに既にLoad済みのModelをそのままJudgeとして使う。専用Load／Artifact／Networkを
一切要求しない）である。User Mac Evidenceが観測した「全件Deferred／evaluated 0」は、User
自身が`Judge Built-in Deterministic`（構造的にゼロ評価しかできないProvider）を選択していた
ことの正しい帰結であり、Main-shared自己Judgeへ切り替えれば同じProduction Codeパスが
既に実評価する。

## 2. WU-004: 実施内容

既存`test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_provider`
（`test_judge_live_integration_dispatch_router.py`）はRouting／Tagging止まりで、
Criterion無しの汎用応答（`recommendation`のみ）しかExerciseしていなかった。

新規Test`test_main_shared_active_adapter_genuinely_evaluates_semantic_criteria`を追加し、
実Semantic Snapshot（1 Criterion）付きでMain-shared Dispatchを駆動、`criterion_results`を
含む正しいJudge Decode JSONをFake Serviceへ返させ、次を証明した。

- `service.calls`が実際に1回、正しい`model_key`で呼ばれる（実LLM呼び出し）。
- `result.criteria_evaluated == 1`（Deferred/0から脱却する実証）。
- `result.criteria_passed == 1`、`criteria_deferred == 0`。
- `semantic_result_recorder`が実Decode結果からLosslessに1件Recordする
  （`_record_semantic_result()`のCriterion Identity／Descriptor突合を経由）。

Regression Guard: `_judge_criterion_counts()`の`evaluated=passed+deviated`を`evaluated=0`へ
一時破壊し、新規Testが実際に`assert 0 == 1`でFailすることを確認してから復元、diff完全一致
確認。

## 3. WU-005: 実施内容

Golden Caseは上記WU-004の新規Testが担う。Negative／Malformed／Budget／Cancel／Restartは
既存Preserved As-built Testが既に厳密に担っており、再実装不要と判断した（確認のみ）。

```text
test_judge_enforce_also_runs_and_malformed_output_fails_closed          既存・PASS
test_presented_final_enforce_turns_malformed_judge_output_into_safe_fallback  既存・PASS
test_built_in_judge_reports_every_semantic_criterion_as_not_applicable  既存・PASS
test_built_in_judge_reports_not_applicable_never_as_evaluated_or_unknown 既存・PASS
test_built_in_enforce_resolves_synchronously_with_zero_pipeline_budget_no_race 既存・PASS
test_canonical_corpus_compiles_all_109_descriptors_without_silent_drop  既存・PASS
```

Cancel時のMain-self Dispatchも`_record_semantic_result(provider_state=FAILED,
criterion_results=(), ...)`を経由する既存Codeで、Criteriaを捏造Evaluatedへ格上げしない
Fail-closed設計を確認済み（無改造）。

## 4. Changed Paths

```text
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py  (modified: +1 test)
```

`judge_live_integration.py`本体、`semantic_criterion_adapter.py`、`runtime_governance/`は
無変更（Preserved As-built）。

## 5. Test Result

```yaml
package_regression:
  scope: >-
    tests/unit/runtime_governance, tests/unit/governance_definitions,
    tests/unit/bootstrap, tests/unit/evaluation
  result: "369 passed"
mypy: clean (touched file)
ruff_check: clean (touched file)
ruff_format: clean (touched file)
```

## 6. Authority／Action Inventory

```yaml
real_artifact_touched: false
network_used: false
real_model_load: false
git_mutation: false
user_runtime_data_touched: false
```

## 7. Exact Next Action

```text
P9-1-C（Judge／Repair／Rejudge／Semantic ENFORCE）へ進む。
P9-1-C-WU-001から開始し、Main Candidate、Frozen Context、Independent Judge Dispatchおよび
Strict DecodeがProduction Turnへ配線されていることを確認する。P9-1-Bで確認した通り、
Selene（P9-1-A同様Authority Gate内）とMain-shared（Authority非依存）の双方でRepair／Rejudge
経路が既にCodeとして接続されていることは判明済みのため、WU-002以降はMain-shared経路の
Repair Eligibility／Rejudge Evidence連鎖を中心にVerifyする。
```
