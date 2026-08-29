# Codex 5時間制限・手動再開・Resource消費・Project重量・将来Provider比較 Evidence

```yaml
document_id: codex_five_hour_manual_resume_resource_consumption_project_weight_and_future_provider_comparison_evidence_20260826145850
status: recorded_with_future_validation_reserved
classification: automation_resource_and_platform_observation
created_at: 2026-08-26 14:58:50 JST
scope: phase_6_remaining_rework_codex_two_task_operation
provider_behavior_claim_grade: user_observation_plus_controller_inference
execution_activation: not_performed_by_this_document
git_authority: not_granted_by_this_document
```

## 1. 目的

本書は、2026-08-26のPhase 6 Remaining ReworkにおけるCodex 2 Task運用中に観測・検討した、次のResource／Platform事項をAppend-only Evidenceとして記録する。

1. Codex側でUserが初めて観測した5時間制限。
2. 制限解除後にCodex Taskが自動再開しなかった実測。
3. Claude側で過去に成立した5時間制限解除後の自動再開との差分。
4. Fresh Executor Task、最小Mandatory Reading、Controller非並走でもCodex利用可能量の減少が速かった観測。
5. Claude側週間利用可能量50%増加Campaignによる単純比較不能。
6. Context長、Provider固有消費、Quota計算変更およびProject重量の切り分け。
7. Phase 0とPhase 6でUserが感じた消費速度差。
8. Phase 10冒頭で、Portable Development Governance Packageを使い、Copilotを含む第三Provider比較を行う将来候補。

本書はCodex製品内部のQuota Formula、恒久的な自動再開仕様、Provider間の優劣または将来の利用可能量を断定しない。

## 2. Codex 5時間制限の初回User観測

Userは2026-08-26、Codex側へ5時間制限が表示されるようになったことを初めて認識したと報告した。

```text
Codex Five-hour Limit
  User first observed date : 2026-08-26
  Prior known behavior     : no Codex five-hour limit observed by User
  Provider rollout date    : UNVERIFIED
  Account-wide availability: UNVERIFIED
```

「2026-08-26から全Codex利用者へ5時間制限が導入された」とは主張しない。User Account、Plan、App Version、段階Rolloutまたは表示変更のいずれによるものかは未確認である。

## 3. 制限解除後の再開挙動

Phase 6 Remaining Rework実行中に5時間制限へ到達し、その後User画面上で制限が解除された。しかし、新`設計者兼実装者役`Taskは自動再開せず、停止状態を維持した。

Userは対象Taskへ途中報告を求め、TaskはCurrent StateをDirect Returnした。その後、Controllerが明示Continuation Messageを送り、P6-RR-EのCurrent Integration地点から再開させた。

```text
Limit reached                       : USER OBSERVED
Limit reset／recovered              : USER OBSERVED
Automatic task resume               : NOT OBSERVED
Explicit User／Controller action     : REQUIRED IN THIS CYCLE
Completed package redo              : 0 instructed
Recovery-based differential resume  : PERFORMED
```

### 3.1 Claude側との観測差

Claude側では、過去の5時間制限到達時に、制限解除後、User入力が自動生成されて作業が自動再開する挙動を実測している。

今回のCodexでは同様の自動再開は成立しなかった。この差について、UserとControllerは「Codex Runtime／Platform側に、Claudeと同種の自動再開機能がまだ存在しない可能性」を推論した。

ただし、次を分離する。

```text
Observed
  Claude : past cycleでautomatic resume成立
  Codex  : current cycleでautomatic resume不成立

Inferred
  Codex Runtime／Platformにautomatic resume機能が未実装の可能性

Unknown
  恒久仕様／段階導入／一時的不具合／Task状態依存／Account依存
```

したがって、現時点の運用はCodex制限解除後にUserまたはControllerがCurrent Recoveryを確認し、Exact Continuationを明示する方式とする。

## 4. Sequential Two-Task運用

5時間制限解除後も、次の順番を維持した。

```text
Codex／設計者兼実装者役が単独Long Run
  -> Complete Candidate／STOPPED_SAFE／User-requested Interim Return
  -> Codex／プロジェクト責任者兼設計統括者役が境界Review
  -> Exact Resume／Reworkを送信
  -> Controllerは再びWAITING
```

Executor実行中のController Polling、途中Source Review、並行Testおよび先回りReworkは行わない。今回のInterim ReturnはUser明示依頼によるものであり、通常のPackage進捗報告ではない。

## 5. User観測Resource Snapshot

Phase 6 Remaining Reworkの途中で、Userは次を報告した。

