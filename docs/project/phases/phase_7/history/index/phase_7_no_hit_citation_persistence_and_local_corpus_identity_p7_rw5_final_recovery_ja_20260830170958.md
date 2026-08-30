# Phase 7 NO_HIT Citation保持／Local Corpus表示Identity 最小Rework — Package Recovery Index

```yaml
document_id: phase_7_no_hit_citation_persistence_and_local_corpus_identity_p7_rw5_final_recovery_20260830170958
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 17:09:58 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_7
execution_scope: P7-RW5
```

## 1. Recovery Index Pointer

```text
前Package（P7-RW4）:
  docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_stale_code_prevention_bounded_rework_exact_return_handoff_ja_20260830143000.md
  SHA-512:
  30c271507e81fcf2d8ad33a2cebeaefcb41d8baf15b00d2716c357e753f3c75bf4c53dab05e5c74bcf98405139a28f341ba8ba418d5d3cde8de00cae11a7c9b4

本Package自身のExact Return Handoff:
  docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_return_handoff_ja_20260830171200.md
```

## 2. Digest照合

対象Exact Handoff（正本）の実File SHA-512を`shasum -a 512`で照合し、指示書記載値と一致を確認した。

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_handoff_ja_20260830164309.md
SHA-512:
b899630ebb162ebdf16f53955a72bcd8edde7ca5a97ea2e5b5e313159837e7a2138418ac32cf1dd27ced805933259253335423423e9bdfd37b559fe7fa8099b3
```

Active Baselineとして指定されたP7-RW4 ReturnおよびP7-RW4 Controller Reviewも同様に実File SHA-512を照合し、指示書記載値と一致を確認した（値はHandoff §2に記載のとおり）。

## 3. 対象Findingの再確認

```text
P7-CODEX-014: RAG ONのNO_HIT CitationがRetrieval直後には表示されるが、
  Final回答確定後のPersistent Detail再投影で消える。
P7-CODEX-015: Local Corpus Citationが空のHeadingを表示する。
P7-CODEX-016: Local Corpus CitationのPathが、実在しないSynthetic Path
  `local-corpus/<slug>.md`をUserへ表示・Copyする。
```

## 4. Root Cause

### 4.1 P7-CODEX-014

`build_turn_citation_evidence()`（`documentation_rag/contracts.py`）は`augmentation.citations`が空であれば、Retrieval Stateに関わらず一律`None`を返し、Turn Citation Evidenceを1件も書き込まない設計だった。NO_HIT状態は`DocumentationEvidence`のSchema Invariantにより`citations`が必ず空になるため、RAG OFFと同じ「永続化不要」経路へ誤って合流していた。結果、`PersistentConversationService.complete_generation()`はNO_HIT Turnに対して`turn_citations`行を1件も書かず、Persistent Detail再投影（`_project_turn_citations`）は`entry is None`（Store側の`not_present`）を返し、FrontendはNO_HIT表示を`null`へ落としていた。Live SSEの`retrieval`Eventは別経路（`_retrieval_event()`／`_completed_event()`の`documentation_retrieval`）で構築されており、この欠落の影響を受けなかった——これがUser Mac実画面で「Retrieval直後は見えるが、Final回答確定後に消える」という非対称症状として現れていた。

### 4.2 P7-CODEX-015

`DeterministicMarkdownChunker`の`heading_breadcrumb`は、本文中のATX Markdown Heading（`#`〜`######`）からのみ導出される。Local Corpus Documentは登録時に`title`Fieldを持つが、本文そのものにMarkdown Headingを含む保証はなく（User登録の生Text/短文が典型）、Heading非存在時は空文字列になる。Citation UIは`Heading`Labelで`heading_breadcrumb`を無条件表示していたため、Local Corpus Citationは常に空のHeading行を表示していた。

### 4.3 P7-CODEX-016

`LocalCorpusDocumentSource`の`project_relative_path`は`local-corpus/<slug>-<id8>.md`という決定論的だが実在しないSynthetic Identity（`LocalCorpusDocumentRecord.path_slug`）である——`LocalCorpusDocumentSource`は本文をこのRecordから直接供給し、Diskからは一切読まない。Citation UIはこの`project_relative_path`をそのままPath行として表示・Copyしており、実際にLocal Corpus Documentが保存されている実File（`JsonFileLocalCorpusRegistry`の単一JSON Store）とは無関係な文字列をUserへ提示していた。

## 5. Fix（最小差分）

Handoff §4の3項目それぞれについて、既存の型・Adapter境界・Event経路を再利用し、新しいSubject／Identifier検出Heuristicや新規Persistence Schemaを一切追加しなかった。

### 5.1 P7-RW5-A — NO_HIT Citation Evidenceの永続保持

