# Phase 9-1 Judge Token Budget／Planner Proof／Context 16K Decision／Role分離予約

```yaml
document_id: phase_9_1_judge_token_budget_planner_proof_context_16k_decision_and_deferred_role_split_20260902150815
document_type: append_only_user_decision_evidence_and_planned_work_reservation
document_state: accepted_waiting_for_package_2_return
language: ja
created_at: 2026-09-02 15:08:15 JST
owner: Nazuna Research
phase: phase_9
program: phase_9_1
source_mutation_by_recorder: none
runtime_action_by_recorder: none
network_action_by_recorder: none
git_action: none
package_2_planner_proof_required_first: true
user_manual_recheck_required_before_context_expansion: true
context_expansion_package_state: reserved_not_started
role_specific_context_split_state: deferred_after_mvp
```

## 1. Trigger

Phase 9-1 Package 2実行中、Claudeは次を報告した。

> 共通基盤の主要な修正（トークン予算超過によるトランケーション、失敗コード不整合）を実装した。次に既知の2件のテスト失敗（Selene用Fixtureの`count_chat_prompt_tokens`欠落）を修正する。

これを受け、過去に観測したMain-shared Qwenの`malformed_output`、Seleneの`unavailable`およびSemantic Judgeの`evaluated 0`に、Token Budget超過または出力Truncationが関係していた可能性を再検討した。

## 2. Causal Classification

Token Budget／Truncationは有力な一因だが、全Judge Failureの単一Root Causeとはしない。

| Observation | Token Budgetとの関係 |
|---|---|
| Main-shared `malformed_output` | JSON末尾切断で発生し得るため有力 |
| Selene `unavailable` | Deadline／Truncationの誤分類はあり得るが、Load／Lifecycle／Memoryも候補 |
| `The model is not loaded` | Role Lifecycle／Model Load問題であり、Tokenだけでは説明不能 |
| Built-in `evaluated 0` | Model CallがないためToken原因ではない |
| Semantic 109 `Deferred 109` | Prompt／Output Budget、Criterion Selectionおよび能力境界を分離して確認する |

Judge内部には通常Chatとは別の出力上限がある。2026-09-02確認時点で、Main Live Judgeには小さい固定Output枠、Semantic EvaluatorにはProvider共通のBatch／Prompt／Output枠が存在した。Application全体の`max_new_tokens`を増やすだけでは、Judge内部上限が自動的に増えるとは限らない。

## 3. Planner Fix Acceptance Proof

Codex週間Quotaを温存するため、Claudeの自己申告だけでPlanner修復を受理しない代わりに、第三者が後から一Commandで再実行できるRegression EvidenceをPackage 2へ追加するようUserが指示した。

必須Evidenceは次である。

1. Planner無効時、一括Criteriaと小Output枠でJSON Truncation／`malformed_output`が再現する。
2. Planner有効時、各Batchで次をAssertする。

```text
prompt_tokens
+ reserved_output_tokens
<= effective_context_limit
```

3. Criterion欠落0、重複0、Provider／Request Identity Drift 0。
4. Partial JSONを成功Decodeしない。
5. Budget、Truncation、Timeout、Unavailableを別Typed Failureへ保持する。
6. Plannerを一時Sabotageすると新Testが失敗し、復元後にPASSする。
7. Main-shared Qwen／Selene／Gemmaを同一条件で最低3回記録し、Provider別に`malformed_output`常態化が解消したか示す。
8. Exact ReturnへFocused pytest Command、Test名、Before Failure、After PASSおよびToken計測値を記載する。

このEvidenceはIndependent Reviewそのものではない。Codex利用可能量回復後、説明文ではなくFocused TestとSource差分だけをTargeted Reviewする。

## 4. Current Hardware／Configuration Facts

2026-09-02のRead-only確認値：

```text
Host                  : MacBook Pro Mac14,9
Chip                  : Apple M2 Pro, 10 Core
Unified Memory        : 16 GB
Observed Free Memory  : 51%（全Model同時Load時の測定ではない）
Current Context       : 8192
Current max_new_tokens: 2048
Main Native Context   : 40960
```

Artifact Size：

```text
Main Qwen 4B Q4       : 2,497,280,256 bytes
Gemma 4 E2B Q4_0      : 3,349,516,256 bytes
Qwen3Guard 0.6B Q8_0  :   804,753,472 bytes
Selene 8B Q5_K_M      : 5,732,992,896 bytes
```

16GB環境ではMain単体またはMain＋Gemmaは16K化を段階検証する価値がある。一方、Main＋Selene＋Guardを全て16Kで常用するのはMemory Pressure Riskが高い。

## 5. User Decision — Post-Package-2 Context Expansion

Package 2のPlanner修復と上記証明を確認した後、次の値を独立Packageで実装する。

```text
Current Context Size        : 16384
Effective Context Maximum   : 16384

Current max_new_tokens      : 4096
Maximum max_new_tokens      : 8192
```

`max_new_tokens = -1`というUnlimited Sentinelは使用しない。現契約は正整数を要求する。通常値4096、選択可能上限8192とする。

Maximum 8192は`context_size - 1`からの自動導出ではなく、Deployment／Application Profileに由来する明示的なOutput Ceilingとして扱う。Source内へMac固有値を散在Hard-codeしない。

## 6. Scope Decision — Role別Context分離は予約

Dedicated Judge／Guardが起動時の共通`load_config.context_size`を使うCurrent Architectureでは、Global Profileを16KにするとDedicated Roleも16KでLoadされる。

Role別Context設定は設計として妥当だが、Config Schema、Resolver、Bootstrap、Provider Lifecycle、UI、TestおよびManualへ変更が広がる。MVPを遅らせる可能性があるため、今回の16K Packageには含めない。

当面の運用：

```text
Main Qwen + Gemma Judge通常運用:
  context 16384／default output 4096／maximum output 8192

Selene使用時:
  local_macos_arm64 Profileを8192へ戻す
  Server Restart後にSeleneをLoadする
```

UI上でMain Contextを下げるだけではDedicated Roleの起動時Load Configへ確実に反映されないため、Selene時はProfile変更＋Restartを正本手順とする。

Role別Context分離は、MVP後、Selene常用頻度増加、16K／8K切替Cost増大または実測Memory問題が発生した時に再評価する。

## 7. Package Boundary

Context Expansion PackageのEntry条件：

- Package 2 Exact Returnが存在する。
- Planner専用Regression EvidenceがPASSする。
- Sabotage時Failure／復元後PASSが記録される。
- Package 2完了後、UserがJudge／Repair／Semantic 109／Main Runtime Governance ENFORCEの実画面再確認を行う。
- User Manual結果がContext拡張前Baselineとして記録され、Context拡張開始をUserが許可する。
- Current Working Treeに復旧不能な競合がない。
- Active Judge／Guard WorkerおよびLoad途中Modelがない。

実行順序は次で固定する。

```text
Package 2 Long-run
-> Planner Proofを含む二段階Internal Review／Exact Return
-> User実画面テスト
-> UserによるPackage 3開始
-> Context 16K／Output 4K・8K Expansion
```

Entry条件前にContext値だけを増やして、Planner FailureまたはPackage 2の実画面FailureをMemory／Context増加で隠さない。

## 8. Claim Boundary

本書はContext Expansion実装Authorityではない。実装は専用Exact Handoffで開始する。

16K Main単体とMain＋Gemmaの実機Smokeを通過するまで、`deployment_hardware_verified_context_limit=16384`を成立済みと主張しない。Selene 16K、全Role同時16Kまたは16GB環境での無制限安定性はClaim対象外とする。
