# Phase 9-2 Whole Scope R4 Evidence Truth Rework Recovery

記録時刻: 2026-09-09 12:54:04 JST  
実行役: 設計者兼実装者役（Task `01a03b6c-2a68-7881-99bc-c788a600f632`）  
Controller: プロジェクト責任者兼設計統括者役（Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`）

## 1. Recovery State

- State: `P9_2_WHOLE_SCOPE_R4_EVIDENCE_TRUTH_REWORK_CANDIDATE_FOR_CONTROLLER_REREVIEW`
- Authority: `phase_9_controller_phase_9_2_whole_scope_r3_residual_evidence_truth_rework_handoff_ja_20260909122244.md`
- Scope: `IR-P9-2-WHOLE-R4-01`〜`03`と直接必要なFixture Adapter／Case・Variant Contract／Evaluator／Comparison／Testだけ。
- Phase 9-2 Complete／Closure、Real Model、Real Browser、User Manual、Phase 9-3／10、Git write／Commit／Push／Stash／Cleanは実行・主張していない。
- 先行R1〜R3差分、既存Dirty Working Tree、Controller-owned concurrent artifactはRollback／Clean／意味変更せず保持した。

## 2. IR-P9-2-WHOLE-R4-01 — FIXED CANDIDATE

### Before Probe

```text
current_source_value = "000"
answer = "000 is not the current value; 765 is current."
actual = current_fact_used
expected = non-PASS
```

新規Probe Testを修正前に実行し、`actual=current_fact_used`対`expected=insufficient_evidence`で1件FAILすることを固定した。

### After

- `classify_freshness_answer()`へ、回答文字列とは独立したRule／Judge Evidence `current_value_adopted`を追加した。
- `current_value_adopted is True`かつCurrent Valueが実回答へ存在する場合だけ`CURRENT_FACT_USED`となる。単なる出現、引用、否定、無関係、空、EvidenceなしはPASSにならない。
- `CaseSemanticEvidence.answer_adopts_current_value`をRaw Evidence／Comparisonへ永続化した。`CURRENT_FACT_USED`なのに明示Adoption Evidenceがない矛盾はTyped validationで拒否する。
- Historical Citation Digest改変の最優先、Updated／Deleted、Production semantic未観測`None`を維持した。
- Evaluator意味変更を同一Revisionとして再解釈しないためCase Pack Revisionを`phase-9-2-semantic-research-case-pack-rev-3`へ更新した。

After raw values:

```text
direct negative probe outcome = insufficient_evidence
top-level affirmative = answer_adopts_current_value:true / observation:pass
top-level unrelated = answer_adopts_current_value:false / observation:inconclusive
top-level negative = answer_adopts_current_value:false / observation:inconclusive
restart negative = answer_adopts_current_value:false / observation:inconclusive
```

Evidence:

- `src/margpa_runtime_llm/modules/experiment/domain/freshness.py:47`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py:27`
- `src/margpa_runtime_llm/modules/experiment/domain/case_pack.py:20`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py:140`
- `tests/unit/experiment/test_freshness_case.py:47`
- `tests/integration/web/test_experiment_routes.py:1774`

### Sabotage

Adoption Evidence条件を一時除去して旧substring判定へ戻すと、否定文Probeが再び`current_fact_used`になり新規Unit TestがFAILした。直後に`apply_patch`で完全復元し、最終Scope TestでPASSを再確認した。

## 3. IR-P9-2-WHOLE-R4-02 — FIXED CANDIDATE

### Before Probe

```text
fixture-main-active.components == fixture-manual-url-fail-closed.components = true
fixture-main-active.main.called = true
fixture-manual-url-fail-closed.main.called = false
```

Top-level Probeを修正前に追加し、同一Main Selectionであることを検出してFAILした。

### After

- Manual URL Fail-closedをMain Selection mode `manual_url_fail_closed`、Guard short-circuitをGuard Selection mode `short_circuit`としてPlanへ明示した。両modeはPlan Digestの実入力であり、Variant ID分岐ではない。
- `_execute_components()`／`_trace_for()`からManual URL／Guardの`variant_id`条件を除去し、同じComponent SelectionからInvocationとTraceを一度に導出する。
- Manual URLは`fixture-main-active`との差をMain 1要因、Guard short-circuitは同Baselineとの差をGuard 1要因として、実Planから再計算したRelationshipをComparisonへ永続化する。
- 同一Configで名前だけが違う`fixture-main-active-replica`をReplication controlとして追加し、Main Invocation、全Invocation、Trace stages、Dispositionが一致することをTop-levelでHard Assertした。
- Strict NO_HITはCase ID文字列分岐ではなく、Revision付きRetrieval Caseの`STRICT_NO_HIT_MODEL_CALL_ZERO` Scenario Contractから導出する。

After raw values:

```text
main-active vs manual-url identical_components = false
main-active.main.called = true
manual-url.main.called = false
manual-url.trace.disposition = failed
manual-url relationship varied_component_keys = [main]
guard-short-circuit relationship varied_component_keys = [guard]
main-active vs replica identical_components = true
main-active vs replica invocations_equal = true
main-active vs replica trace_stages/disposition_equal = true
```

Evidence:

- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:79`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:91`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:230`
- `src/margpa_runtime_llm/web/experiment_routes.py:128`
- `src/margpa_runtime_llm/web/experiment_routes.py:208`
- `tests/integration/web/test_experiment_routes.py:1979`

