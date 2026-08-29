# Phase 6 Copilot R4 WU-003 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
package: P6-RR-R4
work_unit: R4-WU-003
status: COMPLETE
```

Built-in Profileは`deterministic_no_model_call`で、Load、Prompt、Inference、Decode、Repair、Rejudgeの全Budgetを0とする。Built-in経路は既存どおりModel Call 0であり、Fixture RegressionでProfileとCall 0を検証した。
