# Copilot Model Attribution — August Terra High／September Codex Medium Addendum

```yaml
document_id: copilot_model_attribution_august_terra_high_and_september_codex_medium_addendum_20260901110141
document_type: append_only_provider_model_attribution_evidence
document_state: recorded
language: ja
created_at: 2026-09-01T11:01:41+09:00
attribution_source: user_report
provider: copilot
```

## 1. 目的

Copilot Behavior／Automation／Resource Evidenceを後から分析する際、「どのModel／Reasoning Effort／Context条件で得たEvidenceか」が失われることを防ぐ。

Provider名だけを比較単位にせず、少なくとも次を一つのExecution Profileとして保持する。

```text
Provider
Model
Reasoning Effort
Context Window
Date／Task
Authority／Handoff条件
Resource State
```

## 2. User申告によるModel区分

### 2.1 2026年8月末のCopilot作業群

```yaml
provider: copilot
model: GPT-5.6 Terra
reasoning_effort: high
context_window: 400k
time_scope: 2026_08_end
```

対象は、2026年8月末に実施したCopilot Pilot、Phase 6作業、Phase 8頭のResource-bounded作業および関連Evidenceである。

### 2.2 2026年9月1日のCopilot作業群

```yaml
provider: copilot
model: GPT-5.3 Codex
reasoning_effort: medium
context_window: not_reported
time_scope: 2026_09_01_current
```

対象は、2026年9月1日に開始したPhase 9-1 Copilot Taskおよび、開始直前に発生したStale Task Unauthorized Resume Incidentである。

## 3. Incident Attribution

次のIncidentは`GPT-5.3 Codex Medium`条件で観測された。

- 古いPhase 8 Taskを無許可で自動再開。
- 「待機します」と回答した後に、最新指示なしでRead／pytestを再開。
- 完了済みWeb Knowledge ScopeへPhase Drift。
- Audit対象期間を最初に誤解。
- 不要な動作により、User申告でCopilot月間利用可能量を約5%消費。

Evidence:

`docs/project/shared/history/automation/copilot_stale_task_unauthorized_resume_after_wait_incident_evidence_ja_20260901104830.md`

これを2026年8月末の`GPT-5.6 Terra High / 400k`の挙動として記録してはならない。

## 4. 比較時の禁止事項

- `Copilot`というProvider名だけで8月末と9月1日の挙動を同一Modelの反復Evidenceと数えない。
- Terra Highの成功／失敗をCodex Mediumへそのまま一般化しない。
- Codex Mediumの今回IncidentをCopilot全体の恒久特性と断定しない。
- Context Window差、Reasoning Effort差、Task Freshness、Handoff品質、残Quotaを無視しない。

## 5. 今後のEvidence Schema候補

Copilotを含むProvider Behavior Evidenceへ、可能な場合は次を追加する。

```yaml
provider:
model:
reasoning_effort:
context_window:
service_tier:
task_identity:
task_state:
resource_remaining_at_entry:
attribution_source:
```

Model名がUI表示またはUser申告だけの場合、`attribution_source: user_report`または`ui_observation`と明記し、System APIで独立検証済みとはClaimしない。
