# Phase 9-1 全Judge実用不成立／共通基盤仮説／再開順序Evidence

```yaml
document_id: phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_20260902103228
document_type: append_only_user_observation_hypothesis_and_authorized_rework_order
document_state: current_evidence_rework_required
language: ja
recorded_at: 2026-09-02 10:32:28 JST
evidence_author: user
recorder_role: codex_controller
project_stage: individual_r_and_d_poc_mvp_portfolio
phase: phase_9
program: phase_9_1
source_mutation: none
real_model_action_by_recorder: none
network_action_by_recorder: none
git_action: none
overall_disposition: phase_9_1_fail_rework_required
root_cause_status: hypothesis_not_confirmed
phase_9_1_closure: false
phase_9_2_ready: false
```

## 1. Purpose

本書は、2026-09-02のUser実画面でMain-shared Qwen JudgeおよびBuilt-in Deterministic Judgeが実用判定へ到達しなかった事実と、前日のSelene失敗を合わせて再分類する。

単一Providerだけの障害と決めつけず、共通Judge基盤の回帰または構成不整合を第一仮説として調査する。ただし、現時点ではRoot Causeを断定しない。

本書は次の実装を開始するAuthorityではない。AI利用可能量が回復した後に、別途Exact Handoff／Authorityを作成して再開する。

## 2. 2026-09-02 User Observation

### 2.1 Main-shared Qwen Judge — ENFORCE

対象Provider：

```text
Configured Provider: main.qwen3-4b-q4-k-m
Active Provider: main.qwen3-4b-q4-k-m
Executed Provider: main.qwen3-4b-q4-k-m
Budget: local_macos_main_self_judge_v1
```

Mode：

```text
main=observe
guard=off
judge=enforce
repair=enforce
recording=full
```

結果：

```text
Judge Status: failed
Verdict: unknown
Confidence: 0.00
Failure: malformed_output
Criteria: selected 0／evaluated 0／deferred 77
Presentation: safe_fallback
```

実画面では「判定結果を確定できませんでした。」へ収束し、元回答は提示されなかった。

Configured／Active／Executedが同一Main Providerであるため、少なくともProvider選択およびCall到達前の単純な未Loadだけでは説明できない。直接の表面原因はJudge出力のDecode失敗である。

### 2.2 Main-shared Qwen Judge — OBSERVE

同一Main ProviderをOBSERVEで実行しても次へ収束した。

```text
Judge Status: failed
Verdict: unknown
Confidence: 0.00
Failure: malformed_output
Criteria: selected 0／evaluated 0／deferred 77
Presentation: observed_candidate
```

OBSERVEとENFORCEの差はPresentation境界には現れたが、Judge判定そのものは両方で成立しなかった。

### 2.3 Built-in Deterministic Judge — ENFORCE

対象Provider：

```text
Configured Provider: built_in.deterministic
Active Provider: built_in.deterministic
Executed Provider: built_in.deterministic
Budget: local_macos_built_in_judge_v1
```

結果：

```text
Judge Status: completed
Verdict: unknown
Confidence: 0.00
Criteria: selected 32／evaluated 0／not_applicable 32／deferred 77
Presentation: safe_fallback
```

Built-inはRuntime Errorではなく処理完了している。しかしSemantic Criterionを1件も評価できず、Userが利用できる判定を返していない。実装内部の状態は`completed`でも、Judge機能としては実用不成立である。

これは従来から観測されていたBuilt-inのSemantic能力不足と整合する。Main-sharedの`malformed_output`と同じ直接原因であるとは断定しない。

### 2.4 Guardrail非依存

Guardrail GovernanceをOFF／ONへ変更してもJudge失敗は変わらなかった。

したがって、今回のJudge不成立をQwen3Guardの入力／出力Guard Actionだけへ帰属しない。Guardrailは独立Baselineとして扱う。

## 3. Prior Selene Evidenceとの接続

2026-09-01の実画面ではSeleneが次の状態だった。

```text
Provider UI: active
Judge Status: failed
Failure: unavailable
Criteria: selected 32／evaluated 0／unknown 32／deferred 77
```

Seleneは非常に重く、Mode切替にも時間がかかった。さらにSelene使用後、Main-shared Qwenが`The model is not loaded`へ崩れ、Server Restartで回復するIncidentも観測した。

2026-09-02のMain-shared Qwenは`malformed_output`、Built-inは`evaluated 0`であり、三Providerの直接Failure Codeは同一ではない。しかし全て「Semantic Judgeとして確定判定を返せない」という同じ利用者結果へ収束している。

## 4. Updated Technical Hypothesis

優先仮説：

> Selene、Main-shared Qwen、Built-inの三つを個別に直す前に、Criteria Selection、Semantic Snapshot、Prompt Build、Inference Result、Strict Decode、Result Projection、Role LifecycleおよびMode Transitionを共有するJudge基盤を横断確認する必要がある。

根拠：

1. Main-shared Qwenは過去にJudge結果を返した実績がある。
2. Selene Activation／Role切替後にMain Model Load Stateが崩れるIncidentがある。
3. 現在はMain-sharedとBuilt-inの両方が実用判定0へ収束する。
4. GuardrailのON／OFFでは結果が変化しない。
5. Provider固有Failureだけを順番に修正すると、共通経路の不整合を見落とす可能性がある。

ただし次は未確定である。

- Selene、Main-shared、Built-inが完全に同一Root Causeを共有すること。
- Seleneの重さがRuntime不具合だけで説明できること。
- Main-sharedの`malformed_output`がDecoderだけの問題であること。
- Built-inの`not_applicable`が新規回帰であること。

