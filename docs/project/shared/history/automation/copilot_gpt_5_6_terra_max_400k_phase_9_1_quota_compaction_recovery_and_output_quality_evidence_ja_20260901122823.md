# Copilot GPT-5.6 Terra Max 400k Phase 9-1 Quota／Compaction／Recovery／Output Quality Evidence

```yaml
document_id: copilot_gpt_5_6_terra_max_400k_phase_9_1_quota_compaction_recovery_and_output_quality_evidence_20260901122823
document_type: append_only_provider_model_resource_compaction_recovery_and_quality_evidence
document_state: recorded_with_controller_review
language: ja
created_at: 2026-09-01T12:28:23+09:00
provider: copilot
model: GPT-5.6 Terra
reasoning_effort: max
context_window: 400k
model_attribution_source: user_report
service_plan: copilot_pro_10_usd_user_report
nominal_monthly_ai_credits: 1500_user_report
task: phase_9_1_p9_codex_011_to_014
session_end: monthly_ai_credits_exhausted
provider_generalization: prohibited_insufficient_sample
model_comparison_state: exploratory_observation_only
```

## 1. 目的

2026-09-01に新規Copilot Sessionで実行した`GPT-5.6 Terra Max / 400k`について、開始条件、Quota消費、AI Credits、Auto-Compaction、Compaction後Recovery、実装Output、Controller Review後の実品質をLosslessに記録する。

比較対象は同日に実行した`GPT-5.3 Codex Medium`と、2026年8月末に使用した`GPT-5.6 Terra High / 400k`である。ただしComparable Sampleは極めて少なく、Task難度、開始状態、Context、Rework内容が同一ではない。恒久的なModel優劣やProvider一般傾向へ昇格しない。

## 2. Model／Session条件

### 2.1 Current Session

```yaml
provider: copilot
model: GPT-5.6 Terra
reasoning_effort: max
context_window: 400k
task_state: fresh
task_scope: P9-CODEX-011_to_014
monthly_availability_at_entry: 57_percent_remaining_user_report
monthly_usage_at_entry: 43_percent_used_user_report
session_ai_credits_at_entry: 0_user_report
```

Binding Handoff:

`docs/project/phases/phase_9/handoffs/phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_ja_20260901113052.md`

SHA-512:

`7d73a96a2539623bc7f4f3502a14b8df4feb76d0827a6fa3709e58ebca711bfc8926004687d3691630eaa7b431db3dd16ff563b945887471ca35fdbeadb4ad86`

### 2.2 Comparison Baselines

```text
2026-08末:
  GPT-5.6 Terra High / 400k
  Model attribution: User report
  Directly comparable quota sample: insufficient

2026-09-01 earlier:
  GPT-5.3 Codex Medium
  Task: preceding Phase 9-1 Real Dedicated work
  Elapsed: approximately 16 minutes
  Session work credit estimate: approximately 600
  Monthly availability consumed: approximately 38 percentage points
```

Medium Evidence:

`docs/project/shared/history/automation/copilot_gpt_5_3_codex_medium_phase_9_1_execution_resource_quality_and_review_evidence_ja_20260901112423.md`

## 3. User報告の時系列Resource観測

```text
T0:
  monthly used: 43%
  monthly remaining: 57%
  session AI Credits: 0

approximately 9 minutes:
  monthly used: 70%
  delta: +27 percentage points

approximately 20 minutes:
  monthly used: 93%
  session AI Credits: approximately 750
  UI event: Compacted conversation

approximately 22 minutes:
  Monthly AI credits exhausted
  final session AI Credits: 816
  monthly remaining: exhausted
```

単純参考値:

```text
Terra Max observed credits/minute:
816 / 22 ≈ 37.1

Codex Medium observed work credits/minute:
approximately 600 / 16 ≈ 37.5

Terra Max first 9-minute monthly percentage rate:
27 / 9 = 3.0 percentage points/minute

Terra Max full observed monthly percentage rate:
57 / 22 ≈ 2.59 percentage points/minute

Codex Medium observed monthly percentage rate:
38 / 16 ≈ 2.38 percentage points/minute
```

