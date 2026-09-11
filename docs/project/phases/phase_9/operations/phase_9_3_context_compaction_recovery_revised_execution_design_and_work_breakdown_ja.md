# Phase 9-3 Context Compaction／Recovery 改訂実行設計・工程分解

```yaml
document_id: phase_9_3_context_compaction_recovery_revised_execution_design_and_work_breakdown
document_type: phase_execution_design_and_work_breakdown
document_state: frozen_ready_for_cross_provider_implementation
phase: phase_9
program: phase_9_3
recorded_at: 2026-09-11 17:40:51 JST
language: ja
authority_owner: Nazuna Research
decision_authority: user
controller_provider: codex
controller_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
controller_role: project_controller_design_governor
executor_provider: claude_code
executor_identity_type: session_id
executor_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
executor_role: designer_implementer
routing_method: user_relay
entry_backup_complete: true
source_implementation_started: false
phase_9_2_dependency: complete_user_accepted_minimal_closure
core_default: enabled
auto_compaction_default: enabled
manual_compaction_available: true
normal_ui_mode_selector: none
minimal_context_actions_ui: in_scope
full_context_observatory_ui: out_of_scope
git_write_authorized: false
network_authorized: false
```

## 0. Authority／改訂関係

本書をPhase 9-3の現行Canonical実行設計とする。次の旧設計は履歴として保持するが、`OFF／OBSERVE／ENFORCE／MANUAL`を単一Modeとして扱う箇所、Default OFF、UI完全対象外およびBackup待ちの状態は本書が置換する。

- `phase_9_3_context_compaction_recovery_execution_design_and_work_breakdown_ja.md`

置換理由は、Context Compactionの責務へGovernance用Mode体系を持ち込み、Manual Compactionの可用性とAuto Compactionの設定を不必要に結合していたためである。本改訂ではUser Decisionに従い、Compaction Core、Manual Action、Auto PolicyおよびPreviewを分離する。

本書はPhase 9-3 Source実装、Git Write、NetworkまたはPhase 10開始を単独で許可しない。実装は、本書を参照するExact HandoffとUser Relayによって開始する。

## 1. 結論

Phase 9-3では、会話原本を変更せず、モデルへ渡すActive Contextだけを安全に圧縮・切替・復旧するTechnical Coreを構築する。

中核機能は次の二つである。

1. 任意の時点で実行できるManual Compaction。
2. Effective Context Budgetと予約領域に基づくAuto Compaction。

次は独立した追加Productではなく、上記二機能を安全に成立させるための必須基盤である。

- Context Budget／Pressure計測。
- Pre-action Snapshot。
- Structured Context Artifact。
- Atomic Activation／Compare-and-Swap。
- Rollback。
- Recovery Index。
- Selective Rehydration。
- Restart Read／Corruption検知。
- Handoff Artifact。
- Evidence／Event／Phase 9-2比較Adapter。

さらに、実際にManual CompactionとRecovery／Handoff Logを利用できるよう、既存Context Usage Surface付近へ最小の2 Icon UIを追加する。Full Governance Trace、履歴管理画面、複数Snapshot比較等の大規模UIは対象外とする。

## 2. 今回確定したUser Decision

### 2.1 Coreと操作の分離

```text
Compaction Core:
  Current Runtimeで常時利用可能
  通常UIにON／OFF Mode Selectorを置かない

Manual Compaction:
  常に利用可能
  Auto CompactionのON／OFFへ依存しない

Auto Compaction:
  独立したBoolean Policy
  Default ON
  OFFにしてもManual Compaction、Recovery、Previewは利用可能

Preview／Dry-run:
  Modeではなく明示Action
  Budget／Plan／予想削減／Riskだけを返し、Mutation 0
```

### 2.2 旧Modeの失効

次の単一Mode体系は採用しない。

```text
OFF／OBSERVE／ENFORCE／MANUAL
```

理由：

