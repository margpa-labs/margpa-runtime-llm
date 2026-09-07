# Phase 9-1 Claude Fresh Session — SSS Resource Gate局所復旧 Exact Return Addendum: Selene ENFORCE即時失敗のRead-only調査

```yaml
document_id: phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_addendum_selene_failure_point_20260903020447
document_type: exact_return_addendum
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
work_package: P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY
from: Claude Code Fresh Session
to: Codex Controller
created_at: 2026-09-03 02:04:47 JST
language: ja_with_structured_english_terms
supplements: docs/project/phases/phase_9/handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_handoff_ja_20260903013117.md
in_response_to: |
  User提供の実UI Evidence(Selene Judge ENFORCE: Configured/Active/Executed
  Providerとも一致するがInference未成立、55ms即時失敗)、および明示指示
  (Activation成功とInference成功を混同しない、Read-onlyでExact Failure Point
  を特定する、Scope超過の修正はSourceを変更せずOpen Findingとして記録する)。
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none
```

## 0. 位置づけ

本Docは、直前のExact Return(§13:31:17 JST)提出直後にUserから提供された実UI
Evidenceを受けての、追加のRead-only調査結果である。前回Exact Returnの内容を
書き換えず、Append-onlyで追記する。

**局所復旧の成功(Resource Gate除去、Main+Gemma/Main+Qwen3Guard同時Load成功)と、
このSelene Judge ENFORCE Inference未成立は別の事象である。前者をもって後者が
解決したと主張しない。**

## 1. Userが提示した実UI Evidence(再掲・そのまま記録)

```text
Configured Provider : judge.selene-1-mini-llama-3.1-8b-q5-k-m
Active Provider      : judge.selene-1-mini-llama-3.1-8b-q5-k-m
Executed Provider    : judge.selene-1-mini-llama-3.1-8b-q5-k-m
Started              : 2026-09-02T16:55:03.158090+00:00
Completed            : 2026-09-02T16:55:03.213648+00:00 (約55ms)
Status               : failed
Failure Reason       : unavailable
Criteria             : selected=32, evaluated=0, unknown=32, deferred=77
Presented Result     : safe_fallback

Main Governance表示:
  Selected Rule数=109, Pass=0, Deviation=0, Deferred=77, Observation数=109
  (Judge側 unknown=32 + deferred=77 = 109。Main Governance概要表示では
   unknown 32が欠落している可能性がUserより指摘済み)
```

Userの整理(同意して引き継ぐ):

```text
Resource Gateによる事前拒否 : 解消候補
Selene Provider Activation/Routing : 成立
Selene実Inference           : 未成立
Judge ENFORCE                : 未成立
Main Governance ENFORCE      : ModeはONだが意味評価未成立
Safe Fallback                : 成立
Qwen3Guard                   : 復旧確認済み
```

## 2. 永続Evidence Fileの直接確認(Read-only)

`runtime_data/persistent/f4624912.../evaluations/afcb5774-....json`:

```json
{"request_id":"afcb5774-b1b1-43ab-a458-3688235be74d",
 "timestamp":"2026-09-02T16:55:03.369275+00:00",
 "metadata_fields":{"model_identity":"main.qwen3-4b-q4-k-m","backend_key":"llama_cpp"},
 "canonical_input":"あまねかなただけど！",
 "presented_answer":"選択したProviderをLoadまたは使用できませんでした。"}
```

`runtime_data/persistent/f4624912.../evidence/afcb5774-....json`:

```json
{"request_id":"afcb5774-b1b1-43ab-a458-3688235be74d",
 "metadata_fields":{"judge_role":"independent_artifact",
   "rubric_id":"live_conversation_general_quality_v1",
   "recommendation":"unknown","confidence":0.0,"token_usage":0,
   "latency_ms":54,"call_count":1,"execution_state":"failed",
   "failure_reason":"unavailable"}}
```

`call_count`はSource上`recording_live_integration.py:213`で常に固定`1`が書かれる
実装であることを確認した(実際の`calls_started`/`calls_completed`を反映しない)。
したがってこのFieldからは実Generate呼び出しの有無を判定できない。

`token_usage=0`は、`_judge_response_from_semantic_results()`の
`response.provider_state is not ACTIVE`早期Returnパス(token_usage=0固定)から
来ている可能性が高いが、これも単独では確定材料にならない。

## 3. Sourceの追跡結果(Read-only)

```text
表示"Failure Reason: unavailable"の出処:
  judge_live_integration.py の `_judge_failure_reason_from_semantic_response()`
  が、`response.failure_reason`が
    "malformed_output"始まり     -> MALFORMED_OUTPUT
    "deadline_exceeded"含む      -> TIMEOUT
    "cancelled"含む              -> CANCELLED
  のいずれにも一致しない場合、無条件で `JudgeFailureReason.UNAVAILABLE`
  ("unavailable")へ集約する。

  `SeleneSemanticEvaluator.evaluate()`(adapters/evaluation/selene.py)内で、
  この集約に該当する生の`failure_reason`候補は次の3箇所:
    L348-354  self._plan_batches(request=request) が例外 ->
               f"{label}_unavailable:{ExceptionType}"
    L379-396  run_tracked_stage(work=generate_batch, ...) が例外 ->
               f"{label}_unavailable:{ExceptionType}"
    L464-468  decode_judge_output()が JudgeDecodeError以外の例外 ->
               f"{label}_unavailable:{ExceptionType}"

  いずれも実際のException Type名を文字列へ埋め込むが、この詳細文字列は
  永続Evidence(§2)にもUI表示にも残らず、`JudgeFailureReason.UNAVAILABLE`
  という集約Categoryだけが記録される。
```

