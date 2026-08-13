# Phase 2-B Conversation Persistence／Lifecycle Architecture

```yaml
document_id: phase_2_b_conversation_persistence_architecture
status: accepted_for_phase_2_b_implementation
phase: phase_2
subphase: phase_2_b
language: ja
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
decision_authority: project_controller_and_user
```

## 1. Architecture Goal

Phase 2-AのDomain／Portを変更せず、Local Private Profileだけが明示生成できる永続Conversation Kernelを追加する。

```text
Local Private caller (Phase 2-CでAPI Binding)
  -> ConversationPersistenceFactory
  -> PersistentConversationService
       -> GenerationContextMapper
       -> Existing ConversationGenerationService (unchanged)
       -> ConversationRepositoryPort
            -> SQLiteConversationStore

Existing /api/v1/chat/*
  -> Existing ConversationGenerationService
  -> Persistence Factory未参照／Storage Write 0

Public Demo／Shared Basic Preview
  -> Persistence Bindingなし／Storage Write 0
```

Phase 2-BはWeb Route、Browser UIまたは既存Profileへ接続しない。FactoryをImportしただけではDirectory、DB、Lock、LogまたはRuntime Dataを作らない。

## 2. Package／Dependency Boundary

```text
src/margpa_runtime_llm/modules/conversation/
├─ domain/                              # Phase 2-A frozen
├─ ports/                               # Phase 2-A frozen
├─ contracts.py                         # existing v1 frozen
├─ public.py                            # existing v1 frozen
├─ application/
│  ├─ conversation_generation.py        # existing v1 frozen
│  ├─ persistence_models.py             # lifecycle commands／safe result
│  ├─ recording.py                      # metadata-only future port／default unbound
│  ├─ generation_context_mapper.py      # Domain -> existing v1 input
│  └─ persistent_conversation_service.py
└─ adapters/
   ├─ __init__.py
   ├─ sqlite_conversation_store.py       # Repository + schema status
   ├─ sqlite_migration.py                # explicit migration/checkpoint
   └─ persistence_factory.py             # opt-in local construction
```

Dependency directionは`application -> domain／ports／existing contracts`、`adapters -> domain／ports／application construction contract`とする。Domain／PortからAdapterへ逆Importしない。Web／CLI／LightningからのImportはPhase 2-Bで追加しない。

## 3. Explicit Local Binding

`LocalConversationPersistenceSettings`は次だけを受け取るImmutable Valueとする。

```text
enabled                  # default false
runtime_data_root        # explicit Path, enabled時必須
scope_id                 # explicit ConversationScopeId, enabled時必須
busy_timeout_ms          # bounded, safe default
recording_mode           # off only in Phase 2-B
```

- `build_local_conversation_persistence(settings, generation_service, ...)`は`enabled=false`でAdapterを作らず、明示的なDisabled Resultを返す。
- `enabled=true`でもBuilderはFilesystem Mutationを行わない。呼出元が`initialize_new_store()`または`open_ready_store()`を選ぶ。
- Rootは呼出元注入とし、Environment Variable、Repository Root、User HomeまたはCWDから暗黙推定しない。
- Phase 2-Bでは既存TOML、Web Access Profile、CLI ArgumentおよびEnvironment Loaderを変更しない。Local Private Bindingの公開SurfaceはFactoryまでとする。

## 4. Physical Layout／Permissions

`scope_key = sha512("margpa-conversation-scope-v1\0" + scope_id.value).hexdigest()`とし、Scope本文をPathへ出さない。

```text
<runtime_data_root>/
├─ persistent/<scope_key>/conversations/conversations.sqlite3
└─ recovery/
   ├─ checkpoints/<scope_key>/conversations/<checkpoint_id>.sqlite3
   └─ migrations/<scope_key>/conversations/<migration_id>.json
```

- Path Resolution後、全対象がRoot配下であることを`relative_to()`相当で確認する。Symlinkを含む親、非Regular DB、Group／Other書込可能な既存Directoryを拒否する。
- 新規Directoryは`0700`、DB／Checkpoint／Markerは`0600`で作成する。既存対象を黙って`chmod`しない。
- `inspect_schema()`とBuilderはRead-onlyで、Path不存在時は`EMPTY`を返す。
- `initialize_new_store()`だけが不足Directory／DBを作る。既存非Empty未知DBを初期化しない。
- Runtime Data本体はGit管理対象外であるが、Phase 2-Bは`.gitignore`を変更しない。Testは`tmp_path`だけを使い、Project Rootへ`runtime_data/`を作らない。

## 5. SQLite Store

### 5.1 Connection Policy

各Repository Operationは短命Connectionを使用し、生成中にConnection／Transaction／File Lockを保持しない。