```text
1. build_turn_citation_evidence()（documentation_rag/contracts.py）:
   「augmentation.state is not ENABLED」の場合のみ即Noneを返すよう分離し、
   続けて「citationsが空 かつ grounding_stateがNO_HITではない」場合のみ
   Noneを返すよう変更した。NO_HITは既存のPersistedTurnCitationEvidence
   （citations=()、warning_codes=既存augmentation.warningsのcode列）を
   そのまま構築する——新しいField、新しいSchema Versionは1つも追加して
   いない。CONTEXT_INSUFFICIENT／UNAVAILABLE（Bounded Rework対象外）は
   従来どおりNoneのまま。
2. PersistentTurnCitationsResponse（web/persistent_contracts.py）に
   `warning_codes: tuple[str, ...] = ()`を追加し、_project_turn_citations()
   がPersistedTurnCitationEvidence.warning_codesをそのまま投影する。
3. Frontend detailToMessages()（persistentDetailProjection.ts）は
   `turn.citations.warning_codes`から`{code, message: ""}[]`を組み立て、
   CitationsSectionの既存EmptyCitations（knownServerMessagesによる
   Code→翻訳のLookup、Live SSE経路と共有）へそのまま渡す——新しい
   翻訳経路、新しいUI Componentを1つも追加していない。
```

Live SSEの`retrieval`／`completed`Eventは元々NO_HITを正しく表示していたため無変更。Streaming方式（RAG ON+NO_HIT TurnのみのMinimal Buffering、P7-RW4で確立）にも触れていない。

### 5.2 P7-RW5-B — Local CorpusのTitle表示

```text
DocumentManifestEntry／DocumentationChunk／DocumentationReferenceBlock／
DocumentationCitationへ、既存のcorpus_source_class／source_classと
全く同じ中継パターンで`document_title: str | None = None`を追加した
（Manifest -> Chunk -> ReferenceBlock -> Citationの4段階、各Adapterで
1行ずつ書き足しただけ）。LocalCorpusDocumentSourceのみが
`record.title`を設定し、Project Docs側は常にNoneのまま
（Backward-compatible、旧Recordも欠損値としてLossless Decode）。
Citation UIはsource_class局所判定でLocal Corpusのみ
Label「Title」+ document_titleを表示し、Project Docsは従来どおり
Label「Heading」+ heading_breadcrumbを表示する。
```

Local Corpus本文・Document Digest・Chunk内容・Model渡しEvidence Text（`_render_block`／`REFERENCE_INSTRUCTION`）はいずれも無変更。

### 5.3 P7-RW5-C — 実保存Pathの表示

```text
1. LocalCorpusRegistryPort（Protocol）へ`document_store_path: Path`
   （読み取り専用Property）を追加。JsonFileLocalCorpusRegistryは
   既存の内部`self._path`をそのまま返す（新しいI/O、新しい状態を
   一切追加していない）。
2. LocalCorpusDocumentSource.__init__へ`project_root: Path`を追加し、
   構築時に1度だけ`_storage_display_path(project_root, registry.
   document_store_path)`を計算してキャッシュする（全Local Corpus
   Documentが同じJSON Storeを共有するため、Document単位の再計算は
   不要）。Project Root内であればProject-relative文字列
   （現行User Profileでは`runtime_data/persistent/mac-local-primary/
   local_corpus/documents.json`）、Project Root外であれば
   Host絶対PathやUser名を含まない`persistent/`以降のScope相対
   Suffixのみを返す（Handoff §4.3の「Project Root外情報を漏らさない」
   要件への対応）。
3. document_title同様の中継パターンで
   `storage_display_path: str | None = None`を4段階の型へ追加し、
   Citation UIのPath行は`storage_display_path ?? project_relative_path`
   を表示・Copyする——Project Docs（常にNone）とP7-RW5-C以前に
   作成されたLocal Corpus Citation（Historical Immutability、
   Handoff §4.3-6）は従来どおりproject_relative_pathへFallbackする。
```

`mac-local-primary`／`runtime_data`のHard-codeは一切行っていない——`bootstrap/documentation_rag.py`の`build_documentation_rag()`が既に受け取っている`project_root`引数を`LocalCorpusDocumentSource`へ1行追加で渡しただけで、実際のScope／Runtime Data Rootは`entrypoints/web/main.py`のCLI引数解決（`_local_corpus_registry_settings`）が従来どおり決定する。

## 6. Scope遵守の確認

