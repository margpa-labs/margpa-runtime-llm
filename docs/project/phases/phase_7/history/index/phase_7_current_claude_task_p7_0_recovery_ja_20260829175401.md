# Phase 7 Current Claude Task — Package P7-0 Recovery（Entry／As-built Freeze）

```yaml
document_id: phase_7_current_claude_task_p7_0_recovery_20260829175401
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 17:54:01 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-0
```

## 0. Recovery Index Pointer

本Packageの後継（次のRecovery Index）: [P7-A Recovery](phase_7_current_claude_task_p7_a_recovery_ja.md)（作成後にPath確定）。

## 1. Mandatory Reading確認

Handoff §2記載の13文書を指定順で全文読了した（Role/Execution 4件、Phase 7 Canonical Design 6件、Boundary/Known Debt 3件）。Fresh Task化・旧Context否定は行わず、`fresh_task_required: false`のCurrent Roleをそのまま継続する。

## 2. Phase 2 RAG／Citation／Conversation As-built Map

```text
modules/documentation_rag/contracts.py
  DocumentManifestEntry, CorpusManifest, DocumentationChunk, RetrievalQuery/Result,
  AssembledDocumentationContext, DocumentationCitation, DocumentationEvidence,
  DocumentationAugmentation, PersistedTurnCitationEvidence（Reload/Restart/Branch/
  Regenerate後もCitationを復元する既存Contract）。
modules/documentation_rag/ports.py
  DocumentSourcePort, ChunkerPort, EmbeddingPort（未使用のReserved Boundary）,
  IndexStorePort, RetrieverPort, ContextAssemblerPort, CitationPort,
  ContextualRagOrchestratorPort, CitationEvidenceStorePort。
modules/documentation_rag/application/documentation_rag.py
  DocumentationRagApplicationService.augment_with_context() — Source非依存の
  Orchestrator。Manifest取得→Index Build（Lock保護）→BM25 Retrieve→Context Assemble→
  Citation Build→Evidence構築、の一本のPipeline。
adapters/documentation_rag/*
  local_filesystem_source.py（_ProjectMarkdownDocumentSource / LocalMarkdownDocumentSource
  / ExplicitMarkdownDocumentSource — 固定Whitelist Path、Symlink拒否、UTF-8必須）
  markdown_chunker.py（ATX見出し＋Fenceを認識するDeterministic Chunker）
  bm25_retriever.py（Score = body+heading+path+exact_phrase+corpus_priority、
    corpus_priority項は `(3 - int(corpus_priority)) / 3 * weight`）
  bounded_context_assembler.py（Token Budget内でReference Blockを構築、
    `[REFERENCE ref-N]...[/REFERENCE ref-N]` 形式でPrompt Injection対策）
  system_citation_adapter.py（選定Chunkだけから機械的にCitationを導出）
  in_memory_lexical_index.py, lexical_tokenizer.py, query_analyzer.py
bootstrap/documentation_rag.py
  build_documentation_rag() / build_local_documentation_rag() —
  Defaults(disabled/enabled) + Feature Profile(Local Schema 1 / Lightning Schema 2)を
  Toml Loadし、Adapter Graphを合成。`_DeferredTextTokenCounter`でModel Token Counterを
  遅延Bindする。
web/persistent_contracts.py
  PersistentTurnResponse.citations（PersistedTurnCitationEvidenceの安全な射影）。
conversation_generation.py
  ConversationGenerationSession が単一の`documentation_rag: ContextualRagOrchestratorPort`
  を保持し、`events()`冒頭で`augment_with_context()`を呼ぶ。`_context_source_items()`が
  `augmentation.reference_blocks`（`DocumentationReferenceBlock`、各own `source_class`
  フィールドを保持）を`_ContextSourceItem`へ展開し、Guardrail判定とPrompt Composition
  （`_inject_documentation_reference()`）の双方が同一Tupleを参照する。
```

## 3. Phase 7 Local Corpus拡張のためのCross-component設計判断（先行確定）

P7-B以降の実装Riskを最小化するため、本Package内で次を確定する。

### 3.1 既存Pipelineの再利用（新Orchestrator追加ではなく、Source合成）

`ConversationGenerationSession`は単一の`documentation_rag` Orchestratorしか受け取らない
Contractであり、これをN-source化するReworkはPhase 2の全Citation Contract（Evidence
Cross-field Validator群）に対するRegression Riskが高い。

そのため、Local Corpus（User登録Document）は**新しいOrchestratorを追加するのではなく、
既存`DocumentationRagApplicationService`が使う`DocumentSourcePort`を合成
（Project Docs Source + Local Corpus Source）する**設計を採る。これにより
`conversation_generation.py`、`persistent_contracts.py`、`sqlite_conversation_store.py`、
既存Frontend Citation表示は無変更のまま、Local Corpus由来のCitationが同じPipelineへ
自然に合流する（ADR-7-001「Phase 2 RAGを破棄せず拡張する」に合致）。

### 3.2 Corpus区別はSource Classフィールドで行う（CorpusPriority Enumは不変更）

`CorpusPriority`は`bm25_retriever.py`のScoring式`(3 - int(corpus_priority)) / 3 * weight`が
`0..3`の値域を前提にHard-codeされている。新しいEnum値（例：4）を追加すると
`(3-4)/3`が負値になりExisting Regression Riskとscoring破壊を招くため、追加しない。

代わりに、`DocumentManifestEntry`／`DocumentationChunk`／`DocumentationReferenceBlock`へ
`corpus_source_class: str`（Default値は現状Hard-codeされている
`DOCUMENTATION_RAG_CITATION_SOURCE_CLASS`と同一）を追加し、既存Sourceの出力・既存Testの
期待値を変えないまま、Local Corpus Sourceだけがこのfieldへ`"local_corpus"`を設定する。
`bounded_context_assembler.py`のBlock構築を、Hard-coded Defaultから
`selected.chunk.corpus_source_class`を読む形へ最小変更する（既存Sourceは同じDefault値を
経由するため、出力バイト列は不変）。

Local Corpus Documentの`corpus_priority`自体は既存`CorpusPriority.CURRENT`（0）を再利用する
（Userが明示登録したDocumentという性質上、既存の「現在Phase」相当の最高優先Tierが妥当で、
Enum変更・Scoring式変更を一切要さない）。

### 3.3 永続化Path規約

Local Corpus Document Registryは、既存`SqliteConversationStore`と同じ`runtime_data_root`配下
（`runtime_data/persistent/<scope>/local_corpus/`）へ書く。全Testは`tmp_path`等の一時Fixtureを
使い、実`runtime_data/`は一切参照・変更しない（運用メモ第2.5節）。

## 4. Phase 6 Known Debtとの非依存境界

次はPhase 7実装Scope外として触れない。

```text
Selene／Qwen3Guard実Activation（Configured／Active none）。
ARGD／DAGD Semantic 109件Deferred。
Built-in Judge evaluated 0、Judge／Repair Golden Path未成立。
```

Phase 7のRAG／Web Evidence機能が上記を解決済みへ読み替えることはない
（`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`が正本のまま）。

## 5. Test／Temp／Network Boundary固定

```text
pytest: --basetemp=<Project内一時Dir>を使用（Root外Temp不使用）。
Frontend: NPM_CONFIG_CACHE, TMPDIRをProject内へ明示。
Network: 本Package（P7-0）はNetwork Action 0。P7-E／FでFixture／Fake Providerのみ使用し、
  Real Public Web Probeは実施しない（費用対効果とResource制約により見送り、Evidence化する）。
Git: Read/Write一切行わない。
```

## 6. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package P7-A（Attachment Sizing）へ継続。
