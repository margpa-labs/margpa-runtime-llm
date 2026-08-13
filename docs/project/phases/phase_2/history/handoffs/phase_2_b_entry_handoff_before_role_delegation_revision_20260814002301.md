# Phase 2-B Conversation Persistence／Lifecycle Entry Handoff

```yaml
handoff_id: phase_2_b_entry_handoff
status: ready_after_phase_2_a_user_acceptance
created_at: 2026-08-12 02:10:52 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: future_phase_2_designer_and_implementer
start_authority: user_only
```

## 1. Entry Condition

Phase 2-AのTechnical Validationは完了している。Phase 2-Bは、Phase 2-A User Final Acceptance、区切りBackupおよびユーザーの明示的開始指示後にだけ開始する。

## 2. Frozen Inputs

- [Phase 2-A Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Phase 2-A Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [Phase 2-A ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- `src/margpa_runtime_llm/modules/conversation/domain/`
- `src/margpa_runtime_llm/modules/conversation/ports/`
- Phase 2-A Unit／Contract Tests

## 3. Phase 2-B Scope

- Concrete Local Persistence AdapterとSerialization／Storage Envelope。
- Atomic CAS、Operation Idempotency、Read-your-writes。
- Pending Commit、Terminal Commit、Crash Recovery／Interrupted確定。
- Persistent Application Orchestrator。
- Domain Completed Branchから既存`ConversationGenerationInput`へのMapper。
- Existing Input Limit超過時の明示Policy。
- Explicit Schema Preflight／Migration／Checkpoint／Rollback実装。
- Persistent ProfileのBindingとEphemeral Profileの明示分離。

## 4. Phase 2-B Invariants

- Existing `/api/v1/chat/*`を変更しない。
- Client full historyとRepository historyをMergeしない。
- Model生成中にStorage Transaction／Lockを保持しない。
- Terminal Commit成功前にCompletedを通知しない。
- Storage失敗をEphemeral成功として扱わない。
- Raw Thinking、System／Tool Prompt、RAG Injected Context、Partial DeltaまたはHidden OriginalをMessageへ保存しない。
- Public Demo／Shared Basic Previewは安全な個別Scopeが確定するまでAdapter未Binding／Zero Write。
- Corruption／Unknown Schema／Migration IncompleteはFail-closed。
- Migration後Writeを含むRollbackはHuman Gate。

## 5. Deferred to Phase 2-C

- Separate Versioned Persistent API。
- Chat List／Resume／New Chat。
- Retry／Regenerate／Branch UX。
- Multi-browser UX Conflict表示。

## 6. Required First Actions

1. Phase 2-B Requirements／Architecture／ADRを局所設計する。
2. Concrete Adapter候補を比較し、Domain／Portへ製品前提を逆流させない。
3. Persistence Location、Permission、Backup、Corruption、Multi-process LockおよびMigration FailureをThreat Model化する。
4. Exact Adapter／Application／Test Scopeを承認可能なEnvelopeへ固定する。
5. Phase 2-A v1 Zero-write RegressionをAcceptanceへ含める。

## 7. Prohibited Assumptions

- Storage RevisionをDomain Schema Versionへ流用できる。
- Conversation IDだけでOwner／Authorizationを確定できる。
- Browser Memoryを自動Migrationできる。
- Full Durable Historyを既存Generation Limitへそのまま渡せる。
- Projection／ListをPrimary Recordとして扱える。
- Timeout後にCommitをBlind Retryできる。

## 8. Validation Baseline

```text
Phase 2-A Target Tests : 49 passed
Conversation／Web      : 107 passed
Full Suite             : 479 passed／3 deselected
Ruff Format／Check     : PASS／130 files
Mypy                   : PASS／130 source files
Existing v1 Mutation   : 0
Concrete Storage I/O   : 0
```