これらはUI Sample、丸め、Request境界、Context量、内部Rate、Compaction、Cache等を統制していないため、Provider Billing式や将来消費速度の推定値ではない。

## 4. Nominal 1500 AI Creditsとの整合仮説

User報告ではCopilot Proは10 USD、Nominal AI Creditsは月1500である。

```text
Codex Medium current-task estimate: approximately 600
Terra Max final session: 816
combined: approximately 1416
```

Medium側のUI累計727には以前の約115 Creditsが含まれるというUser推定があり、Current Medium作業分は約600〜612と推定されている。これとTerra Max 816の合計は1416〜1428で、Nominal 1500に近い。

したがって「UI Percentage、内部Rate増加、丸め、Reserved Amount等を経た結果としてNominal 1500 Poolと概ね整合した可能性」はある。ただしProvider Accounting APIで検証しておらず、確定Claimにしない。

## 5. Rate変更閾値に関するUnverified Note

Userは過去に別LLMから「約273K付近以降でRateが変わる」と聞いた記憶がある。ただし次は不明である。

- 正確な数字。
- Source。
- 対象Provider／Model／Plan。
- Token、Context、Creditのどの単位か。
- 現行仕様か。

よって本Evidenceでは、`approximately_273k_rate_shift_user_memory_source_unknown_unverified`として保持するだけとし、816 Creditsと1500 Poolの差を説明する事実には使わない。

## 6. Auto-Compaction観測

User Screenshot `スクリーンショット 2026-09-01 12.01.02.png`および`12.18.25.png`には、Copilot実行ログ内の`Compacted conversation`が表示されている。

観測できる順序:

```text
Source Edit／Focused Test
→ Compacted conversation
→ 互換性回復を宣言
→ Selene／Judge／Semantic Runtime／Tracked Worker／Lifecycleを再読
→ Source Edit／Focused Testを継続
→ Monthly AI credits exhausted
```

これは少なくとも一回のAuto-Compaction発生と、その後の作業再開を示す。複数Screenshotに同じ表示があるが、同一Eventを別Scroll位置で写した可能性があるため、二回以上発生したとはClaimしない。

`Compacted conversation`は400k Context全量を厳密に使い切ったことの証明ではない。Reserved Context、内部Summarization閾値、Tool Log圧縮、Rate境界などがあり得る。したがって正確なPre-compaction Token CountはUnknownとする。

## 7. Compaction Recovery評価

### 7.1 成立した点

Compaction後、Copilotは無関係な旧Phaseへ逸脱せず、Current P9-CODEX-011〜014に関係するSourceを再読し、次の実装を継続した。

- Selene Bounded Batch／Token Budget。
- Judge Dispatch／Semantic Evidence。
- Qwen3Guard Cancellation。
- Role Lifecycle Active Lease Cancellation。
- Conversation User Stop／Guard Hook接続。

よって次は成立観測とする。

```text
Post-compaction task identity recovery: observed
Post-compaction relevant-source recovery: observed
Post-compaction mutation continuation: observed
Immediate stale Phase 8 resume: not observed in this session
```

### 7.2 不成立の点

Recovery成功はTask Completionを意味しない。最終的にQuota Exhaustionまでに次へ到達しなかった。

- Acceptance Runner。
- Real Production Evidence。
- Canonical Green Test。
- Mypy Clean。
- Acceptance／Manual／Index Alignment。
- Two-cycle Internal Review。
- Recovery Index。
- Exact Return。

したがって今回の評価は次である。

```text
Context Recovery: partial success
Execution Continuation: success
Safe Resource-stop Convergence: failure
Task Completion: failure
Return Contract Completion: failure
```

400kと1.1M等の比較では、Context WindowだけでなくAuto-Compaction後のTask Identity保持率、再読Cost、重複作業率、Regression率、Return到達率を測る必要があるというUser判断は妥当である。