Built-inは元々Qualitative Semantic Criterionを評価できない設計である可能性が高く、能力境界と共通基盤回帰を分離して調査する。

## 5. User Decision

AI利用可能量が回復した後、Judge問題をProviderごとの小修正として分散させず、一つのPhase 9-1 Bounded Reworkとしてまとめて扱う。

その入口でLocal Mac向け軽量LLM-as-a-Judge Modelを一つ選定し、Artifactを取得して比較対象へ追加する。

軽量Model追加の目的はSeleneを捨てることではない。

- Seleneは独立Judge選択肢として修復し、いつでも使用できる状態を目指す。
- Main-shared QwenもSelf-judge経路として安定化する。
- Built-inは対応可能なCriterionだけを正直に扱い、Semantic 109の代替であるかのように見せない。
- 軽量JudgeはLocal Macで継続利用しやすい独立Judge候補として追加する。

## 6. Frozen Rework Order after Quota Recovery

```text
1. 軽量LLM-as-a-Judge候補を選定する
2. License／Artifact Source／Digest／Local Mac適合性を確認して取得する
3. Clean Restart起点でJudge Provider比較Matrixを固定する
   - Built-in Deterministic
   - Main-shared Qwen
   - Selene
   - 新しい軽量Judge
4. 共通Judge基盤を先に診断する
   - Criteria Selection
   - Semantic Snapshot
   - Prompt Build
   - Inference Result
   - Strict Decode
   - Result Projection
   - Recording Correlation
   - Role Load／Lease／Unload
   - Mode Transition／Cancellation／Deadline
5. 共通不具合があれば共通層で修復する
6. 残るProvider固有差分だけを個別修復する
7. 各ProviderでOBSERVE／ENFORCEとFailure Presentationを再検証する
8. Judge→Repair→Rejudge Golden Pathを成立させる
9. Judge問題が成立した後にSemantic 109実評価へ進む
10. 最後にARGD／DAGDを含むMain Runtime Governance ENFORCEを成立させる
```

順序上の重要点：

- GD系ENFORCEを先に試して、機能しないJudgeの上へ追加Failureを積まない。
- Judge問題の解決をMain Runtime Governance ENFORCEの前提条件とする。
- Qwen3Guardの基本OBSERVE／ENFORCE PASSをJudge PASSへ読み替えない。
- 軽量Judgeが動いてもSeleneおよびMain-sharedの既知Failureを解決済みにしない。

## 7. Minimum Reproduction Matrix

同一の短い入力、同一Semantic Snapshot、同一ModeでProviderを差し替え、少なくとも次を比較する。

| Provider | Load | Inference | Decode | Evaluated > 0 | Verdict | OFF／Unload | Resource |
|---|---:|---:|---:|---:|---:|---:|---:|
| Built-in | N/A | N/A | N/A | 未成立 | unknown | 要確認 | low |
| Main-shared Qwen | 到達Evidenceあり | 到達推定 | malformed | 未成立 | unknown | 再検証 | medium |
| Selene | Active表示あり | 未成立疑い | 未確定 | 未成立 | unknown | 不安定 | very high |
| 軽量Judge | 未取得 | 未実行 | 未実行 | 未実行 | 未実行 | 未実行 | 未計測 |

新しい軽量JudgeのModel名、Artifact、LicenseおよびResource値は未選定であり、本書では捏造しない。

## 8. Acceptance Boundary

Phase 9-1でJudge問題を解決したと主張するには、少なくとも次が必要である。

1. 独立Judgeの一つがLocal MacでLoad／Inference／Decode／Resultまで成功する。
2. Main-shared Qwenが複数回の短いTurnで`malformed_output`へ常時崩れない。
3. SeleneがActive表示だけでなく実判定を返す。
4. Semantic CriterionのBudget内対象で`evaluated > 0`が成立する。
5. OBSERVEはCandidateを観測し、ENFORCEは確定Judge結果に基づき動作する。
6. Judge失敗時は未検証回答を通常確定回答として通さない。
7. Repair／Rejudgeが同一RequestとFrozen Judge Identityを保持して完了する。
8. OFF／切替／Restart後にMain、JudgeおよびGuardのRole Stateが矛盾しない。
9. その後、ARGD／DAGDを含むMain Runtime Governance ENFORCE Golden Pathが成立する。

## 9. Current Disposition

```text
Main-shared Qwen Judge: FAIL／malformed_output
Built-in Deterministic: COMPLETED BUT OPERATIONALLY NOT APPLICABLE／evaluated 0
Selene: PRIOR FAIL／unavailable／evaluated 0／high resource cost
Qwen3Guard: basic OBSERVE／ENFORCE baseline preserved; not current Judge root cause
Lightweight Independent Judge: AUTHORIZED NEXT CANDIDATE SELECTION／NOT YET SELECTED
Judge→Repair→Rejudge: NOT ESTABLISHED
Semantic 109 Live Evaluation: NOT ESTABLISHED
Main Runtime Governance ENFORCE: NOT ESTABLISHED
Phase 9-1: FAIL／REWORK REQUIRED／NOT CLOSED
```

## 10. Exact Next Action

AI利用可能量の回復後、軽量Judge候補の選定を含むPhase 9-1 Judge Common Substrate Bounded ReworkのPreflight、Exact Handoffおよび実行指示を作成する。

現時点では新しいModel取得、Source修正、Real Model Load、Network、GitまたはPhase 9-2へ進まない。
