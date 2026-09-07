# Phase 10 Docs統合 — Planned Work統合予約

```yaml
document_id: phase_10_docs_integration_planned_work_consolidation_reservation_20260906182208
document_type: planned_work_reservation
document_state: reserved
phase: phase_10
recorded_at: 2026-09-06 18:22:08 JST
language: ja
authority_owner: Nazuna Research
append_only: true
```

## 1. User決定

Phase 10のDocs統合では、Constitution、Shared Docs、各Phase累積文書だけでなく、Planned Workも統合対象へ含める。

対象は次の両方である。

- `docs/project/shared/planned_work/`
- `docs/project/shared/history/planned_work/`

## 2. 統合時の扱い

- `shared/history/planned_work/`は過去の予約、判断経緯、変更履歴を保持するAppend-only Historyとして残す。
- 現在も有効な予約、未着手作業、Phase 11以降の候補を抽出し、重複・失効・上書き関係を整理する。
- `shared/planned_work/`は、統合後に現在有効なPlanned Workを参照しやすくする非History側の整理先として扱う。
- History文書を削除、移動、上書きして整理したことにしない。
- 統合後の文書から、根拠となったHistory文書を追跡できる状態を維持する。
- 粒度、Index構造、正本境界はPhase 10の要件定義時に確定する。今回は実移行を行わない。

## 3. Phase 10 Gate

Phase 10 Docs統合の完了判定では、Planned Workの棚卸し・現行化・History分離が完了していることも確認する。Planned Workだけを統合対象から落とした状態でDocs統合完了とは扱わない。
