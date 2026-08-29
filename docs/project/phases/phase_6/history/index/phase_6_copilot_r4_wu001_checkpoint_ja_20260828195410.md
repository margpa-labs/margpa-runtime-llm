# Phase 6 Copilot R4 WU-001 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
package: P6-RR-R4
work_unit: R4-WU-001
status: COMPLETE
```

Judge Hook開始時にActive Adapter/ProviderからStage Budgetを一回だけ解決し、Run全体へFrozen `StageBudgetProfile`を渡す。Resolver例外は既存Main-shared Profileへ明示的にfail-safeする。
