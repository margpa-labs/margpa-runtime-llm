# Phase 7 NO_HIT Citation保持／Local Corpus表示Identity 最小Rework — Exact Return Handoff

```yaml
document_id: phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_return_handoff_20260830171200
document_type: exact_differential_execution_return_handoff
document_state: final
language: ja
created_at: 2026-08-30 17:12:00 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
phase: phase_7
execution_scope: P7-RW5
active_contract: docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_handoff_ja_20260830164309.md
active_contract_sha512: b899630ebb162ebdf16f53955a72bcd8edde7ca5a97ea2e5b5e313159837e7a2138418ac32cf1dd27ced805933259253335423423e9bdfd37b559fe7fa8099b3
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
network_authority: false
```

## 1. Digest照合

対象Exact Handoff（正本）の実File SHA-512を`shasum -a 512`で照合し、上記`active_contract_sha512`と一致を確認した。Active Baselineとして指定されたP7-RW4 ReturnおよびP7-RW4 Controller Reviewについても、実File SHA-512がHandoff §2の記載値と一致することを確認した。

## 2. Package Recovery Index

```text
P7-RW5（NO_HIT Citation保持／Local Corpus表示Identity 最小Rework）:
  docs/project/phases/phase_7/history/index/phase_7_no_hit_citation_persistence_and_local_corpus_identity_p7_rw5_final_recovery_ja_20260830170958.md
  SHA-512:
  6a26cd5552351bd1f1e0cb5b88c81c75d52d691b5e2ed60b8933a9477ff7784cd7877e64c964f630b472723aea998e9bcf48877ff32e822e6042f988f474c211
```

## 3. Finding解決状況

```yaml
P7-CODEX-014:
  title: RAG ON NO_HIT CitationがFinal回答確定後のPersistent Detail再投影で消える
  disposition: RESOLVED_FOR_THIS_REWORK_SCOPE
  root_cause: build_turn_citation_evidence()がcitationsの空をRAG OFFと
    同一視し、NO_HIT Turnに対してTurn Citation Evidenceを1件も書き込ま
    なかった。Live SSEの retrieval/completed Eventは別経路のため無傷
    だったが、Persistent Detail再投影（complete_generation後のfinally
    ブロックで必ず走るloadPersistentDetail()）が毎回この欠落を踏んで
    citationsをnullへ上書きしていた。
  fix: build_turn_citation_evidenceの早期return条件を
    「stateがENABLEDでない」場合と「citationsが空 かつ
    grounding_stateがNO_HITでない」場合とに分離し、NO_HITはcitations=()
    のままPersistedTurnCitationEvidence（既存warning_codesを再利用）を
    構築するよう変更。PersistentTurnCitationsResponseへwarning_codesを
    追加投影し、Frontend detailToMessages()がそこからCitationEvidenceを
    再構成する。
  verification: 新規Integration Test（Live SSE + Persistent Detail
    reload、両方をHTTP経由で検証）+ 新規Unit/Component Test。

P7-CODEX-015:
  title: Local Corpus Citationが空のHeadingを表示する
  disposition: RESOLVED_FOR_THIS_REWORK_SCOPE
  root_cause: heading_breadcrumbは本文のMarkdown ATX Headingからのみ
    導出され、Local Corpus Documentの本文がHeadingを含まない場合は
    常に空文字列になる。
  fix: DocumentManifestEntry/DocumentationChunk/DocumentationReference
    Block/DocumentationCitationへ、既存source_class中継と同一パターンで
    document_title（Optional、既定None）を追加し、LocalCorpusDocument
    Sourceのみがrecord.titleを設定する。Citation UIはsource_class局所
    判定でLocal CorpusのみLabel「Title」+ document_titleを表示。
  verification: 新規Component Test（Local CorpusはTitle行/Project Docs
    はHeading行を維持）。

P7-CODEX-016:
  title: Local Corpus CitationのPathが実在しないSynthetic Pathを表示・Copyする
  disposition: RESOLVED_FOR_THIS_REWORK_SCOPE
  root_cause: project_relative_pathはlocal-corpus/<slug>.mdという
    決定論的だが実Filesystemに存在しないCitation Identityであり、
    Citation UIがこれをそのままPath表示・Copy値に使っていた。
  fix: LocalCorpusRegistryPortへ読み取り専用document_store_path
    Propertyを追加（JsonFileLocalCorpusRegistryは既存self._pathを
    返すのみ）。LocalCorpusDocumentSourceがproject_rootを新たに受け取り、
    構築時に1度だけActive Runtime設定から実表示Pathを導出・キャッシュ
    （Project Root内はProject-relative、Project Root外はHost絶対Path/
    User名を含まないScope相対Suffixのみ）。document_title同様の
    4段階中継でstorage_display_pathを追加し、Citation UIは
    storage_display_path ?? project_relative_pathを表示・Copyする。
  verification: 新規Unit Test（既定Scope/別Scope/Project Root外の
    3ケース）+ Bootstrap Composition Testの拡張 + HTTP End-to-End Test
    + Component Test（表示値とCopy値の一致）。
```

