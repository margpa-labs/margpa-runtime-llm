# Phase 2-A Conversation Domain Foundation 要件定義

```yaml
document_id: phase_2_a_conversation_domain_requirements
status: design_frozen
phase: phase_2
subphase: phase_2_a
language: ja
created_at: 2026-08-12 01:43:31 JST
updated_at: 2026-08-12 01:51:52 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2実装者役
decision_authority: user
implementation_authority: accepted_phase_2_a_scope_only
```

## 1. 目的

Phase 2-Aは、Phase 1のBrowser Memory型Conversationを直ちに永続化するのではなく、Phase 2-B以降が依存するConversation Domain、Identity、State、Storage Port、Schema、Failure、MigrationおよびCompatibility ContractをTest可能な形で固定する。

本SubphaseのMilestoneは次である。

> Conversationの存在、Identity、順序、状態、保存境界および失敗を、Web UI、Storage製品、Model Backendから独立したDomain Contractとして成立させる。

## 2. Source Priority

Phase 2-AのScopeは次の順序で解決する。

1. ユーザーによるPhase 2-A開始・完全自動化指示
2. `docs/project/phases/phase_2/phase_index_ja.md`
3. `docs/project/shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md`
4. `docs/public/roadmap_ja.md`
5. Current Canonical
6. Phase 1およびHistoryの将来予約

旧Phase 1 Architectureにある`Phase 2-A: Component Registry／Switchboard`はHistorical Inputである。現行計画ではSwitchboardをPhase 2-Eへ配置し、Phase 2-Aへ混入させない。

## 3. Identity Contract

次のIdentityを相互に代用しない。

| Identity | 責務 |
|---|---|
| `ConversationScopeId` | Storage上の分離Namespace。Accountや認証Tokenそのものではない |
| `ConversationId` | 永続Conversation Aggregate |
| `ConversationSessionId` | Conversationを開く／再開するInteraction Episode |
| `ConversationTurnId` | 一回のUser Submissionと0または1件のCanonical Assistant Result |
| `ConversationMessageId` | 保存対象Canonical Message |
| `ConversationOperationId` | Storage Commitの冪等相関 |
| 既存`request_id` | 一回のGeneration実行／Cancel相関。永続Domain Identityではない |

IdentityはOpaqueであり、名前、時刻、Path、Model、User情報または順序を埋め込まない。生成方式はAdapterまたはFactoryへ閉じ、Domainは非空、長さおよび安全な形式を検証する。Repository操作は常に`scope_id`と`conversation_id`を組み合わせ、推測困難なIDだけを認可境界にしない。

## 4. Aggregate Contract

### 4.1 Conversation

ConversationはAggregate Rootであり、少なくとも次を保持する。

- `scope_id`／`conversation_id`
- Lifecycle State: `active | archived`
- `head_turn_id | None`
- Created／Updated Timestamp
- Session／Turn／MessageのImmutable Snapshot

Hard Delete、Retention、RestoreおよびTombstoneの最終Contractは未確定であるため、Phase 2-A Domainへ入れない。Chat List用Title生成、検索、Pin、共有またはUser Accountも必須化しない。

### 4.2 Conversation Session

- SessionはConversationを開く／再開するInteraction Episodeである。
- HTTP Session、Authentication Token、Browser Cookie、Model Runtime Instance、Generation RequestまたはLockではない。
- 状態は`active | closed | interrupted`とする。
- Resumeは旧Sessionを再Openせず、新しいSessionを生成する。
- 既存`ConversationGenerationSession`は一回のGenerationを扱うEphemeral Runtime Objectであり、永続Sessionと同一視しない。

### 4.3 Turn

- 一つのTurnは一つのUser Messageと、0または1件のCanonical Assistant Messageを持つ。
- 状態は`pending | generating | completed | cancelled | failed | interrupted`とする。
- Turnは必ず`session_id`を持ち、同一Conversationの既存Sessionだけを参照する。
- `parent_turn_id`は選択Branch上の直前Completed Turnを示す。
- Retry／Regenerateは元Turnを変更せず、新しいTurnを作る。
- Retry／Regenerate由来は`derived_from_turn_id`で示す。
- `parent_turn_id`はCompleted Turn、`derived_from_turn_id`は先行するTerminal Turnを参照し、Retry／Regenerateは元Turnと同じBranch Parentを維持する。
- Terminal Turnを再Openしない。
- 同一ConversationのNon-terminal Turnは最大1件とする。

複数Assistant候補を同一Turnへ追加する方式は採用しない。将来Generation Attemptを独立Aggregateへ昇格させる場合は別ADRで行う。

### 4.4 Message

