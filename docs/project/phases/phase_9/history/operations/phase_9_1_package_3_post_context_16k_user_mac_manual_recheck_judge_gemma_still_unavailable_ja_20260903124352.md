# Phase 9-1 Package 3後 User Mac Manual Recheck — Context 16K成立／Judge(Gemma)依然Unavailable

```yaml
document_id: phase_9_1_package_3_post_context_16k_user_mac_manual_recheck_judge_gemma_still_unavailable_20260903124352
document_type: user_manual_recheck_evidence
document_state: current_evidence
language: ja
recorded_at: 2026-09-03 12:43:52 JST
phase: phase_9
program: phase_9_1
package: P9-1-CONTEXT-PACKAGE-3（着手後）
recorder_role: Claude（Bounded Implementation Worker）
source: User提供の実画面Evidence(2026-09-03 03:33 UTC台のTurn)
source_mutation_by_recorder: none
runtime_action_by_recorder: none
git_action: none
```

## 0. 位置づけ

Phase 9-1 Claude Package 3 Exact Return
(handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_return_handoff_ja_20260903114816.md)
提出後、UserがContext 16K Package 3の動作確認を含む実画面Manual Testを実施し、その結果をそのまま本Taskへ提供した。本Docはこれをそのまま記録する。Codex Controllerが週間Quota枯渇中のため、Independent Reviewが行えない状態でのUser自身によるRecheckである。

## 1. User提供の生Evidence(そのまま記録)

### 1.1 Userの要約コメント

```text
・コンテキストのやつ2個は動作確認した。
・Judgeはあいわらず『選択したProviderをLoadまたは使用できませんでした。』でしんだままだ。
・guardrailは生きてる。
```

### 1.2 Main Governance Mode(ENFORCE) 表示

```text
main_model.pre
State: evaluated · Selected Rule数: 109 · Severity: moderate · 実行Action数: 0 ·
Observation数: 110 (Pass 0, Deviation 1, Deferred（意味評価待ち） 109)

main_model.post
State: evaluated · Selected Rule数: 109 · Severity: none · 実行Action数: 0 ·
Observation数: 109 (Pass 0, Deviation 0, Deferred（意味評価待ち） 77)

Evidence状態
正常
```

### 1.3 Judge/Repair/ENFORCE/Recording full 表示

```text
現在のJudge Run状態: 失敗

直近のJudge結果
* Request ID: 7cc0620a-eec6-4e58-806b-f381316b9b44
* 判定: unknown
* 確信度: 0.00
* 実行状態: failed
* Started: 2026-09-03T03:33:36.616682+00:00
* Completed: 2026-09-03T03:33:36.741925+00:00
* Configured Provider: judge.gemma-4-e2b-it-q4-0
* Active Provider: judge.gemma-4-e2b-it-q4-0
* Executed Provider: judge.gemma-4-e2b-it-q4-0
* Budget: local_macos_gemma_e2b_judge_v1
* Frozen Modes: main=enforce, guard=enforce, judge=enforce, repair=enforce, recording=full
* Criteria: selected=32, evaluated=0, passed=0, deviated=0, unknown=32, not_applicable=0, deferred=77
* 失敗理由: unavailable
* 選択したProviderをLoadまたは使用できませんでした。
* 提示結果: safe_fallback
* 検証に失敗した元回答は表示されませんでした
```

```text
Request ID: 7cc0620a-eec6-4e58-806b-f381316b9b44
Status: completed (started 2026-09-03T03:33:31.997665+00:00)
        (completed 2026-09-03T03:33:36.911016+00:00)
直近の記録（Turn）: 正常に記録されました [7cc0620a-eec6-4e58-806b-f381316b9b44]
直近の記録（Judge Evidence）: 正常に記録されました [7cc0620a-eec6-4e58-806b-f381316b9b44]
```

### 1.4 Runtime Model Control 表示

```text
Effective Limit Reason
deployment_hardware_verified_limit

Current LLM-as-a-Judge Model
judge.gemma-4-e2b-it-q4-0

Current Guardrail Model
guard.qwen3guard-gen-0.6b-q8-0
```

### 1.5 Provider Status Panel 表示

```text
Main Provider: Qwen3 4B
  Configured: main.qwen3-4b-q4-k-m
  Active: main.qwen3-4b-q4-k-m
  State: active
  Independence: self
  Budget: none

Guardrail Provider: Qwen3Guard-Gen 0.6B
  Configured: guard.qwen3guard-gen-0.6b-q8-0
  Active: guard.qwen3guard-gen-0.6b-q8-0
  State: active
  Independence: independent_other_model
  Budget: local_macos_qwen3guard_v1 / configured_not_hardware_verified

Judge Provider: Gemma 4 E2B (lightweight independent)
  Configured: judge.gemma-4-e2b-it-q4-0
  Active: judge.gemma-4-e2b-it-q4-0
  State: active
  Independence: independent_other_model
  Budget: local_macos_gemma_e2b_judge_v1 / configured_not_hardware_verified
```

