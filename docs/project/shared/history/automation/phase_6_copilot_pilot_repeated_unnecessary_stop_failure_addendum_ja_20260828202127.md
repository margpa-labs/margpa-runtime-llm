# Phase 6 Copilot Pilot — Repeated Unnecessary Stop Failure Addendum

```yaml
document_type: pilot_automation_failure_evidence
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
occurred_at: 2026-08-28 20:21:27 JST
severity: major
disposition: observed_and_remediated_for_this_task
supersedes: no
related_evidence: phase_6_copilot_pilot_unexpected_stop_and_microphone_ui_failure_ja_20260828200549.md
```

## Failure Matrix

| ID | 不適切な停止契機 | 本来の正しい挙動 | 実害 |
|---|---|---|---|
| COPILOT-P6-AUTO-STOP-001 | R6-WU-001完了をTask完了相当としてfinal応答 | R6-WU-002へ連続実行 | R6〜R8が未完了のまま停止 |
| COPILOT-P6-AUTO-STOP-002 | R3〜R5対象Regression完了をfinal応答 | R5残部とR6〜R8を継続 | Userによる再指示が必要 |
| COPILOT-P6-AUTO-STOP-003 | 停止理由の説明応答後に自走を再開しない | 説明後ただちに最後のRecoveryから再開 | Userによる再指示が必要 |
| COPILOT-P6-AUTO-STOP-004 | Tool結果のProvider側一時表示退避をRoot外Actionと誤認しSTOPPED_SAFEを宣言 | 自身のCommand/Mutationではない表示実装はIncidentとして記録し、許可Scopeを継続 | 不要な停止とUser負担 |

## Root Cause

CopilotがLong-running Companion §2の`Progress Reportは停止理由にしない`を、実行時に守らず、Work Unit完了・テスト完了・Provider Tool表示をTask終端と誤分類した。これはAuthority不足、Real Model Gate、実際のRoot外Command、Git、Network、runtime_data、Provider Memory、Browser、MicrophoneまたはOS Permission操作による停止ではない。

## Measured Action Inventory

```text
Git: 0
Network: 0
Provider Memory: 0
User runtime_data: 0
Real Model Load/Inference: 0
Browser/Microphone/OS Permission Tool/Command: 0
Project Root外Command/Mutation: 0
```

`/var/folders/.../T/` はCopilot Tool結果のProvider側退避表示として観測された。Copilot自身がそのPathを対象にCommand、Read、Write、Delete、NetworkまたはPermission操作を行った証拠はない。ゆえにCOPILOT-P6-AUTO-STOP-004のSTOPPED_SAFE判定は誤りである。

## Corrective Rule for This Pilot

1. `final`応答はExact Return、True StopまたはUser明示停止だけに限定する。
2. Work Unit/Test/Static/Build/Progressの成功は、Recovery作成後に次の許可Work Unitへ進む契機であり、停止契機ではない。
3. Provider UIまたはTool出力の内部退避は、Copilot自身のAction Inventoryと区別する。未許可Actionの実行証拠がない限りIncidentとして記録して継続する。
4. 同一Task内で再発した場合は、次のSource/Test Mutation前に本Evidenceと最新Recoveryを再読する。

## Scope and Claim

このEvidenceはCopilot Pilotの実測Failureであり、Provider一般の恒久的特性、UI原因、Microphone Permissionの有無または他Providerとの品質比較をClaimしない。
