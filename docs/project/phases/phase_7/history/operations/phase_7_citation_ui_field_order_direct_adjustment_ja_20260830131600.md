# Phase 7 Citation UI Field Order — Direct Adjustment

```yaml
document_id: phase_7_citation_ui_field_order_direct_adjustment_20260830131600
document_type: direct_user_requested_adjustment_record
document_state: final
language: ja
created_at: 2026-08-30 13:16:00 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_7
related_package: P7-RW3-A（P7-CODEX-011のCitation UI一回修正）
```

## 1. 経緯

P7-RW3-A（[Recovery](../index/phase_7_rag_final_bounded_rework_p7_rw3_a_recovery_ja_20260830123500.md)）で実装したCitation UIのField順序（Source／Path／Heading／Chunk ID／Document Digest）について、User実画面確認後、Userから直接「PathとHeadingの表示順を入れ替えてほしい」との指示を受けた。Bootstrap／Handoff経由ではない、直接のUI微調整依頼として即時対応した。

## 2. 変更内容

`frontend/src/components/CitationsSection.tsx`のField表示順を変更した。

```text
変更前: Source / Path / Heading / Chunk ID / Document Digest
変更後: Source / Heading / Path / Chunk ID / Document Digest
```

Field Label・Copy Button・短縮値表示など、P7-RW3-Aで実装した他の挙動（3 Button独立表示、Full値Copy等）はいずれも変更していない。Row単位のJSX 2ブロックを入れ替えただけであり、CSS（`app.css`）・i18n（`translations.ts`）・型（`types.ts`）はいずれも無変更。

## 3. 検証

```text
frontend: npx vitest run src/components/CitationsSection.test.tsx -> 7 passed
frontend: npx vitest run（全件）                                  -> 29 files, 262 tests passed
frontend: npx tsc --noEmit                                        -> エラーなし
frontend: npx eslint src/components/CitationsSection.tsx          -> エラーなし
frontend: npm run build                                            -> 成功
  （src/margpa_runtime_llm/web/static/app.js／app.css／index.htmlを再生成）
```

既存Testは`within(row).getByText(...)`等のSemantic Query（DOM順序に依存しない）でFieldを検証しているため、Test自体の変更は不要だった。

## 4. Action Inventory

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Source Mutation: frontend/src/components/CitationsSection.tsx（Row順序のみ）
Build Artifact再生成: src/margpa_runtime_llm/web/static/app.js, app.css, index.html
Test Mutation: 0（既存Testで無変更のままCover）
```

## 5. Scope

本調整はP7-RW3の3件Finding（P7-CODEX-011〜013）の解決状況には影響しない。[Exact Return Handoff](../../handoffs/phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_return_handoff_ja_20260830133000.md)（`maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`）の内容・Claimに変更はない。Codex Controller Bounded Independent Review待ちのStop状態は維持する。
