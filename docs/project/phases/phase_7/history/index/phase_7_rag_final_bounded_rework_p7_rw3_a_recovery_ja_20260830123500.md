# Phase 7 RAG Grounding／Citation UI Final Bounded Rework — Package P7-RW3-A Recovery（Citation UI一回修正）

```yaml
document_id: phase_7_rag_final_bounded_rework_p7_rw3_a_recovery_20260830123500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 12:35:00 JST
active_contract: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md
package: P7-RW3-A
finding: P7-CODEX-011
```

## 0. Recovery Index Pointer

前Package: [P7-RW3-0 Recovery](phase_7_rag_final_bounded_rework_p7_rw3_0_recovery_ja_20260830122000.md)。次Package: [P7-RW3-B Recovery](phase_7_rag_final_bounded_rework_p7_rw3_b_recovery_ja_20260830125500.md)。

## 1. Root Cause

`frontend/src/styles/app.css`の`.message-citation`が2列CSS Gridで、3つのCopy Button全てへ同一の`grid-column: 2; grid-row: 1 / span 2;`を指定していた。3個のButtonが同一Cellへ強制配置され、最後のButtonだけが可視状態になっていた。加えて、短縮Chunk ID／Document DigestにField Labelがなく、どちらがChunk IDでどちらがDocument Digestか画面上で判別できなかった。

## 2. 修正内容

### 2.1 CSS（`frontend/src/styles/app.css`）

Grid由来の共有Cellを廃止し、Citation 1件をField単位の独立Flex Rowへ分解した。

```text
.message-citation: display:flex; flex-direction:column（各Rowを縦積み）。
.message-citation-row: display:flex; flex-wrap:wrap（各Fieldを横並び、狭幅で折り返し）。
.message-citation-field-label: 固定幅のLabel。
.message-citation-row button: flex:0 0 auto（Rowごとに1個だけ、重なりが構造的に不可能）。
```

Grid（同一Cellへの強制配置）を完全に削除したため、以前のOverlap Bugと同じ機構は物理的に再発しない。

### 2.2 Markup（`frontend/src/components/CitationsSection.tsx`）

Citation 1件を、Handoff §6.1指定の5独立Rowへ分解した。

```text
Source: Local Corpus / Project Docs
Path: <project_relative_path>          [Pathをコピー]
Heading: <heading_breadcrumb>
Chunk ID: <短縮chunk_id>               [Chunk IDをコピー]
Document Digest: <短縮document_sha512> [Document Digestをコピー]
```

各短縮値は`title`属性へ完全値を保持（既存のHover挙動を維持）。過去Citation Recordの値自体は変更していない（Renderer変更だけで新Layoutが適用される）。

### 2.3 i18n（`frontend/src/i18n/translations.ts`）

`citationFieldSource`／`citationFieldPath`／`citationFieldHeading`／`citationFieldChunkId`／`citationFieldDocumentDigest`をja/en両方に追加した。

## 3. Test（`frontend/src/components/CitationsSection.test.tsx`）

既存4 Testに加え、Handoff §6.3の必須観点を直接Assertする3 Testを追加した。

```text
test_shows_a_distinct_labeled_row_for_every_required_citation_field:
  全FieldのLabelが可視Textとして存在することを確認。
test_renders_three_distinct_visible_copy_buttons_that_each_copy_their_own_field:
  3個のButtonがSetとして3個（＝別Element）であること、それぞれが
  Path／Chunk ID／Document Digestの正しい値だけをCopyすることを確認。
test_shows_distinct_chunk_ids_sharing_the_same_document_digest_for_two_chunks_of_one_document:
  同一DocumentのChunk 2件がChunk IDは異なりDocument Digestは同一のまま
  正しく表示されることを確認。
```

Narrow Container Layoutでの視覚的重なりなしは、jsdomがCSS Layoutを計算しないためAutomated Testでは直接検証できない。共有Grid CellというOverlap Bugの機構自体をCSSから完全に除去したこと（Flex Rowは構造的にOverlapし得ない）をCode Reviewで確認した。ライブBrowserでの視覚確認は、Project外へのLocalhost HTTP Serverを要する（本Handoffの「Network Access不可」制約と衝突するため）行わず、Structural CodeとTestの両輪で代替した——詳細はP7-RW3-D Recoveryの§5（Network Action Disclosure）を参照。

## 4. 検証

```text
frontend: npx vitest run src/components/CitationsSection.test.tsx -> 7 passed
frontend: npx tsc --noEmit -> エラーなし
frontend: npx eslint . -> エラーなし
```

## 5. Scope境界

Local Corpus／Project DocsのSource Label、Project Docs Citation Identityはいずれも保持した。過去Citation Recordの値は変更していない。UI Polish（配色調整、Animation等）や製品化Hardeningへは踏み込んでいない。

## 6. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation:
  Frontend: CitationsSection.tsx, translations.ts, app.css（Source）、
    CitationsSection.test.tsx（Test、3新規Test）
Root外Read/Write: 0
```

Exact next action: P7-RW3-B（Identifier False Grounding一回修正）へ連結して進む。
