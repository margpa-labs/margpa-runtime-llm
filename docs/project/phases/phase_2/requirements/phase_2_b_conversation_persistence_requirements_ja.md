# Phase 2-B Conversation Persistence／Lifecycle 要件定義

```yaml
document_id: phase_2_b_conversation_persistence_requirements
status: accepted_for_phase_2_b_implementation
phase: phase_2
subphase: phase_2_b
language: ja
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
decision_authority: project_controller_and_user
```

## 1. 目的

Phase 2-Bは、Phase 2-AでFreezeしたConversation AggregateとRepository Portを変更せず、Local Private環境で差替可能な永続化、Lifecycle Application Service、Crash Recoveryおよび既存Generation ContractへのMapperを実装可能に固定する。

到達線は次である。

> CanonicalなUser／Assistant Messageだけを、Scope分離されたLocal StoreへAtomic CASで保存し、Process Crash、競合、不明なCommit Outcome、破損およびSchema不整合を、無言の成功またはEphemeral Fallbackに変換しない。

## 2. Frozen Boundary

次を変更しない。

- `conversation.domain`のIdentity、Aggregate、State、ProjectionおよびPrivacy Contract。
- `conversation.ports.conversation_store`のCAS、Idempotency、Revision、Schema／Migration Contract。
- 既存`ConversationMessage`、`ConversationGenerationInput`、`ConversationGenerationService`、`ConversationGenerationSession`。
- `POST /api/v1/chat/stream`、`POST /api/v1/chat/stop`、SSE Shape／OrderおよびStorage Write 0。
- Public Demo／Shared Basic PreviewのAdapter未Binding、List／Resume不可、Zero Write。
- Persistent API／UI、Chat List／Resume／Retry／Regenerate UXはPhase 2-Cの責務。

Phase 2-Bの新Application／Adapterは既存Web RuntimeへBindingしない。Local Private向けの明示的なConstruction境界だけを提供し、Import、デフォルト起動または既存Profileの読込みでDirectory／DBを作らない。

## 3. Concrete Local Store

### 3.1 Adapter Selection

Python Standard Libraryの`sqlite3`をPhase 2-Bの初期Local Adapterに採用する。理由は次である。

- 一つのConversation AggregateとOperation Receiptを一つのACID Transactionで確定できる。
- Conditional UpdateとUnique Keyにより、複数Process間のCAS／Operation Idempotencyを一つのAdapter内で検証できる。
- 追加DependencyやNetwork ServiceなしでmacOS／LinuxのLocal Private Runtimeに適用できる。
- Repository／Maintenance PortはSQLiteに依存しないため、将来の別Adapterへ差替えできる。

SQLiteをDomain Model、Port、API ContractまたはScope Identityの意味に逆流させない。Network Database、Cloud Storage、複数Host共有Filesystemは対象外とする。

### 3.2 Data Root／Scope

- Adapterは明示的に注入された`runtime_data_root`と`bound_scope_id`を必須とする。
- Absolute Path、Project RootまたはEnvironment VariableをCore／DomainにHard-codeしない。
- Scope ID本文をPath Segmentに使わず、安定Digestから局所Scope Directory Keyを作る。
- Concrete Pathは`<root>/persistent/<scope_key>/conversations/conversations.sqlite3`とする。
- Constructor／Import／`inspect_schema()`はPath不存在時に作成しない。新規作成は明示`initialize_new_store()`だけが行う。
- 新規DirectoryはOwner-only、DB／Checkpoint／MarkerはOwner read／writeを目標とする。既存PathのPermissionを自動変更せず、安全条件を満たさなければFail-closedとする。
- `scope_id`は常にSQL ValueとしてParameter Bindingし、Path／Table／SQL Identifierに連結しない。

## 4. Storage Record／Serialization

SQLiteには一つのConversation AggregateをCanonical JSON Envelopeとして保存し、List／CASに必要な安全なMetadataを列として持つ。

```text
store_metadata
  application_id, storage_schema_version, domain_schema_version,
  migration_state, active_migration_id

conversations
  scope_id, conversation_id, storage_revision, last_operation_id,
  storage_format_version, snapshot_json, snapshot_sha512,
  state, head_turn_id, created_at_utc, updated_at_utc, updated_at_us

commit_operations
  scope_id, operation_id, conversation_id, command_sha512,
  expected_revision, previous_revision, committed_revision,
  receipt_json, committed_at_utc
```

