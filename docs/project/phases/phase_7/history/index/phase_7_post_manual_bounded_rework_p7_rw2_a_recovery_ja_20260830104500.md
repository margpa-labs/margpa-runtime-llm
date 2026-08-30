# Phase 7 Post-Manual Bounded Rework — Package P7-RW2-A Recovery（Citation Identity Projection）

```yaml
document_id: phase_7_post_manual_bounded_rework_p7_rw2_a_recovery_20260830104500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 10:45:00 JST
active_contract: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
package: P7-RW2-A
finding: P7-CODEX-007
```

## 0. Recovery Index Pointer

前Package: [P7-RW2-0 Recovery](phase_7_post_manual_bounded_rework_p7_rw2_0_recovery_ja_20260830103000.md)。次Package: P7-RW2-B Recovery。

## 1. 実施内容

Handoff §6.1が要求する8Field（source_class, project_relative_path, heading_breadcrumb, chunk_id, document_sha512, retrieval_score, selected_order, truncated）を、Live SSEとPersistent Detailの双方へ損失なく投影した。

```text
Backend:
  DocumentationCitation（modules/documentation_rag/contracts.py）
    -> source_class Fieldを追加（既定値
       DOCUMENTATION_RAG_CITATION_SOURCE_CLASS付き、既存Recordを
       Backward Compatibleに読める）。
  SystemCitationAdapter.build()（adapters/documentation_rag/
  system_citation_adapter.py）
    -> DocumentationReferenceBlock.source_classをCitationへ渡すよう1行追加。
  PersistentCitationResponse（web/persistent_contracts.py）
    -> source_class, chunk_id, document_sha512の3 Fieldを追加。
  _project_turn_citations()（web/persistent_contracts.py）
    -> 上記3 Fieldを新たに投影。
  project_persistent_event()のRETRIEVAL分岐（web/persistent_streaming.py）
    -> 同じ3 FieldをLive SSE Dataへ追加。

Frontend:
  Citation型（types.ts）
    -> source_class, chunk_id, document_sha512, retrieval_score,
       selected_order, truncatedを追加（既存project_relative_path,
       heading_breadcrumbは維持）。
  CitationsSection.tsx
    -> source_classでLocal Corpus／Project Docsを明示Label区別。
    -> Chunk ID／Document Digestを短縮表示（title属性へ完全値）。
    -> Path／Chunk ID／Document DigestそれぞれへCopy Button追加
       （Copyされる値は常に完全値、短縮表示ではない）。
  i18n（translations.ts）
    -> citationSourceLocalCorpus, citationSourceProjectDocs,
       copyChunkId, copyDocumentDigestをja/en両方へ追加。
```

## 2. Backward Compatibility

`DocumentationCitation.source_class`は既定値付きのため、`P7-CODEX-006`以前に永続化されたCitation Record（`source_class`列を持たないJSON）も`PersistedTurnCitationEvidence.model_validate()`でそのまま復号できる。`citation_schema_version`は`1`のまま変更していない（Handoffの「必要なら追加Fieldを既存既定値付きで読む」指示に一致、Version Bumpは不要と判断）。

## 3. Regression（Handoff §6.2 全項目に対応）

```text
Live SSE Projection Test:
  tests/integration/web/test_persistent_web_app.py::
  test_citations_survive_reload_fetch
  -> CitingSession.events()へRETRIEVAL Eventを追加し、実際の
     project_persistent_event()経路を通過させた上でSSE Text内の
     chunk_id/document_sha512/source_classを直接assert。

Persistent Detail Projection Test:
  同上Test内、Reload GETのJSON Bodyでchunk_id/document_sha512/
  source_classを直接assert（既存project_relative_pathのAssertも維持）。

Citation SQLite Round-trip／旧Record Compatibility Test:
  tests/unit/conversation/test_citation_evidence_sqlite_store.py::
  test_pre_source_class_citation_record_still_decodes_with_default
  -> 保存済みJSONからsource_classを削除しDigestを再計算した上でDecodeし、
     既定値documentation_rag_citationへ復元されることをassert（新規追加）。

Frontend Type／Render／Copy Test:
  frontend/src/components/CitationsSection.test.tsx（新規4 Test）
  -> Local／Project Docs区別描画、短縮表示と完全値のtitle属性、
     Chunk ID／Document DigestのCopy Buttonが完全値をClipboardへ渡すこと、
     Citation 0件時のEmpty表示を確認。

Local CorpusとProject DocsのSource Class区別Test:
  test_citations_survive_reload_fetchの_citation_augmentation()を
  2件Citation（documentation_rag_citation 1件、local_corpus 1件）へ拡張し、
  SSEとPersistent Detailの両方で両Source Classを区別してAssert。
```

## 4. 実行結果

```text
uv run pytest tests/unit/conversation/test_citation_evidence_sqlite_store.py
  tests/integration/conversation/test_persistent_citation_evidence.py
  tests/integration/web/test_persistent_web_app.py::
  test_citations_survive_reload_fetch
  -> 24 passed

uv run pytest tests/unit/documentation_rag/ tests/integration/documentation_rag/
  tests/integration/web/ tests/unit/web/
  -> 391 passed（Regression 0を確認）

uv run mypy <touched backend files>       -> Success, no issues
uv run ruff check <touched backend files> -> All checks passed

frontend: npx tsc --noEmit                -> エラーなし
frontend: npx eslint <touched files>      -> エラーなし
frontend: vitest run CitationsSection.test.tsx -> 4 passed
```

## 5. Scope境界の遵守

Title変更時のSource／Chunk ID再生成、Embedding、Vector Store、汎用File Attachment、Phase 6 Debtへは触れていない。過去Turnの永続Citation Identityは書き換えていない（既存`citation_schema_version=1`のまま、追加Fieldは既定値経由の後方互換のみ）。

## 6. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation: Backend 5File（contracts.py, system_citation_adapter.py,
  persistent_contracts.py, persistent_streaming.py,
  test_persistent_web_app.py）＋test_citation_evidence_sqlite_store.py。
  Frontend 4File（types.ts, CitationsSection.tsx, translations.ts,
  CitationsSection.test.tsx新規）。
Root外Read/Write: 0
```

Exact next action: P7-RW2-B（Current Turn Freshness／Grounding）へ連結して進む。