## 8. Screenshotから復元したExecution内容

ScreenshotsとCurrent Diffから次を確認した。

### 8.1 Planned Task List

- Implementing reproducible real dedicated evidence。
- Implementing guard cancellation preemption。
- Implementing Selene semantic bounds。
- Aligning acceptance and operator docs。
- Creating real dedicated acceptance runner。
- Completing Qwen cancellation coverage。
- Completing Selene bounded evaluation。
- Producing acceptance evidence documents。
- Conducting two-stage internal review。

### 8.2 Material Edits

- `selene.py`: 大規模Batch／Budget／Deadline差分。
- `judge_live_integration.py`: Cancellation／Selene Dispatch差分。
- `role_lifecycle_manager.py`: Active Lease Cancellation管理。
- `qwen3guard_detector_adapter.py`: External／Internal Cancellation合成。
- `guardrail_governance.py`: Hook Cancellation伝播。
- `conversation_generation.py`: User StopからGuard Tokenへの配線。
- `web_application.py`: Production Composition接続。
- `dedicated_role_adapters.py`、Manifest、Semantic Runtime／Domain、関連Tests。

### 8.3 Copilot Progress Messages

```text
Cancellation ownership is now being pushed down to the role lease and bounded-worker layers so user stops, mode changes, and shutdown can preempt the same in-flight call.

The Selene path is being converted from one unbounded request into batched, token-accounted calls with an explicit deadline and deferred-result accounting.

互換性の回復後、実装済みの境界条件と受入経路をまとめて精査し、残る回帰試験・実証・文書連結を完了します。
```

最初の二文はCurrent Source差分と概ね一致する。三文目の「互換性の回復」は最終Working Treeと一致しない。Controller Full SuiteでSelene Production Wiring 2件がFailし、Mypyも45 Errorsだったためである。

## 9. Controller Review後のOutput Quality

Review:

`docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_terra_max_quota_exhaustion_partial_state_review_ja_20260901122823.md`

Validation:

```text
Syntax: PASS
Terra Max focused tests: 184 PASS
Expanded integration review: 137 PASS / 2 FAIL / 2 DESELECTED
Canonical full pytest: 2214 PASS / 2 FAIL / 7 DESELECTED
Ruff: PASS
Mypy: 45 ERRORS
```

有効な成果:

- Medium Reviewで発見したCancellation／Batch不足をSource上で真正面から修正し始めた。
- Scope逸脱やRoutine User確認を挟まず、Core Pipelineへ深い差分を入れた。
- Auto-Compaction後もTask Identityを保って作業を継続した。

品質不足:

- Focused Testだけでは既存Production Wiring Regressionを検出できなかった。
- MypyをCleanへ戻せなかった。
- Whole-stage Selene DeadlineがBatch数倍へ増える設計欠陥が残った。
- Mandatory Thread Regressionを作成しなかった。
- Runner／Real Evidence／Docs／Review／Returnへ到達しなかった。
- Resource Hard Stop前のRecovery Serializationを行わなかった。

## 10. GPT-5.3 Codex Mediumとの暫定比較

| 観点 | GPT-5.3 Codex Medium | GPT-5.6 Terra Max / 400k | 暫定解釈 |
|---|---|---|---|
| 約Credits／分 | 約37.5 | 約37.1 | 観測上はほぼ同程度。統制不足 |
| 月間%／分 | 約2.38 | 約2.59、最初9分は3.0 | Maxの明確な節約効果なし |
| Task Return | 約16分でReturn | 約22分でQuota Exhaustion、Returnなし | Mediumのみ形式Return到達 |
| Return正確性 | Complete Claim後に4 Blocker | Return未作成 | 直接比較不能 |
| Task Identity | 開始前にStale Phase 8 Resume Incident | Current Scopeを維持 | Max Sessionは良好 |
| Core実装深度 | Direct Smoke／部分修正 | Cancellation／Batch／Lifecycleへ広い差分 | Maxがより深い |
| Canonical Quality | Executor報告Green、後続ReviewでSemantic Blocker | Full Test 2 Fail、Mypy 45 Error | Maxは未収束 |
| Compaction | 今回Comparable観測なし | Auto-Compaction後も継続 | MaxでPartial Recovery観測 |
| Accepted Closure Progress | Rework Required | Rework Required | どちらもPhase 9-1未完了 |