## 4. Acceptance（P7-RW5-ACC-001〜012）

```text
ACC-001: PASS - Live Retrieval直後にNO_HIT Citationが表示され、Final
  回答確定後も回答本文の下に残る（handlePersistentEvent completed分岐
  はcitationsへ触れないことをSource確認、かつ以降のPersistent Detail
  Reload後もACC-002で保持を確認）。
ACC-002: PASS - test_no_hit_citation_survives_reload_fetch（Live SSE
  streamed.text + 直後のGET reloaded.json()を同一Testで検証）、
  persistentDetailProjection.test.tsの新規Testで検証。
ACC-003: PASS - test_rag_disabled_turn_reports_not_present_not_corrupt
  （既存、無変更のままPASS）。通常Citation（Grounded）の永続化も
  test_citations_survive_reload_fetch拡張版でRegression 0を確認。
ACC-004: PASS - CitationsSection.test.tsx新規Test
  「shows a Title row (not Heading)...」。
ACC-005: PASS - test_local_corpus_document_source.py
  test_manifest_entry_carries_the_registered_title_and_real_storage_path
  で現行User Profileの厳密Literal一致を確認。
ACC-006: PASS - _storage_display_path()はProduction Source側で完全に
  汎用（project_root/registry.document_store_pathからの導出のみ）、
  `mac-local-primary`/`runtime_data`の固定文字列はTest Fixture側にのみ
  存在することをGrep+Source Readで確認。
ACC-007: PASS - test_citations_survive_reload_fetch拡張版で
  persisted[0]（Project Docs）のdocument_title/storage_display_pathが
  常にNoneであることを直接assert。
ACC-008: PASS - 既存test（shortened/full copy一致）は無変更のままPASS、
  新規Local Corpus Path Copy Testでも表示値=Copy値の一致を確認。
ACC-009: PASS - test_storage_display_path_follows_the_active_scope_key
  （Local Corpus）、test_document_store_path_matches_the_actual_read_
  write_location（Registry）で別Scope Fixtureによる動的変化を確認。
ACC-010: PASS - test_nazuna_probe_orion_freshness_update_delete_
  regression等、既存3件のNazuna Probe Orion系Regression Testを1文字も
  変更せず全件PASSを再確認。
ACC-011: PASS - Qwen回答言語/NO_HIT Model Call自体は本Package内で
  1箇所も変更していない（conversation_generation.pyの生成判断ロジック
  は完全に無変更、変更は全てCitation Evidence/表示Layerのみ）。
ACC-012: PASS - Backend Canonical 1952 passed/7 deselected、mypy/ruff
  clean。Frontend typecheck/vitest 268 passed/eslint clean。
```

## 5. Changed Path一覧

