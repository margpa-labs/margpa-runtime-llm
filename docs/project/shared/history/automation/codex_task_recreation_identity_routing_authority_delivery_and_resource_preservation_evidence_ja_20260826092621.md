# Codex Task再生成・Identity Routing・Authority Delivery・Resource保全 Evidence

```yaml
document_id: codex_task_recreation_identity_routing_authority_delivery_and_resource_preservation_evidence_20260826092621
status: recorded_and_followup_reserved
classification: automation_operational_evidence
created_at: 2026-08-26 09:26:21 JST
scope: codex_two_task_phase_6_remaining_rework_pre_activation
execution_activation: not_performed_by_this_document
git_authority: not_granted_by_this_document
supersedes: none
```

## 1. 目的

本書は、Phase 6 Remaining Rework再開前に行った次の一連の判断と実測結果を、後から欠落なく再構成できるようAppend-only Evidenceとして固定する。

1. Codexの週間利用可能量と新たに観測された5時間制限をScheduling Resourceとして扱う判断。
2. Claude復帰後のIndependent Review等に備え、Codex週間利用可能量を最低50%以上残す方針。
3. 長大化したTask Contextと利用可能量消費の関係について、確認できる事実と推論を分離した検討。
4. 旧「設計者兼実装者役」Taskを改名し、Fresh Contextの新「設計者兼実装者役」TaskへRoleを再Bindingする判断。
5. Task Title、Role ContractおよびTask／Thread IDを分離するRouting規則。
6. 新Taskへ実行AuthorityとDocs取扱Authorityだけを直接送信し、実装を開始させない疎通試験。
7. 新TaskからController TaskへのDirect Return成立。
8. 旧TaskをArchiveせず、Historical Evidence参照用として保持する判断。
9. 後続の実装、Independent Review、ReworkおよびRe-review結果を別のAutomation Evidenceへ記録する予約。

## 2. 起点となったUser観測と要求

Userは、2026-08-26の再開検討時に、次を報告・要求した。

```text
Codexの週間利用可能量が再び回復していた。
Codex側にも5時間制限が表示されるようになった。
Phase 6の続きを進めたい。
Claudeが復活した時のため、Codex側は最低でも50%以上残しておきたい。
Contextが蓄積したTaskほど利用可能量の減少が速くなるのか確認したい。
減りやすいのであれば、別Taskの「設計者兼実装者役」も作り直した方がよいか検討したい。
```

ここでいう週間利用可能量と5時間制限は、UserがCodex製品画面から観測したScheduling Contextである。Project内Telemetryから再導出した値ではなく、正確なToken換算式、Task別内訳またはProvider内部のQuota計算方式を本書は主張しない。

## 3. Resource判断

### 3.1 確認可能な事実

- 新しいTaskを作成しても、Account全体の週間利用可能量または5時間制限そのものはResetされない。
- Model RequestはInput Contextを処理し、Input／Output Tokenという使用量概念を持つ。
- Codex Appの週間表示と5時間表示が、Task Context長、Cached Input、Tool Call、Reasoning、Wall Timeその他の要素をどう換算するかというExact Formulaは、今回確認できた公開仕様だけでは確定できない。
- したがって「Contextが長いほど週間利用可能量が必ず一定比率で速く減る」とは断定しない。

### 3.2 運用上の推論

長い会話履歴、過去Tool Output、撤回済み仕様、古いAuthorityおよび大量のRecovery文脈を持つTaskは、Fresh Taskより大きなEffective Contextを必要としやすい。また、旧情報の再解釈や仕様DriftがReworkを増やせば、直接のInput処理量だけでなく総Turn数も増える。

このため、Frozen HandoffとMandatory Reading Setが既に存在する今回の条件では、設計者兼実装者役をFresh Taskへ切り替えることは、次の両面で合理的と判断した。

- Carry-over Contextを減らし、利用可能量消費を抑えられる可能性がある。
- 過去の撤回済みAuthorityや旧仕様を誤って再使用するRiskを下げられる。

ただし、これはQuota削減量を保証する判断ではない。Fresh Taskが正本Docsを再読するInitial Costや、Context不足によるReworkがSavingsを相殺する可能性も残る。

### 3.3 Resource保全方針

Userの最低保全線はCodex週間利用可能量50%である。表示更新遅延、Return Handoff、Independent Reviewおよび安全停止記録に必要な余白を考慮し、運用上は55〜60%付近を実装継続の警戒／停止判断帯として扱う候補を提示した。

この値は自動停止を実装したものではなく、Userが製品表示を見て判断するOperational Guidelineである。今後Userが別の閾値を宣言した場合は、その新しい宣言を優先する。

## 4. Task再編成

Userは旧Taskを次のように改名し、新Taskへ現行Role Titleを割り当てた。

```text
旧Task Title : 設計者兼実装者役
変更後Title  : 元設計者兼実装者役_1

新Task Title : 設計者兼実装者役
```

Task一覧照合時に確認したIdentityは次の通りである。

