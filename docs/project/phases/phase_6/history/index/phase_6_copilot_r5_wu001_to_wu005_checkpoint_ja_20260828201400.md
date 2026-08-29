# Phase 6 Copilot R5 WU-001〜005 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
package: P6-RR-R5
work_units: [R5-WU-001, R5-WU-002, R5-WU-003, R5-WU-004, R5-WU-005]
status: COMPLETE_CANDIDATE
```

Turn開始時にFreezeした言語を、通常・早期terminal双方のENFORCE Safe Fallbackへ適用した。malformed、deadline、provider unavailable、activation、cancel、repair関連のFailure CodeはFrozen LanguageでPresentationされ、timeout文言は入力内容を原因としない。Failure reasonからFailure Classを決定し、Resultのfailure_message/failure_languageへ同じClassを投影する。
