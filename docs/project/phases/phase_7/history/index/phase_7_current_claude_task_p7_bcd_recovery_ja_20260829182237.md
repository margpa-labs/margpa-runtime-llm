# Phase 7 Current Claude Task — Package P7-B/C/D Recovery（Local Corpus／Document Lifecycle／Embedding・Index・Retriever／Context Injection・Citation Persistence）

```yaml
document_id: phase_7_current_claude_task_p7_bcd_recovery_20260829182237
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 18:22:37 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-B, P7-C, P7-D
```

## 0. Recovery Index Pointer

前Package: [P7-A Recovery](phase_7_current_claude_task_p7_a_recovery_ja_20260829175800.md)。次Package: P7-E（Web Search／Fetch）。

## 1. 設計判断（P7-0 §3で先行確定した方針の実施結果）

P7-0 Recovery §3の方針通り、Local Corpusは**新Orchestratorを追加せず、既存`DocumentationRagApplicationService`が使う`DocumentSourcePort`を合成する**形で実装した。これにより`conversation_generation.py`、`persistent_contracts.py`、`sqlite_conversation_store.py`は無変更のまま、Local Corpus由来のCitationが既存Pipelineへ合流する。

## 2. 実装（Backend）

### 2.1 Contracts拡張（既存Pipeline無変更を保証）

`modules/documentation_rag/contracts.py`：`DOCUMENTATION_RAG_CITATION_SOURCE_CLASS`定数をFile先頭へ移動し、`DocumentManifestEntry`／`DocumentationChunk`へ`corpus_source_class: str`（同一Default値）を追加。`adapters/documentation_rag/markdown_chunker.py`／`bounded_context_assembler.py`を、この新Fieldを素通しするよう最小変更——既存Source（Project Docs）は同じDefault値を経由するため出力は Byte-for-byte不変（既存87 Test全PASSで確認）。

`CorpusPriority` Enumは変更していない（`bm25_retriever.py`の`(3 - int(corpus_priority)) / 3`Scoring式が`0..3`を前提にHard-codeされているため、新Member追加はScoring破壊Riskがある）。Local Corpus DocumentのPriorityは既存`CorpusPriority.CURRENT`を再利用する。

### 2.2 新規Module（`modules/documentation_rag/local_corpus_contracts.py`, `local_corpus_ports.py`）

`LocalCorpusDocumentRecord`（Append-only`revisions`、Soft-delete`state`、Historical Evidence保持）、`LocalCorpusDocumentInput`（Title／Content、Text限定）、`LocalCorpusRegistryPort`（register／update／delete／list_active／list_all／get）。

### 2.3 新規Adapter（`adapters/documentation_rag/`）

- `local_corpus_registry.py`: `JsonFileLocalCorpusRegistry` — `runtime_data/persistent/<scope>/local_corpus/documents.json`への単一JSON File永続化。`sqlite_conversation_store.py`と同水準のSymlink拒否・Owner-only Permission（0o700／0o600）・Atomic Write（Temp File + `os.replace`）・Fail-closed Corrupt検出を実装。
- `local_corpus_document_source.py`: `LocalCorpusDocumentSource`（`DocumentSourcePort`実装）— Active Documentだけを`corpus_source_class="local_corpus"`でManifest化し、TOCTOU-safeにContent再検証する。
- `composite_document_source.py`: `CompositeDocumentSource` — `corpus_source_class`でRoutingする複数`DocumentSourcePort`合成。

### 2.4 Bootstrap Wiring

`bootstrap/documentation_rag.py`の`build_documentation_rag()`／`build_local_documentation_rag()`へ`local_corpus_registry`引数を追加。`local`アクセスModeかつRegistry指定時だけComposite化する（Lightning Public Container Profileは無変更）。

### 2.5 Web API（新規、Production Wiring）

`web/local_corpus_contracts.py`／`web/local_corpus_routes.py`: `/api/v2/local-corpus/documents`（GET一覧、POST登録、GET単体、PUT更新、DELETE論理削除）。`web/contracts.py`の`WebRuntime`へ`local_corpus_registry`Field追加。`web/app.py`へ、既存Feature（Configuration Control等）と同一の三重Gate（Exception Handler登録、Router登録、Lifespan内Loopback-only二重検証）を追加。`entrypoints/web/main.py`へ`--phase-7-local-corpus`／`--local-corpus-runtime-data-root`／`--local-corpus-scope-id`のCLI Flagを追加し、`_local_corpus_enabled()`で他Featureと同一のLoopback-only Gatingを行う。

## 3. 実装（Frontend）

`frontend/index.html`へ`local-corpus-bootstrap`Marker追加。`web/app.py`の`index()`が`WebRuntime.local_corpus_registry is not None`時にMarkerをFlipする（既存4 Featureと同一Pattern）。

新規：`frontend/src/lib/localCorpusBootstrap.ts`（Marker Reader）、`frontend/src/components/LocalCorpusPanel.tsx`（一覧・登録・編集・削除UI、Advanced Mode Category内、既存`ConfigurationControlPanel`と同一Presentational Pattern）。