| Role／状態 | Task Title | Task／Thread ID | 観測状態 |
|---|---|---|---|
| Controller | プロジェクト責任者兼設計統括者役 | `019f739b-8a21-7592-95cc-c83c9c08e5f6` | active |
| Current Executor | 設計者兼実装者役 | `01a03b6c-2a68-7881-99bc-c788a600f632` | idle |
| Historical Executor | 元設計者兼実装者役_1 | `019f7486-5ba3-7e11-8d3a-218f49c30ec9` | notLoaded |

新TaskはTask一覧上`projectId: null`であったが、`cwd`はAuthorized Project Rootと一致していた。今回のTask間Message Deliveryには支障がなかった。これはProject紐付けが一般に不要であるという恒久規則ではなく、今回の実測に限定する。

## 5. Task IdentityとRole Authorityの分離

今回、次の3層を分離して扱う規則を確認した。

```text
Task Title
  = User／Controllerが対象Taskを発見するHuman-readable Label

Task Content／Start Declaration／Frozen Handoff
  = Role、Objective、Authority、ScopeおよびStop Conditionの正本

Task／Thread ID
  = Task間Messageを実際にRoutingする一意の宛先
```

したがって、Task TitleだけではRole Authorityは成立しない。また、Task Renameによって旧Taskの会話履歴、Authorityまたは未完了状態が新Taskへ移動することもない。

今後のRouting規則を次のように固定した。

- `設計者兼実装者役`は、現行新Taskを指す。
- `元設計者兼実装者役_1`はHistorical Taskであり、Userが明示指定しない限り送信先にしない。
- 送信前にTask一覧でTitle、Task／Thread ID、作業Rootおよび必要に応じて最新Summaryを照合する。
- 実配送はTask／Thread IDへ行う。
- 同名Taskが複数存在する場合、Titleだけで推測配送しない。
- サブエージェントには「設計者兼実装者役」等の他Task用Role名を付与しない。

## 6. Authority Delivery疎通試験

Userは、実装開始前の疎通試験として、新「設計者兼実装者役」Taskへ次の2種類のAuthorityだけを送るよう指示した。

1. 実行Authority。
2. Docs取扱Authority。

ControllerはTask一覧を照合し、新Task ID `01a03b6c-2a68-7881-99bc-c788a600f632`を宛先として、旧Taskへ送信せず直接Messageを送った。

### 6.1 指定したFrozen Contract

```text
docs/project/phases/phase_6/handoffs/phase_6_claude_remaining_rework_exact_handoff_ja_20260825130924.md
docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_design_freeze_ja_20260825130924.md
docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md
```

### 6.2 実行Authorityの内容

- 新TaskをMARGPA-RUNTIME-LLMの現行「設計者兼実装者役」として指定した。
- 旧TaskのAuthority、会話Contextおよび未完了状態を自動継承しないよう明記した。
- 別途UserのExact Start宣言を受領した後に限り、Frozen Contractに従ってPhase 6 Remaining Reworkを実行できるとした。
- Authority通知だけでは、実装、検証、Model Load、Network、Git、ClosureまたはPhase 7を開始しないよう固定した。

### 6.3 Docs取扱Authorityの内容

Exact Start成立後、Frozen Contractの範囲内で次を許可した。

- Mandatory Reading DocsのRead。
- Scope内Source、TestおよびConfigのReadと必要な実装Mutation。
- Phase 6 Recovery、Evidence、History IndexおよびCompletion Candidate HandoffのAppend-only作成。
- Package単位Recovery Index作成と、Compaction／利用制限後の差分再開。

別途Exact Authorityなしでは、次を禁止した。

- Frozen／Stable Docsの上書きまたは意味変更。
- Roadmap、Phase IndexまたはClosure文書の更新。
- Git操作。
- Project Root外Action。
- Provider MemoryまたはUser `runtime_data`への接触。
- Network DownloadまたはExternal Service Mutation。
- Destructive Cleanup。

完了時はController TaskへDirect Return Handoffを返し、Independent Review待ちで停止するよう指定した。

送信時の状態は次の通りである。

```text
Authority State : GRANTED_BUT_NOT_ACTIVATED
Execution State : WAITING_FOR_EXACT_USER_START
```

## 7. Direct Return結果

新Taskは、送信元Task ID `01a03b6c-2a68-7881-99bc-c788a600f632`を伴うDirect Returnで次を返した。

```text
Authority通知を受領しました。
旧TaskのAuthority・会話Context・未完了状態は継承しません。
現在はWAITING_FOR_EXACT_USER_STARTとして待機します。
```

この結果から、今回の限定試験では次が成立した。

| 検証項目 | 結果 |
|---|---|
| 新旧TaskのTitle分離 | PASS |
| 新Task IDの解決 | PASS |
| 旧Taskへの誤配送防止 | PASS |
| Controllerから新TaskへのDirect Delivery | PASS |
| AuthorityとActivationの分離 | PASS |
| 旧Context／Authority非継承の明示 | PASS |
| 新TaskからControllerへのDirect Return | PASS |
| 実装非開始 | PASS |

本試験はMessage RoutingとAuthority Receiptの成立を示す。Phase 6 Remaining Reworkの実装、Review、Rework、Closure ReadyまたはResource Savingsの成立を示すものではない。

