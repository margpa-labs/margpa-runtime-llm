# Phase 9-3 Context Compaction／Recovery Technical Core — 実行設計・工程分解

```yaml
document_id: phase_9_3_context_compaction_recovery_execution_design_and_work_breakdown
document_state: frozen_ready_for_implementation_after_user_backup
phase: phase_9
program: phase_9_3_context_compaction_recovery_core
language: ja
created_at: 2026-09-10 12:06:44 JST
owner: project_controller_design_governor
decision_authority: user
implementation_started: false
phase_9_2_dependency: complete_user_accepted_minimal_closure
user_backup_required_before_source_mutation: true
user_backup_complete: false
git_write_authorized: false
network_authorized: false
real_model_run_authorized: false
```

## 1. 結論

Phase 9-3は、会話の原本を消さずに、モデルへ渡すActive Contextだけを安全に圧縮・切替・復旧できる、UI非依存のTechnical Coreを作る。

Phase 9-2で成立したExperiment Identity、Run Lifecycle、Trace、Evidence、ComparisonおよびRestart Readを再利用し、圧縮前後を同じCase／Config／Identityで比較できるようにする。Phase 9-2のExperiment UIは通常画面から非表示のままとし、Phase 9-3から逆依存させない。

本書をPhase 9-3の詳細Freezeとする。Source実装は、ユーザーがCurrent Working TreeのBackup完了と開始を明示するまで行わない。

## 2. Phase 9-3で解く問題

長い会話では、次を一つの「Context残量」にまとめると、安全な圧縮と復旧ができない。

```text
Model Context Capacity
Current Prompt Usage
Generation Reserve
System／Governance Reserve
RAG／Tool Reserve
Compaction Working Reserve
Safety Margin
Effective Remaining Budget
Pressure State
```

また、次も別Artifactとして扱う必要がある。

```text
Original Conversation       原本。自動削除しない
Active Context Projection   次のModel Callへ渡す現在の投影
Pre-action Snapshot         切替前の復旧点
Structured Context          圧縮後の構造化Artifact
Recovery Index              原Turn／Evidence／Artifactへの参照
Selective Rehydration       必要な原情報だけの再注入
Handoff Artifact            別Task／別Sessionへ渡す復旧資料
```

要約から失われた原文を生成的に復号したとは主張しない。`Structured Context`は、参照可能な原本を持つ圧縮投影であり、原本そのものでも、Losslessな複製でもない。

## 3. As-builtと再利用境界

### 3.1 再利用する成立済み基盤

- ConversationのCanonical Persistence、Conversation／Branch／Turn Identity。
- `generation_context_mapper`による保存済みHistoryからGeneration Inputへの変換。
- Runtime Model Controlが持つLoaded Context SizeおよびGeneration上限。
- Conversation Generationが出す低CostのContext Usage推定と内訳。
- Cancellation、Deadline、Typed Failure、Recording、Evidenceの既存Port。
- Phase 9-2のExperiment Plan／Variant／Run、Trace、Comparison、Restart Read。

### 3.2 同一視してはならない既存機能

- 既存`summary_mode`は回答のPresentation用後処理であり、会話HistoryのActive Contextを切り替えるCompactionではない。
- Context Usage Gaugeは観測表示であり、Snapshot／Atomic Swap／Rollbackを行わない。
- RAG Context Budgetは検索Evidence用であり、Conversation History全体のCompaction Budgetではない。
- Phase 9-2 Experiment Runnerは比較の上位層であり、Phase 9-3のActive Context所有者にならない。

### 3.3 まだ存在しない中心機能

- Request／Conversation単位のContext Pressure State。
- Pre-compaction SnapshotとStructured Contextの永続Artifact。
- Active Context ProjectionのCompare-and-Swap切替。
- 失敗／Cancel／Timeout／Digest不一致時のRollback。
- Recovery IndexとSelective Rehydration。
- Handoff／Manual Compaction／RecoveryのUI非依存API／Event Contract。

## 4. 最上位Invariant