- Primary KeyはConversationが`(scope_id, conversation_id)`、Operationが`(scope_id, operation_id)`とする。
- JSONはUTF-8、Key Sort、固定SeparatorのCanonical Formとし、Duplicate Key、Unknown Field、NaN／Infinity、不正UTF-8およびDigest不一致を拒否する。
- EnvelopeはStorage Format Version、Domain Schema Version、Conversation Snapshotを明示し、Version間の代用を禁止する。
- Serialization後に`ConversationSnapshot.model_validate()`を再実行し、不整合Recordを部分読取り／自動修復しない。
- `pickle`、任意Object Hook、SQL文の文字列連結を禁止する。
- Canonical Message本文はLocal Private DBに平文保存される。OS PermissionはEncryption at Restの代替ではなく、暗号化が必要なProfileは本AdapterをBindingしない。

## 5. Atomic CAS／Operation Idempotency

各`commit(command)`は次を同一SQLite Transactionで実行する。

1. Schema Readinessを確認する。
2. `(scope_id, operation_id)`を確認する。同じCommand Digestなら保存済みReceiptを返し、異なるなら`conflict／not_applied`とする。
3. Current Revisionと`expected_revision`を比較する。CreateはRecord不存在かつ`None`、Updateは一致する既存Revisionを必須とする。
4. Conditional INSERT／UPDATEでRevisionを1つだけ進める。
5. 同じTransaction内でCommand DigestとReceiptを`commit_operations`へ保存する。
6. Commit後にだけ成功Receiptを返す。

- `BEGIN IMMEDIATE`、有界`busy_timeout`、`journal_mode=DELETE`、`synchronous=FULL`、`foreign_keys=ON`および`trusted_schema=OFF`を使う。
- Model生成中にTransaction、ConnectionまたはFile Lockを保持しない。
- `commit()`の成功後は同じAdapterからRead-your-writesを満たす。
- Commit呼出し中のI/O Errorで適用有無を証明できない場合は`unknown`とする。同じOperation IDのReceiptを新しいConnectionで照合し、一致すれば同じ成功へ収束し、照合不能ならBlind Retryしない。
- Operation Receiptは自動削除しない。Retention／Compactionは後続Decisionとする。

## 6. List／Read Isolation

- Adapterは一つの`bound_scope_id`専用とする。異なるScopeの`get()`／`get_commit_receipt()`はNot Foundと同じ外部意味、`list()`は空Pageとする。異Scopeへの`commit()`は安全な`permission_denied／not_applied`とする。
- Listは`updated_at DESC, conversation_id ASC`のKeyset Paginationとする。CursorはVersion、Scope Digest、UTC時刻およびConversation IDを含む完全なOpaque Valueとし、Scope／Version不一致を拒否する。
- List ProjectionへMessage Content、Raw JSON、PathまたはOperation Dataを入れない。

## 7. Schema／Migration／Rollback Readiness

- 初期Current Storage Schemaを`sqlite-1`、Current Domain Schemaを既存Contractの`1`とする。
- Empty、Ready、Migration Required、Migration Incomplete、UnsupportedおよびCorruptを書込み前に識別する。Ready以外の通常Read／WriteはFail-closedとする。
- 新規Empty Storeの`initialize_new_store()`と、既存StoreのMigrationを別Operationとする。Read時の暗黙Migrationを行わない。
- Migration Engineは明示登録されたSource／Target／StepだけをPlanできる。Phase 2-B時点のProduction Legacy Stepは0件とし、存在しない過去Schemaを捏造しない。
- Engineの成立性は、Test専用の旧Schema Fixtureと登録StepでPreflight、Checkpoint、Staging Transform、全Record Validation、Atomic `os.replace`およびFailure Recoveryを検証する。
- Migration Markerが残るStoreは`migration_incomplete`とし、自動再開／自動Rollbackしない。
- RollbackはCheckpointからのAtomic Restoreだけとする。Cutover後のActive Store DigestがReceiptのTarget Digestと異なる場合は、Migration後WriteがあるとみなしHuman Gateで停止する。
- Checkpoint／Markerは`recovery/migrations/`に分離し、通常Conversation Recordと混在させない。自動削除はしない。

