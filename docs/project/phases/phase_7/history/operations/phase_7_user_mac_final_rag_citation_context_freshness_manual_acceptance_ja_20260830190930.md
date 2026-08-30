---
document_id: phase_7_user_mac_final_rag_citation_context_freshness_manual_acceptance_20260830190930
document_type: user_mac_manual_acceptance_evidence
document_state: final
language: ja
recorded_at: 2026-08-30 19:09:30 JST
phase: phase_7
authority_owner: Nazuna Research
executor: user
controller: Codexプロジェクト責任者兼設計統括者役
result: pass_with_deferred_non_blockers
---

# Phase 7 User Mac最終RAG／Citation／Context Freshness Manual Acceptance

## 1. 結論

Phase 7のLocal Corpus、RAG Current Retrieval、Citation Identity、NO_HIT、Persistence、Reload、Restart、
別TabおよびProject Docs CitationはUser Mac実画面でPASSした。

削除済みLocal Corpusの旧FactがRAG OFF時に再出力された現象は、Current Retrievalの残留ではなく、
過去Conversation Contextからの再生成である。RAG ONでは同じ質問がNO_HITへ正しく収束した。

```text
Phase 7 RAG Manual Acceptance : PASS
Phase 7 Closure               : ALLOWED
Deferred UI／Model／Governance: RECORDED / NON-BLOCKING
```

## 2. Local Corpus登録／更新／Citation Identity

同一Conversationで次を確認した。

### 2.1 Probe 10

```text
Title: MARGPA Manual Probe 10
Revision: 1
Content: Nazuna Probe Orionの検証コードは CEDAR-153である。
Answer: Nazuna Probe Orionの検証コードはCEDAR-153です。

Source: Local Corpus
Title: MARGPA Manual Probe 10
Path: runtime_data/persistent/mac-local-primary/local_corpus/documents.json
Chunk ID:
8ece0173f80efe3316b984a1fd864ce62be6ca6d1a0c11edd05413985492f69a629095f39f0ee5c1074db0eab7d37ed5eba2e4c862d8d64e596b2c406c4bf5e3
Document Digest:
90b6b7f92e333bffaa7ca877e2aeb8dbc6fec058de90a8b9072c67e0e0375df6f533748871b533bfa0e16081c36fe5fe847acf0810323769636b0a5f7b9f5320
```

### 2.2 Probe 11へ更新

```text
Title: MARGPA Manual Probe 11
Revision: 2
Content: Nazuna Probe Orionの検証コードは CEDAR-953である。
Answer: Nazuna Probe Orionの検証コードはCEDAR-953です。

Source: Local Corpus
Title: MARGPA Manual Probe 11
Path: runtime_data/persistent/mac-local-primary/local_corpus/documents.json
Chunk ID:
a58150aa0eb7ec526da2152fd966a9c5c614cdf1b81a6ecaec3f8ba8db00722ab865f542658eedd4f0bd4009f70dd97592a96a8af27c379aa0330251ee6ff670
Document Digest:
f5cc5efe2d0e3061739a99feae3be5210d75ce77e6fe30401fe2b8823fe6d4aac3ff8bf7e966f7dd1dd60401210e04c6a9a5f83bcdf3215cfa8e1efeb46a7079
```

Path、Chunk ID、Document DigestのCopy結果は完全値と一致し、更新後はTitle、Chunk ID、Digestおよび
回答が新Revisionへ変化した。過去Turnは書き換えられていない。

## 3. 削除後NO_HIT

Local Corpus削除後、RAG ONで同じ質問を行い、次へ収束した。

```text
現在の情報源／Project Docsでは具体的な検証コードを確認できない旨の日本語回答

参照文書
参照対象のDocsから対応する根拠を取得できませんでした。
```

NO_HIT Citationは一瞬で消えず、回答下部へ永続表示された。Reload、Server Restart、別Tabで行った
内容の元Tabへの反映も成立した。

## 4. Project Docs Citation

`MARGPA Runtime LLMとは？`に対し、Project Docs Citationで次を確認した。

- `Source: Project Docs`。
- `Heading`。
- 実Project Path。
- Chunk ID。
- Document Digest。
- Copy操作。

Local Corpusは`Title`、Project Docsは`Heading`を使用し、Source Classごとの表示契約が成立した。