```text
Codex five-hour availability : 34% remaining
Codex weekly availability    : 74% remaining
Observation source           : User-visible product meter
Exact token／task breakdown  : UNAVAILABLE
```

この時点で、Codex週間利用可能量のUser Policyは最低50%保全、55〜60%付近を警戒／安全停止判断帯とする方針だった。

5時間枠34%の方が先に尽きる可能性が高い一方、週間74%から警戒帯までの余白も大きくないと判断した。Task自身がMeterを観測できないため、数値を推測せず、User通知をStop Authorityの正本とする。

## 6. Fresh Task／最小Contextでも速い消費

今回のCodex Executorは、旧Taskを再利用せずFresh Taskとして作成した。また、次のResource Correctionを適用していた。

- 旧Taskの会話Context、Authorityおよび未完了状態を非継承。
- Frozen Exact HandoffとMandatory Reading Setを正本とする。
- 関係のないProject Docsを無差別に読ませない。
- Controller TaskはExecutor実装中に完全WAITING。
- 完了済みPackageを再実行しないDifferential Resume。

それでもUserは利用可能量の減少を速いと感じた。このため、次の仮説を分離した。

| 仮説 | 現時点の評価 |
|---|---|
| 旧巨大Contextだけが主因 | 単独説明としては弱まった |
| Controller／Executor並走が主因 | 前回消費には大きく寄与。今回は除去済み |
| Codex自体の消費特性 | 依然として有力、未確定 |
| Codex Quota計算／Product方針変更 | 可能性あり、未確認 |
| Phase 6／Project自体の重量 | 有力 |
| 複数要因の合成 | 最有力候補 |

```text
Minimum Docs
  != Small Effective Context
  != Small Codebase
  != Light Implementation Task
```

## 7. Claude 50%増加Campaignによる比較交絡

Userは後から、Claude側で2026-08-31まで週間利用可能量上限を50%増加するCampaignが行われていたらしいと認識した。

```text
Campaign Provider : Claude
Reported Benefit  : Weekly availability ceiling +50%
Reported End      : 2026-08-31
Source            : User observation／recognition
Controller independent verification : NOT PERFORMED
```

この条件が前回のClaude利用期間へ適用されていた場合、製品画面上の残量減少率をCodexと単純比較できない。

したがって、現時点で許されるClaimは次までとする。

```text
Allowed Claim
  今回の条件ではCodexのUser-visible availabilityが速く減少した。

Not Yet Allowed
  CodexはClaudeより本質的に常に燃費が悪い。
```

比較時には、Campaign、Plan、Model、Reasoning、Task Context、Tool Call、並列度、Compaction、5時間制限、自動再開およびProject重量を条件として記録する。

## 8. Project／Phase 6の重量

今回、Mandatory Docsを限定しても、実装対象Project自体が大きいため、Taskが軽量になるとは限らないと整理した。

Phase 6 Remaining ReworkのFrozen Scopeおよび直前Baselineには、少なくとも次が含まれる。

```text
Packages                    : 11
Work Units                  : 68
Acceptance IDs              : 40
Backend baseline            : 1602 passed / 7 deselected
Frontend baseline           : 221 tests
Canonical mypy scope        : 443 source files
Semantic criteria           : 109
Major integration areas     : Semantic Runtime／Main／Judge／Guard／Repair／Recording
Dedicated provider targets  : Selene／Qwen3Guard
Additional concerns         : Lifecycle／Concurrency／Timeout／Evidence／Browser／Real Model
```

実装TaskはDocsだけでなく、大量の既存Source、Test、Composition、API、FrontendおよびTool Outputを関連付ける必要がある。変更1件の影響範囲、Regression確認およびEvidence生成が、Project成長とともに非線形に増えた可能性が高い。

## 9. Phase 0とのUser長期観測

Userは、Codexの`プロジェクト責任者兼設計統括者役`TaskとPhase 0の初期要件定義段階から継続しており、初期には現在ほど利用可能量が急減していなかった印象を持っていると報告した。

この長期観測は有用だが、統制された比較ではない。Phase 0と現在では次が異なる。

| Phase 0頃 | Phase 6現在 |
|---|---|
| 要件・Architecture・Docs中心 | Source／Test／Runtime統合中心 |
| 小規模Source／Test | Backend 1600超、Frontend、実Model |
| Regression影響範囲が限定的 | Multi-component／Concurrency／Evidence |
| Task間Automationが未成熟 | Cross-task Handoff／Review／Rework |
| Product／Model／Quota条件が当時のもの | Current Product／Model／Quota条件 |

したがって、Userの記憶違いと決めつけず、次の組合せを暫定仮説とする。