## 8. Lifecycle Application Service

Framework非依存のServiceが次を行う。各Mutationは一つの明示Operation IDと、Create以外では呼出元が知るExpected Revisionを受け取る。

- Conversationと最初のActive SessionのCreate。
- Terminal Session後に新Sessionを追加するResume。旧Sessionを再Openしない。
- 一つのCanonical User MessageとPending TurnのAtomic Commit。
- Generation Request IDを関連付けた`pending -> generating`のCommit。
- Canonical Assistant Message、`completed` Turn、HeadおよびUpdated TimeのAtomic Commit。
- `cancelled／failed／interrupted`へのTerminal Commit。Error文、Warning、Partial OutputまたはModel OutputをそれらのTurnへ保存しない。
- Session Close／Interrupt、Conversation Archive／Unarchive。

Phase 2-BのPersistent Generation OrchestratorはNormal Turnだけを開始する。Retry／Regenerate／BranchのUser-visible Commandと選択はPhase 2-Cへ延期し、Frozen Projectionを暗黙拡張しない。

## 9. Generation Context Mapper／Limit Policy

- Mapperは`project_generation_history(snapshot, pending_turn_id)`の結果だけを既存`ConversationMessage`へ写像する。
- Persisted `user／assistant`以外のRole、System Prompt、Tool Data、RAG Injected Context、Thinking、Status／Warning／ErrorおよびPartial Deltaの入力経路を作らない。
- `ConversationSettings`は永続Messageから復元せず、呼出元が明示したEffective Settingsを別引数で受け取る。
- 既存上限`64 messages／1 message 32,768 characters／total 131,072 characters`を超える場合は、生成を開始せず`generation_context_limit_exceeded`とする。
- 無言Truncate、古いTurnの暗黙破棄、自動Summaryおよび永続Recordの書換えを禁止する。Compaction Policyは別Decisionまで未実装とする。

## 10. Persistent Generation Orchestration

1. User／Pending TurnをCAS Commitする。
2. Commit済みSnapshotからGeneration InputをMapする。
3. 既存Generation Serviceを開始し、その`request_id`でTurnをGeneratingへCAS Commitする。
4. GenerationはDB Transaction／Lockの外で実行する。
5. `completed`ではEventの`assistant_message.content`だけをCanonical AssistantとしてAtomic Commitし、その成功後にEventを呼出元へ渡す。
6. `cancelled／error`では本文を保存せずTerminal StateをCommitし、その成功後にEventを渡す。
7. Iterator Close、Consumer DisconnectまたはTerminal Eventなしの終了は`interrupted`をCommitする。

Terminal Commitの失敗時はTerminal Eventを渡さない。`unknown`ではOperation Receiptを照合し、完全な同一Operationの適用が証明できた場合だけ継続する。Storage失敗をEphemeral Successとして通知しない。

## 11. Crash Recovery

- Persistent ServiceをReadyにする前に、Bound ScopeのActive ConversationをStable Paginationで検査する。
- `pending／generating` Turnを`interrupted`、Active Sessionを`interrupted`とする新Snapshotを1 ConversationごとにCAS Commitする。Assistant Message、Partial Output、Failure Textを追加しない。
- RecoveryはStartup Gate内で行い、同時に新しいGenerationを受け付けない。
- CAS Conflictは最新Snapshotを再読込みし、まだRecovery対象なら新しいOperation IDで有界再試行する。`unknown`はBlind Retryしない。
- Recovery完了前のSchema／Store／Commit失敗はStartup Fail-closedとする。
- Recovery後のResumeは旧Sessionを再Openせず新しいSessionを作る。

## 12. Recording／Sensitive Data

Canonical Conversation PersistenceとRuntime／Research Recordingを別Capabilityとする。

