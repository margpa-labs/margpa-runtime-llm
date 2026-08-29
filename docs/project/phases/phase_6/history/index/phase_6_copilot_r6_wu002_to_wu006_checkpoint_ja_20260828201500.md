# Phase 6 Copilot R6 WU-002〜006 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
package: P6-RR-R6
work_units: [R6-WU-002, R6-WU-003, R6-WU-004, R6-WU-005, R6-WU-006]
status: COMPLETE_CANDIDATE
```

Current Runはcurrent_request_id一致時だけlast_resultへ投影し、それ以外をHistoricalとして明示する既存境界を再導出した。OFFではCurrent Resultを持たずHistoricalを分離する。Configured/Active/Executed Providerはnull時もnoneとして表示し、Turn RecordingとJudge Evidence RecordingはRequest ID付きの一つのCorrelation Summaryへまとめた。Activation FailureはProvider Selectionのcanonical statusにFailure Reasonを保持し、Panel再表示で再取得する。
