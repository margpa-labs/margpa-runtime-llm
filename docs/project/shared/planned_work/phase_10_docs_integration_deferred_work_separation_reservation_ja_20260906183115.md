# Phase 10 Docs統合 — Deferred Work分離予約

```yaml
document_id: phase_10_docs_integration_deferred_work_separation_reservation_20260906183115
document_type: planned_work_reservation
document_state: reserved
phase: phase_10
recorded_at: 2026-09-06 18:31:15 JST
language: ja
authority_owner: Nazuna Research
append_only: true
```

## 1. 実施内容

Phase 10のDocs統合時に、既存`docs/project/shared/history/planned_work/`を棚卸しし、予約・保留・未解決を分離する。

- 実施方針が決まっている予約は、`shared/planned_work/`のStableへ統合する。
- 意図的に先送りされ、時期・採否・再開条件が未確定な事項は、`shared/deferred_work/`のStableへ統合する。
- 現在も解決していない問題は、`shared/unresolved_work/`のStableへ統合する。
- 重複、上書き関係、失効済み事項を区別し、元Historyへの追跡情報を残す。

## 2. History移動方針

既存`history/planned_work/`文書は移動しない。Path変更によるLink破損と履歴改変を避けるためである。

Phase 10以降の新規保留履歴は`shared/history/deferred_work/`へ記録する。Phase 10では必要に応じ、旧`history/planned_work/`から保留として抽出した事項の対応表または統合Evidenceを`history/deferred_work/`へ新規追加する。

## 3. 完了条件

Phase 10 Docs統合は、予約・保留・未解決のStableが分離され、旧Historyとの対応を追跡できる状態までを完了条件に含める。