- ManualとAutoは相互排他的Modeではない。
- Manual-only運用ではAutoだけをOFFにする必要がある。
- `OBSERVE`はCompactionの継続状態ではなくPreview／Dry-run Actionで足りる。
- Compaction Core全体をOFFにすると、必要な時点でManual CompactionやRecoveryまで失う。
- Governance用語の`ENFORCE`をContext保守操作へ流用する必然性がない。

内部のEmergency／Migration Kill Switchは実装上保持してよいが、通常利用Modeではなく、UIへ公開しない。Kill Switchが作動した場合は`disabled_by_internal_safety_gate`等のTyped Stateを返し、Manualが利用可能であるかのように表示しない。

### 2.3 UI範囲

今回追加するのは次の最小UIだけである。

1. Recovery／Handoff Log Icon。
2. Manual Compaction Icon＋Warning Dialog。

Mobile専用Drawer／Bottom Sheet、Recovery履歴一覧、複数Snapshot比較、Rollback管理画面、圧縮前後Diff、Full Governance Trace ObservatoryおよびPhase 10全体Responsive再編は後続へ残す。

## 3. 解く問題と非目標

### 3.1 解く問題

- Context Window限界到達後の突然の生成Failure。
- System、Governance、RAG、Tool、Generation、Compaction用Reserveを混同した残量表示。
- 圧縮後のContextが原会話を置換・破壊するRisk。
- 圧縮失敗、Cancel、Timeout、Digest不一致、並行Turnによる新旧Pointer競合。
- 圧縮Artifactから省略された原Turnを必要時に再注入できない状態。
- Manual CompactionがAuto設定や閾値に巻き込まれて利用不能になる状態。
- Recovery／Handoff ArtifactをUIから生成・Copyできない状態。

### 3.2 非目標

- 要約から失われた原文を生成的に復号すること。
- ProviderのHidden Reasoningを取得した、保存した、復元したと主張すること。
- Phase 11以降のLossless Ledger／Graph／OCILNS研究を先取りすること。
- Full Governance Trace UIを作ること。
- Judge、Guard、GovernanceまたはRepairをCompactionの必須依存にすること。
- Model品質だけをもってCompaction Core成立とすること。

## 4. 最上位Invariant

1. Original ConversationはCanonicalなまま保持し、自動削除、上書きまたは短縮しない。
2. Original ConversationとActive Context Projectionを別Artifact・別Mutationとして扱う。
3. Manual CompactionはAuto Compaction設定およびAuto Trigger Thresholdへ依存しない。
4. Auto OFFでもBudget Measurement、Hard Reserve保護、Manual、Preview、RecoveryおよびHandoffは利用可能である。
5. Auto ONでもActive Generation中に別Pointerへ無条件切替しない。
6. Snapshot永続化成功前はCandidate生成Call 0、Activation Mutation 0とする。
7. Candidate生成、Validation、PersistenceおよびCAS Activationが全て成功した場合だけ新Projectionを有効化する。
8. Failure、Cancel、Timeout、Conflict、Schema Unknown、Digest不一致またはStale Revisionでは旧Projectionを維持する。
9. 遅延結果、二重Terminalまたは別TurnがActive Pointerを巻き戻すことを禁止する。
10. Recovery／RehydrationはCanonical SourceをIdentity／Digest付きで再読込し、欠落を推測補完しない。
11. Context上限へ到達してManual Compaction自体が実行不能になる前にCompaction Working Reserveを確保する。
12. Deterministic BuilderはLLM Callなしで動作でき、LLM BuilderのUnavailable時も安全な圧縮経路を残す。
13. Unknown Measurementを0へ変換しない。異なるTurn、単位またはModelの値を合算しない。
14. Provider名、Model Path、固定Context値またはUser固有PathをDomain CoreへHard-codeしない。
15. Compaction Coreの不在または内部Safety Failureが、Original Conversationを破壊しない。
16. Main／Judge／Guard／Governance／Repair／Recording／RAG／Web／Dev AgentのAuthorityをCompactionから生成しない。
17. UI表示状態はRuntime StateまたはArtifact Identityの正本にならない。
18. Call 0、Unavailable、Failed、UnknownをCompletedとして記録しない。

