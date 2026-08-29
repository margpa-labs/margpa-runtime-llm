# Phase 6 Copilot Pilot — Unexpected Stop and Microphone UI Failure

```yaml
document_type: pilot_incident_evidence
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
occurred_at: 2026-08-28 20:05:49 JST
severity: major
disposition: open
```

## Observed Failure

CopilotはR4/R5の中間進捗後に、Complete／Incomplete Return／True Stopのいずれも成立していないにもかかわらず`final`応答を返し、連続実行を停止した。これはActive Handoff §9およびLong-running Companion §2に反する。

Userは同じ停止局面でマイクアクセスUI挙動を観測した。CopilotがこのTaskで実行したTool/Commandにはマイク、Browser、OS Permission、Network、外部Accountへのアクセスは含まれない。原因、権限状態、実アクセスの有無は未検証であり、推測しない。

## Action Inventory

```text
Microphone Tool/Command: 0
Browser Tool: 0
OS Permission Command: 0
Git: 0
Network: 0
Provider Memory: 0
User runtime_data: 0
Project Root-outside Action: 0
```

## Required Rework

以後、Complete Candidate、Incomplete/Stopped-safe Return、またはTrue Stopまで中間進捗を`final`として返さない。マイクUI挙動はProvider UIに属するため、Project Root外の調査、Permission変更、Browser/OS操作を行わない。
