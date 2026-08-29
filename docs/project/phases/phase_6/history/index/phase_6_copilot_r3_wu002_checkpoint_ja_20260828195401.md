# Phase 6 Copilot R3 WU-002 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
package: P6-RR-R3
work_unit: R3-WU-002
status: COMPLETE
```

Current Sourceを再導出し、Main-shared DispatchはFrozen `SemanticTurnSnapshot.criteria`を`JudgePromptCriterion`へ、Dedicated Selene Dispatchは同一Snapshotを`SemanticEvaluationRequest`へ渡すことを確認した。Dispatch RouterのFocused Regressionで両経路を検証した。