## 5. Control Model

### 5.1 Capability State

```text
core_state:
  ready
  degraded
  unavailable
  disabled_by_internal_safety_gate
```

`core_state`は技術状態であり、ユーザーが通常操作するModeではない。

### 5.2 Auto Policy

```text
auto_compaction_enabled: true | false
```

- Defaultは`true`。
- 通常UIには表示しない。
- 初期実装ではApplication／Runtime Configurationまたは認証済みLocal APIから変更可能にする。
- `false`はManual-only運用を意味し、Core停止を意味しない。
- 設定変更は新しいTurn／Actionから有効とし、進行中Attemptへ遡及させない。

### 5.3 Manual Action

Manual CompactionはCommand／API Actionとして定義する。

```text
preview_manual_compaction
request_manual_compaction
cancel_compaction
```

Manual ActionはAuto Trigger Thresholdを開始条件にしない。Canonical Conversation、Snapshot Store、Source Revisionおよび最低限のWorking Resourceが利用可能なら、Context使用率にかかわらず実行できる。

### 5.4 Preview Action

Previewは次を返し、Active Projectionを変更しない。

- 現在のBudget Snapshot。
- 選択Strategy。
- 推定削減量。
- 保持予定Section。
- 省略予定範囲。
- 脱落Risk。
- Snapshot作成予定Identity。
- 実行可能性とTyped Reason。

Previewは旧`OBSERVE`の有用部分を明示Actionへ置き換えたものである。Backgroundで恒常Modeとして保持しない。

## 6. Context Budget／Threshold／Reserve

### 6.1 Effective Budget

```text
Effective Remaining Budget =
  Model Context Capacity
  - Current Prompt Usage
  - Generation Reserve
  - System／Governance Reserve
  - RAG／Tool Reserve
  - Compaction Working Reserve
  - Safety Margin
```

各値には`observed`、`provider_reported`、`runtime_calculated`、`estimated`または`unknown`のMeasurement Class、Source、取得時刻、Model／Context Config Identityを付す。

### 6.2 Pressure State

Pressure StateはModeではなく、計測結果である。

```text
normal
approaching_auto_trigger
auto_compaction_required
manual_compaction_required
hard_reserve_protected
unknown
```

### 6.3 Threshold

固定95%をHard-codeしない。最低限、次を分離する。

```text
advisory_threshold:
  UIまたはEventへ予告を出す線

auto_trigger_threshold:
  Auto ON時に安全なCompactionを開始する線

hard_reserve_boundary:
  通常GenerationよりCompaction可能性を優先して保護する線
```

Thresholdは使用率だけでなく、次のTurnで必要となるGeneration／Governance／RAG／Tool ReserveとCompaction Working Reserveを考慮する。

### 6.4 Hard Reserve時の動作

Auto ONの場合、正常なPreflight、Snapshot、ValidationおよびCASを通してAuto Compactionを開始する。

Auto OFFの場合、勝手にAuto Compactionへ切り替えず、通常Generationを`manual_compaction_required`で一時拒否し、Manual Compactionを利用可能なまま提示する。

LLM Structured Builder用Budgetが足りない場合も、Deterministic Extractive Builderへ明示的に切り替えられる。これはMalformed結果を採用するFallbackではなく、別の登録済みStrategyとしてEvidenceへ記録する。

## 7. Target Architecture

