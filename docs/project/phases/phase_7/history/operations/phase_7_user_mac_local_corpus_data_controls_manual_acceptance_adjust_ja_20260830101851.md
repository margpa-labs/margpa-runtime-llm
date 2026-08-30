# Phase 7 User Mac Local Corpus／Data Controls Manual Acceptance — ADJUST

```yaml
document_id: phase_7_user_mac_local_corpus_data_controls_manual_acceptance_adjust_20260830101851
document_type: user_mac_manual_acceptance_evidence_and_controller_disposition
document_state: current_decision
language: ja
created_at: 2026-08-30 10:18:51 JST
authority_owner: Nazuna Research
phase: phase_7
verdict: ADJUST
phase_7_closure: blocked_by_bounded_rework
manual_items_total: 10
manual_items_pass: 9
manual_items_fail: 1
new_findings: 3
```

## 1. 目的

本書は、Controller Revision Manual Test Sheetに対してUser Mac実画面で得られた結果を、表示文言、会話差分、Source照合およびClosure判定とともに固定する。

正本Manual Test Sheet:

`docs/project/phases/phase_7/history/operations/phase_7_local_corpus_data_controls_user_manual_test_sheet_controller_revision_ja_20260829230354.md`

本書は過去Turn、過去CitationまたはLocal Corpus Revisionを更新しない。User実画面で成立しなかったP7-ACC-012をPASSへ捏造せず、Controllerの以前のComplete Candidate判定をADJUSTへ戻す。

## 2. User Manual結果

### 2.1 RAG OFF

```text
結果: PASS
RAG OFFでChatは動作し、Local Citationは付かなかった。
```

### 2.2 Local Document登録

```text
結果: PASS
表示: MARGPA Manual Probe 7 / rev 1 / 41 chars
表示: Documentを登録しました。
```

登録した固有Factは次の検証コードである。

```text
Nazuna Probe Orion: CEDAR-7319
```

### 2.3 Local Fact Grounding

```text
結果: PASS
質問: Nazuna Probe Orionの検証コードは？
回答: Nazuna Probe Orionの検証コードはCEDAR-7319です。
```

一般Web検索は要求または実行されなかった。

### 2.4 Citation Identity

```text
結果: FAIL
Local Source表示:
  local-corpus/margpa-manual-probe-7-ac94c08e.md
Project Docs表示:
  docs/project/phases/phase_1/handoffs/phase_1_handoffs_ja.md
  docs/project/phases/phase_1/requirements/phase_1_requirements_ja.md
```

Local CorpusとProject DocsはPath Prefixで区別できた。一方、画面にはChunk IdentityまたはDocument Digestに相当する識別値が表示されなかった。

Source限定照合では、内部正本`DocumentationCitation`に`chunk_id`、`document_sha512`、`retrieval_score`、`selected_order`が存在する。しかし、`PersistentCitationResponse`、Persistent SSE Projection、Frontend `Citation`型および`CitationsSection`がChunk IDとDocument Digestを投影していない。

したがって、次の既存Claimは誤りである。

```text
P7-ACC-012: PASS
Citation Identity完備
```

Correct Disposition:

```text
P7-ACC-012: FAIL / BOUNDED REWORK REQUIRED
```

### 2.5 Reload／別Tab／Server Restart

```text
結果: PASS
```

Conversation本文、CitationおよびLocal Corpus Documentは、Reload、別Tab、Server Restart後にも復元された。

ただしServer Restart時、非Archive Conversationでも手動の「再開」操作が必要である。これはCitation Persistence Failureではないが、別Finding P7-CODEX-009として本差分で修正する。

### 2.6 Document更新

```text
結果: PASS_WITH_FRESHNESS_OBSERVATION
rev 1: CEDAR-7319
更新1: CEDAR-8420
更新2: CEDAR-9847
```

新規Chatでは更新直後からCEDAR-8420を回答した。同一Chatでは一度旧値を回答した後、再質問時にCEDAR-8420へ更新された。その後CEDAR-9847への更新は同一Chatでも回答へ反映された。

Index Revision更新自体は成立している。最初の旧値は単純なIndex反映遅延とは確定せず、Conversation History内の旧回答をMain Modelが優先した可能性を含む。

### 2.7 Document削除

```text
結果: CORE_DELETE_PASS / CURRENT_TURN_GROUNDING_FAIL
```

