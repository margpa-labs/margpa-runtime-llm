# Phase 6 Copilot R12 Internal Review Finding Ledger

```yaml
document_type: internal_review_finding_ledger
cycle_1: complete
cycle_2: pending_canonical_verification
scope: P6-CODEX-069_TO_073
```

| ID | Finding | Disposition |
|---|---|---|
| P6-R12-IR-001 | ENFORCE cancel graceのproduction defaultがbootstrap fixed constantに残っていた。 | Reworked: Frozen `StageBudgetProfile.cancel_grace_ms`からrun内で導出。 |
| P6-R12-IR-002 | ENFORCE terminal projectionのdefensive empty-content pathが英語固定fallbackへ到達した。 | Reworked: `present_evaluation_failure(..., frozen_language)`へ統一。 |
| P6-R12-IR-003 | Judge Evidenceのsuffix identityを除去するとlatest outcomeだけのUIがcurrentと誤表示し得る。 | Reworked: API `correlation`とUIのsame-id Current／Historical-Unmatched分離を追加。 |

Cycle 2はcanonical static/full regression後に記録する。Self-reviewであり、Codex Independent Reviewではない。