```text
Canonical Conversation Store
        │ read-only source
        ▼
Context Source Projection Port
        ├─ original／legacy projection
        └─ active structured projection
                │
                ▼
Conversation Generation Input

Context Measurement ──> Pressure State ──> Auto Policy
        │                                      │
        │                          auto enabled + threshold
        │                                      ▼
        ├──────────────> Manual／Preview Action Router
                                             │
                                             ▼
Pre-action Snapshot ─────────────────────────┐
        ▼                                    │ rollback target
Frozen Compaction Plan                       │
        ▼                                    │
Candidate Builder                            │
        ▼                                    │
Validation／Digest                           │
        ▼                                    │
Artifact Persistence                         │
        ▼                                    │
Revision Compare-and-Swap ───────────────────┘
        ▼
Active Context Projection
        ├─ Recovery Index
        ├─ Selective Rehydration
        └─ Context Handoff Artifact

Local API／Event Projection
        ├─ Context Action Icons
        └─ Phase 9-2 Comparison Adapter
```

Domain CoreはStorage、LLM、WebおよびUIを知らない。既存Conversationへの接続はPort／Adapterで行う。

## 8. Identity／Artifact Contract

### 8.1 Identity Chain

```text
conversation_id
branch_id
source_conversation_revision
source_head_turn_id
request_id
context_action_id
snapshot_id
compaction_plan_id
compaction_attempt_id
structured_context_id
recovery_index_id
active_projection_revision
handoff_artifact_id
experiment_id／run_id（比較時だけ）
```

Configured BuilderとExecuted Builder、Requested ActionとActual Action、Artifact IDとDigestを混同しない。

### 8.2 必須Artifact

- `ContextBudgetSnapshot`
- `PreActionSnapshot`
- `CompactionPlan`
- `CompactionAttempt`
- `StructuredContextArtifact`
- `ActiveContextProjection`
- `ActivationRecord`
- `RecoveryIndex`
- `SelectiveRehydrationRequest／Result`
- `ContextHandoffArtifact`

### 8.3 Structured Context Section

- Current Objective／Current Position。
- Fixed Decision／Constraint／Authority。
- Completed／Unfinished／Deferred／Blocked。
- Known Failure／Risk／Recovery Point。
- Important Fact＋Source Turn Reference。
- Evidence／Artifact Pointer＋Digest。
- Exact Next Route。
- Recent Verbatim Tail。
- 省略範囲と再水和可能性。

Sourceに存在しないFactをCanonical Factとして追加しない。「重要」と判断したStrategyとSource Referenceを保存する。

### 8.4 Persistence／Privacy

- 初期MVPはLocal Runtime Data Rootだけを使用する。
- Atomic Write、Schema Version、Digest再検証、Restart Readを必須とする。
- Canonical Conversation本文を不要に重複Copyせず、Identity／Digest付き参照を優先する。
- Raw Secret、CredentialまたはProvider非公開情報を新Artifactへ複製しない。
- Visibility、Persistence、Redaction、Retentionを別Fieldとする。

## 9. Lifecycle／Concurrency

```text
requested
  -> preflight
  -> snapshot_persisted
  -> planned
  -> candidate_building
  -> validating
  -> candidate_persisted
  -> activating
  -> completed

Terminal:
  completed
  rejected
  failed
  cancelled
  conflicted
  rolled_back
  interrupted_by_restart
```

- Conversation／Branch RevisionとActive Projection RevisionをCASで同時確認する。
- Concurrent Conversation／BranchをRequest-local Ledgerで分離する。
- 二重Publish、遅延Worker、古いRevision、二重Cancelを拒否する。
- Process再起動後の非Terminal Attemptを勝手に再実行せず、旧Projectionを維持する。
- Rollback自体もIdentity、Expected／Observed RevisionおよびResultをEvidence化する。

## 10. Compaction Strategy

### 10.1 必須Baseline

Deterministic Extractive Builderを必須とする。Decision、Authority、Open Item、Evidence Pointer、Important FactおよびRecent Verbatim TailをSource Reference付きで選択し、Token Budget内へ収める。

このBuilderはModel Call 0で動作し、次を可能にする。

- AtomicityとRecoveryをModel品質から独立検証。
- Hard Reserve時のManual Compaction維持。
- LLM Builder Unavailable時の登録済み代替Strategy。

### 10.2 Optional Structured Builder

