# P9-1-C Judge／Repair／Rejudge／Semantic ENFORCE — Package Recovery

```yaml
document_id: phase_9_1_p9_1_c_judge_repair_rejudge_enforce_recovery_20260901020000
document_type: compact_recovery_index
language: ja
created_at: 2026-09-01 02:00 JST
phase: phase_9
program: phase_9_1
package: P9-1-C
disposition: COMPLETE
```

## 1. Work Unit別Disposition

```text
P9-1-C-WU-001  Main Candidate／Frozen Context／Judge Dispatch／Strict Decode配線  VERIFIED（既存）
P9-1-C-WU-002  Judge Outcome -> Repair Eligibility／Plan／Budget／Candidate      NEW TEST
P9-1-C-WU-003  Repair Candidate -> Rejudge -> Adopt／Reject／Fallback収束        NEW TEST
P9-1-C-WU-004  Semantic ENFORCE Supported Action／Conflict／Priority／Authority  NEW TEST
P9-1-C-WU-005  Cancel／Deadline／Provider Failure／Malformed／Late／OFF／Shutdown VERIFIED（既存）
P9-1-C-WU-006  Configured／Active／Executed／Criterion／Judge／Repair／Rejudge/Recording Identity Chain  NEW TEST
```

## 2. 実施内容

### WU-001／WU-005（検証のみ・追加実装なし）

`judge_live_integration.py`を実読し、Main Candidate、Frozen Context（`JudgeCompletionContext`）、
Independent Judge Dispatch（Built-in／Selene／Main-shared 3分岐）、Strict Decode
（`decode_judge_output_fail_closed`）はすべて既にProduction Turnへ配線済みで、Stub／
TODOは皆無であることを確認した（`grep`で無検出）。Cancel／Deadline／Provider Failure／
Malformed／Late Result／Shutdownは`test_judge_live_integration.py`に既に厚いPreserved
As-built Coverageがある：

```text
test_inference_stage_deadline_actually_interrupts_a_slow_model_call
test_prompt_build_stage_deadline_interrupts_a_slow_builder_with_no_late_publish
test_decode_stage_deadline_interrupts_a_slow_decoder_with_no_late_publish
test_presented_final_enforce_deadline_is_bounded_and_late_worker_cannot_overwrite
test_enforce_cancel_before_terminal_authorization_discards_pending_evidence
test_main_preemption_reaching_judge_produces_cancelled_terminal_state
test_judge_enforce_also_runs_and_malformed_output_fails_closed
```

Mode OFF／ShutdownはPackage Aで検証済みの`RoleProviderLifecycleManager`（Preserved As-built）
が担う。いずれも再実装・追加Testは不要と判断した。

### WU-002／WU-003／WU-006（新規Test 1件）

既存の`test_selene_initial_judge_repair_and_frozen_selene_rejudge_single_turn_e2e`は
Initial Judge -> Repair -> Frozen Rejudgeを1本のTurnとして証明しているが、Selene限定で
（本Task未保有のReal Artifact Authorityが必要）、この経路はCode上Connected／Fixture-tested
ではあるが実行不能である。

`test_main_shared_judge_needs_repair_and_rejudge_reuses_the_same_main_service_single_turn_e2e`
（新規、`test_judge_live_integration_dispatch_router.py`）を追加し、Authority非依存で
実際に到達可能なMain-shared自己Judge経路について同じ証明を行った。

- 実Semantic-109 Criterion 1件がDEVIATIONへ解決 -> `needs_repair`。
- Repair Eligibility ELIGIBLE、Repair Executorが実際に呼ばれる。
- **Rejudgeの実Identityは、同じ既にLoad済みMain Service／Providerそのもの**
  （`rejudge_service is service`、`rejudge_model_key == _DEEPSEEK_PROVIDER_ID`、
  `rejudge_role is JudgeIndependenceClass.MAIN_SELF`）――Selene版のS9 Regression
  Scenarioと同じ「Frozen Identityの連鎖」を、Authority非依存経路で証明した。
- Turn Leaseは1回のみAcquire／Release（`release.released == [...]`で確認）。
- `criteria_evaluated == 1`／`criteria_deviated == 1`（P9-1-B脱却経路の再確認）。

Regression Guard: `rejudge_service=service`を`rejudge_service=None`へ一時破壊し、新規Testが
実際にFail（`assert None is <FakeInferenceService>`）することを確認してから復元、diff完全
一致確認。

### WU-004（新規Test 3件）

`resolve_semantic_action()`（`runtime_governance/application/semantic_runtime.py`、Preserved
As-built）は`if has_uncertain / if has_deviation`の優先順位で実装されているが、既存の唯一の
Test（`test_action_resolver_keeps_recommendation_separate_from_execution`）は単一Criterion・
`main_mode="observe"`のみで、複数Criterion間のConflict／Priorityも、実`main_mode="enforce"`の
Deviation／Uncertain分岐も一度も演習していなかった。

新規Test 3件（`tests/unit/runtime_governance/test_semantic_runtime.py`）を追加した。

1. `test_enforce_conflict_uncertain_takes_priority_over_deviation` — Uncertain 1件 +
   Deviation 1件の同時ConflictでUncertainが優先しSafe Fallbackへ収束することを証明。
2. `test_enforce_multiple_deviations_resolve_as_one_repair_request_when_authorized` —
   PassとDeviationの混在が単一の一貫したRepair Requestへ収束することを証明。
3. `test_enforce_deviation_never_executes_repair_when_repair_authority_is_off` —
   Authority非拡張：`repair_mode="off"`ではRecommendationは正直にREPAIR_REQUESTEDのまま、
   Executed DispositionはSafe Fallbackへ留まり、`repair_eligible`はFalseのままであることを
   証明。

Regression Guard: `has_uncertain`／`has_deviation`の分岐順序を一時的に入れ替え、Test 1が
実際に`REPAIR_REQUESTED != SAFE_FALLBACK`でFailすることを確認してから復元、diff完全一致
確認。

## 3. Changed Paths

```text
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py  (modified: +1 test)
tests/unit/runtime_governance/test_semantic_runtime.py               (modified: +3 tests)
```

`judge_live_integration.py`、`semantic_runtime.py`本体は無変更（Preserved As-built）。

## 4. Test Result

```yaml
package_regression:
  scope: >-
    tests/unit/bootstrap, tests/unit/repair, tests/unit/runtime_governance,
    tests/unit/evaluation, tests/unit/governance_definitions
  result: "406 passed"
mypy: clean (touched files)
ruff_check: clean (touched files)
ruff_format: clean (touched files)
```

## 5. Authority／Action Inventory

```yaml
real_artifact_touched: false
network_used: false
real_model_load: false
git_mutation: false
user_runtime_data_touched: false
```

## 6. Exact Next Action

```text
P9-1-D（Integration／二段階Review／Return Candidate）へ進む。
P9-1-D-WU-001から開始し、通常Chat、RAG、Citation、Manual URL、Dev Agent、Persistence、
Cancel／RestartのFocused Regressionを実施する。続けてCanonical Backend／Mypy／Ruff検証、
観点変更二段階Internal Review（Cycle 1: Requirement／Negative Path／Concurrency／Resource、
Cycle 2: Evidence Truthfulness／Acceptance／User Journey／PoC停止線）を行い、Exact Return
Handoffを作成してCodex Controller Review待ちで停止する。
```
