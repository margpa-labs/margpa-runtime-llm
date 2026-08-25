# Codex Two-Task Long-run／Review／Rework Orchestration Reservation

## 1. 文書状態

```text
Document Class : Planned Operating Mode Candidate / Append-only History
Status         : RESERVED / NOT ACTIVATED
Recorded At    : 2026-08-23 09:53:16 JST
Automation     : NOT ACTIVATED BY THIS DOCUMENT
Task Creation  : NOT AUTHORIZED BY THIS DOCUMENT
Git Mutation   : NOT AUTHORIZED BY THIS DOCUMENT
```

本書は、Claude側利用可能量の不足時、またはCodex Task間の直接連携がResource・速度・伝達コスト上有利な場合に、Codexの2 Taskを用いてPhase実装をClosure Readyまで進める運用候補を記録する。

これは現時点での起動指示ではない。対象Phase、Exact Scope、Task Identity、権限、開始条件を固定し、Userが開始を宣言した時だけ有効化できる。

## 2. 構成する2 Role／Task

### 2.1 プロジェクト責任者兼設計統括者役

現在のController Taskを想定する。主な責務は次の通り。

- Project目的、最上位規則、Authority BoundaryおよびUser Gateの維持
- Phase目的、Acceptance、Architecture Invariant、Exact EnvelopeのFreeze
- 実装TaskへのHandoff、Recovery、Evidence Contractの定義
- Complete Candidateに対するSource-based Independent Review
- FindingのBlocker Eligibility、SeverityおよびEvidence Gradeの判定
- Exact Rework Handoffの作成と担当Taskへの直接Routing
- 技術的Closure RecommendationとClosure Ready判定
- Human Decisionを本当に人間にしか決められない事項へ限定

Controllerは、通常の実装作業を自分へ回収しない。緊急で有界な修正、独立検証に不可欠なProbe、または担当Taskが安全に継続不能な場合を除き、実作業は設計者兼実装者役へ委任する。目的はControllerの利用可能量をReview、Governance、Critical DecisionおよびClosureへ集中させることである。

### 2.2 設計者兼実装者役

既存の設計者兼実装者役Taskを想定する。主な責務は次の通り。

- FrozenなPhase目的とAcceptanceからの動的な工程分解
- 必要十分なSubphase／Work Unit設計
- Source、Test、必要な新規Docsの実装
- Static／Unit／Integration／Regression Test
- 自己Review、Failure修正、Material Boundary Recovery
- Complete Candidate Handoffの作成
- Controllerから受領したExact Reworkの実装と再検証

同Taskは、与えられたRole、Authorized Root、Phase Scope、Authority Envelopeおよび運用規則の範囲内で、都度の動的判断を行う。通常の設計選択や実装詳細を毎回Controllerへ返す運用にはしない。

## 3. 基本Execution Loop

```text
User Start / Human Gate
        ↓
Controller: Phase Contract／Exact Envelope／Acceptance Freeze
        ↓ Direct Task Message or Frozen Repository Handoff
Designer + Implementer: Long Run
        ↓
Material Boundary Recovery／Tests／Self-review
        ↓
Complete Candidate Handoff
        ↓ Direct Report
Controller: Independent Review
        ├─ PASS → Closure Ready Recommendation
        ├─ REWORK → Exact Rework Handoff
        │               ↓
        │       Designer + Implementer Rework
        │               ↓
        └────── Independent Re-review
        ↓
User Acceptance／Backup／Final Closure Gate
```

Rework回数は固定しない。重大Findingが0になる、真のBlockerが確認される、Resource Limitにより安全停止する、またはUserが方針を変更するまで、必要な範囲で往復する。

途中報告はEvidenceとして残してよいが、通常のSubphase完了報告を理由にLong Runを止めない。

## 4. Task間の直接通信

Codex側で対象TaskがAddressableなLive Coordination Targetである場合、ControllerはTask間通信を使用して、Handoff、Review結果、Rework指示および完了報告を直接往復できる。この経路により、Claude併用時にUserが担っているCopy／Relay負担を減らせる。

ただし、次を必須とする。

- 実在するExact Task Identityを送信前に確認する。
- `From`、`To`、Phase、Work Unit、Revision、Authority、Stop Conditionを明記する。
- Repository内のFrozen HandoffまたはDigest付きContractを正本とする。
- 受領確認またはTask Statusを確認し、送信しただけで適用済みとみなさない。
- UI／Tool仕様により直接通信できない場合、送信済みと偽らない。

直接通信が利用できない場合は、Repository内HandoffとUser RelayへFallbackする。このFallbackは自動化の失敗Evidenceとして記録できるが、Taskが権限外手段で迂回する理由にはならない。

## 5. Long Run中に自己解決する事項

設計者兼実装者役は、次の条件を全て満たす事項を、原則としてUserやControllerへ逐一確認せず処理する。