LLM等のBuilderはProvider-neutral Portとして追加できる。使用する場合はStrict Schema、Frozen Config／Sampling、Call Budget、Deadline、CancelおよびMalformed OutputのTyped Failureを必須とする。

不正Candidateを自動修復して採用しない。Failure時は旧Projectionを維持する。Optional Builderの文章品質をPhase 9-3 Core成立条件にしない。

## 11. Minimal Context Actions UI

### 11.1 配置

既存のContext Usage Gauge／Popover付近へ、次の2 Iconを追加する。

```text
Recovery／Handoff Log Icon
Manual Compaction Icon
```

Context Usage表示設定がOFFでもManual Action自体が利用不能にならないよう、Action ClusterのCapabilityはGauge表示設定から分離する。Gauge表示時はその右側、非表示時もComposer内の同一Action Areaから利用可能にする。

### 11.2 Recovery／Handoff Log Icon

押下時にActive Contextを変更せず、現在Conversationから`ContextHandoffArtifact`を生成または取得する。

表示内容：

- Current Objective／Position。
- Decision／Constraint／Authority。
- Completed／Incomplete／Deferred／Blocked。
- Evidence／Source／Identity／Digest。
- Failure／Risk／Recovery Point。
- Exact Next Route。

最小UIは専用Dialog／Popover／Log Surfaceで表示し、Copyと任意の`.md` Downloadを提供する。履歴一覧、複数Artifact比較および編集UIは作らない。

### 11.3 Manual Compaction Icon

即実行せず、Previewを取得してWarning Dialogを表示する。

```text
モデルへ送信される過去文脈が圧縮版へ切り替わります。
元のChat履歴は保持されますが、一部の細部が今後の回答へ
反映されにくくなる可能性があります。
実行前Snapshotを作成した上で圧縮しますか？
```

Dialogには次を表示する。

- 推定Token削減量。
- 保持予定項目。
- 省略予定範囲／脱落Risk。
- Snapshot IDまたは実行時発行予定Identity。
- Cancel。
- Execute。

実行中は二重送信を防止し、Cancel可能な段階ではCancelを表示する。Terminal後はCompleted／Failed／Cancelled／Conflictedを明確に表示し、失敗を成功表示しない。

### 11.4 Accessibility／Localization

- IconのみでもAccessible Nameを持つ。
- Keyboard、Focus、Tooltip、TouchをTestする。
- 日本語／英語Labelを追加する。
- Errorを色だけで区別しない。
- Buttonは既存Theme Tokenを使い、灰色背景＋白文字等の低Contrastを新設しない。

## 12. Package／工数分解

### P9-3-A — As-built／Budget／Pressure Core（M）

1. Conversation Mapper、Persistence、Context Usage、Runtime Model ContextおよびPhase 9-2 Portの接続点を固定する。
2. Identity、Budget Snapshot、Pressure StateおよびTyped Failureを実装する。
3. Measurement Class付きBudget Adapterを作る。
4. Advisory／Auto Trigger／Hard ReserveをConfig化する。
5. Auto ON／OFFとManual Availabilityの独立ContractをTestする。
6. 旧`OFF／OBSERVE／ENFORCE／MANUAL` Modeを実装しないRegressionを置く。

### P9-3-B — Artifact／Persistence／Integrity（M〜L）

1. Snapshot、Structured Context、Plan、Attempt、Projection、Recovery IndexおよびHandoff Schemaを実装する。
2. Save／Load／List、Idempotency、Digest、Restart ReadのStore Portを作る。
3. Local Runtime Data Root Adapter、Atomic Write、Corrupt Artifact Fail-closedを実装する。
4. Visibility／Persistence／Redaction／Retentionを分離する。
5. Tamper、欠落、旧Schema、部分WriteおよびRestartを検証する。

### P9-3-C — Plan／Candidate／Validation（M）