## 4. 再現の試み(Read-only、Source変更なし)とその結果

Userの安全確保方針(Main同時Loadの新規リスクを増やさない)を踏まえ、
Main非同時(Selene単独)で、実Production Class(`SeleneRoleAdapter`,
`SeleneSemanticEvaluator`, 実Local Artifact `models/judge/
selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`)を
使い、`response.failure_reason`の生文字列を直接取得するScriptを実行した
(独立Subprocess、Source変更なし)。

```text
preflight: ready=True
load: 成功(real 5.7GB Artifact, semantic_evaluator構築成功)
evaluate()の結果:
  provider_state=FAILED
  RAW failure_reason='malformed_output:repair recommendation has no
                       deviated criterion'
  latency_ms=14198 (約14.2秒)
  budget: calls_started=1, calls_completed=1, completion_tokens=283
```

**この再現はUser実UIの55ms即時失敗と一致しなかった。** 本Scriptは実際に
Generate呼び出しを完走し(14.2秒)、Decode段階で別種の失敗
(`malformed_output`、`JudgeDecodeError`由来)に到達した。これはUIで観測された
"unavailable"カテゴリとは異なる("malformed_output"は別の分岐でMALFORMED_OUTPUT
へ写像され、UI上は別表示になっていたはずである)。

## 5. 未特定である理由(正直な記録)

本Scriptと実Production Dispatchの間には、次の未検証の相違が残っている。

```text
1. `tracked_stage_registry`:
   Production(web_application.py)は実`TrackedStageWorkerRegistry()`
   Instanceを`ProductionRoleAdapterFactory`経由でSeleneRoleAdapterへ渡す。
   本ScriptはDefaultの`None`のまま(Registry未接続)で`run_tracked_stage`を
   呼んでいる。この差が、55ms級の即時失敗(Registry側の何らかの状態異常/
   容量制限/多重実行検知等)を再現できなかった一因である可能性がある。

2. 実Semantic Snapshot:
   実UIのCriteria内訳(selected=32, deferred=77, 合計109)は、実Runtime
   Governance ModuleがそのTurnの実対話Contextから構築した実Snapshotである。
   本Scriptは32件の合成Criterion(Deferralなし)で代替しており、
   `_plan_batches()`のDeferral分岐やBudget境界条件を完全には再現していない。

3. Presented Answer自体が異常値である可能性:
   このTurnのMain自身のPresented Answerが
   「選択したProviderをLoadまたは使用できませんでした。」という、それ自体が
   Provider失敗を示す文字列だった(§2)。これがJudgeへのCandidate Answerとして
   渡っていたとすれば、Main側で別の失敗が先行していた可能性がある
   (Main Provider自体、またはこのTurnに関わる別Providerの失敗)。本Scriptは
   この文字列をそのままCandidate Answerとして使ったが、これ自体がJudge
   失敗のTriggerになっているかは未確認(§4の再現はDecode段階まで到達して
   おり、この文字列自体がJudge側の即時失敗原因ではなさそうという弱い反証には
   なるが、確定ではない)。

4. `stage_budget.py`のDiffをRead-only確認したが、Selene用の
   `LOCAL_MACOS_SELENE_JUDGE_BUDGET`自体は`1f0e70e`から無変更
   (今回のPackageで追加されたのはGemma用の新規Budgetのみ)。したがって
   Selene固有のTimeout/Budget設定自体が原因である可能性は低いと判断した。
```

## 6. Open Finding(記録のみ、Source変更なし)

```text
Open Finding 5 (Selene Judge ENFORCE 即時Inference失敗、未特定・
                Resource Gate Scope外):
  実UIでSelene ProviderのActivation/Routingは成立するが(Configured=
  Active=Executed=Selene確認済み)、実Judge Turn Dispatchが約55msで
  即時失敗し、Criteria 32件全てがunknown、Judge ENFORCEもMain Governance
  ENFORCEも意味評価未成立、Safe Fallbackのみ成立する。

  失敗のExact Trigger(§3記載3候補のいずれか)はRead-only調査およびSelene
  単独Diagnosticでは特定できなかった。単独Diagnosticは同じ"unavailable"
  Categoryを再現せず、別の、より遅い(14.2秒)"malformed_output"失敗に
  到達した — これは実Production Dispatch(実TrackedStageWorkerRegistry、
  実109件Semantic Snapshot)固有の何かが関与している可能性を示唆するが、
  確証ではない。

  本Task(Resource Gate局所復旧)のScopeを超えるため、Source変更は一切
  行っていない。Judge共通基盤(SeleneSemanticEvaluator/`run_tracked_stage`/
  Runtime Governance連携)側の追加調査が必要。
```

## 7. Gemma/Qwen3Guard Positive-path Acceptanceへの影響

```text
影響なし。前回Exact Return(§6/§7)のGemma/Qwen3Guard実Evidence
(実Load成功、Main保全、正常Unload)はHandoffどおり継続してAcceptance対象と
する。本AddendumはSelene単独の別事象を記録するものであり、Gemma/Qwen3Guard
のClaimを撤回・変更しない。
```

## 8. Exact Next Action for Codex Controller (Addendum分)

```text
1. 本Addendumと前回Exact Returnをあわせてレビューする。
2. Open Finding 5の調査を別Task/別Authorityとして起票するかを判断する
   (実TrackedStageWorkerRegistry接続込みの再現、または実サーバー起動下での
   Live Log採取が次の妥当な手段候補と考えられるが、これはController/User
   Authority判断であり、本Task内では実行していない)。
3. Presented Answer自体がProvider失敗Fallbackだった点(§5-3)について、
   このTurn固有の別要因(Main側)がなかったか、Userの記憶/操作履歴と
   突き合わせるかを判断する。
```