1. Original ConversationはCanonicalなまま保持し、自動削除・上書き・短縮しない。
2. Active Context Projectionの変更とOriginal Conversationの変更を同一操作にしない。
3. 自動CompactionはDefault `OFF`。`OBSERVE`はActive Contextを変更しない。
4. `ENFORCE`／`MANUAL`は、Pre-action Snapshotの永続化成功後だけ候補生成へ進む。
5. Candidate生成、Validation、永続化、Active Pointer切替の全てが成功した場合だけ新Projectionを有効化する。
6. Pointer切替はConversation／Branch Revisionに対するCompare-and-Swapで行い、遅延結果や別Turnが新しい状態を巻き戻さない。
7. Failure、Cancel、Timeout、Conflict、Schema Unknown、Digest不一致では旧Projectionを維持する。
8. OFF／Unavailable／Unsupported／Unknown／Failedを、Compaction成功またはRecovery成功として記録しない。
9. RecoveryはCanonicalな原Turn／ArtifactをDigest付きで再読込する。欠落内容を推測して補完しない。
10. Provider名、Model Path、固定Context値、ユーザー固有PathをDomain CoreへHard-codeしない。
11. Runtimeが観測できないHidden Reasoningを保存・復元・表示したと主張しない。
12. Phase 9-3を既存Main／Judge／Guard／Governance／RepairのActivation Dependencyにしない。Context Coreが無効または不在ならLegacy Context経路が同一挙動を保つ。

## 5. Target Architecture

```text
Canonical Conversation Store
        │ read-only source reference
        ▼
Context Source Projection Port
        ├─ legacy/full projection（Phase 9-3 OFF／unavailable）
        └─ active structured projection
                │
                ▼
Conversation Generation Input

Context Measurement
        ▼
Pressure Decision
        ▼
Pre-action Snapshot ────────┐
        ▼                    │ rollback target
Compaction Plan             │
        ▼                    │
Candidate Builder           │
        ▼                    │
Validation／Digest           │
        ▼                    │
Artifact Persistence        │
        ▼                    │
Revision Compare-and-Swap ──┘
        ▼
Active Context Projection
        ├─ Recovery Index
        ├─ Selective Rehydration
        └─ Handoff Artifact

Phase 9-2 Experiment Adapter
        └─ before／after Run、Trace、Cost、Retention、Recovery比較
```

Domain CoreはStorage、LLM、Web、UIを知らない。既存Conversationへの接続はPort／Adapterで行い、Phase 9-3 Adapterが無い場合は既存のHistory Projectionをそのまま使用する。

## 6. Contract Freeze

### 6.1 Identity Chain

最低限、次を分離して関連付ける。

```text
conversation_id
branch_id
source_conversation_revision
source_head_turn_id
request_id
context_action_id
snapshot_id
compaction_plan_id
structured_context_id
recovery_index_id
active_projection_revision
experiment_id／run_id（比較時だけ）
```

Artifact IDとDigest、Configured BuilderとExecuted Builder、Requested ModeとFrozen Modeを混同しない。

### 6.2 Context Budget Snapshot

`ContextBudgetSnapshot`は少なくとも次を持つ。

- capacity、prompt usage、completion usage。
- generation reserve、system／governance reserve、RAG／tool reserve。
- compaction working reserve、safety margin、effective remaining。
- measurement class：`observed`／`provider_reported`／`runtime_calculated`／`estimated`／`unknown`。
- Measurement source、取得時刻、対象Model／Context Config Identity。
- Pressure State：`normal`／`observe`／`snapshot_recommended`／`compaction_required`／`hard_stop`／`unknown`。

異なる単位や異なるTurnの値を足し合わせない。Unknownを0へ変換しない。

### 6.3 Snapshot／Structured Context

`PreActionSnapshot`は旧Active Projection、Source Revision、Ordered Turn Reference、Authority／Decision／Open Item／Evidence Reference、Schema Version、Digestを持つ。

`StructuredContextArtifact`は次のSectionを明示的に分離する。

- Current Objective／Current Position。
- Fixed Decision／Constraint／Authority。
- Completed／Unfinished／Deferred／Blocked。
- Known Failure／Risk／Recovery Point。
- Important FactとSource Turn Reference。
- Evidence／Artifact PointerとDigest。
- Exact Next Route。
- 保持するRecent Verbatim Tail。
- 省略した範囲と再水和可能性。

「重要」と判断した根拠、選択Strategy、Source Referenceを残す。Sourceにない事実をCanonical Factとして追加しない。

### 6.4 Plan／Attempt／Activation

