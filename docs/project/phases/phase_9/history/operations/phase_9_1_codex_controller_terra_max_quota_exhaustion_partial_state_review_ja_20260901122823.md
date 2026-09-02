# Phase 9-1 Codex Controller Terra Max Quota Exhaustion Partial State Review

```yaml
document_id: phase_9_1_codex_controller_terra_max_quota_exhaustion_partial_state_review_20260901122823
document_type: append_only_controller_partial_state_independent_review
document_state: rework_required
language: ja
created_at: 2026-09-01T12:28:23+09:00
phase: phase_9
program: phase_9_1
provider: copilot
model: GPT-5.6 Terra
reasoning_effort: max
context_window: 400k
model_attribution_source: user_report
review_target: current_working_tree_after_monthly_ai_credits_exhausted
binding_handoff: phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_20260901113052
controller_disposition: rejected_partial_state_rework_required
phase_9_1_closure: not_claimed
```

## 1. 結論

Copilot `GPT-5.6 Terra Max / 400k`は、P9-CODEX-012のExternal Cancellation配線とP9-CODEX-013のSelene Bounded Batch化へMaterialなSource差分を残した。しかし、月間AI Credits Exhaustion時点でReturn、Recovery、Acceptance Runner、Real Evidence、二段階Internal Reviewへ到達せず、Current Working Treeは検証済みの安全なPartial Stateへ収束していない。

```text
P9-CODEX-011: OPEN
P9-CODEX-012: PARTIAL IMPLEMENTATION／MANDATORY THREAD EVIDENCE NOT RUN
P9-CODEX-013: PARTIAL IMPLEMENTATION／REGRESSION AND BUDGET DEFECT
P9-CODEX-014: OPEN

New Findings:
P9-CODEX-015: CRITICAL / CANONICAL REGRESSION AND TYPECHECK BLOCKER
P9-CODEX-016: MAJOR / SELENE WHOLE-STAGE DEADLINE MULTIPLICATION
P9-CODEX-017: MAJOR / RESOURCE HARD-STOP RECOVERY CONTRACT FAILURE
```

Phase 9-1 Complete Candidateは不成立である。今回のSource差分は全Rollback対象ではないが、成立済みとみなしてReal Manualへ進めない。

## 2. Review入力

- Binding Handoff:
  `docs/project/phases/phase_9/handoffs/phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_ja_20260901113052.md`
- SHA-512:
  `7d73a96a2539623bc7f4f3502a14b8df4feb76d0827a6fa3709e58ebca711bfc8926004687d3691630eaa7b431db3dd16ff563b945887471ca35fdbeadb4ad86`
- Entry Receipt:
  `docs/project/phases/phase_9/history/operations/phase_9_1_copilot_terra_max_fresh_p9_codex_011_014_entry_receipt_ja_20260901113601.md`
- Current Working Tree Source／Test。
- User提供のCopilot Log断片と2026-09-01 12:01／12:18〜12:19のScreenshots。

Copilotは月間AI Credits ExhaustionによりExact Returnを作成できなかったため、Current Working Treeを唯一の実装正本としてReviewした。

## 3. Current Working Treeで確認した実装前進

### 3.1 Selene

- `SeleneSemanticEvaluator`を単一無制限PromptからCriterion Batchへ変更。
- `max_criteria_per_call=8`、`max_calls=4`、Prompt／Output Token上限をContract化。
- Runtime Context Sizeを考慮したPrompt Fit判定。
- Budgetに収まらないCriterionを`budget_exhausted` Deferredへ分類。
- Turn Cancellationを`InferenceService.generate()`まで伝播。
- Tracked Stage WorkerとStage Deadlineを追加。
- Prompt／Call／Completion Token、Deferred数、Deadline／Cancelledを`SemanticEvaluationBudget`へ記録。

### 3.2 Qwen3Guard／Guardrail

- Guardrail Hook、Point Runtime、Detector PortへTurn-owned Cancellationを通す形へ変更。
- Conversation SessionのUser Stop TokenをInput／Context Source／Output Candidateへ共有。
- Role LeaseとCancellation Tokenを対応付け、Mode OFF／ShutdownでActive LeaseのTokenをCancelする実装を追加。
- Qwen3Guard内部Deadline TokenをExternal TokenへLink。
- Timeout／Cancel後のLate Worker完了までLease ReleaseをDeferredする設計を維持。

