# Phase 6 Governance Debt — 新Phase 10移管Snapshot

```yaml
document_id: phase_6_governance_debt_new_phase_10_transfer_snapshot_20260829175551
document_state: historical_snapshot
language: ja
created_at: 2026-08-29 17:55:51 JST
authority_owner: Nazuna Research
source_registry: docs/project/shared/未解決/current_unresolved_findings_registry_ja.md
decision: transfer_to_new_phase_10
```

## Decision Snapshot

2026-08-29、UserはPhase 6で未成立だった次の中心課題を、新Phase 10へ正式移管した。

| Finding | 技術状態 | Phase 7〜9暫定 | 再開先 |
|---|---|---|---|
| Selene Dedicated Judge | Configured／Active none | Built-in DeterministicまたはNone／OFF | 新Phase 10 |
| Qwen3Guard Dedicated Guard | Configured／Active none | Built-in Rule／Pattern Base | 新Phase 10 |
| GD Semantic 109件 | Deferred／evaluated 0 | 未評価を捏造せずDeferred保持 | 新Phase 10 |
| Judge／Repair Golden Path | 未成立 | Built-inの能力範囲だけ使用 | 新Phase 10 |
| Main Semantic ENFORCE | 未成立 | 構造Rule／既存Baselineのみ | 新Phase 10 |

SeverityはMajorのまま保持するが、現在のPoC／MVP進行に対するClosure Blockerではない。Phase 6で成立したProvider Registry、Lifecycle、Budget、Failure、Recording、Built-in／Rule-based PortおよびGD Compiler入口を再利用し、ゼロから再実装しない。

詳細理由とConstitution層への教訓は次を正本とする。

`docs/project/phases/phase_6/history/operations/phase_6_governance_semantic_runtime_difficulty_retrospective_and_phase_10_transfer_ja_20260829175551.md`
