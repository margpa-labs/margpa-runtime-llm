# Phase 8 P8-RW6 二段階Controller Review — 未解決Snapshot

```yaml
document_id: phase_8_rw6_two_cycle_controller_review_unresolved_snapshot_20260831065406
document_type: unresolved_finding_snapshot
document_state: frozen_historical
language: ja
created_at: 2026-08-31 06:54:06 JST
source_review: docs/project/phases/phase_8/history/operations/phase_8_codex_controller_rw6_two_cycle_targeted_re_review_ja_20260831065406.md
```

## Snapshot

| Finding | Severity／Priority | Closure Blocker | Disposition |
|---|---|---:|---|
| P8-CODEX-011 | Moderate／P1 | No | Completion GateはRuntimeで成立するが、Frozen Envelopeの`gate_reasons`へ`completion`が現れない。未解決Registryへ延期。 |
| P8-CODEX-012 | Major／P0 | Yes | Constitution PreviewがDecision Outcomeだけを表示し、Exact Handoff指定のAction Permission／Violation Presentation比較を欠く。P8-ACC-021をPARTIALへ戻し、User Manual前に限定Rework。 |

P8-CODEX-005／006は解消済み。P8-CODEX-007は中心Runtime上解消済みで、P8-CODEX-011はAuthority Bypassを伴わない
Observability Contract差として分離した。P8-CODEX-008はPreview入口までは成立したが、P8-CODEX-012により完全解消Claimを撤回する。

Canonical検証はFrontend 302件、Mypy、RuffがPASS。Backendは2121 PASS／3 FAIL／7 deselectedで、3件は既知の
P8-CODEX-010（Network制限下の非Hermetic Test）と同一であり、RW6 Regressionではない。