```text
Title-Case Run Heuristic再導入: 0件。
固有名Allowlist新設: 0件。
`mac-local-primary`／`runtime_data`のHard-code: 0件。
新しい意味解析基盤: 0件。
P7-CODEX-011（Citation UI Field順）: 無変更
  （Source -> Heading/Title -> Path -> Chunk ID -> Document Digestの
  行順は既存のまま、2行目の表示内容のみsource_class分岐で切替）。
P7-CODEX-012（Current Reference修正）: `conversation_generation.py`の
  `_splice_before_final_user_message()`／
  `CURRENT_EVIDENCE_AUTHORITY_INSTRUCTION`は本Package内で1行も
  Read/Editしていない。
Auto-Resume: `persistent_conversation_service.py`のResume経路／
  `ChatListItem.tsx`は本Package開始時点から一切Read/Editしていない
  （`persistent_conversation_service.py`は`complete_generation()`の
  既存呼び出し1箇所のみ、行番号での参照確認のみでEdit 0件）。
CitationをFinal回答まで遅延させる方式: 採用していない
  （Live Retrieval直後の即時表示は無変更のまま維持）。
Qwen回答言語・表現・Strict NO_HIT Mode・Judge／Governance・
  Web Search・Phase 8・UI全体再設計: 0件着手。
```

## 7. 必須Regression Test（Handoff §7、1〜10）

```text
1. Live NO_HIT retrieval EventがCitation 0+Warning Codeを返す:
   tests/integration/web/test_persistent_web_app.py::
   test_no_hit_citation_survives_reload_fetch（streamed.text検証）
2. Turn完了後のPersistent Detailが同じWarning Codeを返す:
   同上（reloaded.json()検証）+
   tests/integration/conversation/test_persistent_citation_evidence.py::
   test_no_hit_turn_persists_zero_citation_evidence_and_survives_restart
3. FrontendがLive->Final MergeでNO_HIT Citationを消さない:
   handlePersistentEvent()のcompleted分岐がcitationsへ触れないことを
   Source Readで確認済み（App.tsx）+
   frontend/src/lib/persistentDetailProjection.test.ts（新規2件）
4. Browser Reload相当のPersistent DetailだけからNO_HIT Citationを再構成:
   persistentDetailProjection.test.ts
   「reconstructs a non-null CitationEvidence」
5. RAG OFFはCitation Store Row 0:
   tests/integration/conversation/test_persistent_citation_evidence.py::
   test_rag_disabled_turn_reports_not_present_not_corrupt（既存、無変更・PASS維持）
6. Local Corpus CitationがTitleを持ち、UI Labelが"Title"になる:
   frontend/src/components/CitationsSection.test.tsx（新規2件）
7. Project Docs Citationは既存"Heading"のまま:
   CitationsSection.test.tsx（新規1件）+ 既存Field順Test群PASS維持
8. Current Runtime Root/ScopeからLocal Corpus実保存Pathを導出し表示/Copy:
   tests/unit/documentation_rag/test_local_corpus_document_source.py（新規）+
   tests/unit/documentation_rag/test_bootstrap.py（拡張）+
   tests/integration/web/test_persistent_web_app.py（拡張）+
   CitationsSection.test.tsx（新規2件、表示とCopy値の一致を検証）
9. 異なるScope FixtureでPathが動的に変わる:
   test_local_corpus_document_source.py::
   test_storage_display_path_follows_the_active_scope_key、
   test_local_corpus_registry.py::
   test_document_store_path_matches_the_actual_read_write_location
10. Project Docs Path/Chunk ID/Document Digest/Historical Citation不変:
    test_persistent_web_app.py::test_citations_survive_reload_fetch
    （persisted[0]のdocument_title/storage_display_pathが常にNoneを検証）+
    test_nazuna_probe_orion_freshness_update_delete_regression／
    test_nazuna_probe_orion_candidate_presentation_regression／
    test_deleted_local_corpus_document_denies_a_stale_code_from_
    conversation_history_regression（いずれも既存、無変更のままPASS維持）
```

Test Fixture内でUser固有絶対Path、`mac-local-primary`固定、`MARGPA Manual Probe 9`固定または`Nazuna Probe Orion`専用分岐をProduction Sourceへ入れていないことを確認済み（`_storage_display_path()`はProduction Source側で完全に汎用、固定値はTest側のFixtureにのみ現れる）。

## 8. 検証順・結果

```text
1. Exact Regression Test（上記9項目のTest File）: 個別実行PASS
2. 関連Conversation／Local Corpus Focused Test:
   uv run pytest -q tests/unit/documentation_rag/ \
     tests/unit/web/test_persistent_web_contracts.py \
     tests/unit/conversation/test_conversation_store_contract.py \
     tests/unit/conversation/test_conversation_generation.py \
     tests/unit/conversation/test_citation_evidence_sqlite_store.py \
     tests/integration/documentation_rag/test_local_corpus_end_to_end.py \
     tests/integration/conversation/test_persistent_citation_evidence.py \
     tests/integration/web/test_persistent_web_app.py \
     tests/integration/web/test_local_corpus_web_app.py
   -> 242 passed
3. Backend Canonical（Focused成立後、1回）:
   uv run pytest -q                     -> 1952 passed, 7 deselected
   uv run mypy                          -> Success, no issues found in 526 source files
   uv run ruff check .                  -> All checks passed
   uv run ruff format --check .         -> 526 files already formatted
   （P7-RW4基準1944 passedから+8、全件新規Test。Regression 0。）
4. Frontend Source変更あり（本Package）につきFrontend再検証実施:
   Node追加Install/Download 0件、既存Node v25.8.1のみ使用。
   cd frontend && npm run typecheck     -> エラー0件
   cd frontend && npm test
     (NODE_OPTIONS=--no-webstorage vitest run)
                                         -> 29 files, 268 tests passed
   cd frontend && npm run lint          -> エラー0件
   （P7-RW3-DのFrontend基準262 testsから+6、全件新規Test。Regression 0。
   npm install等のNetwork Actionは1度も実行していない——既存
   node_modulesを再利用。）
```