- 最上位規則およびAuthorized Rootを超えない。
- Frozen ObjectiveとAcceptanceを変更しない。
- 既存Authority Envelope内である。
- 外部Action、Git Mutation、Secret、実User Data、不可逆操作またはHuman-only Gateを伴わない。
- Safe rollbackまたはRecovery Evidenceを維持できる。
- 通常の設計、実装、Test、限定的Reworkとして合理的に解決できる。

依存関係不足、既存Test失敗、設計内の小さな矛盾、ToolのSafe Unsupportedなどは、即座にUser Escalationするのではなく、現在工程への影響と自己解決可能性を分類する。

## 6. 真のStop／Escalation条件

少なくとも次の場合は安全に停止し、現在地をRecoveryへ残す。

- 最上位規則、Authorized Rootまたは明示Scopeを超える必要がある。
- 新しいAuthority、外部Network、External Service、Git、Credential、Secretまたは課金を要する。
- Destructive／Irreversible Action、User Data mutationまたはProject外Actionを要する。
- Objective、Product RequirementまたはRisk AcceptanceをUserが決める必要がある。
- Evidence Integrity mismatch、正本衝突、重大Security／Privacy Incidentがある。
- Resource LimitによりRecoveryを残さず安全に続行できない。
- 同じFailureがRework後も継続し、担当Taskの権限・能力内で解消不能である。

停止時は、最後に成立した状態、変更Path、Validation、Open Finding、再開入口および必要Authorityを明記する。未完了をCompleteまたはClosure Readyと報告しない。

## 7. Closure境界

2 Task運用の自動到達目標は、原則として`Closure Ready`までとする。

```text
Technical Implementation Complete
Independent Review Complete
Required Rework Closed
Tests／Evidence Complete
Controller Closure Recommendation Ready
```

最終Acceptance、Backup確認、Phase完了宣言、Git Commit／Push、次Phase Startなどは、そのPhaseで事前に明示的Authorityが与えられていない限りUser Gateとして残す。

## 8. Resource／利用可能量の設計

Task分離は、同一Provider／Account全体の利用可能量を増やすものではない。目的は、高コストなController ContextをRoutine Implementationで消費せず、実装を別Taskへ集中させることである。

運用上は次を採用する。

- ControllerはRisk-based Reviewを行い、全Fileを毎回無差別再走査しない。
- 実装TaskはMaterial BoundaryごとにRecoveryを作り、各小Taskごとの文書爆増を避ける。
- Complete Candidate時に、Changed Path、Test、Known Limitation、Deferred、Boundary Evidenceを一つの入口へ集約する。
- 利用可能量切れが近い場合、未完了状態を差分から再開可能な形で固定する。
- Resource残量はUser報告または製品表示に基づくScheduling Contextであり、Task自身が未確認の数値を断定しない。

本書記録時点で、UserからClaude側週間利用可能量約24%、Codex側約64%との報告があった。これは本運用候補を検討する契機であり、固定値ではない。

## 9. 同一Provider 2 Task運用のRisk

Controllerと設計者兼実装者が同じCodex Provider／Model系統である場合、Contextは分離できても、Model固有の共通Blind Spot、過剰慎重、過剰一般化、証跡解釈傾向などは共有され得る。

したがって、Codex 2 Task Reviewは実装TaskのSelf-reviewより独立性が高い一方、Cross-provider Reviewと同一ではない。重大Phase境界や高Risk機能では、Resourceが許す場合にClaudeその他ProviderまたはUser実機Acceptanceを追加する価値がある。

その他のRiskと対策は次の通り。

| Risk | 対策 |
|---|---|
| Task通信の未達・宛先誤り | Exact Task Identity、Receipt、Status確認 |
| 古いHandoffの参照 | Revision／Digest／Frozen Entry Point |
| Controllerの過剰ReviewによるQuota消費 | Acceptance／Riskに基づく差分Review |
| 実装TaskのFalse Completion | Source-based Independent ReviewとUser Acceptance |
| Progress Reportによる不要停止 | 真のStop Condition以外はLong Run継続 |
| Docs爆増 | Material Boundary単位のRecovery／集約Handoff |

## 10. 評価指標

試行時は、少なくとも次を記録する。

- Human Clarification回数
- User Relay回数と時間
- Controllerと実装Taskの直接往復成功率
- Long Run中の不要停止回数
- False Completion申告数
- Independent Reviewで検出した重大Finding数
- Rework Cycle数とSelf-repair成立数
- Compaction／Resource Interruption後のRecovery Fidelity
- Scope／Authority逸脱数
- Controllerと実装Taskそれぞれの利用可能量消費傾向
- User開始からClosure ReadyまでのWall Time
- User Intervention Time

速度だけでなく、Review、Rework、Acceptanceまで含む実効Throughputで評価する。

## 11. Activation条件

本運用候補を開始する前に、少なくとも次を確定する。