- 保存Roleは`user | assistant`だけとする。
- User TextまたはUserへ提示されたCanonical Assistant Final Textだけを保持する。
- Summary成功時はSummary、Fallback時は提示されたOriginalをCanonical Assistant Messageとする。
- `system`、Tool Output、RAG Injected Context、Citation本文、Hidden／Visible Thinking、Partial Delta、内部Prompt、Rendered DOM、Status／Warning／Error文言および非表示Original Summary OutputをMessageとして保存しない。
- MessageはImmutableであり、編集、Retry、Regenerateで上書きしない。
- 空白、未知Role、重複Identity、Conversationを跨ぐ参照および順序不整合を拒否する。

## 5. State／Ordering／Branch Contract

```text
Conversation : active <-> archived
Session      : active -> closed | interrupted
Turn         : pending -> generating | cancelled | failed | interrupted
               generating -> completed | cancelled | failed | interrupted
```

- Terminal Session／Turnからの遷移を禁止する。
- Timestampだけを順序の正本にしない。
- Conversation内のTurnとMessageは明示Sequenceを持つ。
- Parent／Derived参照Cycleを禁止する。
- `head_turn_id`は同一Conversation内のCompleted Turnだけを指す。
- CompleteはAssistant Message、Turn State、Conversation Head、Updated Timestampを同一Atomic Commitで確定する。
- Cancel／Complete競合はCASで一方だけをTerminalへ確定し、Cancel確定後のModel OutputをCanonical化しない。

## 6. Display HistoryとGeneration Projection

次を混同しない。

```text
Display History
  completed／cancelled／failed／interruptedをEvidenceとして表示可能

Generation Projection
  head_turn_idからparent_turn_idを辿ったcompleted Turnの
  user -> assistantだけ
  + 現在処理するpending User Message
```

Cancelled／Failed／Interrupted Turn、Partial Output、Thinkingおよび内部Contextを次Generationへ渡さない。これにより、Phase 1のCancel／Error時にPending UserをBrowser HistoryからRollbackする意味Contractを維持する。

永続Conversationの容量と、既存Generation Requestの`64 messages／1 message 32,768 characters／total 131,072 characters`を分離する。Phase 2-B Mapperは選択Branchから既存入力上限内のProjectionを構築し、超過時の明示Error、明示Compactionまたは将来Summary Policyを選ぶ。無言Truncateは禁止する。

## 7. Storage Port Contract

Domain／ApplicationはFilesystem、SQLite、JSON、Cloud Database、Browser StorageまたはDriverへ依存しない。Repository Portは次を表現する。

- `get(scope_id, conversation_id)`
- `commit(command)`
- `list(query)`
- Atomic Compare-and-swap
- Operation Idempotency
- Stable Pagination Order
- Page自身が`scope_id`を持ち、異Scope Summaryの混入を拒否する

Storage RevisionはStore所有の単調増加Concurrency Tokenであり、Domain Schema Version、Storage Format Version、Migration Plan VersionまたはAPI Versionと兼用しない。

- Createは`expected_revision=None`。
- Updateは既知の`expected_revision`を必須とする。
- StoreがRevisionを一つ増分しReceiptを返す。
- 同じ`operation_id`と同じ内容の再送は同じ成功結果へ収束する。
- 同じ`operation_id`と異なる内容は拒否する。
- Blind Last-write-wins、暗黙MergeおよびModel生成中の長時間Transactionを禁止する。
- Atomic Unitは一つのConversation Aggregateとする。
- 成功後の同一AdapterはRead-your-writesを満たす。

Generic Transaction、Hard Delete、PurgeおよびProduction In-memory Adapterは公開しない。Phase 2-A Test DoubleはMemoryだけを使い、Repository内へ保存File／DBを作らない。

## 8. Persistence Timing Contract

Persistent Applicationは少なくとも次の二Commitへ分ける。

1. Generation前にPending User／TurnをAtomic Commitする。
2. Generation成功後にCanonical Assistant／Terminal Turn／Conversation Headを別CASでAtomic Commitする。

Crashで残ったNon-terminal Turnは`interrupted`へ明示遷移できる。Persistent ModeではTerminal Commit成功後にだけ`completed`をClientへ通知する。Commit失敗をCompletedとして通知せず、Ephemeral Modeへ無言Fallbackしない。

Phase 2-AではApplication ServiceとWeb接続を実装しない。このContractをPhase 2-Bへ渡す。

## 9. Schema／Migration／Rollback

次を別概念として固定する。

```text
API Version
Conversation Domain Contract Schema Version
Storage Format Schema Version
Storage Revision／ETag
Migration Plan Version
Model／Backend Version
```

- WriterはCurrent Domain Schemaだけを書く。
- ReaderはCurrentと明示登録済み旧Schemaだけを読む。
- Unknown／Future SchemaをCurrent ModelへBest-effort Parseしない。
- Read時の暗黙In-place Migration、自動修復、自動Quarantineおよび部分復元を禁止する。
- Migrationは全Record Preflight、Checkpoint、Staging変換、全件検証、Atomic Cutoverの順で行う。
- 失敗または中断時に旧原本を変更しない。
- RollbackはDown-convertではなくPre-migration Checkpointへの復旧とする。
- Migration後に新しいWriteがある場合の自動Rollbackは禁止し、Human Gateへ送る。