```text
PRAGMA foreign_keys = ON
PRAGMA trusted_schema = OFF
PRAGMA journal_mode = DELETE
PRAGMA synchronous = FULL
PRAGMA busy_timeout = <bounded milliseconds>
```

DB Schemaは`store_metadata`、`conversations`、`commit_operations`で構成し、SQL IdentifierはSource定数、Valueは全てParameter Bindingとする。

### 5.2 Canonical Envelope

SnapshotはPydantic JSON Modeへ変換後、UTF-8、Sorted Key、Compact Separator、`allow_nan=false`のCanonical JSONへSerializeする。SHA-512はCanonical Bytesに対して計算する。Readでは次の順で検証する。

1. Storage／Domain Version。
2. UTF-8／JSON ParseとDuplicate Key拒否。
3. SHA-512一致。
4. Exact Field Contract。
5. `ConversationSnapshot.model_validate()`。
6. SQL MetadataとSnapshot Identity／State／Timestampの一致。

一段でも失敗すればRecord全体を返さずTyped Storage Errorとする。`pickle`、任意Decoder Hook、部分Skipまたは自動修復を使わない。

### 5.3 CAS／Idempotency

Command DigestはScope、Operation ID、Expected RevisionおよびCanonical SnapshotをDomain-separated Canonical JSONとしてSHA-512化する。

```text
BEGIN IMMEDIATE
  lookup operation receipt
    same digest      -> stored receiptを返す
    different digest -> conflict/not_applied
  read current revision
  compare expected revision
  conditional INSERT or UPDATE
  insert operation command digest + receipt
COMMIT
```

Conversation UpdateとReceipt Insertを同一Transactionに置く。SQLite Commit境界でI/O Errorが発生し適用有無を証明できない場合、`unknown`を返し、呼出元は新Connectionの`get_commit_receipt()`で照合する。Operation IDを変えたBlind Retryは禁止する。

### 5.4 Read／List

Adapter Instanceは一つの`bound_scope_id`だけを扱う。異ScopeReadはNot Found／Empty Page、異ScopeWriteは`permission_denied/not_applied`とする。

Listは`updated_at_us DESC, conversation_id ASC`のKeyset Paginationとする。CursorはVersion、Scope Digest、Updated Time、Conversation IDをCanonical JSON＋URL-safe Base64化し、署名による認可の代替とはしない。Malformed／別Scope／別Version Cursorを`invalid_record`として拒否する。

## 6. Schema／Migration

Phase 2-B Current SchemaはStorage `sqlite-1`、Domain `1`とする。

```text
Pathなし                         -> EMPTY
Current Metadata + Integrity OK  -> READY
登録済み旧Version               -> MIGRATION_REQUIRED
Markerあり                       -> MIGRATION_INCOMPLETE
未知／Future Version             -> UNSUPPORTED
Malformed／Digest不一致          -> CORRUPT
```

`initialize_new_store()`と`migrate()`は別Operationであり、Read時Migrationはない。Production Registryは初期状態でLegacy Step 0件とする。Migration Engine自体はTest用Fixture Stepで次を検証する。

1. Sourceを変更しないPreflightとExclusive Access確認。
2. `0600`Checkpoint作成、Digest／Record Count確定。
3. Migration MarkerをAtomic Write。
4. 同一FilesystemのStaging DBへ全件変換。
5. 全RecordをCurrent Domainとして再読込・検証。
6. `fsync`後`os.replace`でCutover。
7. Receiptを確定しMarkerを完了状態へ更新。

失敗時は旧Active Storeを変更しない。残存Markerは次回StartupをFail-closedにする。RollbackはReceiptのTarget DigestとActive Digestが一致する場合だけCheckpointからAtomic Restoreできる。不一致はMigration後Writeの可能性としてHuman Gateに送る。

## 7. Application Lifecycle Service

Application ServiceはClock、Identity Factory、Repositoryおよび既存Generation ServiceをConstructor Injectionする。MutationごとにOperation IDを呼出元から受け、内部で暗黙再発番しない。

主なCommandは次である。

- `create_conversation()`：Conversation＋Active SessionをRevision 1へCommit。
- `resume_conversation()`：Terminal Session後に新Active Sessionを追加。
- `append_user_turn()`：User Message＋Pending Turnを一Commit。
- `start_generation()`：Pending Turnへrequest_idを関連付けGeneratingへCommit。
- `complete_generation()`：Canonical Assistant＋Completed＋Headを一Commit。
- `cancel／fail／interrupt_generation()`：本文なしTerminal Turnを一Commit。
- `close／interrupt_session()`、`archive／unarchive_conversation()`。

Applicationは既存SnapshotをImmutable Copyで置換し、各段階でDomain Validatorを通す。CAS Conflictを無言Mergeしない。Retry／Regenerate／Branch選択は2-Cまで公開しない。

## 8. Generation Mapper／Orchestrator