1. 対象Phase／Subphase
2. Controller Task Identity
3. 設計者兼実装者Task Identity
4. Authorized Root
5. Exact Scope／Allowed Mutation Paths
6. Git／Network／External／Secret／User Data Authority
7. Acceptance Matrix
8. Recovery／Compaction Entry Point
9. Stop Conditions
10. Userの明示的開始宣言

これらが揃うまでは`RESERVED / NOT ACTIVATED`を維持する。

## 12. Automation結果の必須記録

本運用候補を実際に使用した場合は、試行、成功、失敗、停止、再開、Review、Rework、Closure Ready到達の結果を問わず、**毎回必ず**次の正本Directoryへ新規Append-only Evidenceとして記録する。

`docs/project/shared/history/automation/`

既存Evidenceを上書きして結果を置換してはならない。各記録には、少なくとも対象Phase／Work Unit、使用Task、開始・終了状態、直接通信結果、実施範囲、Validation、Review Finding、Rework回数、Stop／Recovery状態、Authority／Scope逸脱の有無および利用可能量に関する観測可能な情報を含める。

記録を作らずに次の試行または正式運用へ進んではならない。結果が不完全または途中停止であっても、省略せず、その不完全状態自体をEvidenceとして残す。

## 13. 後順位Correction — Controller非並走／Return-boundary Review

```text
Correction Recorded At : 2026-08-25 01:48:41 JST
Trigger                : Phase 6 Codex Two-Task Rework実測
Precedence             : 本節が§3、§4、§8の並走可能な解釈をSupersede
Default                : Executor Running中、ControllerはWAITING
```

### 13.1 実測からの変更理由

Phase 6 Reworkで、設計者兼実装者役Taskの実装中にController TaskもSource確認、独立Test、途中Finding整理および先回り指示を並走した。この方式はWall Timeを短縮し得る一方、User報告では一連の工程だけでCodex利用可能量を約70〜80%消費し、Resource残量を予測・管理しにくくした。またController Turnが長時間継続するため、Userが別の確認、予約事項または方針変更を差し込みにくい運用となった。

この値はProvider TelemetryをControllerが独立取得したものではなく、Userが製品表示から観測した概算である。正確なToken消費量とは主張しないが、運用変更を必要とする十分なResource Evidenceとして扱う。

### 13.2 新しいDefault Loop

```text
User Start
  -> ControllerがFrozen Handoff／Exact Authorityを作成して送信
  -> 設計者兼実装者役TaskがLong Run
  -> Controller TaskはWAITING
  -> Complete Candidate／STOPPED_SAFE／True Blockerが返る
  -> Controllerが集中Independent Review
       +-- PASS   -> Closure Ready／User Gate
       +-- REWORK -> Exact Rework Handoffを送信
                       -> Controllerは再びWAITING
```

Executor稼働中のController WAITINGでは、原則として次を行わない。

- 定期Pollingまたは進捗追跡。
- Working Tree／Source／Testの途中Review。
- Executorと同じTestの並行実行。
- 未完成Diffに対する先回りFinding送信。
- 完了前の追加Scope、隣接機能またはClosure作業。
- 単なるSubphase完了報告を契機としたReview開始。

Independent Reviewは、Executorが一旦すべてのAuthorized Workを終え、集約Complete Candidateを返した後に開始する。Reworkでも同じであり、Exact Reworkを渡した後は再度Return Boundaryまで待機する。

### 13.3 WAITING中のController可用性

WAITINGはController Taskを長いTool CallやMonitorで占有することを意味しない。ControllerはUserへTurnを返し、Userからの質問、予約事項、優先順位変更または別のRead-only相談を受けられる状態を維持する。

Executor Taskの進行は別Taskへ委任済みであり、Userが明示的にStatus確認、停止、追加指示または方針変更を求めた場合だけ、その要求に必要な範囲で対象Taskを確認・操作する。

### 13.4 例外

ControllerがExecutor完了前に介入できるのは、次に限定する。

- Executorから`STOPPED_SAFE`、True Blocker、Authority要求または重大Incidentが明示返送された。
- Userが明示的に進捗確認、停止、割込みまたはScope変更を指示した。
- 不可逆Mutation、Secret／Privacy、Project Root外Action、課金または外部Side Effectが進行中である具体的Evidenceを受領した。
- ExecutorがCompleteと誤認して停止し、UserまたはControllerへReturn済みである。

通常の設計判断、Test Failure、追加Rework候補、進捗の遅さ、Auto-Compaction、5時間制限または利用可能量待ちは、Controller常時並走の理由にしない。

### 13.5 Resource評価

今後のCodex 2タスク試行では、次を別々に記録する。

- Executor Long Run中のController実作業回数。
- Return前のPolling／Source Review／Test回数。Default目標は0。
- Complete Candidate後のController Review消費傾向。
- Rework回数。
- UserがControllerへ別件を差し込めなかった時間。
- User報告に基づく利用可能量の開始値／終了値／概算消費。

速度だけでなく、Resource予測可能性とUserがControllerへ随時相談できる状態を成功条件へ追加する。
