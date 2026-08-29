# Phase 6 Copilot R4 Final Recovery

```yaml
document_type: phase_package_final_recovery_index
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
package: P6-RR-R4
status: COMPLETE_CANDIDATE
next_exact_work_unit: R5-WU-001
```

R4-WU-001〜006を完了した。Provider別Stage BudgetをJudge開始時にFreezeし、Built-inのModel Call/LLM Deadline 0を維持した。Repair RejudgeはFrozen Service/Provider/Role/Budgetを受け、Dedicated Service不在でMainへ暗黙Fallbackしない。R4 Focused Regression 64件と対象Mypy/Ruffは成立した。