1. Source Revision、Budget、Action、Strategy、DeadlineおよびCall上限をFreezeする。
2. Deterministic Extractive Builderを実装する。
3. Optional Structured Builder Portを定義する。
4. Schema、Digest、Reference、必須Section、Token、Recent Tail、Authority／Decision保持を検証する。
5. 空Candidate、Source不明Fact、欠落Reference、Token超過、MalformedおよびCall 0捏造を拒否する。

### P9-3-D — Atomic Compaction／Rollback／Concurrency（L、最大Risk）

1. Manual ActionとAuto Triggerを同じCoordinator Pipelineへ接続する。
2. Snapshot失敗時のCall 0／Mutation 0を保証する。
3. Conversation／Branch／Projection RevisionのCAS Activationを実装する。
4. Failure、Cancel、Timeout、Conflict時の旧Projection維持／Rollbackを実装する。
5. 並行Turn、二重実行、遅延Worker、Restart孤立Attemptおよび二重Terminalを検証する。

### P9-3-E — Recovery／Rehydration／Handoff／Generation接続（M〜L）

1. Recovery IndexをSource Pointer／Digest付きで構築する。
2. Token Budget内Selective Rehydrationを実装する。
3. Not Found、複数候補、Stale RevisionおよびDigest MismatchをTypedに返す。
4. Active Contextを変えないHandoff Builderを実装する。
5. Existing Generation Mapper手前へOptional Projection Portを接続する。
6. Original ConversationのByte-equivalent Preservationを証明する。

### P9-3-F — Local API／Event／Experiment／Top-level Verification（M〜L）

1. Status、Budget、Preview、Manual Compact、Cancel、Rollback、Rehydrate、HandoffおよびArtifact Read APIを接続する。
2. Auto Policy変更を認証済みLocal Contractへ接続する。通常UI Toggleは作らない。
3. Request-correlated Progress／Terminal／Failure Eventを作る。
4. Phase 9-2 AdapterでOriginal／Compacted Variantを同一Frozen Caseで比較する。
5. Token削減、Retention、Missing／Conflict、Rehydration、Latency、RollbackおよびCall 0を保存する。
6. API→Coordinator→Store→Projection→Generation→Evidence→Comparison→Restart ReadをTop-level Fixtureで通す。
7. Resource Preflight後、Mainだけを逐次最大2 Scenarioで使うBounded Real-model Gateを必要に応じて実行する。

### P9-3-G — Minimal Context Actions UI／User Gate（S〜M）

1. Frontend API Type／Clientを追加する。
2. Context Action ClusterをContext Usage表示設定から分離してComposerへ接続する。
3. Recovery／Handoff Log Icon、表示、Copyおよび任意`.md` Downloadを実装する。
4. Manual Icon、Preview、Warning Dialog、Cancel／ExecuteおよびTerminal表示を実装する。
5. Accessibility、日英翻訳、Error、二重送信防止およびComponent Testを追加する。
6. Frontend Full Test、Typecheck、LintおよびBuildを実行し、配信Bundleを更新する。
7. User Manual Checklistを作成し、User実画面Acceptance待ちで停止する。

### 工数評価

```text
最大Risk: P9-3-D（CAS／Rollback／Concurrency）
次点    : P9-3-B／E／F（Persistence／Generation接続／Top-level）
軽量    : P9-3-G（Core API完成後の薄いUI）
```

初回実装はClaude Code Long Run 1回を基本とし、Codex Independent ReviewとClaude Reworkを反復する。順調時はReview／Rework 2〜3 Round、Concurrency／Restart Findingが出た場合は追加Roundを許容する。Test件数や文書量だけで完了判定しない。

## 13. Codex／Claude Code実行体制

### 13.1 Active Identity

```text
Controller:
  Provider      : Codex
  Identity Type : Task ID
  Task ID       : 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role          : プロジェクト責任者兼設計統括者役

Executor:
  Provider           : Claude Code
  Identity Type      : Session ID
  Task ID Equivalent : local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role               : 設計者兼実装者役

Routing Method: user_relay
```