### 3.3 Provenance

- Selene Official CopyとProject-derived Contractの区別を維持。
- `official_upstream_revision=null`、Project-derived Basis、Template Digest、Project Contract Digestを分離。
- `unknown_network_prohibited`をExact Revisionとして扱わない形へ前進。

これらはP9-CODEX-012／013の正しい方向へのMaterial Progressであり、理由なく全Rollbackしてはならない。

## 4. Verification結果

### 4.1 Syntax

```text
./.venv/bin/python -m compileall -q src/margpa_runtime_llm
PASS
```

### 4.2 Terra Max差分中心のFocused Test

```text
184 passed in 1.55s
```

対象:

- Selene Prompt／Decoder。
- Judge Dispatch Router。
- Qwen3Guard Detector／Adapter／Hook。
- Semantic Runtime。
- Role Lifecycle。
- Web CLI。

### 4.3 Production Wiring／Conversation／Integration追加検証

```text
137 passed
2 failed
2 deselected
```

失敗:

1. `test_selene_authority_granted_preflight_load_and_evaluate_wire_correctly`
2. `test_selene_role_adapter_composes_with_the_real_lifecycle_manager`

どちらもAuthority ONのSelene実Composition Fixtureで、`SemanticEvaluationResponse.provider_state`が期待する`active`ではなく`unavailable`へ退行した。

### 4.4 Canonical Backend Full Suite

```text
2214 passed
2 failed
7 deselected
78.10 seconds
```

Focused Testだけでは検出されず、Canonical Full Suiteで同じ2件のSelene Production Wiring Regressionが再現した。

### 4.5 Ruff／Mypy

```text
ruff check src tests
PASS

mypy src tests
FAIL: 45 errors in 5 files
```

Source側の直接Error:

- `selene.py`: `criteria`引数を`str`へ上書きする型不整合と、Replacement値のUnion混入。
- `judge_live_integration.py`: Optional CallableのNarrowing不足で`None not callable`。

Test側の大量Error:

- `DetectorPort.detect()`へCancellation引数を追加した結果、既存Test Double群がProtocolを満たさなくなった。
- Stream Guard、Point Runtime、Conversation Integrationを含む既存Typed Test境界が未修復。

## 5. P9-CODEX-015 — Canonical Regression／Typecheck Blocker

Severity: `CRITICAL / MVP BLOCKER`

Terra MaxはFocused Testを複数回実行したが、Binding Handoffが必須としたCanonical Full SuiteとMypy Cleanへ到達する前にQuota Exhaustionした。Current Working Treeは次の二点でComplete Candidateにできない。

### 5.1 Selene Production Wiring Regression

新しいBatch Plannerは`InferenceService.count_chat_prompt_tokens()`を前提にした。一方、既存Production Wiring Fixtureが包むModel Portは生成契約を満たすがToken Counterを持たず、Selene Evaluationは`selene_unavailable:*`へ収束する。

これは「Testだけが古い」と即断できない。Dedicated BackendのToken Counter Capabilityをどの層が保証するか、FixtureとProduction Contractを一致させた上で修復する必要がある。

### 5.2 Mypy 45 Errors

Source三件に加え、Cancellation対応のために`DetectorPort`全体を拡張した影響が既存Test Doubleへ広範囲に波及している。Runtimeが偶然動くことと、Typed Port Contractが成立していることは別である。

Required Rework:

1. Token Counter CapabilityをProduction Port／Fixture双方で正しく成立させる。
2. 上記2 Regression TestをPASSへ戻す。
3. Selene Prompt buildの変数Shadowingを除去する。
4. Judge CallableのNarrowingを型安全にする。
5. Cancellation対応PortをBackward-compatibleな別Protocolに分けるか、全実装／Test Doubleを正しく更新する。
6. Full Suite、Mypy、Ruffを再実行する。

## 6. P9-CODEX-016 — Selene Whole-stage DeadlineがBatch数倍へ増える

Severity: `MAJOR / SEMANTIC BUDGET BLOCKER`

`_run_selene()`はJudge Stageの`stage_budget.inference_budget_ms`をEvaluatorへ一度渡す。しかしEvaluatorは最大4 Batchの各Callに同じ全Budgetを再付与する。