```text
Phase 0当時は実際にTaskが軽かった
+ Projectが大規模化した
+ 変更影響が非線形に増えた
+ Codex側のModel／Product／Quota条件も変化した可能性
```

「途中からCodexが改悪された」とは断定しない。

## 10. 第三Provider／Copilot研究候補

CodexとClaudeだけの二者比較では、共通Blind Spot、Campaign、QuotaおよびProject適応差の影響を分離しにくい。Userは将来、経済的資金力が許せば、Copilotを第3研究所として追加する案を提示した。

期待する価値は次の通りである。

- Codex／Claude共通Blind Spotに対する第三者比較。
- Provider Resource Limit発生時の継続性。
- 同一Frozen Handoffに対する理解、実装、自己Reviewおよび燃費比較。
- Cross-provider Development Governance Packageの移植性検証。

ただし、直ちにProviderを追加せず、Phase 10冒頭での検討を優先する。

## 11. Phase 10冒頭での比較候補

揺れを減らし、開発Governance移植用Packageの動作確認を兼ねるため、次の順序を候補とする。

```text
Phase 9 Closure
  -> Phase 3〜9 Docs統合
  -> docs/project/shared/constitution/ 再編成
  -> MARGPA-RUNTIME-LLM直下の開発Governance移植用Package作成
  -> 別環境への移植Acceptance
  -> Copilotを第3研究所として投入
  -> Codex／Claude／Copilot比較
```

ここで検証するPackageは、Phase 8 Agent／Tool Runtimeへ適用する`margpa-runtime-llm/constitution/`とは別である。

```text
Development Governance Portability
  : docs/project/shared/constitution/
    + MARGPA-RUNTIME-LLM直下の移植用Package

Runtime Constitution
  : margpa-runtime-llm/constitution/
```

同一Package、同一Task Role、同一Frozen Handoff、同一Acceptance、同一Evidence Formatを使用し、ProviderとTask Identityだけを主要変数に近づける。

Copilot投入はUserの経済的資金力、利用可能なPlan、Phase 10時点のProject状態およびUser開始宣言をGateとする。本書は導入、契約、課金またはTask作成を許可しない。

## 12. 将来比較で記録する条件

Provider燃費を比較する場合、少なくとも次を記録する。

1. Provider、Product、Plan、Model、Reasoning設定。
2. Campaign、Bonus、週間上限、5時間上限およびReset条件。
3. TaskがFreshか、継続Taskか、Compaction後か。
4. Mandatory Reading数、Input量およびProject Scope。
5. Source／Test規模、Tool Call数、Full Test回数。
6. 並列Task数とController並走の有無。
7. 開始／終了時のUser-visible Meter。
8. Completion CandidateまでのWall Time。
9. Review Finding、Rework回数、False CompletionおよびIncident。
10. Acceptanceを満たした実効Throughput。

速度または残量だけでなく、同一品質Gateを満たすまでの総消費で比較する。

## 13. 現在地

```text
Codex Five-hour Limit First User Observation : 2026-08-26
Codex Automatic Resume                       : NOT OBSERVED IN CURRENT CYCLE
Codex Explicit Continuation                   : PERFORMED
Claude Historical Automatic Resume            : OBSERVED IN PRIOR CYCLE
Fresh Codex Executor                           : ACTIVE IN CURRENT OPERATION
Controller Parallel Work                       : DISABLED／WAITING DEFAULT
Observed Five-hour Remaining                   : 34%
Observed Weekly Remaining                      : 74%
Weekly Minimum Reserve                         : 50% USER POLICY
Warning／Stop Candidate Band                   : 55-60%
Claude +50% Campaign                           : USER REPORTED／COMPARISON CONFOUNDER
Codex-vs-Claude Intrinsic Efficiency            : UNRESOLVED
Project Weight Contribution                    : PLAUSIBLE／LIKELY MATERIAL
Copilot Third Laboratory                       : PHASE 10 CANDIDATE／NOT AUTHORIZED
```

## 14. Evidence限界

- Product内部のQuota Accounting、Token Cache、Context Compression、Tool Call Weightおよび5時間制限実装は観測不能である。
- User-visible Percentageは正確なToken量またはCostを表すとは限らない。
- Phase 0とPhase 6はTask内容、Project規模、Product VersionおよびModel条件が一致しない。
- Claude CampaignのExact適用条件はControllerが独立検証していない。
- 今回のCodex自動再開不成立を、全Account／全Version／将来Versionの恒久仕様へ一般化しない。
- Provider固有消費とProject重量の分離には、Phase 10候補の統制比較が必要である。