```text
[Backend Source]
  src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  src/margpa_runtime_llm/modules/documentation_rag/local_corpus_ports.py
  src/margpa_runtime_llm/adapters/documentation_rag/local_corpus_registry.py
  src/margpa_runtime_llm/adapters/documentation_rag/local_corpus_document_source.py
  src/margpa_runtime_llm/adapters/documentation_rag/markdown_chunker.py
  src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  src/margpa_runtime_llm/adapters/documentation_rag/system_citation_adapter.py
  src/margpa_runtime_llm/bootstrap/documentation_rag.py
  src/margpa_runtime_llm/web/persistent_contracts.py
  src/margpa_runtime_llm/web/persistent_streaming.py

[Backend Test]
  tests/unit/documentation_rag/test_citation_persistence_contracts.py
  tests/unit/documentation_rag/test_local_corpus_document_source.py
  tests/unit/documentation_rag/test_local_corpus_registry.py
  tests/unit/documentation_rag/test_composite_document_source.py
  tests/unit/documentation_rag/test_bootstrap.py
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py
  tests/integration/conversation/test_persistent_citation_evidence.py
  tests/integration/web/test_persistent_web_app.py

[Frontend Source]
  frontend/src/types.ts
  frontend/src/lib/persistentDetailProjection.ts
  frontend/src/components/CitationsSection.tsx
  frontend/src/i18n/translations.ts

[Frontend Test]
  frontend/src/components/CitationsSection.test.tsx
  frontend/src/lib/persistentDetailProjection.test.ts
```

P7-CODEX-011（Citation UI Field順）/P7-CODEX-012（Current Reference修正）/Auto-Resumeに関連するFile（`CitationsSection.tsx`のField順自体、`conversation_generation.py`の`_splice_before_final_user_message()`、`persistent_conversation_service.py`のResume経路、`ChatListItem.tsx`）はいずれも本Package内でEdit 0件。

## 6. NO_HIT Live／Persistent／Reload経路の証拠

```text
Live: tests/integration/web/test_persistent_web_app.py::
  test_no_hit_citation_survives_reload_fetch内で
  `"event: retrieval" in streamed.text`、
  `'"citations":[]' in streamed.text`、
  `'"code":"documentation_no_hit"' in streamed.text` を直接assert。
Persistent(reload): 同Test内、直後の`client.get()`で取得したDetail JSONへ
  `turn_citations["available"] is True`、
  `turn_citations["citations"] == []`、
  `turn_citations["warning_codes"] == ["documentation_no_hit"]` を直接assert
  （本Fix以前はavailableがFalse相当/citationsがnull相当になっていた経路）。
Restart: tests/integration/conversation/test_persistent_citation_evidence.py::
  test_no_hit_turn_persists_zero_citation_evidence_and_survives_restart
  で、新規SQLiteConversationStoreインスタンス（プロセス内状態を持たない）
  からの再読み込みでも同じgrounding_state/warning_codesを確認。
Frontend Reload再構成: frontend/src/lib/persistentDetailProjection.test.ts
  の新規Testで、`{available: true, citations: [], warning_codes:
  ["documentation_no_hit"]}` からnullでないCitationEvidenceが
  再構成されることを直接assert。
```

## 7. Local Corpus Title／実保存Pathの動的導出経路

```text
Title: DocumentManifestEntry.document_title <- LocalCorpusDocumentSource
  （record.titleをそのまま設定）-> DocumentationChunk -> Reference
  Block -> DocumentationCitation -> PersistentCitationResponse -> Frontend
  Citation.document_title。全段階Optional/Backward-compatible。

Path: JsonFileLocalCorpusRegistry.document_store_path（内部self._path、
  runtime_data_root/scope_keyから構築済み）
  -> LocalCorpusDocumentSource.__init__が受け取ったproject_rootと
  組み合わせて_storage_display_path()で1度だけ導出・キャッシュ
  -> 同じ4段階中継でDocumentationCitation.storage_display_pathへ。

現行User Profile相当（project_root配下にruntime_dataがNestされる既定
構成）での実測値: "runtime_data/persistent/default/local_corpus/
documents.json"（test_bootstrap.py拡張Testで確認、Scope Keyを
"mac-local-primary"にすれば同じPatternで
"runtime_data/persistent/mac-local-primary/local_corpus/documents.json"
となることをtest_local_corpus_document_source.pyのScope-key-differs
Testで別途確認済み）。
Project Root外Fallback（Host絶対Path非漏洩）:
  test_storage_display_path_never_leaks_a_host_absolute_path_outside_
  project_rootで確認。
```

## 8. Project Docs／Historical Citation／RAG OFFのRegression結果