現時点で言える最小結論:

1. `Mediumへ下げればQuotaが明確に長持ちする`という仮説は支持されなかった。
2. `Maxなら一発で高精度完了する`という仮説も今回の一例では支持されなかった。
3. MaxはMedium Reviewで指摘された核心へ、より深くSource修正を進めた。
4. しかしQuota ExhaustionまでにGreen／Evidence／Returnへ収束できず、Accepted Outcomeはまだ得ていない。
5. Quota速度だけを見るとMedium／Maxは大差が見えず、実効価値はRework後の最終Accepted Progressで測る必要がある。

## 11. Terra High／Medium／MaxについてのCurrent Claim Ceiling

Terra Highは同一Task、同一開始State、同一計測方式のQuota／Creditsがないため、定量比較できない。Userの体感としてHigh／Medium／Maxの消費速度に大差がないという観測は保存するが、結論にはしない。

```text
Current evidence permits:
- MediumとMaxの一回ずつの観測では消費速度が近かった。
- 設定を下げてもQuota改善が明確でなかった。
- MaxでもContext CompactionとQuota Exhaustionが起きた。
- Maxは深い実装を進めたが未収束だった。

Current evidence does not permit:
- High／Medium／MaxのQuota Costは同一。
- MaxはMediumより高品質／低品質。
- 400kはMARGPAに常に不足。
- 1.1Mなら常に有利。
- 約273KでRateが必ず変わる。
```

## 12. 今後の比較Metrics

次回以降は最低限、Task／Modelごとに次を同じFormatで取る。

```text
Provider
Model
Reasoning effort
Context window
Task identity and difficulty
Entry canonical state
Entry monthly percentage
Entry session credits
Elapsed time
Exit monthly percentage
Exit session credits
Compaction count
Post-compaction recovery success
Duplicate read/edit count
Unauthorized action count
Focused test result
Canonical test result
Mypy/Ruff result
Controller findings
Rework count
Human interventions
Recovery/Return completeness
Final accepted work units
Closure result
```

主要評価式:

```text
Effective Engineering Efficiency
=
Controller-accepted Progress
/
(AI Credits + Rework Cost + Review Cost + Human Attention Cost)
```

Context Window評価:

```text
Compaction Utility
=
Post-compaction Correct Continuation
- Duplicate Work
- State Reconstruction Cost
- Regression introduced after Recovery
```

## 13. 研究上の意味

今回の観測は、Model設定を単純に上げ下げするだけではLong-run Automationの経済性を説明できないことを示す初期Evidenceである。

```text
High Capability
!= Guaranteed One-pass Completion

Lower Reasoning Setting
!= Guaranteed Quota Savings

Auto-Compaction Recovery
!= Task Completion

Large Context
!= Recovery-free Execution

Fast Material Editing
!= Controller-accepted Output
```

したがって研究対象はModel単体の速度ではなく、`Quality × Quota × Compaction Recovery × Rework × Human Attention × Accepted Completion`の複合評価とする。

## 14. Evidence Source Inventory

User提供Screenshot:

- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.01.02.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.18.08.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.18.25.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.18.38.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.18.49.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.19.00.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.19.11.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.19.23.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.19.35.png`
- `/Users/yukitakagi/Desktop/スクリーンショット 2026-09-01 12.19.44.png`

その他:

- User Resource／Credits報告。
- User貼付のCopilot Progress Message三件。
- Current Working Tree Source／Test。
- Codex ControllerによるFocused／Expanded／Full Test、Ruff、Mypy結果。