### Sabotage

Manual URL VariantのMain modeを一時的に`active`へ戻すと、Comparison生成が`actual diff touches 0 components`を検出してHTTP 409 `multi_factor_difference`となり、Top-level TestがFAILした。明示modeへ完全復元した。

## 4. IR-P9-2-WHOLE-R4-03 — FIXED CANDIDATE

### Before Probe

```text
called = [judge, definition_set, repair]
main_governance.called = false
actual repair_propagation = judge_and_main
expected repair_propagation = judge
```

Top-level Probeを修正前に実行し、`judge_and_main`対`judge`でFAILすることを固定した。

### After

- Judge request mode `enforce_repair_requested`とMain Governance request mode `strict_repair_requested`を明示Component SelectionとしてPlanへ固定した。単なるJudge ENFORCE／Main Governance STRICTやVariant名をRequester Evidenceにしない。
- Fixture実行を二段階化した。まずRepair Actorを除外してRequester候補Actorを実行し、実際にCalledかつ明示request modeだったActorだけから`judge`／`main_governance`／`judge_and_main`を導出する。その後、Repair mode有効かつObserved Requesterありの場合だけRepair Actorを1回実行する。
- Repair modeだけでRequesterがない場合、Repairは`called=False`、Raw outcome=`call_zero:no_eligible_repair_requester`、Trace reason=`no_eligible_repair_requester`、`repair_adopted=False`となる。
- `CaseSemanticEvidence`が、Accepted Repair without Requester、Repair Trace CallとAdoption不一致、Governance propagationとRequester不一致を拒否する。
- `ComparisonRow`がmetric `repair_adopted`とPersisted Semantic Evidenceの矛盾を拒否する。
- Belief Revision／False Improvementは、Requesterを持つ`fixture-judge-enforce-no-repair`と、同一ConfigでRepairだけ有効にした`judge-enforce-repair`を比較する。Repair差はPlanから1要因として再計算される。
- Definition Judge requester、Main Governance requester、両RequesterをTop-level ComparisonとFresh Store Restart Readで個別検証した。

After raw values:

```text
definition+judge+repair: requester=judge / repair.called=true / repair_adopted=true
repair-mode-only: requester=None / repair.called=false / repair_adopted=false
main-governance+repair: requester=main_governance / repair.called=true
judge+main-governance+repair: requester=judge_and_main / repair.called=true
belief/false-improvement no-repair baseline: requester=judge / repair_adopted=false
belief/false-improvement repair variant: requester=judge / repair_adopted=true
```

Evidence:

- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:199`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:213`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py:230`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py:57`
- `src/margpa_runtime_llm/modules/experiment/domain/trace.py:36`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py:67`
- `src/margpa_runtime_llm/web/experiment_routes.py:1185`
- `tests/integration/web/test_experiment_routes.py:1826`
- `tests/integration/web/test_experiment_routes.py:1979`
- `tests/unit/experiment/test_comparison_report.py:274`

### Sabotage

Judge-onlyのObserved Originを一時的に`judge_and_main`へ戻すと、Top-level ComparisonのRequester Assertが`judge_and_main != judge`でFAILした。直後に完全復元し、最終Scope TestでRequester／Call／Adoption／Restart Readの全Assertを再確認した。

## 5. Validation

| Validation | Result |
|---|---|
| Controller Probe Before R4-01 | `1 failed`、actual=`current_fact_used` |
| Controller Probe Before R4-02 | `1 failed`、identical Main Selectionを検出 |
| Controller Probe Before R4-03 | `1 failed`、actual=`judge_and_main` |
| Restore後R4主要Top-level | PASS |
| Handoff記載の既存66件を包含するPhase 9-2 Backend scope（最終） | `283 passed in 4.45s` |
| Frontend Full | `34 files / 339 tests` PASS |
| Frontend typecheck | PASS |
| Frontend lint | PASS |
| Frontend build | PASS、60 modules transformed |
| Changed Python paths Ruff | `All checks passed!` |
| Changed Python paths Mypy | `Success: no issues found in 8 source files` |
| `git diff --check` | PASS |

Real Model／Browser／User Manualは実行していない。非Model Backend Full全体も本Bounded R4では再実行せず、Phase 9-2対象を包含する283件とFrontend影響範囲で検証した。

## 6. R4 Changed Paths

Product:

- `src/margpa_runtime_llm/modules/experiment/domain/freshness.py`
- `src/margpa_runtime_llm/modules/experiment/domain/semantic_evidence.py`
- `src/margpa_runtime_llm/modules/experiment/domain/trace.py`
- `src/margpa_runtime_llm/modules/experiment/domain/case_pack.py`
- `src/margpa_runtime_llm/adapters/experiment/semantic_fixture_adapter.py`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py`
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`

Tests:

- `tests/unit/experiment/test_freshness_case.py`
- `tests/unit/experiment/test_acceptance_mapping_p9_2.py`
- `tests/unit/experiment/test_case_evaluator.py`
- `tests/unit/experiment/test_comparison_report.py`
- `tests/integration/web/test_experiment_routes.py`

Generated validation artifact:

- `src/margpa_runtime_llm/web/static/app.js`（Frontend canonical build。R4のFrontend source変更はなし）

Docs（Append-only）:

- 本Recovery
- 対になるR4 Exact Return

## 7. Two-perspective Self Review

1. Declarative Identity／Hidden Factor観点: AdapterのBehavior分岐を検索し、Variant IDはRelationship登録とTrace identityにだけ残り、Invocation／Trace／Dispositionの判断には使われていないことを確認した。同一Config replicaが同じInvocation／Trace結果となり、Manual URL／Guard／Repair requestはPlan Digestへ入るComponent mode差として観測できる。Blocker／Major残件なし。
2. Evidence／Failure／Persistence観点: Repairは実Requester Call確認後だけ起動し、Raw Invocation、Trace、Semantic Evidence、Metric、Governance propagationを相互validationした。RequesterなしRepair、否定Freshness、同一Config別名、Restart Readをfail-closedで確認した。自己Review中、Judge ENFORCE自体をRequestと見なす曖昧さを検出し、専用request modeへ分離した。Blocker／Major残件なし。

## 8. Open Boundary

- Real Model／Real Browser／User Manual: `NOT RUN`（Authorityで禁止）。
- Production semantic未観測は引き続き`None`であり、Fixture EvidenceをProduction結果へ昇格していない。
- Fixture request modeはDeterministic Scenario Contractであり、Production Provider behaviorの成立主張ではない。
- Phase 9-2 Complete／Closure: `NOT CLAIMED`。最終DispositionはController Independent Re-review所有。

## 9. Exact Next Action

Controller Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`が`IR-P9-2-WHOLE-R4-01`〜`03`の生Probe値、Top-level Evidence、Sabotage、Restart ReadをIndependent Re-reviewする。本TaskはExact Return後に停止し、追加修正、Phase 9-2完了承認、User Manual、Phase 9-3／10、Closure、Gitへ進まない。
