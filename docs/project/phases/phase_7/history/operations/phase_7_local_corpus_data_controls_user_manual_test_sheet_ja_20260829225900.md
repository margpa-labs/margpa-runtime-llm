# Phase 7 Local Corpus／Data Controls — User Manual Test Sheet（Candidate）

```yaml
document_id: phase_7_local_corpus_data_controls_user_manual_test_sheet_20260829225900
document_type: user_manual_test_sheet_candidate
document_state: candidate_awaiting_user_execution
language: ja
created_at: 2026-08-29 22:59:00 JST
active_contract: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md
package: P7-NW-D
execution_authority: user_only
claude_execution: not_performed
```

## 0. 本書の位置付け

本書はP7-ACC-032のうち**Local Corpus／Citation／Data Controls User Gate部分**に対応するCandidate Test Sheetである。Claudeは本書に基づく実画面操作を一切行っていない（`USER MANUAL GATE／NOT RUN`）。Userが実Mac／実Browserで本書の手順を実施し、結果をController Independent Reviewまたは次Handoffへ報告することを想定する。

Web Source（実General Web検索）に関する確認項目は含めない。実Web検索、Public URL、External NetworkまたはUser既存`runtime_data/`への接触は本書のいずれの項目でも要求しない。

## 1. 事前準備

```text
- Loopback（127.0.0.1 / localhost）かつ認証なしの状態でRuntimeを起動する
  （--phase-7-local-corpus, --phase-7-web-search, --phase-7-data-controls
  等のPhase 7 CLI Flagを有効化した状態）。
- Browserで通常のChat画面を開く。
- 画面右上（または既存Settings起動位置）の設定Iconから「設定」Modalを開く。
```

## 2. Test項目

### 2.1 初期状態とRAG OFF副作用0

```text
手順:
  1. 「設定」Modalの基本設定Tab（「設定」）で、要約Mode／RAG設定行を確認する。
  2. RAG（Documentation RAG）をOFFにした状態でChatへ質問を送る。
確認:
  - Network／Retrieval Callが発生しないこと（Devtools Network Tabで
    /api配下のRetrieval関連Requestが送信されないことを確認できれば十分。
    詳細なPacket解析は不要）。
  - 回答にCitationが付与されないこと。
```

### 2.2 Local Document登録

```text
手順:
  1. 「設定」Modalの「アドバンスモード」Tabを開く。
  2. 「Local Corpus Document」Panelで、短いTitleと本文（数百文字程度で十分）
     を入力し登録する。
確認:
  - 登録がSuccessし、一覧に表示されること。
  - Titleと登録日時が画面に表示されること。
```

### 2.3 登録Documentだけで答えられる固有Factを質問

```text
手順:
  1. RAGをONに戻す。
  2. 登録したDocumentにしか書かれていない、一般的なModel知識では
     答えられない固有の事実（例: 独自の製品名、架空の設定値など）を
     Chatで質問する。
確認:
  - 回答が、登録したDocumentの内容に基づいて生成されること。
  - Web検索が発生しないこと（Web検索TogglはOFFのままでよい）。
```

### 2.4 CitationにLocal Source／Chunk／Digestが表示されること

```text
手順:
  1. 2.3の回答に付随するCitation表示を開く。
確認:
  - CitationのSourceがLocal Corpus由来であることが分かる表示になっていること
    （Project Docs由来のCitationと区別できること）。
  - Chunk IdentityまたはDigestに相当する情報が確認できること
    （厳密なHash文字列の目視照合までは不要、「識別可能な値が存在する」
    ことの確認で足りる）。
```

### 2.5 Reload／別Tab／Server Restart後のConversation／Citation

```text
手順:
  1. 2.3のConversationを保持したままPageをReloadする。
  2. 同じConversationを別Tabで開く。
  3. Server Processを再起動し、同じConversationを開き直す。
確認:
  - いずれの場合もConversation本文とCitationが同一内容で復元されること。
```

### 2.6 Document更新後のRevision／回答／Citation

```text
手順:
  1. 2.2で登録したDocumentの内容を更新する（本文を書き換える）。
  2. 更新後の内容についてChatで再度質問する。
確認:
  - 新しいRevisionの内容に基づいて回答が変わること。
  - 更新前の会話履歴に付いていたCitationが、更新前の内容を指す
    Historical Evidenceとして壊れずに残っていること
    （更新後の内容へ書き換わっていないこと）。
```

### 2.7 Document削除後のCurrent検索除外とHistorical Citation保持

```text
手順:
  1. 2.2で登録したDocumentを削除する。
  2. 削除後に、そのDocumentの内容についてChatで再度質問する。
  3. 削除前に得た2.3／2.6のConversationを開き直す。
確認:
  - 削除後の新規質問では、そのDocumentがCurrent検索対象から除外され、
    もし他にEvidenceがなければ「関連情報なし」相当の回答になること。
  - 削除前に得たConversationのCitationは、削除後も壊れずに残っていること
    （過去のCitationが消えたり、Errorになったりしないこと）。
```

### 2.8 Data Controls全Default OFF

```text
手順:
  1. 「設定」Modalの「データコントロール」Tabを開く。
確認:
  - Retention（現在の実挙動）Sectionが読取専用の説明として表示され、
    設定変更UIになっていないこと。
  - 用途別Consent（外部送信同意、Feedback研究利用、Synthetic Data利用、
    将来Training用Export）が、初期状態で全てOFFであること。
```

### 2.9 各Consentの独立切替／Reload後の反映

```text
手順:
  1. 2.8の各Consent項目を1つだけONにする。
  2. Pageをreloadする。
確認:
  - ONにした項目だけがONのまま保持され、他の項目はOFFのままであること
    （1項目のONが他項目へ波及しないこと）。
  - 「既定値へ戻す」Buttonで全項目がOFFへ戻ること。
```

### 2.10 未実装Capabilityと実Web未実装が虚偽成功表示されないこと

```text
手順:
  1. データコントロール画面全体を見渡し、Data Export・一括Deleteに相当する
     Buttonや説明がUI上に存在しないことを確認する。
  2. 「アドバンスモード」TabのWeb Search Panelで、検索を1回実行する
     （Fixture Providerによる固定結果が返る）。
  3. Web Search結果がChatの回答へ自動的に反映されるかどうかを確認する。
確認:
  - Data Export／一括Deleteを実行できるかのようなUI表現が存在しないこと。
  - Web Search Panelでの検索結果は、Panel内で閲覧できるのみで、
    通常のChat回答へは自動的に反映されないこと（反映された場合は、
    P7-I Finding-002／本Addendum§1の記述と矛盾するため、Controllerへ
    報告すること）。
  - Web Search PanelがReal Public Webではなく固定Sample（Fixture）を
    返していることが、表示文言や結果内容（Python／FastAPI／Wikipedia等の
    固定Topic）から見分けられること。
```

## 3. 報告方法

各項目についてPASS／FAIL／不明を記録し、FAILまたは不明な項目があれば、再現手順と画面Evidence（Screenshot等）を添えてCodex Controller Independent Reviewまたは次Handoffへ報告する。本Test SheetをClaudeが実行したとみなさない——本書はCandidateであり、実施と結果判定はUser Authorityに属する。

## 4. Action Inventory

```text
Git Action: 0
Network Action: 0（Fixture Provider経由のWeb Search Panel操作はUser自身が任意で実施する
  もので、Claudeが本書作成中に実行したものではない）
Real Browser Action（Claude by本書作成）: 0
```

Exact next action: P7-NW-E（Internal Review／Return）へ連結して進む。
