# Phase 6-0 DeepSeek Local Runtime Switch／Dynamic Token Control 実行予約Handoff

```yaml
document_id: phase_6_0_deepseek_local_runtime_switch_handoff_20260822105531
status: planned_handoff_not_activated
document_type: append_only_planned_work_handoff
target_phase: phase_6_0_before_judge_repair_freeze
recorded_at: 2026-08-22 10:55:31 JST
from: プロジェクト責任者兼設計統括者役
to: future_phase_6_controller_and_executor
implementation_authorized: false
```

## 1. Objective

Phase 5 Accepted／Closed後、Phase 6 Judge／Repair Exact Freezeより前に、次を一つの有界なLocal Model Gateとして設計・実装・検証する。

1. Official DeepSeek-R1-0528-Qwen3-8Bから追跡可能なMac向けQ4 Derived Artifact。
2. Qwen／DeepSeekのServer再起動不要Runtime Switch。
3. Sidebar／Advanced SettingsのCurrent Model同期。
4. ModelごとのDynamic Context Size表示・変更。
5. ModelごとのDynamic Max New Tokens表示・変更。
6. Conversation／RAG／Governance／Guardrail／Evidence非Regression。

## 2. Mandatory Entry Documents

1. `docs/project/shared/history/planned_work/phase_6_0_deepseek_local_runtime_switch_design_ja_20260822105531.md`
2. `docs/project/shared/history/planned_work/phase_6_judge_repair_observability_design_candidate_ja_20260821220422.md`
3. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_candidate_inventory_ja_20260821170522.md`
4. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_selection_recommendation_ja_20260821170522.md`
5. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_selection_status_ja_20260821170522.md`
6. Phase 5 Final Index／Closure／As-built／Acceptance。
7. Phase 4 Model Port／Runtime Governance As-built Source／Tests。
8. Current Model Definition、Deployment Profile、Configuration Control、Web Settings、Sidebar、Context Usage Source／Tests。
9. Model Artifact配置とDownload／Integrity Evidenceの利用可能なRepository内正本。

Provider Memory、Conversation SummaryまたはModel Directoryの存在だけでRecovery／Integrity／Authorityを代替しない。

## 3. Entry Preconditions

```text
Phase 5 Accepted／Closed               : REQUIRED
User Backup                            : REQUIRED
Codex Phase 6-0 Activation／Authority : REQUIRED
Current Qwen Regression               : PASS REQUIRED
DeepSeek Canonical Snapshot Integrity : REVALIDATE
Mac Resource／Disk Gate               : USER／CONTROLLER GATE
Automation                            : EXPLICIT ACTIVATE ONLY
```

Phase 5実行中に本Gateを並行実装しない。

## 4. Execution Order Candidate

### P6-0-DS-WU-001：Read-only Reconciliation

- Current Qwen／llama.cpp／Model Definition／Profile／Configuration／Web UIをAs-built確認する。
- Download済みDeepSeek SnapshotのExact Revision、Manifest、Size、Missing FileおよびIntegrity Evidenceを再確認する。
- Mac Unified Memory、Disk余力およびNative Backend Compatibilityの確認方法をHuman Gateへ提示する。

### P6-0-DS-WU-002：Exact Artifact／Backend Freeze

- Q4 Exact Scheme、Conversion Tool／Revision、Recipe、Output Path、Digest、License、Rollbackを決定する。
- llama.cpp Compatibilityを満たさない場合は無理にGGUF化せず`unsupported`として別Backend候補を提示する。
- Qwen Current ArtifactへMutationしない。

### P6-0-DS-WU-003：Runtime Model Manager Contract

- Current／Candidate／Loading／Rollback／Unavailable State。
- Idle-only Switch、Generation競合、Unload／Load、Rollback、Safe Status。
- Model／Artifact／Backend／Context／Generation Identity。

### P6-0-DS-WU-004：Q4 Artifact／Local Load Gate

- 明示的Human Gate後にだけArtifact Conversion／Loadを行う。
- Load、First Token、Streaming、Cancel、Unload、Reload、Memory／Latencyを確認する。
- 実用不能でもFalse Successにせず、Reason付きSafe Unsupportedを成果とする。

### P6-0-DS-WU-005：Server Runtime Switch

- Qwen→DeepSeek→Qwen Round-trip。
- Server／Conversation継続。
- Active Generation Reject。
- Candidate Load failure／Rollback failure Matrix。

### P6-0-DS-WU-006：Dynamic Context Size

- Model／Backend／DeploymentからSelectable Maximumを導出する。
- Serverを維持したModel内部Reload。
- Success Receipt後だけCurrent State更新。

### P6-0-DS-WU-007：Dynamic Max New Tokens

- 固定Frontend上限`2048`をCapability-derived Validationへ置換する。
- Model Reloadなしで次Generationへ反映する。
- Prompt／History／RAG／Reserved Tokens込みのRequest上限を検証する。

### P6-0-DS-WU-008：Sidebar／Advanced Settings

- Current Model、Switch State、Context Size、Max New TokensをServer Snapshotから表示する。
- Settings再Open／Browser Reload／別Tab同期。
- Apply Failure／Rollback時の表示整合。

### P6-0-DS-WU-009：Integrated Acceptance

- Persistent／Ephemeral／RAG／Citation／Retry／Regenerate／Branch／Stop／Resume。
- Main Governance／Guardrail OFF／OBSERVE／ENFORCE。
- Turn／Evidence Identity。
- Qwen非Regression、DeepSeek supported／unsupported Evidence。
- Real Browser Manual Matrix。

### P6-0-DS-WU-010：Controller Closure／Phase 6 Freeze Input

- Open Major Finding 0または明示Safe Unsupported。
- Qwen／DeepSeek比較可能範囲をPhase 6 Judge／Repairへ渡す。
- DeepSeekが不成立でも、Model-neutral Contractを壊さずQwen Phase 6を開始可能にする。

## 5. Fixed Decisions

```text
Startup Default                 : Qwen3-4B
Local DeepSeek Candidate        : R1-0528-Qwen3-8B Derived Q4
V4 Flash Local                  : OUT OF SCOPE
Server Restart for Switch       : NOT REQUIRED
Model Internal Reload           : ALLOWED／REQUIRED WHEN NEEDED
Simultaneous Residency          : NOT REQUIRED
Active Generation Switch        : REJECT
Conversation／RAG Preservation  : REQUIRED
Sidebar Current Model           : REQUIRED
Advanced Current Model          : REQUIRED
Advanced Context Size           : CURRENT／LIMIT／STATE REQUIRED
Advanced Max New Tokens         : CURRENT／LIMIT／STATE REQUIRED
Server Restart Default          : Qwen
Runtime Selection Persistence   : DEFERRED
```

## 6. Stop Conditions

- Project Root外、Network、External Service、AWS、Lightning、Secretまたは課金が必要。
- Canonical Snapshot／Derived Artifact Integrityが不明。
- QuantizationがCurrent Qwen Artifact、Canonical Weightまたは他Modelを上書きする。
- Disk／Unified Memory／Thermal Riskの受容が必要。
- User実`runtime_data/`への接触が必要。
- Existing Conversation／RAG／Governance／Guardrailの不可逆Migrationが必要。
- Frozen Phase 6 ScopeまたはHuman Decisionを変更する必要。

Local Source／Testの通常Rework、UI同期BugまたはExpected Contract Test Failureは、権限範囲内で自己修正し、人間へRoutine判断を返さない。

## 7. Completion Handoff Requirements

Future ExecutorはAppend-only Completion Handoffへ次を記録する。

```text
Exact Model／Artifact／Backend Identity
Canonical／Derived Provenance
Mac Resource Evidence Class
Qwen→DeepSeek→Qwen Round-trip
Server／Conversation／RAG Continuity
Context Size Current／Limits／Reload／Rollback
Max New Tokens Current／Limits／Request Validation
Sidebar／Advanced Settings／Browser Reopen
Governance／Guardrail Model-neutral Regression
Focused／Full／Static／Frontend／Real Browser
Open Major Finding
Supported／Unsupported Decision
Exact Mutation／Rollback
Human Intervention／Compaction／Quota Evidence
Next Action: Codex Independent Review before Phase 6 Judge／Repair Freeze
```

## 8. Non-Authorization Statement

本Handoffは予約であり、実行指示ではない。Phase 5実行、Phase 6開始、Model Conversion／Load、Source／Config／Test／Frontend変更、Git／GitHub、Network、AWS／Lightning、User Data、Secretまたは外部公開を許可しない。