- `CompactionPlan`：Frozen Budget、Frozen Mode、Source Revision、選択Strategy、保持／省略予定、Call Budget、Deadline。
- `CompactionAttempt`：Requested／Started／Completed、実Call数、Token、Latency、Builder Identity、Failure Stage／Reason。
- `ActiveContextProjection`：現在有効なArtifact、前Revision、Activation時刻、Rollback Target。
- `ActivationRecord`：Compare-and-SwapのExpected／Observed Revision、Disposition、旧／新Pointer。

Call 0は0のまま記録し、固定説明文やConfigured値を実行Evidenceとして捏造しない。

### 6.5 Recovery／Rehydration／Handoff

- `RecoveryIndex`：原Turn、Artifact、Evidence、Decision、Open Itemへの順序付きPointer。
- `SelectiveRehydrationRequest`：要求Source、Token Budget、目的、必要Digest、適用範囲。
- `SelectiveRehydrationResult`：Found／Not Found／Conflict／Digest Mismatch、実際に注入したSourceとToken。
- `ContextHandoffArtifact`：Objective、Position、Authority、Decision、Incomplete、Evidence、Next Route、Source Pointers。

Handoff生成だけではActive Contextを変更せず、Authorityや承認を新しく発生させない。

### 6.6 Visibility／Persistence／Redaction／Retention

四つを独立Fieldとして持つ。初期MVPではLocal Runtime Data Root内だけを対象とし、外部送信を行わない。

Pre-action SnapshotはRollbackに必要な範囲を永続化するが、Canonical Conversation本文を重複Copyするのではなく、可能な限りIdentity／Digest付き参照を保存する。Raw Secret、Credential、Providerが露出しない内部情報を新規Artifactへ複製しない。

## 7. ModeとState Machine

### 7.1 Mode

```text
OFF:
  Compaction Actor Call 0、Active Projection Mutation 0。
  既存Context Usage表示とLegacy Generationは独立して継続できる。

OBSERVE:
  Budget／Pressure／推奨Planを算出してEvidence化する。
  Active Projection Mutation 0。自動Compaction Call 0。

ENFORCE:
  Frozen Pressure Gate成立時だけSnapshot→Candidate→Validation→Atomic Swap。

MANUAL:
  明示Actionにより同じPipelineを実行する。Pressure Thresholdだけを開始条件にしない。
```

### 7.2 Lifecycle

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
  completed／rejected／failed／cancelled／conflicted／rolled_back
