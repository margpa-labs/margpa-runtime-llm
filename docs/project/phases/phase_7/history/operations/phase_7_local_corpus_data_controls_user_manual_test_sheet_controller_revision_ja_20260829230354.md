# Phase 7 Local Corpus／Data Controls — User Manual Test Sheet（Controller Revision）

```yaml
document_id: phase_7_local_corpus_data_controls_user_manual_test_sheet_controller_revision_20260829230354
document_type: user_manual_test_sheet_controller_revision
document_state: current
language: ja
created_at: 2026-08-29 23:03:54 JST
authority_owner: Nazuna Research
supersedes_by_reference:
  - phase_7_local_corpus_data_controls_user_manual_test_sheet_ja_20260829225900.md
execution_authority: user_only
```

## 1. 訂正理由

Claude Candidateには、次の2点の手順上のズレがあった。

1. Documentation RAGのRetrievalはChat Request内部で実行されるため、Browser DevToolsで独立したRetrieval API Requestの不在を確認する手順は、`Retrieval Call 0`の直接Evidenceにならない。
2. 実Web機能はPhase 11以降へ延期済みであるのに、Non-Web Manual SheetへFixture Web Search Panel操作が残っていた。これはController Handoff側の10項目指定にも存在した矛盾であり、Claudeだけの逸脱として扱わない。

本書はFrozen Acceptance Matrixを改竄せず、P7-ACC-032のうちCurrent Phase対象であるLocal Corpus／Citation／Data ControlsだけをUser Manual Gateへ渡す。

## 2. 事前条件

- Loopbackかつ認証なしのLocal Runtimeを、Conversation Persistence、Documentation RAG、Phase 7 Local Corpus、Phase 7 Data Controlsを有効にして起動する。
- 実Public Web、一般URL、外部Provider、User既存Dataの追加調査は行わない。
- Web Search Panelが表示されても、本Gateでは実行しない。実Web機能の成否はPhase 11以降へ延期済みである。

## 3. User Manual Test（10項目）

### 1. 初期状態／RAG OFF

1. 設定画面でDocumentation RAGをOFFにする。
2. 短い質問を1回送る。

確認:

- Chat自体は通常どおり完了する。
- 回答へLocal Corpus Citationが付かない。
- `Retrieval Call 0`の内部契約は既存自動Test Evidenceを正本とし、DevToolsだけで直接証明しようとしない。

### 2. Local Document登録

Advanced ModeのLocal Corpus Document Panelで、一般知識から推測しにくい固有Factを含む文書を登録する。

例:

```text
Title: MARGPA Manual Probe 7
Content: Nazuna Probe Orionの検証コードは CEDAR-7319 である。
```

確認:

- Success表示になる。
- 一覧へTitleと登録情報が表示される。

### 3. Local Fact Grounding

1. Documentation RAGをONにする。
2. 「Nazuna Probe Orionの検証コードは？」と質問する。

確認:

- 登録Documentの固有Factに基づく回答になる。
- 一般Web検索を要求または実行しない。

### 4. Citation Identity

3の回答に付いたCitationを開く。

確認:

- Local Corpus由来とProject Docs由来を区別できる。
- Source／Chunk／Digestに相当する識別値が表示される。
- 識別値の完全なHash目視照合までは要求しない。

### 5. Reload／別Tab／Server Restart

3のConversationを、Page Reload、別Tab、Server Restart後の順で開き直す。

確認:

- Conversation本文が復元される。
- Citationが同一Conversationへ復元される。

### 6. Document更新／Revision

1. 2で登録したDocumentのコードを`CEDAR-8420`へ更新する。
2. 新しいConversationまたはTurnで同じ質問をする。

確認:

- 新規回答は更新後Factに基づく。
- 更新前ConversationのCitationは更新前Evidenceとして保持され、後から書き換わらない。

### 7. Document削除／Historical保持

1. 対象Documentを削除する。
2. 削除後に同じ質問をする。
3. 削除前Conversationを開き直す。

確認:

- 削除後の新規Retrievalでは対象DocumentがCurrent検索対象にならない。
- 削除前ConversationのHistorical Citationは消失または別Revisionへ置換されない。

### 8. Data Controls初期状態

Data Controls画面を開く。

確認:

- Retentionは読取専用の現在事実として表示される。
- External Query Transmission、Feedback Research Use、Synthetic Data Use、Future Training ExportのConsentは全てDefault OFFである。

### 9. Consent独立性／Reset

1. Consentを1項目だけONにする。
2. Reloadする。
3. 既定値へ戻す。

確認:

- 選んだ項目だけがONとして保持される。
- 他項目へ波及しない。
- Reset後は全項目OFFへ戻る。
- Consent保存を、実際の外部送信、Feedback収集、Synthetic生成またはTraining完了と表示しない。

### 10. False Capability Claimなし／Phase 11境界

設定画面とData Controls画面を確認する。

確認:

- 全Data Exportまたは一括Deleteを今すぐ実行できるかのようなButton／Success表示がない。
- Local Corpusの個別Document削除と、全Conversation／全Data Deleteを混同させない。
- Fixture／Security Scaffoldを、実Public Web検索またはWeb-grounded Chatが完成したかのように表示しない。
- Web Search Panelの動作確認は行わず、Phase 11以降のGateへ残す。

## 4. 判定と返却

各項目を`PASS／FAIL／不明`で返す。FAILまたは不明の場合だけ、実際の表示文言、再現手順および可能ならScreenshotを添える。

本Gateは、Model回答品質、実Web、Selene、Qwen3Guard、Semantic 109件、Embedding品質または汎用AttachmentをPhase 7 PASSへ昇格させない。