```text
Run-level Budget: B
Batch 1 allowance: B
Batch 2 allowance: B
Batch 3 allowance: B
Batch 4 allowance: B
Worst-case inference allowance: approximately 4B + cancellation grace
```

`SemanticEvaluationBudget.inference_deadline_ms`は一つの値だけを記録するため、Evidence ReaderがWhole-stage Deadlineと誤読し得る。Binding Handoffが要求した「Bounded Batch＋明示Deadline」は、Call単位だけでなくJudge Stage全体としてBoundedである必要がある。

さらに、Current Testは1 Criterion中心であり、32 Selectedを4 Batchで実行してTotal Deadline／途中Timeout／Completed Batch／Remaining Deferredを確認していない。

Required Rework:

1. Absolute Whole-stage DeadlineまたはRemaining BudgetをBatch間で共有する。
2. Budget EvidenceにPer-callとWhole-stageを区別して記録する。
3. 32 Selected／4 BatchのSuccess、途中Deadline、Cancel、Partial CompletionをTestする。
4. Timeout時にCompleted Criterionと未実行CriterionのDispositionを正直に保持する。

## 7. P9-CODEX-012 Disposition — Sourceは前進、証明は未完了

Source Trace上、次の経路は配線された。

```text
Conversation User Stop
→ Session Guardrail Cancellation
→ Cancellation-aware Guardrail Hook
→ Point Runtime
→ Qwen3Guard Detector
→ Linked Call Token
→ Inference Service

Mode OFF／Shutdown
→ Role Lifecycle Active Lease lookup
→ Registered Cancellation cancel
→ Drain
→ Unload
```

ただしBinding Handoffが必須とした次のThread Regressionは未作成／未実施である。

1. User Stop mid-input-guard。
2. Mode OFF mid-context-source-guard。
3. Shutdown mid-output-candidate-guard。
4. External CancelとInternal DeadlineのRace。
5. Cancel後Late Complete／Late Publish 0。
6. Unload Exception時のTyped Degraded。

よってP9-CODEX-012は`PARTIAL IMPLEMENTATION`であり、Completeへ上げない。

## 8. P9-CODEX-011／014 Disposition

次は未作成である。

- `scripts/models/phase_9_1_real_dedicated_acceptance.py`
- Reproducible Real Selene／Qwen3Guard Production Evidence。
- P9-ACC-001〜038個別再導出Addendum。
- Corrected User Manual。
- Terra Max Package Recovery Index。
- Two-cycle Internal Review記録。
- Exact Return Handoff。

したがってP9-CODEX-011とP9-CODEX-014は`OPEN`のままである。Real ArtifactをMax Session中にLoad／InferenceしたEvidenceもなく、Medium Sessionの再現不能なDirect Smokeを昇格材料にしない。

## 9. P9-CODEX-017 — Resource Hard Stop時のRecovery未収束

Severity: `MAJOR / AUTOMATION RECOVERY BLOCKER`

Binding HandoffはResource Hard Stop接近時に、新WUへ入らずCurrent WUを安全に収束し、COMPLETE／PARTIAL／INVALID、Changed Paths、Last Test、Active Process、Exact Next ActionをRecoveryへ残すよう要求した。

実際にはMonthly AI Credits ExhaustionまでSource探索／編集を継続し、Entry Receipt以外のPackage Recoveryを残さなかった。結果としてControllerがScreenshots、Current Diff、Test再実行からStateを再構築する必要が生じた。

```text
Resource Exhaustion != Work Invalidated
しかし
Resource Exhaustion without Recovery = Handoff Cost and Human/Controller Cost増大
```

Auto-Compaction後に作業継続できた点は評価するが、最終Resource Hard StopでExecution State Serializationに失敗した点は分離して記録する。

## 10. Current Stop Line

```text
Maximum Claim:
P9_1_TERRA_MAX_QUOTA_EXHAUSTED_PARTIAL_REWORK_REQUIRED

Real Selene Production PASS:
NOT ACCEPTED

Real Qwen3Guard Production PASS:
NOT ACCEPTED

P9-CODEX-011:
OPEN

P9-CODEX-012:
PARTIAL

P9-CODEX-013:
PARTIAL / REGRESSED

P9-CODEX-014:
OPEN

P9-CODEX-015〜017:
OPEN

Phase 9-1 Complete Candidate:
false

Phase 9-1 Closure:
false

Phase 9-2:
not started
```