```

Terminal結果の二重Publish、遅延結果、古いRevisionの再Activationを拒否する。Process再起動時に非Terminal Attemptが残っていれば、Actorを勝手に再実行せず、`interrupted_by_restart`として収束して旧Projectionを維持する。

## 8. Compaction Strategy

初期実装はStrategyをPort化し、Provider固有方式をCoreへ埋め込まない。

### 必須Baseline

Deterministic Extractive Builderを用意する。固定Decision／Authority／Open Item／Evidence Pointer、重要Fact、Recent Verbatim TailをSource Reference付きで選択し、Token Budget内へ収める。Fixtureで再現可能なため、AtomicityとRecoveryをModel品質から独立して検証できる。

### 任意Adapter

LLM Structured Builderは別Adapterとして追加できる。使用する場合はStrict Schema、Frozen Sampling／Config、Call Budget、Deadline、Cancel、Malformed OutputのTyped Failureを必須とする。LLM BuilderのFailure時に不正Candidateを採用せず、旧Projectionを維持する。

LLMの文章品質をPhase 9-3 Core成立条件と混同しない。Core成立は、Artifact Integrity、Atomicity、Rollback、参照可能性および比較可能性で判定する。

## 9. Package／Work Unit分解

### P9-3-A — As-built／Budget／Pressure Core

1. **A1 As-built Inventory**：Conversation Mapper、Persistence、Context Usage、Runtime Model Context、Experiment Portの接続点を固定する。
2. **A2 Domain Contract**：Identity、Budget Snapshot、Pressure State、Mode、Typed Failureを実装する。
3. **A3 Measurement Adapter**：既存Context UsageとRuntime情報から、根拠Label付きBudget Snapshotを作る。
4. **A4 Pressure Policy**：ThresholdをConfig化し、境界値、Unknown、Reserve不足、Hard Stopを決定論的に判定する。
5. **A5 Independence Proof**：Phase 9-3不在／OFF時に既存Main／Judge／Guard／RAG等へCall／Mutation／Evidence／Authorityが増えないことを証明する。

### P9-3-B — Artifact／Persistence／Integrity

1. **B1 Artifact Schema**：Snapshot、Structured Context、Plan、Attempt、Active Projection、Recovery Indexを実装する。
2. **B2 Store Port**：Save／Load／List、Idempotency、Digest再検証、Restart Readを定義する。
3. **B3 Local Adapter**：Runtime Data Root内の安全なPath、Atomic Write、Schema Version、Corrupt ArtifactのFail-closedを実装する。
4. **B4 Retention Contract**：Visibility／Persistence／Redaction／Retentionを分離し、原Conversationの重複保存を抑える。
5. **B5 Tamper／Restart Tests**：Digest不一致、欠落、旧Schema、部分Write、Process再起動を検証する。

### P9-3-C — Plan／Candidate／Validation

1. **C1 Frozen Plan Builder**：Source Revision、Budget、Mode、Strategy、Deadline、Call上限をFreezeする。
2. **C2 Deterministic Builder**：Source Reference付きの構造化Extractive Candidateを作る。
3. **C3 Optional Structured Builder Port**：LLM等のBuilderを差替可能にし、CoreからProvider名を排除する。
4. **C4 Validator**：Schema、Digest、Reference、必須Section、Token上限、Recent Tail、Authority／Decision保持を検証する。
5. **C5 False-success Tests**：空Candidate、Source不明Fact、重複／欠落Reference、Token超過、Malformed、Call 0捏造を拒否する。

### P9-3-D — Atomic Compaction／Rollback／Concurrency

1. **D1 Coordinator**：OFF／OBSERVE／ENFORCE／MANUALを同じLifecycleへ接続する。
2. **D2 Pre-action Snapshot Gate**：Snapshot保存失敗時はCandidate Call 0・Mutation 0にする。
3. **D3 Compare-and-Swap Activation**：Conversation／Branch RevisionとActive Pointer Revisionを同時検証する。
4. **D4 Rollback**：Activation失敗、Post-validation失敗、Cancel、Timeout、Conflict時に旧Projectionを維持・復元する。
5. **D5 Race／Late Result Tests**：並行Turn、二重実行、遅延Worker、Restart孤立Attempt、二重Terminalを検証する。

### P9-3-E — Recovery Index／Selective Rehydration／Handoff／Generation接続

1. **E1 Recovery Index Builder**：原Turn／Evidence／Artifact PointerとDigestを順序付きで作る。
2. **E2 Selective Rehydration**：Token Budget内で必要SourceだけをCanonical Storeから再取得する。
3. **E3 Conflict Handling**：Not Found、複数候補、Stale Revision、Digest Mismatchを推測で埋めずTypedに返す。
4. **E4 Handoff Builder**：Active Contextを変えずに復旧用Artifactを生成する。
5. **E5 Generation Projection Adapter**：既存Mapperの手前にOptional Portとして接続し、不在時はLegacy経路を完全維持する。
6. **E6 Original Preservation Proof**：Compaction／Rollback／Rehydration後もOriginal ConversationのMessage／Turn／BranchがByte-equivalentであることを確認する。

### P9-3-F — Headless API／Event／Experiment／Verification

1. **F1 UI-independent API**：Status、Snapshot、Plan／Preview、Compact、Rollback、Rehydrate、Handoff、Artifact Readを認証済みLocal APIへ接続する。
2. **F2 Event Projection**：Request-correlatedなProgress／Terminal／Failureを出し、CurrentとHistoricalを分離する。
3. **F3 Phase 9-2 Adapter**：同一Case／Frozen ConfigでLegacy ContextとCompacted Contextを別Variantとして比較する。
4. **F4 Metrics**：Prompt Token削減、Retention、Missing／Conflicting Fact、Rehydration Call／Token、Latency、Rollback、Call 0を保存する。
5. **F5 Top-level Fixture Gate**：API→Coordinator→Store→Projection→Generation→Evidence→Comparison→Restart Readを通す。
6. **F6 Bounded Real-model Gate**：Resource Preflight後、必要ならMain Modelだけを逐次最大2 Scenarioで使う。Judge／GuardはPhase 9-3成立の必須依存にしない。
7. **F7 Independent Review／Return**：Critical／Major／MVP BlockerだけをReworkし、Exact Return／Recoveryで停止する。

## 10. Acceptance Mapping

| Acceptance | 主Package | Hard Evidence |
|---|---|---|
| P9-ACC-046 | A | Budget各項目、Measurement Class、Pressure境界のUnit／Integration Test |
| P9-ACC-047 | C／D | Default OFF、OBSERVE Mutation 0、Pre-Snapshot、Atomic Swap、Rollback、Race Test |
| P9-ACC-048 | B／E | Original不変、Artifact分離、Recovery Index、Selective Rehydration、Restart Read |
| P9-ACC-049 | E／F | Handoff／Manual Compaction／Recovery／TraceのHeadless API、Event、Identity相関 |
| P9-ACC-050 | F | 実装／非実装、Resource Gate、Phase 10／11境界の正直なDisposition |

Phase 9-3の最大成立Claimは、少なくともP9-ACC-046〜049のFixture／Integration Evidence、Restart Read、Original Preservation、Atomic Rollbackが成立した場合に限る。Test総数やFile存在だけでPASSにしない。

## 11. Verification Plan

### 必須

- Contract／Budget／Pressure／State Machine Unit Tests。
- Local StoreのRestart Read、Corruption、Digest、Atomic Write Tests。
- OFF Call 0、OBSERVE Mutation 0。
- ENFORCE／MANUAL成功、Snapshot失敗、Candidate失敗、Validation失敗、CAS競合、Cancel、Timeout、Rollback。
- Concurrent Conversation／Branchの相互非干渉。
- Original Conversation不変。
- Selective RehydrationのFound／Not Found／Conflict／Digest Mismatch。
- Top-level Fixtureで圧縮前後ComparisonとRestart Read。
- Sabotage-regression：少なくともSnapshot Gate、CAS、Original Preservation、False PASSの4系統。

### 実Model Gate

実ModelはCoreの正しさをModel品質へ依存させない。実行する場合はMemory Pressureを事前確認し、Main Modelだけを逐次最大2 Scenarioとする。

1. Compacted Projectionを実Generation Requestへ渡し、Call完了、Identity、Prompt Token差、Original不変を確認する。
2. Canonicalな既知FactをSelective Rehydrationし、実RequestへSourceが入ったことを直接計装する。

回答内容の好みだけをOracleにしない。Resource不足ならFixture／Integration成立と実機未実施を分離して返す。

### User実画面

Phase 9-3はHeadless Technical Coreであり、通常UIを変更しない限りUser実画面Gateは不要とする。UIを追加した場合だけ、別の明示ChecklistとUser Acceptanceを必要とする。

## 12. Scope外

- Phase 10のContext Button、右Panel、Settings再編、全体UI改造。
- Phase 10のDocs統合、Portable Package、Runtime Constitution統合。
- Phase 11以降のLossless Context Algorithm、Graph／Ledger／OCILNS等の研究実装。
- 外部Providerの非公開ContextやHidden Reasoningの取得。
- Original Conversationの削除・圧縮置換。
- Cloud Sync、Multi-host、Enterprise Retention、外部Upload。
- Phase 9-2 Experiment Workspace UIの再表示・修復。
- Judge／Guard／RepairのProvider固有品質問題。
- Git add／commit／push、Network Download、公開作業。

## 13. True Stop

- Canonical ConversationまたはActive Projectionの正しいRevisionを一意に決められない。
- Snapshot／RollbackなしにOriginalまたはActive Contextを破壊する必要が生じる。
- Authorized Root外、Network、Secret、追加Costまたは新しいUser Authorityが必要。
- Real Model Load後に安全なUnload／Process停止ができない。
- User Backupが未完了のままSource Mutation開始を求められた。

実装量、既知Minor、UI不在、任意Real Model Trial未実施だけではTrue Stopにしない。

## 14. Entry／Return Line

```text
Current State:
  DESIGN FROZEN
  WORK BREAKDOWN FROZEN
  PHASE 9-3 READY
  SOURCE IMPLEMENTATION NOT STARTED
  USER BACKUP PENDING

Exact Next Action:
  1. UserがCurrent Working Tree Backupを取得する。
  2. UserがPhase 9-3 Source実装開始を明示する。
  3. P9-3-AからFを依存順に実施する。
```

本書はBackup、Source Mutation、実Model、GitまたはPhase 9-3完了Authorityを生成しない。