## 2. 事実の整理

```text
[FACT] Context 16K(Main単体／Main+Gemma同時)は、UserがPackage 3 Exact Return後
       に自ら実画面で動作確認した("動作確認した"と明言)。Package 3 Exact Return
       の実機Evidenceと整合する。
[FACT] Runtime Model Control表示のEffective Limit Reasonが
       deployment_hardware_verified_limitであり、Context 16Kが実際に
       Hardware Verified状態としてUIへ反映されている。
[FACT] Qwen3Guard(Guardrail)はProvider State=active、Userも「生きてる」と明言。
[FACT] Judge(Gemma) Provider Activation(Configured=Active=Executed=
       judge.gemma-4-e2b-it-q4-0)は成立している。
[FACT] 同一Judge Runの実Inference/Decodeは失敗(実行状態=failed、失敗理由=
       unavailable)。所要時間は約125ms(Started 03:33:36.616682 ->
       Completed 03:33:36.741925)であり、実Model Inferenceとしては
       明らかに短い。
[FACT] Criteria内訳(selected=32, evaluated=0, unknown=32, deferred=77)は、
       別Session/別Turnで観測されたSelene Judge ENFORCE失敗時
       (claude_code_fresh_session側のExact Return Addendum参照)の内訳と
       完全に一致する。
[FACT] Turn自体およびJudge Evidenceの記録(Recording full)は「正常に記録
       されました」であり、記録層自体は機能している。
[FACT] Main Governance ENFORCE(main_model.pre/post)は構造評価(State=
       evaluated)は成立しているが、Observationの大半がDeferred(意味評価待ち)
       のまま(pre: 109/110、post: 77/109)であり、Judge失敗と整合する
       (意味評価がJudgeに依存しているため、Judge失敗時はDeferredのまま
       止まる)。
```

## 3. Package 3との関係

```text
Package 3(Context 16K／Output 4K・8K)自体は、UserによるManual Recheckでも
実機成立が確認された。本Docが記録するJudge(Gemma) ENFORCE Dispatch失敗は、
Package 3のScope外(Judge共通基盤側の別問題)であり、Package 3のHardware
Verified Claimを損なわない。
```

## 4. Selene時のFailureとの比較(既存Open Findingとの関係)

```text
既存Open Finding(claude_code_fresh_session側のExact Return Addendum、
Selene Judge ENFORCE即時失敗のRead-only調査)は、Selene Provider限定の
問題という仮説を確定させていなかった。

今回、Selene→Gemmaへ実際にProvider切替した状態でも、
  - 失敗Category(unavailable)
  - Criteria内訳(selected=32, deferred=77)
  - 実推論には短すぎる所要時間
のいずれもが同型で再現した。SeleneとGemmaは共に同一の
`SeleneSemanticEvaluator`(Provider非依存の共有Engine、selene.pyのDocstring
にも明記)を経由してDispatchされる実装であることと合わせると、Provider固有
ではなくJudge Dispatch層(`_run_judge_and_repair`/`TrackedStageWorkerRegistry`
まわり)に共通する問題である可能性を補強する材料である。ただし、Exact
Trigger(具体的にどの分岐が失敗しているか)はまだ特定されていない
(Read-only調査の限界、既存Addendum参照)。断定的なRoot Cause Claimはしない。
```

## 5. Status

```text
Current Point            : Package 3後のUser実画面Recheckで、Context 16K成立
                            (Main単体/Main+Gemma同時)とQwen3Guard生存を確認。
                            Judge(Gemma) ENFORCE実Inferenceは依然失敗
                            (unavailable、約125ms)で、既存のSelene時Open
                            Findingと同型の失敗であることが新たに確認された。
Files Created／Modified   : 本Fileのみ(新規作成)。Source変更なし。
Validation                : N/A(User提供実画面Evidenceの記録)。
Open Current Blocker      : Judge Dispatch層のExact Trigger未特定
                            (既存Open Finding継続)。Codex週間Quota枯渇中の
                            ためController Independent Review不可。
Controller-owned Next Work: Judge Dispatch層(TrackedStageWorkerRegistry
                            接続含む)の実機再現調査、またはCodex Quota回復
                            後のReview。
Exact Next Route          : User指示待ち。
```
