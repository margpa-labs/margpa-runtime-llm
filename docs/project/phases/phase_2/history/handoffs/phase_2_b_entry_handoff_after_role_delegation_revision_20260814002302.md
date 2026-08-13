# Phase 2-B Conversation Persistence／Lifecycle Entry Handoff

```yaml
handoff_id: phase_2_b_entry_handoff
status: ready_after_phase_2_a_user_acceptance_with_independent_role_chain_required
created_at: 2026-08-12 02:10:52 JST
updated_at: 2026-08-14 00:23:01 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
start_authority: user_only
```

## 1. Entry Condition

Phase 2-AのTechnical Validationは完了している。Phase 2-Bは、Phase 2-A User Final Acceptance、区切りBackupおよびユーザーの明示的開始指示後にだけ開始する。

Phase 2-AではControllerが実装責任を兼務したため、独立したPhase Designer／Implementer連鎖は未検証である。Phase 2-Bではこの不足を解消するため、同一Taskが設計、実装および全Reviewを抱えない。

## 2. Frozen Inputs

- [Phase 2-A Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Phase 2-A Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [Phase 2-A ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- `src/margpa_runtime_llm/modules/conversation/domain/`
- `src/margpa_runtime_llm/modules/conversation/ports/`
- Phase 2-A Unit／Contract Tests

## 3. Required Role Delegation Chain

Phase 2-Bは次の段階的責任連鎖で実行する。

```text
プロジェクト責任者兼設計統括者役
  → Phase目標、Authority、到達線、Frozen Input
Phase 2設計担当者役
  → Requirements／Architecture／ADR／Exact Implementation Handoff
Phase 2実装者役
  → Source／Test実装、Target Validation、Status
Phase 2設計担当者役
  → 設計適合Review、Finding、必要な再作業指示、局所Acceptance
プロジェクト責任者兼設計統括者役
  → Cross-Phase／Scope／Evidence／Closure Review、GO／ADJUST／STOP提案
User
  → Human-only GateとFinal Acceptance
```

Role名だけを論理的に付け替えて分業済みと扱わない。Phase 2設計担当者役とPhase 2実装者役は、異なるTask Identityと明示されたAuthority／Docs Scopeを持つ。実装者役はAccepted Design／Handoffの内側を自律実装し、Routine ActionごとにControllerへ確認しない。設計担当者役は実装結果をReviewし、Scope内Findingを実装者役との往復で閉じた後にControllerへ完了報告する。

Controllerがやむを得ず実装を兼務する場合は、理由、対象、代替不能性および独立Review不足をEvidenceへ記録し、そのWork Unitを役割分業型Automationの合格Evidenceに数えない。単一Working Treeへの同時Writeは行わず、Write LeaseをTask間で直列移転する。

## 4. Phase 2-B Scope

- Concrete Local Persistence AdapterとSerialization／Storage Envelope。
- Atomic CAS、Operation Idempotency、Read-your-writes。
- Pending Commit、Terminal Commit、Crash Recovery／Interrupted確定。
- Persistent Application Orchestrator。
- Domain Completed Branchから既存`ConversationGenerationInput`へのMapper。
- Existing Input Limit超過時の明示Policy。
- Explicit Schema Preflight／Migration／Checkpoint／Rollback実装。
- Persistent ProfileのBindingとEphemeral Profileの明示分離。

## 5. Phase 2-B Invariants

- Existing `/api/v1/chat/*`を変更しない。
- Client full historyとRepository historyをMergeしない。
- Model生成中にStorage Transaction／Lockを保持しない。
- Terminal Commit成功前にCompletedを通知しない。
- Storage失敗をEphemeral成功として扱わない。
- Raw Thinking、System／Tool Prompt、RAG Injected Context、Partial DeltaまたはHidden OriginalをMessageへ保存しない。
- Public Demo／Shared Basic Previewは安全な個別Scopeが確定するまでAdapter未Binding／Zero Write。
- Corruption／Unknown Schema／Migration IncompleteはFail-closed。
- Migration後Writeを含むRollbackはHuman Gate。

## 6. Deferred to Phase 2-C

- Separate Versioned Persistent API。
- Chat List／Resume／New Chat。
- Retry／Regenerate／Branch UX。
- Multi-browser UX Conflict表示。

## 7. Required First Actions

1. Project ControllerがPhase 2設計担当者役へ、Frozen Input、到達線、禁止事項およびDocs AuthorityをHandoffする。
2. Phase 2設計担当者役がPhase 2-B Requirements／Architecture／ADRを局所設計する。
3. Phase 2設計担当者役がConcrete Adapter候補を比較し、Domain／Portへ製品前提を逆流させない。
4. Phase 2設計担当者役がPersistence Location、Permission、Backup、Corruption、Multi-process LockおよびMigration FailureをThreat Model化する。
5. Phase 2設計担当者役がExact Adapter／Application／Test Scopeを実装Handoffへ固定する。
6. Phase 2実装者役がAccepted Handoff内だけを実装し、Phase 2-A v1 Zero-write RegressionをAcceptanceへ含める。
7. Phase 2設計担当者役がSource／Test／EvidenceをReviewし、必要な再作業後にControllerへ局所Acceptanceを提出する。
8. Project Controllerが独立してClosure Recommendationを作成し、UserへHuman-only Gateだけを返す。

## 8. Prohibited Assumptions

- Storage RevisionをDomain Schema Versionへ流用できる。
- Conversation IDだけでOwner／Authorizationを確定できる。
- Browser Memoryを自動Migrationできる。
- Full Durable Historyを既存Generation Limitへそのまま渡せる。
- Projection／ListをPrimary Recordとして扱える。
- Timeout後にCommitをBlind Retryできる。
- Controllerが論理Role名を切り替えれば独立Task連鎖を検証済みと扱える。
- Test合格だけでRole Delegation、Handoff往復または独立Reviewも合格したと扱える。

## 9. Validation Baseline

```text
Phase 2-A Target Tests : 49 passed
Conversation／Web      : 107 passed
Full Suite             : 479 passed／3 deselected
Ruff Format／Check     : PASS／130 files
Mypy                   : PASS／130 source files
Existing v1 Mutation   : 0
Concrete Storage I/O   : 0
```
