# Phase 2-A Conversation Domain Foundation Architecture

```yaml
document_id: phase_2_a_conversation_domain_architecture
status: design_frozen
phase: phase_2
subphase: phase_2_a
language: ja
created_at: 2026-08-12 01:43:31 JST
updated_at: 2026-08-12 01:51:52 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2実装者役
decision_authority: user
storage_adapter_implementation: deferred_to_phase_2_b
```

## 1. Architecture Goal

Phase 2-Aは、既存Ephemeral Generation Runtimeを維持しながらPersistent Conversationへ進むDomain Kernelだけを追加する。

```text
Existing /api/v1/chat/*
  Browser full-history request
  -> Existing ConversationGenerationService
  -> Existing Inference／Presentation／RAG
  -> Storage Write 0

New Phase 2-A Foundation
  Conversation Domain／Identity／State
  -> Generation Projection Contract
  -> Conversation Repository Port
  -> Schema／Failure／Migration Contract

Phase 2-B
  Persistent Application Orchestrator
  -> Concrete Store Adapter
  -> Domain-to-v1 Generation Mapper

Phase 2-C
  Separate Versioned Persistent API／UI
```

Phase 2-A FoundationをWeb Request Pathへ接続しない。Client HistoryとServer Historyの二重正本化を防ぎ、既存Runtimeを変更しない。

## 2. Package Boundary

```text
src/margpa_runtime_llm/modules/conversation/
├─ contracts.py                         # Existing ephemeral transport contract／unchanged
├─ public.py                            # Existing Phase 1 export／unchanged
├─ application/
│  └─ conversation_generation.py        # Existing one-request runtime／unchanged
├─ domain/
│  ├─ __init__.py
│  ├─ errors.py
│  ├─ identity.py
│  └─ models.py
└─ ports/
   ├─ __init__.py
   └─ conversation_store.py
```

新Domainは`conversation.domain`、Portは`conversation.ports`から公開する。Top-level`conversation.public`への統合はPhase 2-Bへ延期する。Domain／PortからFastAPI、Browser、Filesystem、JSON、SQLite、PostgreSQL、Cloud SDKまたはModel BackendをImportしない。

## 3. Contract Layers

次のMessage Contractを分離する。

```text
Transport Message
  Existing /api/v1 input
  role = user | assistant

Persisted Message
  Canonical user-visible history
  role = user | assistant

Model Prompt Message
  Internal inference input
  role may include system／tool
```

TransportまたはModel PromptをPersisted Messageの代替にしない。

## 4. Identity Architecture

各Identityは`ImmutableContract`を用いたOpaque Value Objectとする。

```text
ConversationScopeId
ConversationId
ConversationSessionId
ConversationTurnId
ConversationMessageId
ConversationOperationId
```

各Value Objectは`value`を持ち、non-empty、bounded length、安全文字だけを検証する。型間の暗黙変換を提供しない。UUID4等の発番はApplication／Adapter Factory責務である。

```text
scope_id != conversation_id != session_id != turn_id
         != message_id != operation_id != request_id
```

既存`request_id`は一回のGeneration／Cancel相関であり、Summary時に派生Suffixを持ち得る。永続Identityへ流用しない。

## 5. Domain Model

### 5.1 ConversationSnapshot

```text
ConversationSnapshot
  schema_version                 # Domain Contract Version only
  scope_id
  conversation_id
  state: active | archived
  head_turn_id?
  created_at
  updated_at
  sessions[]
  turns[]
  messages[]
```

SnapshotはStorage Revisionを持たない。Storage Revisionは`StoredConversation` EnvelopeのConcurrency Tokenである。TimestampはTimezone-aware UTCだけを受理する。

### 5.2 ConversationSessionRecord

```text
session_id
conversation_id
state: active | closed | interrupted
opened_at
finished_at?
```

`ConversationSessionRecord`という名称で既存`ConversationGenerationSession`との衝突を避ける。ActiveからClosed／Interruptedへだけ遷移できる。

### 5.3 ConversationTurn

```text
turn_id
conversation_id
session_id
sequence
state: pending | generating | completed | cancelled | failed | interrupted
origin: normal | retry | regenerate
parent_turn_id?
derived_from_turn_id?
user_message_id
assistant_message_id?
request_id?
started_at
finished_at?
```

一つのTurnは一つのUser Messageと0または1件のAssistant Messageを持つ。CompletedだけがAssistant Messageを必須とし、それ以外はAssistant Messageを持たない。Retry／Regenerateは新Turnを作り、元Turnを変更しない。

### 5.4 PersistedConversationMessage

```text
message_id
conversation_id
turn_id
sequence
role: user | assistant
content
created_at
```

MessageはImmutableである。保存型にSystem、Tool、Thinking、Partial Delta、Internal Prompt、RAG Injected ContextまたはHidden Original用Fieldを設けない。