Identityが変化した場合、表示名だけで継続せず、新IDへRoleとAuthorityを明示的にRebindする。

### 13.2 作業Loop

```text
Codex:
  設計Freeze／Exact Handoff／Maximum Claim／Acceptanceを定義
        ↓ User Relay
Claude Code:
  P9-3-A〜Gを依存順で実装・検証
  Internal Review A／B
  Identity付きExact Return／Recoveryで停止
        ↓ User Relay
Codex:
  Phase 9-3全Scope Independent Review
  Blocker／MajorをFinding化
  必要時だけExact Rework Handoff
        ↓
Claude Code Rework
        ↓
Codex Final Re-review
        ↓
User Manual Checklist／User Acceptance
```

### 13.3 通信形式

全Handoff／Returnは次を使用する。

```text
Task Communication Identity
  + Natural-language Intent
  + XML／Markdown Section Boundary
  + JSON Execution Contract
  + Artifact Path／SHA-512
```

From／ToはReturnで反転する。Claude CodeはPhase 9-3 Complete、Phase 9 Closure、GitまたはPhase 10を自己承認しない。

### 13.4 Resource／Stop

- 中間報告は不要。User割り込みには応答可。
- Quota Hard Stop時はCurrent WU、Mutation、Test、未完了AcceptanceおよびExact Next ActionをRecoveryへ保存する。
- 未実施をPASSにせずPartial Returnで停止する。
- Real ModelはFixture／Integration後、Mainのみ最大2 Scenario。
- Judge／Guard／Selene／DeepSeekの実行はPhase 9-3必須検証に含めない。

## 14. Acceptance Mapping

| Acceptance | 主Package | Hard Evidence |
|---|---|---|
| P9-ACC-046 | A | Budget各項目、Measurement Class、三Threshold、Auto ON／OFF、Hard Reserve Test |
| P9-ACC-047 | C／D | Manual常時可用、Auto独立、Snapshot Gate、CAS、Rollback、Race／Late Result Test |
| P9-ACC-048 | B／E | Original不変、Artifact分離、Recovery Index、Rehydration、Restart Read |
| P9-ACC-049 | E／F | Handoff／Manual／Recovery／Event／Identity相関、Top-level Generation接続 |
| P9-ACC-050 | G | 2 Icon、Warning Dialog、Log／Copy／Download、Accessibility、配信Bundle、User Manual |

最大成立Claimには少なくとも次を要求する。

- P9-ACC-046〜050のFixture／Integration Evidence。
- Original Preservation。
- Atomic Rollback。
- Restart Read。
- ManualとAutoの独立。
- Hard Reserve下でもManual経路が失われないこと。
- 最小UIの実配信物更新。
- Controller Independent Review。
- User Manual Acceptance。

## 15. Verification Plan

### 15.1 必須Backend

- Budget／Pressure／Threshold境界。
- Auto Default ON、Auto OFF＋Manual Available。
- Preview Mutation 0。
- Manual低使用率／高使用率双方。
- Auto Trigger成功とAuto OFF非発火。
- Hard Reserveと`manual_compaction_required`。
- Snapshot失敗、Candidate失敗、Validation失敗、CAS競合、Cancel、Timeout、Rollback。
- Concurrent Conversation／Branch相互非干渉。
- Restart、Corruption、Digest、Atomic Write。
- Original Conversation不変。
- Selective Rehydration Found／Not Found／Conflict／Digest Mismatch。
- Handoff生成でActive Context Mutation 0。
- Compaction Coreから他ComponentへのAuthority／Call非波及。
- Top-level Original／Compacted ComparisonとRestart Read。

### 15.2 Sabotage

最低限、次の4系統を意図的に壊し、Testが検出した後にByte一致で復元する。

1. Snapshot Gate。
2. CAS Revision検証。
3. Original Preservation。
4. Manual／Auto独立またはFalse Completion。

### 15.3 Frontend