- Runtime RecorderはOptional Portとし、Persistent OrchestratorのDefaultは未Binding／OFFとする。Default PathはRecorderへCallせず、Conversation DB以外のWriteを行わない。
- P2-BはFilesystem Runtime Recorder、`full`記録およびProtected Research Captureを実装／Bindingしない。
- Optional Metadata Event型にMessage Content、Prompt、Context、Thinking、Partial Output、Hidden Original、CredentialまたはPathを表現するFieldを設けない。
- 通常Conversation Recordへ保存できるのはUser TextとUserに提示されるCanonical Assistant Final Textだけである。Summary成功時はSummary、Fallback時は提示されたOriginalだけを保存する。
- Raw Thinking、Visible Thinking、System／Tool Prompt、RAG Injected Context、Citation本文、Hidden Original、Summary Partial、Model Partial Deltaは保存しない。

## 13. Failure Contract

Applicationは少なくとも`not_found`、`invalid_lifecycle`、`generation_context_limit_exceeded`、`storage_not_ready`、`terminal_persistence_failed`をTyped Safe Failureとして区別する。StorageはPhase 2-AのError CodeとMutation Outcomeを維持する。

Safe Failureに次を含めない。

- Filesystem Path／SQLite SQL／Driver Message／Raw Exception
- Message Content／Prompt／RAG Context／Thinking／Partial Output
- Credential／Token／Raw Record／Scopeの他Recordの存在

`locked／busy`は有界Timeout後に`storage_timeout`、容量不足は`capacity_exceeded`、Read-onlyは`read_only`、Permissionは`permission_denied`、Malformed DB／Digest不一致は`corrupt_data`、Decode後Domain不整合は`invalid_record`に正規化する。

## 14. Acceptance Criteria

- 二つのAdapter Instance／Process相当でLost Updateが起きず、CAS ConflictとOperation Idempotencyが決定的に検証できる。
- Commit後Crash／Response喪失相当の再送が同一Receiptへ収束し、異なるPayloadを適用しない。
- Schema不明、Migration中断、DB破損、Record改ざんおよびPermission／Capacity／Lock FailureがFail-closedとなる。
- Migration Testが旧原本不変、Checkpoint、Staging全件Validation、Atomic Cutover、中断MarkerおよびPost-write Rollback拒否を検証する。
- Generation前Pending Commit、Generation中Lock 0、Terminal Commit後Event、Cancel／Complete競合の片方だけが成立する。
- Process再起動相当で残存Non-terminal Turn／Active SessionがInterruptedへ確定し、Canonical AssistantやPartial Textが追加されない。
- MapperがCompleted Branch＋Pending Userだけを古い順に返し、上限を超えるとGeneration Call 0で明示失敗する。
- Summary成功／Fallbackの表示Canonical Textだけが保存され、Thinking／Prompt／RAG Context／Partial／Hidden OriginalはDBとRecording Hookの両方に保存されない。
- Default Recorder Call 0、Project Rootの`runtime_data/`作成0、Public／Basic Preview Binding 0、既存v1 Source変更0を確認する。
- Target Test、Conversation／Web Regression、Full Test、RuffおよびMypyが合格する。

## 15. Out of Scope

- Existing Web／CLI／Lightning RuntimeへのBinding。
- Persistent API／SSE変更／Browser UI／Chat List／Resume／New Chat／Branch UX。
- Client History ImportまたはServer HistoryとのMerge。
- Public Demo／Shared Basic PreviewのPersistent Scope。
- Network／Cloud／Multi-host Database、Encryption at RestおよびExternal Backup。
- Retention／Hard Delete／Purge／Vacuum／Operation Receipt Cleanup／自動削除。
- Full Runtime Recording／Protected Research Capture／Raw Thinkingの保存。
- Generation Contextの無言Truncation／Compaction／自動Summary。
- Component Registry／Switchboard／Research Developer Mode。

## 16. Related Documents

- [Phase 2-A Requirements](phase_2_a_conversation_domain_requirements_ja.md)
- [Phase 2-B Architecture](../architecture/phase_2_b_conversation_persistence_architecture_ja.md)
- [Phase 2-B ADR](../adr/phase_2_b_conversation_persistence_adr_ja.md)
- [Phase 2-B Acceptance／Test Matrix](../operations/phase_2_b_acceptance_matrix_ja.md)
- [Phase 2-B Implementation Handoff](../handoffs/phase_2_b_implementation_handoff_ja.md)
