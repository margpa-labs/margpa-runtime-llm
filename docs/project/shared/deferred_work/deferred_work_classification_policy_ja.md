# Deferred Work分類Policy

```yaml
document_id: deferred_work_classification_policy
document_type: stable_work_status_policy
document_state: active
recorded_at: 2026-09-06 18:31:15 JST
language: ja
authority_owner: Nazuna Research
```

## 1. 三分類

- `planned_work`（予約）：将来実施する方針と、Phase・Trigger・前提条件のいずれかが決まっている作業。
- `deferred_work`（保留）：意図的に先送りまたは停止しており、実施時期・採否・再開条件のいずれかが未確定な作業。
- `unresolved_work`（未解決）：現時点で解決していない欠陥、設計問題、調査事項または判断待ち。

保留を予約や未解決へ混在させない。実施が決まれば`planned_work`へ、問題として追跡すべき状態になれば`unresolved_work`へ、判断記録を残して移管する。

## 2. 保存先

- 現在有効な保留事項のStable整理先：`docs/project/shared/deferred_work/`
- 保留化、再開、移管、失効などのAppend-only履歴：`docs/project/shared/history/deferred_work/`

本Policy制定後に新規作成する保留系文書は、この二つの役割に従い`planned_work`へ入れない。

## 3. History原則

過去文書は所在自体がEvidenceである。既存のHistory文書を移動・削除・上書きして分類を直したことにしない。分類変更は新規文書またはPhase 10統合時の対応表で追跡可能にする。
