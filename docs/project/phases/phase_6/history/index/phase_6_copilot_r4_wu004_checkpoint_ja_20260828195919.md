# Phase 6 Copilot R4 WU-004 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
package: P6-RR-R4
work_unit: R4-WU-004
status: COMPLETE
```

Repair ExecutorへJudge RunでFreezeしたStage Budget、Rejudge Service、Provider Identity、Independence Roleを渡した。Dedicated SeleneのServiceが取得不能ならMainへ暗黙Fallbackせず、`frozen_rejudge_service_unavailable`でfail closedする。