- Icon表示とAccessible Name。
- Gauge表示OFFでもManual Actionへ到達可能。
- Preview前にExecuteしない。
- Warning DialogのCancel／Execute。
- 二重送信防止。
- Current／Historical Event混同防止。
- Recovery Log、Copy、Download。
- Error／Cancelled／ConflictをCompleted表示しない。
- Full Test、Typecheck、Lint、Build、配信Bundle確認。

### 15.4 Real Model

Resource Preflight後、必要な場合だけMain Modelを逐次最大2 Scenarioで使う。

1. Compacted Projectionが実Generation Requestへ入り、Prompt Token差とOriginal不変を確認する。
2. Canonical FactをSelective Rehydrationし、実RequestへのSource注入を直接計装する。

回答表現の好みをCore Oracleにしない。

### 15.5 User Manual

Userへ長い会話を手動生成させない。Auto ThresholdはFixture／Integrationで検証する。Userは最小UIについて次だけ確認する。

- Recovery／Handoff Log Iconが表示される。
- Log生成、Copy、任意Downloadが機能する。
- Manual IconからPreview／Warning Dialogが開く。
- CancelでMutation 0。
- ExecuteでSnapshot IDとTerminal結果が表示される。
- 原Chatが消えない。
- 新しいTurnが圧縮Projectionを使用できる。
- Error、固まり、低Contrastまたは二重表示がない。

## 16. Scope外

- Mobile専用Drawer／Bottom Sheetの完成形。
- Recovery履歴一覧。
- 複数Snapshot比較。
- Rollback管理画面。
- 圧縮前後Diff UI。
- Full Governance Trace Observatory。
- Phase 10全体Responsive UI再編。
- Phase 10 Docs統合／PADG／Runtime Constitution。
- Phase 11以降のLossless Ledger／Graph／OCILNS。
- Cloud Sync、Multi-host、外部Upload。
- Judge／Guard／Repair固有Model問題。
- Git add／commit／push、公開作業。

## 17. True Stop

- Canonical ConversationまたはActive ProjectionのRevisionを一意に決められない。
- Snapshot／RollbackなしにOriginalまたはActive Contextを破壊する必要がある。
- Manual CompactionをAuto設定から独立させられない構造的Blockerがある。
- Hard Reserveを保護せず通常Generationを続ける以外に方法がない。
- Authorized Root外、Network、Secret、追加Costまたは新User Authorityが必要。
- Real Model Load後に安全なUnloadができない。

実装量、Minor、Full UI不在または任意Real Model未実施だけではTrue Stopにしない。

## 18. Entry／Return Line

```text
Current State:
  PHASE 9-2 COMPLETE／USER ACCEPTED／MINIMAL CLOSURE
  PHASE 9-3 DESIGN REVISED／FROZEN
  ENTRY BACKUP COMPLETE（User Report）
  CODEX／CLAUDE EXECUTION HANDOFF READY
  SOURCE IMPLEMENTATION NOT STARTED

Exact Next Action:
  1. Codexが本書を正本とするClaude Code Exact Handoffを発行する。
  2. User Relayで現行Claude Code Sessionへ渡す。
  3. Claude CodeがP9-3-A〜Gを依存順に実行する。
  4. Codex Independent Review／必要時Reworkを行う。
  5. User Manual Acceptanceで停止する。
```

## 19. 関連資料

- 旧Phase 9-3設計：`phase_9_3_context_compaction_recovery_execution_design_and_work_breakdown_ja.md`
- Phase 9 Index：`../phase_index_ja.md`
- 元予約：`../../phase_6/history/operations/phase_9_context_compaction_and_governance_trace_reservation_update_ja_20260823092049.md`
- 詳細予約：`../../../shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md`
- Phase 9-2 Closure Receipt：`../history/operations/phase_9_2_explicit_default_off_experiment_runtime_gate_controller_independent_review_acceptance_and_minimal_closure_receipt_ja_20260911163201.md`
- Identity／Hybrid Handoff Rule：`../../../shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`