削除後の新規Chatでは次の回答となり、削除済みLocal DocumentがCurrent検索から外れたことを確認した。

```text
参照資料には「Nazuna Probe Orionの検証コード」に関する明示的な情報は含まれていません。
```

過去Turnと過去Citationは更新されず保持された。これは正しい。

一方、削除前から継続している同一Chatでは、新しいTurnでもCEDAR-9847を回答した。その新Turnに表示されたCitationは無関係なPhase 1 Project Docsだけで、回答を支持するCurrent Local Citationは存在しなかった。

正しいContractは次である。

```text
過去Turn:
  当時のCitation／Revision／Digestを永久に固定する。

新しいTurn:
  Current Corpusだけを再検索する。
  更新済みなら最新Revisionを使用する。
  削除済みまたはCurrent Evidence不足なら「現在の根拠なし」へ収束する。
  過去Historyの旧FactをCurrent Evidenceとして扱わない。
```

過去Citationを最新Revisionへ書き換えてはならない。必要な修正はHistorical EvidenceのMutationではなく、Current TurnのFreshness／Grounding制御である。Judgeは補助防衛線であり、主責任はRAG Retrieval／Context／Generation Gateにある。

### 2.8 Consent Default OFF

```text
結果: PASS
```

用途別Consentは全て既定OFFだった。

### 2.9 Consent独立保存／Reset

```text
結果: PASS
```

個別切替、複数切替、Browser Reload後の保持およびResetによる全OFF復帰を確認した。

### 2.10 False Capability Successなし

```text
結果: PASS
```

画面はRetention事実と用途別Consentを表示した。Full Export／一括Delete／実Web完成を実行可能または完了済みとするButton／成功表示はなかった。

`将来のTraining用Export`はConsent項目であり、Export実行機能のClaimではない。P7-ACC-025のFull Export／一括Delete未実装PARTIALは引き続き保持する。

## 3. Finding

### P7-CODEX-007 — Citation Chunk／Digest Projection Gap

```yaml
severity: major_acceptance_gap
priority: P0_phase_7_bounded_rework
closure_blocker: true
impact_scope: live_and_persistent_citation_projection_frontend
```

内部Citation EvidenceにはChunk ID／Document Digestがあるが、API／SSE／Frontend表示で落ちる。P7-ACC-012の直接Failureである。

### P7-CODEX-008 — Current Turn Freshness／Unsupported Historical Reuse

```yaml
severity: major_grounding_gap
priority: P0_phase_7_bounded_rework
closure_blocker: true
impact_scope: current_rag_retrieval_context_generation
```

同一Chatで削除済みFactをConversation Historyから再利用し、無関係なCurrent Citationを伴う回答を生成できる。過去Evidenceは固定したまま、Current Turnを最新CorpusまたはNo Current Evidenceへ収束させる必要がある。

### P7-CODEX-009 — Manual Resume Required after Restart／Unarchive

```yaml
severity: moderate_user_flow
priority: P0_user_requested_bounded_rework
closure_blocker: true_by_user_decision
impact_scope: persistent_conversation_session_activation
```

Server Restart後、Active ConversationのSessionはInterruptedとなり、手動Resumeが必要になる。Archive解除後もConversation StateはActiveへ戻るがActive Sessionが作られない。起動時全件Resumeは避け、選択／最初の送信／Unarchive時の遅延自動Resumeで修正する。

## 4. Bounded Rework停止線

現在Phaseで修正するのはP7-CODEX-007〜009だけである。

次は混入させない。

- 過去Turn／過去CitationのRevision書換え。
- Embedding／Vector DB本格化。
- Full Export／一括Delete。
- 一般Web検索／自動検索／Public Provider統合。
- Phase 8 Manual URL Fetch実装。
- Phase 6 Governance Debt。
- 製品化Hardeningを目的とする追加Finding探索。

## 5. Controller判定

```text
Manual Items: PASS 9 / FAIL 1
Core Delete Current Exclusion: PASS
Current Turn Freshness: FAIL
Open Current Critical: 0 known
Open Current Major／MVP Blocker: 2
User-requested Closure Rework: 1
Phase 7 Closure: NOT READY
Verdict: ADJUST / BOUNDED REWORK REQUIRED
```

Exact Next Actionは、P7-CODEX-007〜009だけを実装・検証し、Userへ限定再確認を返すことである。