## 9. Internal Review（1 Cycle）

```yaml
観点1_Controller指摘解決:
  P7-CODEX-014/015/016いずれもRoot Causeを直接特定し、対応するFixが
  Handoff §7の全10 Regression Scenarioを満たすことをTestで確認した。
観点2_既存Boundaryとの非重複:
  P7-RW3-B（_identifier_no_hit_denied）／P7-RW4（_no_hit_rag_turn
  Consistency Check）はいずれも`self._documentation_augmentation`
  Propertyを共有し、complete_generation()への引き渡しは1箇所のみ
  （persistent_conversation_service.py L971）と確認した。P7-RW5-Aの
  Fixはこの共有経路1箇所のみを変更しており、両Boundaryへ等しく
  恩恵が及ぶ（新しい分岐条件を追加していない）。
観点3_Backward互換性:
  document_title／storage_display_pathはいずれも4段階の型で
  `str | None = None`のOptional Field。既存Test（context_citation_
  and_orchestrator.py等、これらFieldを一切設定しないFixture）は
  無変更のまま全件PASSし、旧Local Corpus Citation（Field欠損）は
  Frontendの`?? project_relative_path`FallbackでLosslessに描画される
  ことを確認した。
観点4_Historical Immutability:
  P7-RW5-Aの変更はcomplete_generation()内の新規Write経路のみに
  作用し、既存の`_decode_citation_evidence`／`get_turn_citations`の
  Read経路は無変更。過去に書き込まれなかったTurnの`not_present`
  状態は今後も`not_present`のまま——本Fix以降に生成されるNew Turnの
  みが新しいPersistence契約を得る。Nazuna Probe Orion系Regression
  Test（P7-RW2/RW3/RW4由来）は1文字も変更せず全件PASSを確認した。
観点5_Security:
  `_storage_display_path()`のProject Root外Fallbackが、tmp_path
  自体・User Home相当のDirectory名（"elsewhere_runtime_data"に
  含まれる"elsewhere"文字列）をStorage Display Pathへ含めない
  ことを専用Testで確認した。
観点6_Scope/Claim整合:
  P7-CODEX-011/012/Auto-Resumeへの非接触、CitationをFinal回答まで
  遅延させる方式を採用していないこと、Node/Network Action 0件を
  Action Inventory（§10）で確認した。
```

Critical／Major／MVP Blocker: 0件。

```yaml
finding_id: P7-RW5-IR-001
severity: minor_observation
disposition: known_deferred_non_blocking
summary: >-
  Local Corpus実保存Pathの表示契約のうち、Handoffが明示的Literalで
  指定したのはProject Root内（現行User Profile）の1ケースのみである。
  Project Root外にrutime_data_rootが構成された場合の表示形（
  `persistent/<scope>/local_corpus/documents.json`、Root Prefixなし）
  は、「Host絶対Path/User名を漏らさない」という定性要件からの
  実装側の合理的な補完であり、User自身が確認したLiteralではない。
  現行User Profileはこのケースに該当しない（Project Root内が既定）
  ため、Acceptance判定には影響しない。
```

## 10. Action Inventory

```text
Git Mutation: 0（読み取り専用git statusのみ）
Network Access: 0（npm install等を含め一切実行していない、既存node_modules/uvツールチェーンのみ使用）
Node追加Install/Download/切替: 0（既存Node v25.8.1のみ使用）
Provider Memory使用: 0
Task-owned Project Root外へのRead/Write: 0
Real Model呼び出し: 0（全Test Scripted Inference/Fixtureのみ）
Real Browser操作: 0
Destructive Mutation: 0
Source変更（Backend）: 10 File
Source変更（Frontend）: 4 File
Test変更・追加（Backend）: 8 File
Test変更・追加（Frontend）: 2 File
新規追加Test件数: Backend +8、Frontend +6（合計+14、Regression 0）
```

## 11. Rework Cycle: 不要

Critical／Major／MVP Blocker 0件のため、Handoff §8の指示どおりInternal Reviewの2周目は実施しない。
