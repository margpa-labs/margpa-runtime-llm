# Phase 7 Minimal Final Closure

```yaml
document_id: phase_7_minimal_final_closure_20260830191806
document_state: complete_accepted_closed
phase: phase_7
language: ja
created_at: 2026-08-30 19:18:06 JST
authority_owner: Nazuna Research
closure_style: poc_mvp_minimal
phase_8_transition: ready_not_started
```

## 1. Closure Decision

Phase 7を`COMPLETE／ACCEPTED／CLOSED`とする。これはLocal Knowledge RuntimeとData GovernanceのPoC／MVP Acceptanceであり、General Web Search、Model回答品質またはEnterprise RAGの完成ではない。

```text
Local Corpus CRUD／Revision／Digest       : PASS
Current Local Evidence／Citation          : PASS
NO_HIT Persistent Citation                : PASS
Reload／Restart／Two-tab Continuity        : PASS
Archive解除後Manual Resume不要             : PASS
Data Controls／Purpose Consent             : PASS
User Mac Final Manual Acceptance           : PASS
General Web Search／Automatic Search        : DEFERRED TO PHASE 11+
Phase 6 Semantic／Judge／Guard Debt         : UNRESOLVED／PHASE 9
```

## 2. Accepted Capability

- Local Corpusの登録、更新、Soft Delete、Revision、Digestおよび永続化。
- Current Retrieval、BM25 Baseline、Context InjectionおよびLocal／Project Docs Source分離。
- CitationのTitle／Heading、実保存Path、Chunk ID、Document Digest、Copyおよび永続再投影。
- Document更新後は新TurnでCurrent Revisionを利用し、過去Turn Citationを改変しない。
- 削除後はCurrent検索から外し、RAG ON＋NO_HITで根拠なし表示とCitation 0件Evidenceを保持する。
- Data ControlsのRetention事実と用途別Consent、全Consent既定OFF、Reset。
- Server Restart／Reload／別Tab／Unarchive後のConversation継続とManual Resume不要。
- Web Search／Fetch Port、Fixture、SSRF／Redirect／Size／Timeout／Content Type／Prompt Injection／Secret様Query検査のScaffold。

## 3. Manual Evidence

[User Mac Final RAG／Citation／Context Freshness Manual Acceptance](phase_7_user_mac_final_rag_citation_context_freshness_manual_acceptance_ja_20260830190930.md)を正本とする。

最終Manualでは、Local Corpus Probe 10／11の登録・更新・削除、Title、実保存Path、Chunk ID、Digest、NO_HIT Citation、Project Docs Citation、Reload、Restart、別Tabを確認した。RAG OFF時に過去Conversation Context由来の古いFactが再出力され得る一方、RAG ONはCurrent Corpus不在を正しくNO_HITへ収束した。

## 4. Formal Deferral／Known Non-blocker

- 過去Conversation Context由来の古いFact再出力：Phase 9 Semantic Governance／Judge／Repair。
- Qwenの間欠的言語Drift：Phase 9 Model／Language Governance。
- `RAG ON＋NO_HIT`時にModelを呼ばず固定言語回答へ収束するStrict方式：保留案。
- Local Corpus更新／削除ToastのSettings再Open後残留：UI Minor。
- Buffer後一括表示：Phase 9 Progressive Presentation原則。
- General／Automatic Web Search、Hostile-site Sandbox：Phase 11以降。
- Embedding実Adapter、全Export／一括Delete／完全削除：後続Scope。

これらはStable未解決Registryへ保持し、Phase 7 Closure Blockerへ昇格しない。

## 5. Claim Boundary

次を主張しない。

- 外部Web検索がChatへ自動注入される。
- URLを一般に安全に読める。
- RAGが過去Conversation Factを常に訂正する。
- Qwenの事実性または回答言語が保証される。
- Embedding／Vector Store、Training、Data Export／Deleteが完成した。

## 6. Verification Evidence

- Closure境界Canonical：Backend 1952 passed／7 deselected、Mypy 526 files、Ruff Check／Format PASS、Frontend 29 files／268 tests、Typecheck／Lint／Build PASS、56 modules。
- 最初の`uv run`はSandbox外のUser Cache参照を実行前に拒否されたためCanonical Evidenceへ数えず、Project `.venv`の同一Toolchainを直接実行して上記結果を確定した。
- P7-RW5-E：Frontend Build PASS、56 modules、配信Static Artifact更新。
- User Mac Final Manual：指定5領域PASS。
- 本Closure TurnではPhase 8 Source実装またはUser runtime_data操作を行わない。

`frontend/.build_tmp/`は配信物ではないCompile Cacheであり、Canonical Build後にTask-owned Tempとして削除した。Source、配信Static ArtifactまたはUser runtime_dataは削除していない。

## 7. Successor State

```text
Phase 7                    : COMPLETE／ACCEPTED／CLOSED
Phase 8 Design             : ACCEPTED／FROZEN
Phase 8 State              : READY
Phase 8 Implementation     : NOT STARTED
Phase 8 External Authority : NOT GRANTED
Backup                     : USER WILL PERFORM AFTER PUSH
```