`GenerationContextMapper`はPhase 2-Aの`project_generation_history()`から、Completed BranchのUser／Assistantと現在のPending Userだけを既存`ConversationGenerationInput`へ写像する。Effective Generation Settingsは永続履歴から推測せず呼出元が別途渡す。

上限は既存Contractと同じ`64 messages`、1件`32,768 characters`、合計`131,072 characters`である。超過時はGeneration Service Call 0で`generation_context_limit_exceeded`を返す。Truncate／Summary／Record書換えは行わない。

Persistent OrchestratorのEvent順は次である。

```text
Pending User commit
-> context mapping
-> existing generation start
-> request_id/generating commit
-> generation outside transaction
-> canonical terminal commit
-> terminal event exposure
```

`completed`では既存EventのCanonical `assistant_message.content`だけを保存する。Cancel／Error／Iterator Close／DisconnectはAssistant本文を保存せず、それぞれ`cancelled／failed／interrupted`をCommitする。Terminal Commit失敗時は成功Terminal Eventを渡さず、Ephemeral SuccessへFallbackしない。

## 9. Startup Crash Recovery

`recover_incomplete_conversations()`はPersistent ServiceのReady Gateで実行する。

- Stable PaginationでBound Scopeを全走査する。
- Pending／Generating TurnをInterrupted、Active SessionをInterruptedへ変換する。
- Assistant Message、Partial、Failure Textを追加しない。
- ConversationごとにCAS Commitし、他Conversationと一つのTransactionにしない。
- CAS Conflictは再読込後もRecovery対象の場合だけ有界再試行する。
- Unknown OutcomeはReceipt照合だけを行いBlind Retryしない。
- 全件完了前に新Generationを受け付けない。Schema／Store／Recovery FailureはStartup Fail-closedとする。

## 10. Recording Boundary

Conversation PersistenceとResearch Recordingを別Capabilityとする。Phase 2-BではMetadata-only `ConversationRecordingPort`の型境界だけを追加できるが、Persistent ServiceのDefaultは`None`、Recording Modeは`off`だけを有効値とし、Recorder未Binding／Call 0である。Metadata EventはIdentity、Mode、Timestamp、Duration、Token、OutcomeおよびDigest Referenceだけを許し、Message Content、Prompt、RAG Context、Thinking、Partial、Hidden Original、CredentialまたはPathのFieldを持たせない。Filesystem Recorderは実装しない。

通常DBへ保存する本文はCanonical User TextとUser-visible Canonical Assistant Final Textだけである。Raw／Visible Thinking、System／Tool Prompt、RAG Injected Context、Citation本文、Partial Output、Hidden OriginalおよびSecretは保存しない。Protected Research Captureは別Capabilityのまま延期する。

## 11. Failure Mapping

SQLite／OS Errorは既存`ConversationStorageErrorCode`へ正規化し、Safe MessageにPath、SQL、Driver TextまたはRecord本文を含めない。

| Cause | Code | Outcome |
|---|---|---|
| stale CAS／operation reuse | `conflict` | `not_applied` |
| lock timeout | `storage_timeout` | `not_applied` |
| read-only filesystem／DB | `read_only` | `not_applied` |
| permission failure | `permission_denied` | `not_applied` |
| disk full／quota | `capacity_exceeded` | `not_applied`または`unknown` |
| malformed DB／digest mismatch | `corrupt_data` | `not_applied` |
| valid JSON but invalid Domain | `invalid_record` | `not_applied` |
| unknown schema | `unsupported_schema` | `not_applied` |
| migration marker | `migration_incomplete` | `not_applied` |
| commit boundary uncertainty | `atomic_commit_failed` | `unknown` |

## 12. Verification Boundary

Unit／Integration Testは`tmp_path`をRootとして使用し、Project Root、Home、External Pathまたは実Runtime Dataへ書かない。既存v1回帰ではSource Hash／Adapter Spy／Filesystem InventoryによりStorage Write 0を確認する。Public／BasicのConfig／RuntimeにはBindingを追加しないため、両Surfaceの既存Test合格をZero-binding Evidenceとする。

## 13. Deferred

- Persistent API／UI、List／Resume／Retry／Regenerate／Branch UX：Phase 2-C。
- Recording Mode Control、Apply／Restart Boundary：Phase 2-D。
- Component Switchboard／RAG Follow-up：Phase 2-E。
- Retention／Purge／Encryption／Cloud／Multi-host／Protected Research Capture：後続Decision。

## 14. Related Documents

- [Requirements](../requirements/phase_2_b_conversation_persistence_requirements_ja.md)
- [ADR](../adr/phase_2_b_conversation_persistence_adr_ja.md)
- [Implementation Handoff](../handoffs/phase_2_b_implementation_handoff_ja.md)
- [Acceptance Matrix](../operations/phase_2_b_acceptance_matrix_ja.md)