### 5.5 ConversationSummary

List用Projectionは本文を返さない。

```text
scope_id
conversation_id
state
head_turn_id?
created_at
updated_at
```

## 6. Aggregate Invariants

Snapshot構築時に全体を検証する。

1. 全Childの`conversation_id`がRootと一致する。
2. 全Identityと各Sequenceに重複がない。
3. Turnの`session_id`が同じConversationの既存Sessionを指す。
4. TurnのUser／Assistant参照先が存在しRoleが一致する。
5. TurnごとにUserはちょうど1件、Assistantは最大1件である。
6. Completed TurnだけがAssistantを持ち、CompletedではAssistantが必須である。
7. Parentは同じConversationの過去Completed Turn、Derivedは過去Terminal Turnを指し、Self／Cycleを作らない。Retry／RegenerateはDerived元と同じParentを維持する。
8. Headは同じConversationのCompleted Turnだけを指す。
9. Archived ConversationにNon-terminal TurnまたはActive Sessionを含めない。
10. Created／Started／Finished／Updated Timestampの順序が矛盾しない。
11. 同一ConversationのNon-terminal Turnは最大1件である。
12. Unknown Fieldおよび不可能なState Combinationを拒否する。

不整合Snapshotを部分的に受理、Skipまたは上書き修復しない。

## 7. State Transition／Branch

```text
Conversation
  active -> archived
  archived -> active

Session
  active -> closed | interrupted

Turn
  pending -> generating | cancelled | failed | interrupted
  generating -> completed | cancelled | failed | interrupted
```

Terminal Stateからの遷移を拒否する。Stateを文字列上書きするMutation APIを公開しない。

```text
Normal next turn:
  parent_turn_id = current head
  derived_from_turn_id = None

Retry／Regenerate:
  parent_turn_id = source.parent_turn_id
  derived_from_turn_id = source.turn_id
```

新TurnのCompleteがAtomic Commitされた時だけHeadを新Turnへ動かす。失敗、取消または中断ではHeadを変更しない。

## 8. Generation Projection

Application MapperはHeadからParent Chainを辿り、Completed Turnだけを古い順に並べる。

```text
for each completed turn:
  Persisted USER -> existing ConversationMessage(USER)
  Persisted ASSISTANT -> existing ConversationMessage(ASSISTANT)

then:
  current PENDING USER
```

Cancelled／Failed／Interrupted、Thinking、Partial Outputおよび内部ContextをProjectionへ入れない。永続履歴全体と既存Generation Input上限を分離し、無言Truncateを禁止する。容量PolicyのApplication実装はPhase 2-Bで行う。

## 9. Repository Port

```python
@runtime_checkable
class ConversationRepositoryPort(Protocol):
    def get(
        self,
        scope_id: ConversationScopeId,
        conversation_id: ConversationId,
    ) -> StoredConversation | None: ...

    def commit(
        self,
        command: CommitConversation,
    ) -> ConversationCommitReceipt: ...

    def list(
        self,
        query: ConversationListQuery,
    ) -> ConversationPage: ...
```

```text
StoredConversation
  conversation: ConversationSnapshot
  storage_format_version
  storage_revision >= 1
  last_operation_id

CommitConversation
  scope_id
  operation_id
  expected_revision: None(create) | >=1(update)
  conversation

ConversationCommitReceipt
  scope_id／conversation_id／operation_id
  previous_revision
  committed_revision

ConversationListQuery
  scope_id／states／limit／cursor

ConversationPage
  scope_id／summaries[]／next_cursor?
```

Storeが成功CommitごとにStorage Revisionを一つ増分する。Application SnapshotをStoreが暗黙変更してはならない。List順は`updated_at descending, conversation_id ascending`で安定化し、CursorはOpaqueとする。PageはQuery Scopeを保持し、異Scope Summaryの混入を型Validationで拒否する。

Atomic Unitは一つのConversation Aggregateである。Partial Message、片側Turn、Revisionだけの進行を返さない。CAS不一致はConflictとし、同じStoreを共有する複数Process間のLost Updateも防ぐ。Generic `begin_transaction()`、Hard Delete／PurgeおよびModel生成中のLock保持を公開しない。

## 10. Idempotency／Unknown Outcome

- Createは`expected_revision=None`。
- Updateは既知Revisionを必須とする。
- 同じOperation IDと同じCommandは同じ成功Receiptへ収束する。
- 同じOperation IDと異なるCommandはConflictとする。
- Timeout後のOutcomeがUnknownならBlind RetryせずOperation IDで照合する。

```text
StorageMutationOutcome
  not_applied
  applied
  unknown
```

## 11. Failure Architecture

