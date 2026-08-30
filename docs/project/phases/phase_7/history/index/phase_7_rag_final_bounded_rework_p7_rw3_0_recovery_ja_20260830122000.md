# Phase 7 RAG Grounding／Citation UI Final Bounded Rework — Package P7-RW3-0 Recovery（Entry／Exact Reproduction）

```yaml
document_id: phase_7_rag_final_bounded_rework_p7_rw3_0_recovery_20260830122000
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 12:20:00 JST
active_contract: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md
package: P7-RW3-0
```

## 0. Recovery Index Pointer

前Package: なし（本Handoffの最初のPackage）。次Package: [P7-RW3-A Recovery](phase_7_rag_final_bounded_rework_p7_rw3_a_recovery_ja_20260830123500.md)。

## 1. Digest照合

Exact Handoff (`phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md`) のSHA-512を`shasum -a 512`で照合し、Handoff記載値と一致を確認した。

```text
6820a837b65b3f529842b3b5aed2e9bdc233821f2f6e9b1427b5e75ad35ff6c6c22e641c2ef578f512858ff434e6d2f1d7002fd005bc78036bbb9bfd44fc3627
```

Mandatory Reading 4件のうち、Active Base HandoffとP7-RW2 Exact Returnは前SessionでSHA-512照合済み・全文既読（本Session冒頭でDigestのみ再照合）。Controller ReviewとUser Recheck Sheetの2件は本Sessionで新規にSHA-512照合・全文読了した。4件ともHandoff記載Digestと一致。

## 2. User Mac Failure Evidenceの理解

Handoff §3〜§4を読み、3件のFinding（P7-CODEX-011〜013）を把握した。

```text
P7-CODEX-011: Citation UIの3つのCopy ButtonがCSS Grid Cellを共有し重なって表示される。
P7-CODEX-012: Current ReferenceがSystem直後／全History前へ挿入されており、
  QwenがCurrent Referenceより過去History内の旧Assistant回答を優先してしまう。
P7-CODEX-013: BM25 BackfillがQuery Identifier Tokenとの「any overlap」だけを
  要求するため、`Nazuna`だけを共有するPhase 1 Docsが無関係にBackfillされる。
```

P7-CODEX-007（Backend Citation Projection）とP7-CODEX-009（Auto-Resume）はP7-RW2で解決済みのまま保持し、本Packageでは触れない。P7-CODEX-008はP7-CODEX-012／013へ再分類され、本Handoffで完全解決を目指す。

## 3. 修正前Testによる再現

Handoff §5の指示通り、3 Failureのうち Prompt順序とIdentifier Backfillの2件は、既存のCanonical Test Suiteを事前に全件実行し、修正前のBaselineとして記録した（1934 passed／7 deselected、P7-RW2-Dの最終状態と一致）。Citation UI Overlapは、`frontend/src/styles/app.css`の`.message-citation button { grid-column: 2; grid-row: 1 / span 2; }`を目視でSource確認し、3つのCopyButtonが同一Grid Cellへ配置される構造的BugであることをコードReviewで確認した（jsdomはCSS Layoutを計算しないため、Automated Testでは検出できない種類のBugであることも確認）。

## 4. Auto-Resume Sourceへの不可侵確認

`persistent_conversation_service.py`、`frontend/src/components/Sidebar/ChatListItem.tsx`は本Package開始時点で一切読み書きしていない。本Handoff完了まで、この2ファイル（およびP7-RW2-Cが変更した関連Test）には触れない方針を確認した。

## 5. Action Inventory

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Source／Test Mutation: 0（本Packageは読解・Digest照合・方針確認のみ）
```

Exact next action: P7-RW3-A（Citation UI一回修正）へ連結して進む。
