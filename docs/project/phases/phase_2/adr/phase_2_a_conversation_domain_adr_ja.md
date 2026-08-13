# Phase 2-A Conversation Domain Foundation ADR

```yaml
document_id: phase_2_a_conversation_domain_adr
status: accepted_for_phase_2_a
phase: phase_2
subphase: phase_2_a
language: ja
created_at: 2026-08-12 01:51:52 JST
decision_owner: プロジェクト責任者兼設計統括者役
decision_authority: user_approved_phase_2_a_automation_line
```

## 1. Decision

Phase 2-Aでは、既存Ephemeral Conversation Runtimeを変更せず、新しいPersistent Conversation Domain／Repository Portを独立Packageとして追加する。

```text
Persistent Domain
  -> Phase 2-B Application Mapper
  -> Existing Ephemeral Generation Service
```

Concrete Storage、Persistent Application ServiceおよびWeb接続は後続Subphaseへ延期する。

## 2. Accepted Decisions

### ADR-P2A-001：現行Subphase割当を優先

Phase 2-AはConversation Domain Foundation、Component Registry／SwitchboardはPhase 2-Eとする。Phase 1 Historyの旧割当を現行Scopeへ戻さない。

### ADR-P2A-002：既存v1を変更しない

`/api/v1/chat/stream`と`/api/v1/chat/stop`はPhase 2-A／2-BでEphemeralかつStorage Write 0のまま維持する。Persistent APIはPhase 2-Cで別Versioned Surfaceとして追加する。

### ADR-P2A-003：Transport／Prompt／Persistenceを分離

Transport Message、Model Prompt MessageおよびPersisted Messageを別Contractとする。Current Basic Designのclient-generated `request_id`、`started` Eventおよびclient `system` roleはAs-built Wire Contractと衝突するため、v1互換正本をserver-generated `request_id`、`start` Event、client roles `user／assistant`へ訂正する。

### ADR-P2A-004：Identityを非互換化

Scope、Conversation、Session、Turn、Message、Storage OperationおよびGeneration Requestを別Identityとする。既存`ConversationGenerationSession`は一回のGeneration Runtimeであり、Persistent Sessionへ流用しない。

### ADR-P2A-005：1 Turn = 1 User + 0/1 Assistant

Completed TurnをTerminalとし、Retry／Regenerateは新Turnを作る。`parent_turn_id`と`derived_from_turn_id`でBranchを表し、元Turn／Messageを上書きしない。

### ADR-P2A-006：DisplayとGeneration Projectionを分離

Cancelled／Failed／Interrupted TurnはEvidenceとして保存可能だが、Generation Contextへ入れない。Generation Contextは選択Branch上のCompleted Turnと現在のPending Userだけから構築する。

### ADR-P2A-007：Store-owned RevisionとOperation Idempotency

Domain SnapshotはStorage Revisionを持たない。StoreがAtomic CommitごとにRevisionを増分し、`expected_revision`と`operation_id`でCAS／冪等性を保証する。Domain Schema、Storage Format、Storage Revision、Migration PlanおよびAPI Versionを兼用しない。

### ADR-P2A-008：Terminal Commit後にCompleted通知

Persistent ModeではCanonical Assistant、Terminal TurnおよびConversation HeadのAtomic Commit成功後にだけClientへCompletedを通知する。保存失敗時の無言Ephemeral Fallbackを禁止する。

### ADR-P2A-009：未知／破損RecordをFail-closed

Unknown Schema、CorruptionおよびMigration Incompleteを通常Read／Writeへ通さない。暗黙Migration、自動修復、部分復元およびBlind Retryを禁止する。

### ADR-P2A-010：Public／Shared PreviewのPersistenceを既定拒否

Credentialless Public Demoおよび共有Basic Previewには安全な個別Conversation Scopeがない。Persistent AdapterをBindingせず、Chat List／Resume／Storage Writeを0とする。Identityの推測困難性を認可の代替にしない。

### ADR-P2A-011：初期Hard Deleteを採用しない

Retention、Restore、Auditおよび法的削除Policyが未確定であるため、Phase 2-Aでは`active／archived`だけを定義する。Hard Delete／Tombstone／Purgeは別Decisionとする。

## 3. Rejected Alternatives

- 既存`ConversationMessage`へPersistent Fieldを追加する。
- Client full historyとServer historyを黙ってMergeする。
- `request_id`をTurn／Sessionへ流用する。
- 一つのTurnへ複数Assistantを追加する。
- TimestampだけでBranch／Orderingを復元する。
- DomainへSQLite／JSON／File Layoutを埋め込む。
- Read時に自動Migration／自動修復する。
- Storage Failure時に保存成功としてEphemeral継続する。
- Public DemoへGlobal Conversation Listを公開する。

## 4. Consequences

### Positive

- Phase 1 Runtimeを壊さず、永続化の正本境界をTestできる。
- Model、Web、Storageを交換可能に維持できる。
- Retry／Regenerate／Resumeを後付けしても原本上書きが不要である。
- Storage失敗、競合、CrashおよびMigrationを再現可能に扱える。
- Thinking／Hidden Original／Promptの誤保存を型で抑制できる。

### Cost

- Phase 2-BにPersistent Orchestrator、Mapper、AdapterおよびCrash Recovery実装が必要となる。
- Scope／Ownership未確定ProfileではPersistenceを提供できない。
- Persistent API／UIはPhase 2-Cまで利用できない。

## 5. Supersession／Reopen

本ADRを再Openできるのは、新Evidence、Integrity mismatch、上位規則Conflictまたはユーザーの明示指示がある場合だけである。実装都合だけで既存v1 Wire Contract、Privacy BoundaryまたはPublic Zero-writeを緩和しない。

## 6. Related Documents

- [Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [Execution Plan](../operations/phase_2_a_execution_plan_ja.md)
- [Implementation Handoff](../handoffs/phase_2_a_implementation_handoff_ja.md)