```text
ConversationDomainError
  invalid_identity
  invalid_transition
  invariant_violation

ConversationStorageError
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

ErrorはCode、Safe Message、Retryable、Mutation Outcomeおよび安全な相関情報を持つ。Path、Raw Record、Message本文、CredentialおよびDriver ExceptionをSafe Outputへ含めない。Not Foundは`get()`の`None`で表現し、Scope不一致の存在を漏らさない。

## 12. Schema／Migration Architecture

Domain Contract Version、Storage Format Version、Storage Revision、Migration Plan VersionおよびAPI Versionを別Field／型として扱う。既存`ImmutableContract.schema_version = "1"`はDomain Contract Serializationだけを表し、Disk FormatやRevisionに流用しない。

Maintenance Portは通常Repositoryと分離する。

```text
inspect_schema() -> ConversationStorageSchemaStatus
plan_migration(target_version) -> MigrationPlan
migrate(plan, checkpoint_id) -> MigrationReceipt
rollback(receipt) -> None
```

Read時の暗黙Migrationを禁止する。Preflight、Checkpoint、Staging変換、全件Validation、Atomic Cutoverを必須とする。中断MarkerがあるStoreは通常Openを拒否する。RollbackはCheckpoint復旧であり、Migration後Writeがある場合はHuman Gateとする。Concrete実装はPhase 2-Bへ延期する。

## 13. Persistence／SSE Boundary

```text
1. Pending User／TurnをCAS Commit
2. Existing Generation Runtimeを実行
3. Canonical Assistant／Terminal Turn／HeadをCAS Commit
4. Commit成功後にcompletedを送信
```

Crash後のNon-terminal TurnはInterruptedへ遷移できる。Commit失敗時はCompletedを通知せず、保存されたと偽らない。Persistent BindingがないEphemeral Profileと、Persistent ModeのStorage Failureを混同しない。

## 14. Compatibility Architecture

```text
/api/v1/chat/stream／stop
  unchanged ephemeral path
  server-generated request_id
  SSE event=start
  client role=user|assistant
  browser sends full history
  storage write=0

future persistent surface (Phase 2-C)
  separate versioned API
  repository is sole history source
  client history is not merged
```

Phase 1 Browser Memoryは自動Migration Sourceにしない。RollbackはPersistent Bindingを無効化してv1へ戻し、Storageを削除、Downgradeまたは自動変換しない。

Public Demo／Shared Basic Previewは安全な個別Scopeがないため、Persistence Adapter未Binding、List／Resume拒否、Storage Write 0を維持する。

## 15. Test Architecture

### Identity／Timestamp

- blank／whitespace／oversize／unsafe character
- 型別Round-trip／型取り違え
- Naive／non-UTC Timestamp拒否

### Aggregate／Branch

- duplicate identity／sequence
- cross-scope／cross-conversation reference
- missing／self／cycle parent
- Session参照／Role mismatch
- completed Assistant必須／non-completed Assistant拒否
- deterministic retry／regenerate branch
- Head validation／terminal immutability

### Projection／Privacy

- Completed branchだけをGeneration Contextへ投影
- Cancelled／Failed／Interrupted除外
- System／Tool／Thinking／Partial／Hidden Original表現不能
- Summary success／fallbackのCanonical Assistant選択

### Repository Contract

- create／update CAS
- duplicate operation same／different payload
- stale revision／unknown outcome
- scope isolation／stable pagination
- schema／corruption／migration failure
- memory fake only／repository artifact zero

### Regression

- Existing Conversation Unit／Web Integration
- Existing SSE／Summary／RAG／Busy／Stop／Disconnect
- `ruff format --check`／`ruff check`／`mypy`／Full `pytest`

## 16. Implementation Order

```text
1. errors／identity
2. state／message／turn／session／snapshot
3. aggregate validators／projection
4. repository／maintenance port types
5. domain／ports package exports
6. unit contract tests
7. existing regression tests
8. static checks
```

## 17. Phase 2-B／2-C Handoff Boundary

Phase 2-Bへ渡すもの：

- Frozen Domain／State／Projection Contract
- Repository／Maintenance Port
- Schema／Failure／Migration Contract
- Unit／Compatibility Evidence

Phase 2-Bで実装するもの：

- Concrete Adapter／Serialization／DB Schema
- Atomic Write／Crash Recovery
- Persistent Lifecycle Orchestrator
- Domain-to-existing-Generation Mapper
- Capacity／Compaction Policy

Phase 2-Cで実装するもの：

- Separate Versioned Persistent API
- Chat List／Resume／New Chat
- Retry／Regenerate／Branch UX

Component Registry／SwitchboardはPhase 2-Eで設計・実装する。

## 18. Related Documents

- [Phase 2-A Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Phase 2-A ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- [Phase 2-A Execution Plan](../operations/phase_2_a_execution_plan_ja.md)
- [Phase 2 Index](../phase_index_ja.md)
