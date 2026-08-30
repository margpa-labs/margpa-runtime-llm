# Phase 7 NO_HIT Citation保持／Local Corpus表示Identity 最小Rework — Claude Exact Handoff

```yaml
document_id: phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_handoff_20260830164309
document_type: exact_differential_execution_handoff
document_state: frozen
language: ja
created_at: 2026-08-30 16:43:09 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
task_continuity: continued
phase: phase_7
execution_scope: P7-RW5
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
network_authority: false
```

## 1. 目的

P7-RW4後のUser Mac実画面確認で残った、次の3件だけを最小差分で修正する。

```text
P7-CODEX-014:
  RAG ONのNO_HIT CitationがRetrieval直後には表示されるが、
  Final回答確定後のPersistent Detail再投影で消える。

P7-CODEX-015:
  Local Corpus Citationが空のHeadingを表示する。
  Local CorpusではHeadingではなく、登録済みDocument Titleを表示する。

P7-CODEX-016:
  Local Corpus CitationのPathが、実在しないSynthetic Path
  `local-corpus/<slug>.md`をUserへ表示・Copyする。
  User-facing PathにはActive Runtimeの実保存Fileを表示する。
```

このPackageはRAG再設計、Model品質修正またはPhase 8作業ではない。現在のClaude Taskを継続し、Fresh Task初期化、Role Bootstrapまたは3段階Receiptを行わない。

## 2. Active Baseline

### 2.1 P7-RW4 Return

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_stale_code_prevention_bounded_rework_exact_return_handoff_ja_20260830143000.md

SHA-512:
30c271507e81fcf2d8ad33a2cebeaefcb41d8baf15b00d2716c357e753f3c75bf4c53dab05e5c74bcf98405139a28f341ba8ba418d5d3cde8de00cae11a7c9b4
```

### 2.2 Controller Review

```text
docs/project/phases/phase_7/history/operations/phase_7_codex_controller_p7_rw4_no_hit_stale_code_prevention_independent_review_ja_20260830152558.md

SHA-512:
879c614e0409687fe60be2a1f78e9de3171e7608ef617df62b96584cd46a8163fd8b773acebc51612cce53d08d70f8dd1c718026c699b33c03063bc54ec19436
```

P7-RW4までのSource／TestをCurrent Baselineとする。P7-RW3／RW4を再実装、Rollbackまたは広域整理しない。

## 3. User Mac実画面Evidence

### 3.1 成立済み項目

同一ChatでLocal Corpus `MARGPA Manual Probe 9`を登録・更新した。

```text
Revision 1:
  Title: MARGPA Manual Probe 9
  Fact: Nazuna Probe Orionの検証コードは CEDAR-12583である。
  Answer: CEDAR-12583

Revision 2:
  Title: MARGPA Manual Probe 9
  Fact: Nazuna Probe Orionの検証コードは CEDAR-27561である。
  Answer: CEDAR-27561