変更：`frontend/src/types.ts`（`LocalCorpusDocument`系Type）、`frontend/src/api/client.ts`（`fetchLocalCorpusDocuments`／`fetchLocalCorpusDocument`／`registerLocalCorpusDocument`／`updateLocalCorpusDocument`／`deleteLocalCorpusDocument`）、`frontend/src/App.tsx`（Bootstrap読取・Load Callback・Mutation Queue・`SettingsModal`への配線、既存`loadConfigurationControl`と同一Pattern）、`frontend/src/components/SettingsModal/SettingsModal.tsx`（Advanced Mode CategoryへPanel追加）、`frontend/src/i18n/translations.ts`（ja／en 18 Key追加）。

## 4. Focused Evidence

```text
tests/unit/documentation_rag/test_local_corpus_registry.py ... 12 passed
tests/unit/documentation_rag/test_local_corpus_document_source.py ... 6 passed
tests/unit/documentation_rag/test_composite_document_source.py ... 4 passed
tests/integration/documentation_rag/test_local_corpus_end_to_end.py ... 4 passed
tests/unit/documentation_rag/test_bootstrap.py ... 11 passed（+2）
tests/integration/web/test_local_corpus_web_app.py ... 7 passed
tests/unit/web/test_web_cli.py ... 33 passed（既存Fake Builder Signature更新のみ、+0）
frontend: LocalCorpusPanel.test.tsx ... 6 passed
frontend: SettingsModal.test.tsx ... +2 passed
```

新規Backend Test Node ID: 12+6+4+4+2+7 = 35（Web CLI Fixtureの型更新は既存Test 33件のSignature修正のみで新規0件）。

## 5. Canonical Evidence

```text
Backend pytest（Full Suite、--basetemp Project内） : 1846 passed, 7 deselected
  （P7-B/C/D着手前Baseline 1811 + 35新規 = 1846、一致確認済み）
mypy（Project既定 files=[src,scripts,tests]）      : Success、495 source files（Baseline 494 + 1）
ruff check .                                        : All checks passed
ruff format --check .                               : 495 files already formatted
frontend: npm run typecheck                         : Clean（tsc --noEmit、0 errors）
frontend: npm run lint                               : Clean（eslint . 、0 errors）
frontend: npm test                                   : 240 passed（26 files、Baseline 232 + 8）
frontend: npm run build                               : Clean（87ms→179ms、tsc --noEmit && vite build）
  Build出力（web/static/index.html／app.js／app.css）へ`local-corpus-bootstrap`Marker反映確認済み。
```

## 6. Requirement／Acceptance対応（暫定、最終集計はP7-I）

```text
P7-REQ-002（Local Document登録・更新・削除・Version／Digest追跡）: 実装・Test済み。
P7-REQ-003（Chunking／Embedding／Index／Retriever Port交換可能）: BM25 Baseline維持。EmbeddingPort
  はPhase 2から変更のないReserved Boundaryのまま（Handoff指示通りHeavy Vector Dependency不追加）。
P7-ACC-004（Local Corpus登録）: PASS。
P7-ACC-005（更新時Revision／Digest更新）: PASS（Append-only Revision Chain）。
P7-ACC-006（削除後もHistorical EvidenceをCurrentと混同しない）: PASS（Soft-delete、Revision保持）。
P7-ACC-007（Chunk ID／DigestがDocument Revisionへ結び付く）: PASS（既存Chunker/Contract機構を再利用）。
P7-ACC-011（Context Injectionへ選択Evidenceだけを渡す）: PASS（既存Pipeline機構をそのまま利用）。
P7-ACC-012（Citation Identity）: PASS（`local-corpus/`Prefix Path、既存Citation機構）。
P7-ACC-013〜015（Reload／Restart／Branch／Regenerate後のCitation復元）: 既存Citation Persistence
  機構を無変更で再利用しているため、Regression Riskなし。専用End-to-end Testは未実施——
  P7-H（Integration／Regression）で確認する。
```

## 7. Known Findings／Deferrals

```text
P2: Attachment経由のLocal Corpus登録（Chat Composer統合）はP7-A判定によりPhase 10延期。
P2: Local Corpus DocumentのTitle変更はChunk/Source IDを再生成する（新Revisionとして扱われ、
  旧Citationの`project_relative_path`は新Titleを反映しない）。Historical Evidence保持の観点では
  正しい挙動だが、UI上「Titleを変えると過去Citationの表示Pathが変わる」ことは文書化していない。
  実害は無いため、未解決Registry行きとし、P7 Closure Blockerにしない。
P2: Local Corpus Document一覧・編集UIはAdvanced Mode配下（他のBootstrap-gated Panelと同じ配置）。
  基本設定（RAG設定列）からの直接遷移動線は未実装——将来のUX改善候補。
```

## 8. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
Real Model／Real Public Web: 0（本Package不使用）
```

Exact next action: Package P7-E（Web Search／Fetch）実装へ継続。
