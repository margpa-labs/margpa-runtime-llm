# Phase 8 User Mac Post-MR8 Final Delta — Unresolved Snapshot

```yaml
document_id: phase_8_user_mac_post_mr8_final_delta_unresolved_snapshot_20260831181553
document_type: append_only_unresolved_snapshot
document_state: frozen_history
language: ja
recorded_at: 2026-08-31 18:15:53 JST
decision_authority: user
stable_registry: ../../未解決/current_unresolved_findings_registry_ja.md
```

## 1. Phase 8 Closure前のCurrent Rework

| Stable ID | 内容 | Priority | Closure |
|---|---|---:|---|
| UF-P8-003 | Completion Gateが`external_write`と虚偽表示 | P0 | Block until micro fix |
| UF-UI-011 | 過去Web Failure警告がCurrent Composerへ残留 | P0 | Block until micro fix |
| UF-UI-012 | Untrusted Labelの文字色不統一 | P1 | 同Reworkで修正 |
| UF-UI-013 | 新しいDemo Run Button色不統一 | P1 | 同Reworkで修正 |

## 2. 解決へ更新した主要Finding

| Stable ID | 結論 |
|---|---|
| UF-P8-002 | Injected Resolver／RetryをController Full Suiteで確認 |
| UF-P8-005 | UTF-8 Public URL、Fail-closed Grounding、Hololive 5回以上成功 |
| UF-P8-006 | Phase 8最小本文抽出／Final Prompt Budget／Typed Failure成立 |
| UF-P8-007 | Failure ReasonのLive／Persistence／Reload／Restart成立 |
| UF-P8-008 | Archive Sidebar／Panel同期PASS |
| UF-P8-009 | Web Citation Metadata／Title／Copy／Persistence PASS |
| UF-P8-010 | Runtime Data Root内の実File Fixture／Informed Approval PASS |
| UF-UI-009 | Constitution比較行改行PASS |
| UF-UI-010 | 主要Dev Agent Button Contrast PASS。新例外はUF-UI-013へ分離 |

## 3. 延期

| Stable ID | 内容 | Target |
|---|---|---|
| UF-P7-005 | 無関係Project DocsのFalse-positive Grounding | Phase 9 |
| UF-P8-011 | Model Call 0のLive UI Observability | Phase 9 |
| UF-P8-012 | Shift_JIS／x-sjis対応／Failure Taxonomy | Phase 11 |
| UF-UI-014 | Settings Manual URL結果残留 | Phase 10 |
| UF-UI-015 | Manual URL Card表示整理 | Phase 10 |
| UF-UI-007 | 通常Composer URL貼付UX | Phase 10／11 |
| UF-UI-008 | Archive Dedicated Manage Modal | Phase 10 |

## 4. Research Evidence

公式Hololive Web Evidence取得前はQwenがUser訂正を拒み、誤った読みを維持した。公式Evidence取得後は同じ訂正を受容し、
`あまね かなた`へ修正した。Source Authority／ProvenanceとBelief Revision Successの関係を示す単一観測として、
Constitution／Judge研究Sourceへ分離保存した。因果関係は未確定である。