```

次は成立済みであり、壊さない。

- 新Turnは更新後のCurrent値を使用した。
- 過去Turnと過去Citationは書き換わっていない。
- Source／Chunk ID／Document Digestの表示、短縮表示およびFull Copyは成立した。
- Project Docs CitationのHeading／Path／Chunk ID／Document Digest表示は成立した。
- Local Corpus削除後、旧Code `CEDAR-9847`をCurrent Factとして再提示しなかった。

### 3.2 P7-CODEX-014 再現

Local Corpus削除後、同一Chatおよび新規Chatの双方で、Retrieval直後には次のNO_HIT表示が見える。

```text
参照文書
参照対象のDocsから対応する根拠を取得できませんでした。
```

しかしFinal回答確定後、このCitation表示だけが消える。通常Citationと同様に、Retrieval直後から表示し、Final回答確定後およびConversation Detail再読込後も同じTurnへ保持する必要がある。

### 3.3 P7-CODEX-015／016 再現

現在のLocal Corpus Citationは次のように見える。

```text
Source: Local Corpus
Heading:
Path: local-corpus/margpa-manual-probe-9-e51ed2fa.md
Chunk ID: ...
Document Digest: ...
```

Userが要求する表示は次である。

```text
Source: Local Corpus
Title: MARGPA Manual Probe 9
Path: runtime_data/persistent/mac-local-primary/local_corpus/documents.json
Chunk ID: ...
Document Digest: ...
```

`mac-local-primary`をHard-codeしてはならない。上記は現在の起動設定から導出される実例である。Active `runtime_data_root`／Scopeから実保存Fileを導出し、Project Root内の保存先はProject-relative Pathとして表示・Copyする。

## 4. Required Implementation

### 4.1 P7-RW5-A — NO_HIT Citation Evidenceの永続保持

現在、Live SSEの`retrieval` EventはCitation 0件＋`documentation_no_hit` WarningをFrontendへ渡す。一方、Persistent Citation EvidenceはCitation 0件の場合に書込まれず、Persistent Detail再投影がLive Citation Stateを`null`へ上書きする。

次を成立させる。

1. RAG OFFは従来どおりCitation Evidence Write 0を維持する。
2. RAG ONかつNO_HITでは、Citation 0件でもGrounding State／Warning CodeをTurn Evidenceとして永続化できる。
3. Persistent Detail APIはNO_HITのWarning Codeを損失なく投影する。
4. FrontendはPersistent Detailから`CitationEvidence`を再構成し、既知Codeを現在のUI言語へ翻訳する。
5. Retrieval直後の即時Citation表示を維持する。Final回答までCitationを遅延させない。
6. Final回答確定後は通常Citationと同じく回答本文の下へNO_HIT表示を残し、設定再読込、Conversation Detail再読込およびBrowser Reload後も同じTurnへ保持する。
7. Historical Turn／Citation／Digestを更新、再検索または書き換えない。

既存`PersistedTurnCitationEvidence.warning_codes`を優先的に再利用し、自由文Warningの永続化や新しい重いSchemaを不要に増やさない。旧Citation RecordのDecode互換を維持する。

### 4.2 P7-RW5-B — Local CorpusのTitle表示

Local Corpusでは本文Markdown Headingが空でも、登録Recordの`title`をUser-facing Citation Identityとして保持する。

```text
Local Corpus:
  Label = Title
  Value = LocalCorpusDocumentRecord.title

Project Docs:
  Label = Heading
  Value = 既存heading_breadcrumb
```

Local Corpus Titleを`heading_breadcrumb`へ暗黙流用するだけで意味を混同せず、可能な限りBackward-compatibleなOptional FieldとしてManifest／Chunk／Reference／Citation／Persistent Projection／FrontendへLosslessに運ぶ。旧RecordやProject Docsは既定値でDecodeできなければならない。

Titleの追加を理由に、Local Corpus本文、Document Digest、Chunk内容またはModelへ渡すEvidence Textを改変しない。

### 4.3 P7-RW5-C — 実保存Pathの表示

Synthetic `local-corpus/<slug>.md`は実Filesystem Pathではない。必要なら内部のSource Identity／Retrieval Locatorとして保持してよいが、User-facing `Path`およびCopy値として表示してはならない。

次を成立させる。

1. Local Corpus RegistryのActive設定から、実保存Fileを動的に導出する。
2. 現行User起動条件では、表示／Copy値を次へ収束させる。

   ```text
   runtime_data/persistent/mac-local-primary/local_corpus/documents.json
   ```

3. Scope ID、Runtime Data Rootまたは将来Profileが変われば表示も追随する。
4. Project Root内PathはProject-relativeで表示し、Host絶対Path、User名またはProject Root外情報を漏らさない。
5. Project Docs CitationのPathは一切変えない。
6. 過去Turn Citationは当時のEvidenceとして不変を維持する。新実装後に作成されたLocal Corpus Citationから新表示契約を適用する。

実保存PathとDocument単位の内部Identityは別概念である。全Local Documentが同じ`documents.json`に保存されるため、Title／Chunk ID／Document DigestをDocument・Revision識別として引き続き表示する。

## 5. 明示的Non-goals／Deferred

次は今回実装しない。

- Qwenの回答言語、表現、謝罪文またはModel品質の修正。
- RAG ON＋NO_HIT時にModel Call自体を行わず、固定文だけを返すStrict Deterministic Mode。
- NO_HIT時のFinal回答文とCitationを一括生成・一括表示する方式。
- CitationをFinal回答まで非表示にする方式。
- Local Corpus本文へMarkdown Headingを自動挿入する方式。
- 過去Turn／過去CitationをCurrent Corpusへ追随させる書換え。
- Judge／Semantic Governance／Phase 6残件。
- Web Search／Phase 8／Phase 11以降の作業。
- UI全体の再設計、CSSの無関係な整理または型の広域改名。

将来候補として、次だけをDeferred記録として保持する。

```text
Optional Strict NO_HIT Mode:
  RAG ON＋NO_HITではModel Callを行わず、Turn開始時に固定した回答言語で
  決定論的な「現在の根拠なし」回答へ収束する。

Current Decision:
  Governance未接続状態のQwen出力は現状許容し、Phase 7 ClosureのBlockerにしない。
