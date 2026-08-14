# Phase 2-E Persistent RAG Citation Evidence Reservation

```yaml
document_id: phase_2_e_persistent_rag_citation_evidence_reservation_20260814215110
status: accepted_reservation
phase: phase_2
subphase: phase_2_e
from_role: User
to_role: プロジェクト責任者兼設計統括者役
created_at: 2026-08-14 21:51:10 JST
implementation_started: false
git_mutation: pending_authorized_checkpoint
```

## 1. Observation

Phase 2-CのManual Acceptance Rework後、Documentation RAGの引用元は、同一Browser Page内のCanonical Detail再描画で維持される。一方、Browser ReloadでPage Memoryが初期化されると引用表示は消失する。Server Restartまたは保存済みChatの後日再表示でも同様に復元できない。

これはConversation本文の消失またはRetrieval Failureではない。現行Phase 2-CでCitationはSafe SSE ProjectionとPage Memoryに限定し、Persistent Message Schemaへ保存しない設計境界である。

## 2. Phase 2-E Reservation

Phase 2-E `Runtime Composition Switchboard／Documentation RAG Follow-up`で、Persistent ConversationとCitation Evidenceの永続関連付けを再設計する。完了後は、少なくとも次の再表示でSafe Citation Projectionを復元できることを目標とする。

- Browser Reload後。
- Server Restart後。
- 保存済みConversationをChat Listから再度開いた後。
- Retry／Regenerate／Branch Select後のCanonical Turn再表示。

## 3. Design Boundary

Phase 2-EのExact Designは未Freezeであるが、少なくとも次の境界を維持する。

- Citation EvidenceをAssistant Message本文へ暗黙に埋め込まない。
- Conversation Scope、Conversation ID、Turn IDおよびCanonical Assistant Resultとの関係を明示する。
- Project-relative Path、Heading、Source Digest、Corpus／Index RevisionおよびSafe Retrieval MetadataをTyped Allowlistで扱う。
- Absolute Local Path、Secret、Credential、Raw Thinking、System Prompt、Tool内部情報、Hidden Originalまたは未確定Partial OutputをCitation Evidenceとして保存しない。
- Assistant CompletionとCitation Evidenceの整合、Crash Recovery、Schema Version、Migration、RollbackおよびCorruption時のFail-closedを明示する。
- RAG OFF、Retrieval 0件、Unavailable、WarningおよびCitation Persistence Failureを黙って同一状態に潰さない。
- Public／Basic PreviewへのPersistence Bindingを本Reservationだけで有効化しない。
- Phase 7 Full RAGと差替え可能なEvidence Portを維持する。

## 4. Current Accepted Boundary

Phase 2-A～2-Dは`COMPLETE／USER ACCEPTED`のままである。Current RuntimeのAccepted Boundaryは、引用元を同一Browser Page内のCanonical Detail再描画まで維持することである。Browser Reload／Server Restartを越えるCitation復元はPhase 2-Eの未実装要件であり、Phase 2-A～2-DのCompletionを再Openしない。

## 5. Gate

本文書は後続要件のReservationである。Phase 2-EのDesign、Task作成、Source Mutation、Storage MigrationまたはRuntime Bindingを開始するAuthorityは生成しない。

## 6. Related Evidence

- [Phase 2-B～2-D Manual Acceptance Rework](phase_2_b_to_d_manual_acceptance_rework_20260814205814.md)
- [Phase 2-A～2-D User Manual Acceptance](phase_2_a_to_d_user_manual_acceptance_20260814210500.md)
- [Phase 2 Index](../../phase_index_ja.md)
- [Phase 2 Subphase Preplan](../../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Public Roadmap](../../../../../public/roadmap_ja.md)