## 8. 旧TaskのArchive判断

Userは一時、旧`元設計者兼実装者役_1`をArchiveすることも検討したが、TitleとTask／Thread IDで新旧が明確に分離でき、誤配送防止規則も成立したため、Archiveは不要と判断した。

旧Taskを保持する利点は、過去の実装、Rework、Finding、Direct ReturnおよびProvider挙動をHistorical Evidenceとして後から参照できることである。旧TaskはActive Executorではなく、明示指定がない限り送信対象外とする。

```text
Historical Task Retention : YES
Archive Required           : NO
Default Routing Target     : New Current Executor Task only
```

## 9. 前回のResource Evidenceとの関係

本書は、次の既存記録を置換せず、その後続Evidenceとして扱う。

- `docs/project/shared/history/automation/codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md`
- `docs/project/shared/history/automation/codex_two_task_phase_6_parallel_controller_resource_observation_ja_20260825014841.md`

前回はExecutor稼働中にControllerも並走し、User観測でCodex利用可能量が約70〜80%減少したため、Resource Efficiencyを`FAIL / ADJUST`とした。今回のFresh Task再Bindingは、そのCorrectionで定めた次のLoopを実行しやすくするためのPre-activation準備である。

```text
ControllerがExact Handoff／Authorityを送信
  -> Executorが単独Long Run
  -> ControllerはUserへTurnを返してWAITING
  -> Executor Return後にControllerが集中Review
  -> Exact Rework送信
  -> Controllerは再びWAITING
```

## 10. 後続Automation結果の記録予約

新「設計者兼実装者役」Taskを用いて、実際に次のLoopを一通り実施した後、その結果を必ず新しいAppend-only Evidenceとして記録する。

```text
Implementation
  -> Controller Independent Review
  -> Exact Rework
  -> Controller Independent Re-review
  -> PASS／追加Rework／STOPPED_SAFE／Resource Stop
```

記録先の正本Directoryは次とする。

`docs/project/shared/history/automation/`

後続Evidenceは本書を上書きせず、少なくとも次を含める。

1. 使用したController／Executor Task TitleとTask／Thread ID。
2. Exact Start、Authority Envelope、Frozen Handoff RevisionおよびMandatory Reading Set。
3. 実装開始・終了状態、Package／Work Unit、Changed PathおよびValidation。
4. Direct Message／Direct Returnの成功、失敗、再送および誤配送の有無。
5. Executor実行中にControllerがWAITINGを維持できたか。
6. Controller Reviewで検出したFinding、Severity、Evidence GradeおよびFalse Completionの有無。
7. Exact Rework内容、Rework回数、Re-review結果およびOpen Finding。
8. Auto Compaction、5時間制限、週間利用可能量、Safe Stopおよび差分再開の実測。
9. User観測によるCodex利用可能量の開始値、境界値、終了値。未観測値を推測で補わない。
10. 50%保全方針と55〜60%警戒／停止判断帯が機能したか。
11. Claude復帰時に必要なCodex Resourceを保全できたか。
12. Scope、Root、Docs、Git、Network、Provider MemoryおよびUser Data BoundaryのIncident Accounting。
13. User Intervention回数、Controller可用性、Wall Timeおよび実効Throughput。
14. 最終状態が`COMPLETE_CANDIDATE`、`REWORK_REQUIRED`、`STOPPED_SAFE`、`BLOCKED`または`CLOSURE_READY`のどれであるか。

Loopが途中で停止した場合も記録を延期しない。完遂結果だけでなく、5時間制限、週間Resource保全、安全停止、Task再生成またはDirect Communication FailureそのものをAutomation Evidenceとして残す。

## 11. 現在地

```text
Codex Weekly Availability Recovery        : USER REPORTED
Codex Five-hour Limit                     : USER OBSERVED
Minimum Codex Weekly Reserve               : 50% USER POLICY
Operational Warning／Stop Candidate Band  : 55-60%
Old Executor Rename                       : COMPLETE
New Executor Task Creation                : COMPLETE
Task Identity Resolution                  : PASS
Authority Delivery                        : PASS
Authority Receipt Direct Return           : PASS
Execution Activation                      : NOT PERFORMED
Phase 6 Remaining Rework                  : NOT STARTED BY THIS EVIDENCE
Old Executor Archive                      : NOT REQUIRED／NOT PERFORMED
Implementation／Review／Rework Evidence    : RESERVED／NOT YET RECORDED
```

## 12. Evidence限界

- Codex製品内部のQuota計算式、Context再利用方式、Cached Input適用、Task単位のToken内訳および5時間制限のExact Accountingは本書から確定できない。
- Fresh Taskが旧Taskより何%Resource Efficientかは、後続Loop完了後にUser観測と実行結果から評価する。
- Direct Return成功はRoutingとReceiptの成立を示すが、Long Run継続性、Compaction Recovery、Review品質またはClosure品質を保証しない。
- Task TitleとSummaryはDiscovery Dataであり、Authority正本として単独使用しない。
- 本書はProvider一般の恒久的性質ではなく、2026-08-26時点のCodex App、対象Project、Task構成およびUser運用に限定したHistorical Evidenceである。