```

## 6. Acceptance

```text
P7-RW5-ACC-001:
  Live Retrieval直後にNO_HIT Citationが表示され、Final回答確定後は回答本文の下に残る。

P7-RW5-ACC-002:
  Conversation Detail再読込／Browser Reload後も、同じTurnにNO_HIT表示が残る。

P7-RW5-ACC-003:
  RAG OFFはCitation Evidence Write 0のまま。通常Citationの永続化もRegression 0。

P7-RW5-ACC-004:
  Local Corpus Citationは`Heading`ではなく`Title`を表示し、登録Titleと一致する。

P7-RW5-ACC-005:
  Local Corpus CitationのPath表示／Copy値がActive Runtimeの実保存Fileと一致する。
  現行User Profileでは
  `runtime_data/persistent/mac-local-primary/local_corpus/documents.json`となる。

P7-RW5-ACC-006:
  `mac-local-primary`または`runtime_data`をUIへ固定文字列としてHard-codeしない。

P7-RW5-ACC-007:
  Project Docsは`Heading`と既存Project-relative Pathを維持する。

P7-RW5-ACC-008:
  Chunk ID／Document Digestの短縮表示とFull Copy値は一致し、既存挙動を維持する。

P7-RW5-ACC-009:
  Local Corpus更新後の新TurnはCurrent Revisionを使い、過去Turn／Citation／Digestは不変。

P7-RW5-ACC-010:
  Local Corpus削除後の同一Chat／新規Chatで、NO_HIT表示が持続し、旧Codeを
  Current Citationで裏付けない。

P7-RW5-ACC-011:
  Qwen回答言語やNO_HIT Model Callを今回のPASS条件へ混入しない。

P7-RW5-ACC-012:
  Backend／FrontendのFocused Regression、Canonical Test／Type／Lint／BuildがPASSする。
```

## 7. Required Regression Scenarios

最低限、次を実Testへ含める。

1. RAG ON＋NO_HITのLive Retrieval EventがCitation 0＋Warning Codeを返す。
2. Turn完了後のPersistent Detailが同じWarning Codeを返す。
3. FrontendがLive表示後のFinal MergeでNO_HIT Citationを消さない。
4. Browser Reload相当のPersistent DetailだけからNO_HIT Citationを再構成する。
5. RAG OFFはCitation Store Row 0。
6. Local Corpus CitationがTitleを持ち、UI Labelが`Title`になる。
7. Project Docs Citationは既存`Heading`のまま。
8. Current Runtime Root／ScopeからLocal Corpus実保存Pathを導出し、表示／Copyする。
9. 異なるScope FixtureでPathが動的に変わる。
10. Project Docs Path、Chunk ID、Document DigestおよびHistorical Citation不変。

Test Fixture内でもUser固有の絶対Path、`mac-local-primary`固定、`MARGPA Manual Probe 9`固定または`Nazuna Probe Orion`専用分岐をProduction Sourceへ入れない。

## 8. 実行／検証境界

- Current Sourceと対象Testを必要十分に読む。
- P7-RW5-A〜Cを連結実行し、Routine Test／Lint Findingは自動修正して継続する。
- Internal Reviewを1 Cycleだけ実施する。Critical／Major／MVP Blockerが見つかった場合だけ同一Scope内でReworkする。
- Package FinalでRecovery Indexを1件作る。Platform Hard StopまたはResource Hard Stopが迫る場合だけ途中Recoveryを追加する。
- Project内Task-owned Temp／Cacheを使う。
- Network、Git、Backup、User `runtime_data/`実Data、Provider Memory、Project Root外、Real ModelおよびReal Browserへ触れない。
- Node追加Install、DownloadまたはRuntime切替を行わない。既存Project Toolchainで検証する。
- Phase 7 Closure、Roadmap更新、Phase 8開始を行わない。

## 9. Exact Return

完了時は次を作成する。

```text
Recovery Index:
  docs/project/phases/phase_7/history/index/

Exact Return Handoff:
  docs/project/phases/phase_7/handoffs/
```

Returnには次を含める。

- P7-CODEX-014〜016のDisposition。
- P7-RW5-ACC-001〜012の個別結果。
- Changed Path一覧。
- NO_HIT Live／Persistent／Reload経路の証拠。
- Local Corpus Title／実保存Pathの動的導出経路。
- Project Docs／Historical Citation／RAG OFFのRegression結果。
- Internal Review結果。
- Canonical Backend／Frontend検証結果。
- Incident／PARTIAL／NOT RUN。
- User Manual Testが必要な最小項目。

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。完了後はCodex Controller Independent Review待ちで停止する。