Migration型／Maintenance PortはPhase 2-Aで定義する。Concrete Migration／Rollback実装と実行はPhase 2-B以降とする。

## 10. Failure Contract

少なくとも次をTyped Safe Failureとして区別する。

```text
Domain:
  invalid_identity
  invalid_transition
  invariant_violation

Storage:
  conflict
  invalid_record
  unsupported_schema
  migration_required
  migration_incomplete
  corrupt_data
  storage_unavailable
  storage_timeout
  capacity_exceeded
  permission_denied
  read_only
  atomic_commit_failed
```

Storage Mutation Outcomeは`not_applied | applied | unknown`を区別する。`unknown`ではBlind Retryを禁止し、`operation_id`で照合する。Safe FailureへPath、Message本文、Credential、内部Exception、Raw RecordまたはUser識別情報を含めない。Scope不一致は情報漏えいを避けるためNot Foundと同じ外部意味へ正規化できる。

## 11. Phase 1 Compatibility／Security Boundary

- 既存`ConversationMessage`、`ConversationGenerationInput`、`ConversationGenerationService`および`ConversationGenerationSession`を変更しない。
- 既存`POST /api/v1/chat/stream`、`/api/v1/chat/stop`、SSE Shape／OrderをPhase 2-A／2-Bで変更しない。
- 現行v1はEphemeral Compatibility PathとしてStorage Write 0を維持する。
- Client送信の全HistoryとServer永続Historyを黙ってMergeしない。
- Persistent API／UIはPhase 2-Cで別Versioned Surfaceとして追加する。
- Browser MemoryにはStable Identity／Schemaがないため自動Migrationしない。明示Importは後続Phaseの別Contractとする。
- Public DemoおよびShared Basic Previewには安全な個別Conversation Scopeがないため、Persistence AdapterをBindingせず、List／Resume／Storage Writeを既定拒否する。
- Persistence未構成は明示Ephemeral Profileであり、Persistent Modeの保存失敗とは区別する。
- `request_id`をConversation／Session／Turn／Message Identityへ流用しない。

Current Basic Designにあるclient-generated `request_id`、SSE `started`およびclient `system` roleの記述はAs-builtと衝突する。Phase 2-Aの互換正本はserver-generated `request_id`、SSE `start`、client roles `user／assistant`である。

## 12. Out of Scope

- Concrete Persistence Adapter／Serialization／DB Schema
- Persistent Lifecycle Application Service
- Chat List、Resume、Regenerate、Branch UI
- Browser API変更／Persistent API実装
- Configuration Control Surface／Research Developer Mode
- Component Registry／Switchboard
- Documentation RAG Follow-up実装
- Audit Ledger、Governance Evidence、Agent／Tool Memory
- Multi-user Authorization、Account、Sharing
- Data Retention／Hard Delete Policyの最終確定

## 13. Acceptance Criteria

### 13.1 Design／Source

- Identity、State、Projection、Storage、Schema、Migration、FailureおよびPhase 1互換が相互整合する。
- Domain／PortからFastAPI、Browser、Filesystem、JSON、SQLite、PostgreSQLまたはCloud SDKへのImportがない。
- Persisted Message型でSystem、Tool、Thinking、Partial OutputまたはHidden Originalを表現できない。
- Top-level既存`conversation/public.py`と既存Runtime Pathを変更しない。

### 13.2 Test

- Blank ID、Naive／non-UTC Timestamp、重複ID／Sequence、Cross-scope／Cross-conversation参照、Cycle、不正遷移を拒否する。
- Retry／Regenerateが元Turnを変更せず、新Branchを決定的に表現する。
- Cancelled／Failed／Interrupted TurnがGeneration Projectionから除外される。
- CAS Conflict、Duplicate Operation、Unknown Commit Outcomeを区別する。
- Unknown Schema、Corruption、Migration FailureがFail-closedとなる。
- Scope IsolationとList Isolationを検証する。
- Summary成功／FallbackのCanonical Assistant選択をTestする。
- Existing Conversation Unit／Web IntegrationがRegressionなしで合格する。
- Concrete Persistence I/Oが0件である。

### 13.3 Closure

- Requirements／Architecture／ADR／Implementation／Test／Handoffが整合する。
- P2-A-WU-001～003のStatusと再開点がHistoryへ残る。
- Phase 2-Bが暗黙のIdentity、StorageまたはMigration仕様へ依存しない。
- Technical Blockerが0件である。
- ユーザーのPhase 2-A Final Acceptance前にPhase 2-Bへ進まない。

## 14. Related Documents

- [Phase 2 Index](../phase_index_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Phase 2-A Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [Phase 2-A ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- [Phase 2-A Execution Plan](../operations/phase_2_a_execution_plan_ja.md)