```text
Project Docs: heading_breadcrumb/project_relative_pathは無変更
  （document_title/storage_display_pathは常にNone、Citation UIも
  従来のHeading/Path表示のまま）。既存Field順Test群、既存
  test_project_docs_citation_keeps_its_original_source_class_unchanged
  ともにPASS。
Historical Citation: test_nazuna_probe_orion_freshness_update_delete_
  regression／test_nazuna_probe_orion_candidate_presentation_
  regression／test_deleted_local_corpus_document_denies_a_stale_code_
  from_conversation_history_regression（P7-RW2〜RW4由来、いずれも
  1行も変更せず）全件PASS。過去Turn Citationはstorage_display_path
  欠損のままFallback表示され、当時のEvidenceとして不変。
RAG OFF: test_rag_disabled_turn_reports_not_present_not_corrupt
  （無変更）PASS。Citation Store Write 0を維持。
```

## 9. Internal Review結果

Recovery Index §9に全観点を記録済み。Critical／Major／MVP Blocker 0件。Minor 1件のみ。

```yaml
finding_id: P7-RW5-IR-001
severity: minor_observation
disposition: known_deferred_non_blocking
summary: Local Corpus実保存PathのProject Root外Fallback表示形は
  Handoffが明示的Literalで指定していない実装側の合理的補完（Host絶対
  Path/User名を漏らさない、という定性要件からの導出）。現行User
  Profileは常にProject Root内（既定）に該当するため、Acceptance判定へ
  影響しない。
```

Rework Cycle: 不要（Handoff §8「Critical／Major／MVP Blockerが見つかった場合だけ」に該当する事項が0件のため）。

## 10. Canonical検証（最終差分、各1回）

```text
[Backend]
uv run pytest -q                     -> 1952 passed, 7 deselected
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted

P7-RW4基準（1944 passed）から+8、全件新規Test。Regression 0。

[Frontend]（本Package内でFrontend Sourceを変更したため、Handoff §8
の指示どおり再検証を実施。Node v25.8.1（既存Install）のみ使用、
npm install等のNetwork Actionは0件——既存node_modulesを再利用）
cd frontend && npm run typecheck     -> エラー0件
cd frontend && npm test
  (NODE_OPTIONS=--no-webstorage vitest run)
                                      -> 29 files / 268 tests passed
cd frontend && npm run lint          -> エラー0件

P7-RW3-D基準（262 tests）から+6、全件新規Test。Regression 0。
```

## 11. Incident／PARTIAL／NOT RUN

```text
Incident: 0件（P7-RW3-INCIDENT-001のようなNode再Install等の逸脱は
  発生していない）。
PARTIAL: 0件（Handoff §6のACC-001〜012、§7のRegression Scenario
  1〜10いずれも全件実施・PASS）。
NOT RUN: Real Model／Real Browserでの実画面確認——Handoff §8で
  明示的に禁止されているため未実施。次項User Manual Testへ委譲。
```

## 12. User Manual Testが必要な最小項目

```text
1. Local Corpus Document削除前後で、RAG ON+NO_HIT応答のCitation表示が
   Final回答確定後・Conversation切替後・Browser Reload後も一貫して
   「参照文書」欄に残ることを実画面で確認する。
2. Local Corpus Documentを1件登録し、そのCitationのLabelが「Title」で
   登録Titleと一致し、Project Docs CitationのLabelは引き続き
   「Heading」であることを実画面で確認する。
3. 同Local Corpus CitationのPath行が、Settings画面等で確認できる
   実際のRuntime Data保存場所（例:
   runtime_data/persistent/<現行Scope>/local_corpus/documents.json）
   と一致し、Copy Buttonでコピーした値も同じ文字列であることを
   実画面で確認する。
4. Project Docs CitationのHeading/Pathが、本Package適用前と見た目・
   値ともに変化していないことを実画面で確認する。
```

## 13. Exact Next Action

Codex Controller Bounded Independent Review待ちで停止する。

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Phase 7 ClosureまたはUser Manual PASSを代行しない。P7-CODEX-011／012／013は既存のUser実画面Gate（`TECHNICALLY_RESOLVED_USER_BROWSER_GATE`／`TECHNICALLY_RESOLVED_USER_REAL_MODEL_GATE`）を維持したまま、本Packageでは変更していない。
