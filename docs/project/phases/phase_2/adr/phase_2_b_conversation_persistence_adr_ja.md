# Phase 2-B Conversation Persistence／Lifecycle ADR

```yaml
document_id: phase_2_b_conversation_persistence_adr
status: accepted_for_phase_2_b_implementation
phase: phase_2
subphase: phase_2_b
language: ja
created_at: 2026-08-14 JST
decision_owner: Phase 2設計担当者役
decision_authority: project_controller_and_user
```

## 1. Decision

Phase 2-BではPython Standard Library `sqlite3`を最初のLocal Private永続化Adapterとして採用し、Phase 2-A Repository／Maintenance Portの背後へ置く。Adapter、Application Lifecycle、Context MapperおよびCrash Recoveryを追加するが、既存v1 Web、Public DemoおよびShared Basic PreviewへBindingしない。

## 2. Accepted Decisions

### ADR-P2B-001：SQLiteはAdapter内だけに閉じる

ACID、Conditional Update、Unique Operation KeyおよびLocal multi-process Lockを追加Dependencyなしで扱えるためSQLiteを採用する。Domain、Port、API、Scope Identityまたは将来AdapterへSQLite前提を逆流させない。

### ADR-P2B-002：Explicit Root／Scope／Initialization

RootとScopeは呼出元が明示注入する。Import、BuilderおよびSchema InspectionはWrite 0、初期化は専用Operationだけが行う。CWD、Home、Repository RootまたはEnvironmentからの暗黙推定は禁止する。

### ADR-P2B-003：Canonical Snapshot＋Metadata列

Conversation AggregateをCanonical JSON＋SHA-512としてAtomic保存し、CAS／Listに必要なMetadataだけを列として複製する。Read時はDigest、Version、Domain Validatorおよび列との一致を全て検証する。

### ADR-P2B-004：CASとOperation Receiptを一Transactionにする

Conversation Revision更新とOperation Receiptを同じTransactionで確定する。同じOperation ID＋Commandは同じReceipt、異なるCommandはConflictとする。Unknown OutcomeはReceipt照合へ進み、Blind Retryしない。

### ADR-P2B-005：生成中はStorage Resourceを保持しない

Pending Commit、Generating CommitおよびTerminal Commitを分離し、Model生成はTransaction／Connection／File Lockの外で行う。Terminal Commit後だけTerminal Eventを公開する。

### ADR-P2B-006：Crash残存StateをInterruptedへ収束させる

Startup GateでPending／Generating TurnとActive SessionをInterruptedへCAS Commitする。Partial／Assistant／Error本文を追加せず、Recovery未完了でServiceをReadyにしない。

### ADR-P2B-007：Migrationは明示・Staging・Atomic Cutover

Read時Migration、自動修復およびIn-place変換を禁止する。Production Legacy Stepは0から開始し、Migration EngineはTest FixtureでCheckpoint、Marker、Staging全件検証、Atomic CutoverおよびRollback拒否条件を実証する。

### ADR-P2B-008：Context超過は明示拒否

Completed Branch＋Pending Userを既存入力へ写像する。既存上限超過では生成Call 0で失敗し、無言Truncate、暗黙Summaryまたは永続Record変更を行わない。

### ADR-P2B-009：PersistenceとRecordingを分離

Canonical Conversation保存はPersistent機能、研究用記録は別Capabilityとする。Phase 2-B Recordingは未Binding／OFF／Call 0であり、通常StoreにThinking、Prompt、RAG Context、Partial、Hidden OriginalまたはSecretを保存しない。

### ADR-P2B-010：既存v1／Public／BasicはZero-binding

`/api/v1/chat/*`、Public DemoおよびShared Basic PreviewはAdapter未Binding／Storage Write 0を維持する。Persistent API／UIはPhase 2-Cの別Versioned Surfaceで追加する。

## 3. Rejected Alternatives

- JSON Fileを会話ごとに上書きし、CASをProcess内Lockだけで表現する。
- SQLite型／Path／RevisionをDomain Modelへ追加する。
- Generation全体を一つのDB Transactionで囲む。
- Commit Timeout後に新Operation IDで再送する。
- Unknown／Corrupt RecordをSkipまたは自動修復する。
- Browser HistoryとServer Storeを自動Mergeする。
- Public／BasicへGlobalまたはCredential共有ScopeをBindingする。
- Recording `full`をPersistenceと同時にDefault ONにする。
- Raw Thinking／Internal Promptを通常Conversation Recordへ保存する。

## 4. Consequences

### Positive

- Phase 1互換を壊さず、Local Durable Conversationを差替可能に実装できる。
- Lost Update、Response喪失、Crash、Schema不一致およびMigration Failureを決定的にTestできる。
- Phase 2-CはApplication／Adapterを利用しつつ、独立API／UI境界を設計できる。

### Cost／Limit

- SQLite本体はEncryption at RestやMulti-host共有を提供しない。それらが必須なProfileにはBindingできない。
- Operation Receipt、CheckpointおよびMigration MarkerのRetentionは後続Policyまで自動削除しない。
- Phase 2-B完了時点ではWebから永続Conversationを利用できない。

## 5. Reopen Condition

新Evidence、Integrity mismatch、上位規則Conflictまたはユーザーの明示指示だけが本ADRを再Openできる。実装都合だけでv1 Zero-write、Public／Basic Zero-binding、Fail-closedまたはSensitive Data禁止を緩和しない。

## 6. Related Documents

- [Requirements](../requirements/phase_2_b_conversation_persistence_requirements_ja.md)
- [Architecture](../architecture/phase_2_b_conversation_persistence_architecture_ja.md)
- [Implementation Handoff](../handoffs/phase_2_b_implementation_handoff_ja.md)
- [Acceptance Matrix](../operations/phase_2_b_acceptance_matrix_ja.md)