## 5. ロシア語出力の切り分け

削除後のNO_HIT質問で一度、Qwenがロシア語回答を生成した。同じ条件で後から再実行すると日本語回答が
生成された。回答言語設定、RAG StateまたはCitation永続化が常にロシア語へ固定されたEvidenceはない。

現時点の分類は次とする。

```text
Likely Cause    : Qwenの一時的な言語遵守逸脱／Model出力揺れ
RAG Failure     : NOT SUPPORTED BY EVIDENCE
Phase 7 Blocker : NO
Future Target   : Model／Language Governance／Semantic Judge
```

「Qwenだけが原因」と完全断定はしないが、同一機能経路で日本語へ戻ったため、Phase 7 RAGの構造的不具合
としては扱わない。

## 6. 削除済みFactとConversation Contextの切り分け

Local Corpus削除後、同一Conversationで次を順番に実行した。

```text
1. Project Docs参照 OFF
   質問: Nazuna Probe Orionの検証コードは？
   回答: CEDAR-153

2. Project Docs参照 ON
   同じ質問
   回答: 現在の情報源では確認できない
   Citation: 参照対象のDocsから対応する根拠を取得できませんでした。

3. Project Docs参照 OFF
   同じ質問
   回答: 現在の情報源では確認できない
```

この順序は次を示す。

```text
RAG OFF 1回目
→ 過去Conversation内のCEDAR-153をModelが再利用

RAG ON
→ Current Corpusを再検索
→ 削除済みDocumentはHitしない
→ NO_HIT Boundaryが現在の根拠なしへ収束

RAG OFF 2回目
→ 直前の「現在の根拠なし」回答もConversation Contextへ入ったため、その回答傾向を維持
```

したがって、削除済みDocumentがCurrent RAG Indexへ残っているEvidenceではない。過去TurnとCitationを
改竄しない要件も成立している。

## 7. Governanceによる改善余地

過去Conversation Contextから古いFactが再出力される現象はPhase 7 RAGの失敗ではないが、Phase 9の
Semantic Governance／Judge／Repair再整備で改善価値が高い。

理想経路は次である。

```text
過去TurnのFact＋Local Corpus Citation／Revision／Digest
→ Current Source RegistryでActive／Updated／Deletedを判定
→ Historical Source由来Factをstale_evidenceとして分類
→ Main Governance／Semantic GD／JudgeがCurrent Authorityとの不一致を評価
→ Current Corpus再検索
→ Repair／Rejudge
→ 修復回答またはSafe Fallback
```

RAG ONではCurrent Evidenceと直接比較できる。RAG OFFでも、過去回答にCitation、RevisionおよびDigestが
保存されていれば、そのSourceが現在削除済みまたは更新済みであることを検出できる。

ただしRAG OFFで全Conversation Factを遮断すると通常会話を壊すため、対象は`削除／更新済みSourceに
由来すると追跡できるFact`へ限定する。Strict NO_HIT方式と組み合わせれば、根拠なし時の古いFact再出力を
さらに堅く抑制できる。

## 8. Deferred Non-blockers

### 8.1 Operation Message残留

`Documentを更新しました。`および`Documentを削除しました。`が設定画面を閉じても消えない。
機能、DataまたはCitationは正しいため超軽度UI Findingとして延期する。

### 8.2 Buffered／一括表示

NO_HIT等の一部回答がStreamingされず、一括表示される。将来は原則として、待機中に無表示とせず、
回答または検証StateをBlock単位のProgressive表示へする。単純な一括表示をDefault UXにしない。

### 8.3 Model回答品質

Qwenのロシア語逸脱、過去Contextの再利用およびProject Docsからの不正確な自己説明は、Phase 9の
Semantic Governance／Judge／RepairおよびModel評価候補として保持する。

## 9. Final Disposition

```text
Local Corpus CRUD                 : PASS
Current Retrieval                 : PASS
Update／Delete Freshness           : PASS
Historical Immutability           : PASS
Citation Identity／Copy            : PASS
NO_HIT Presentation／Persistence   : PASS
Reload／Restart／Two-tab Continuity : PASS
Project Docs Citation             : PASS
Data Controls                     : PREVIOUSLY PASS
Phase 7 MVP Closure               : ALLOWED
```

