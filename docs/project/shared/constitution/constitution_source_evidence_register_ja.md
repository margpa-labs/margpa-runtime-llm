# Development Governance Constitution Source Evidence Register

```yaml
document_id: development_governance_constitution_source_evidence_register
status: active_cumulative_register
normative: false
language: ja
created_at: 2026-08-09 18:41:34 JST
updated_at: 2026-08-09 19:56:20 JST
owner_role: プロジェクト責任者兼設計統括者役
constitution_input: true
lossless_policy: source_trace_required
```

## 1. Purpose

本書は、将来のLossless Source CompilationおよびNormative Constitutionへ取り込むSource Domain、Evidence、Rule候補、Conflict、未解決制度課題およびChapter Mappingを累積保持する台帳である。

本書への登録だけでRuleを有効化、改訂または最上位化しない。Normative化にはSource原文確認、History、Conflict Review、検知・違反時動作・Recovery設計およびUser Acceptanceを必要とする。

## 2. Source Domains

```text
Absolute Prohibitions
Authorized Root／Mutation Control
Docs Source of Truth／Lossless／History
Role／Authority／Delegation
Task Lifecycle／Handoff／Review
Automation Profile／Human Gate
Resource／Cost／Context
Stop／Recovery／Backup
Git／External Mutation
Evidence／Audit／Incident／Near Miss
Agent／Tool Governance
Exception／Emergency／Amendment
Provider／Project Portability
```

## 3. Initial Canonical Sources

- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Rules](../conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../operations/documentation_structure_and_task_operations_ja.md)
- [Phase Completion Review／Backup Gate](../operations/phase_completion_review_and_backup_gate_ja.md)
- [Git Workflow Policy](../operations/git_workflow_policy_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)
- [Project Responsibility Handoff](../project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Design Governance Handoff](../design_governance_handoff/design_governance_handoff_ja.md)

本Listは初期Inventoryであり、完全な閉集合ではない。新規SourceはPath、Revision／Timestamp、Source Meaning、関連Rule候補および採否状態を記録して追加する。

## 4. Candidate Register

### CONST-SRC-001 — Authorized Root Supremacy

```yaml
state: candidate_already_effective_in_current_operations
classification:
  - absolute_prohibition
  - cross_role
  - cross_provider
source:
  - ../operations/research_asset_mutation_control_ja.md
  - ../automation/automation_control_profile_ja.md
```

明示されたAuthorized Root／Allowed Path外への無許可接触禁止を、Role、Automation Level、Phase／Project Scope、Agent、ToolおよびProviderを超えて適用する。将来のNormative ConstitutionではRule ID、Exact Detection、Violation Response、RecoveryおよびException不可／可能境界を確定する。

### CONST-SRC-002 — Supremacy Rule Set Extensibility

```yaml
state: candidate
classification:
  - amendment
  - evidence_required
```

最上位規則群は、人間が将来追加を指示できる意味で現時点の列挙に固定しない。ただし、本Registerへの最上位規則候補の追加すら、ユーザーまたはユーザーが明示指定した人間の指示を必要とする。AI側は候補を自発登録、編集、削除または例外化しない。

### CONST-SRC-003 — Automation Gradient／Dual Consent

```yaml
state: candidate_already_designed_for_phase_2_pilot
classification:
  - automation_control
  - human_gate
source:
  - ../automation/automation_control_profile_ja.md
```

AutomationをBinaryでなく段階的Profileとして扱い、Pilot StartにはPreflight、Git Checkpoint、Backup、Control Task Readyおよび後続User Startを必要とする。

### CONST-SRC-004 — Provider／Project-neutral Normative Core

```yaml
state: candidate
classification:
  - portability
  - hard_code_prohibition
```

Normative CoreをCapability／Authority／Evidence／State／Scope／Stop／Recovery／Human Gateとして抽象化し、Project固有値をManifest、Provider固有操作をAdapterへ分離する。

### CONST-SRC-005 — Temporary Artifactを含むAuthorized Root Supremacy

```yaml
state: candidate_already_effective_in_current_operations
classification:
  - absolute_prohibition
  - mutation_control
  - provider_boundary
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2design-010--authorized-root外temporary-artifact-near-miss
```

Authorized Root／Allowed Pathの境界は、Final ArtifactだけでなくTemporary File、Cache、Log、List、Intermediate OutputおよびToolの暗黙Artifactへ適用する。ProviderまたはSandboxがWriteを許していることは、User Authorization、Project ScopeまたはExceptionを生成しない。Root外Writeが必要ならば、対象、目的、復旧および残存Artifactを示してユーザーの明示承認を得るまで停止する。

### CONST-SRC-006 — 違反後の無許可Cleanup禁止

```yaml
state: user_directed_absolute_rule
classification:
  - absolute_prohibition
  - incident_control
  - human_gate
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2design-010--authorized-root外temporary-artifact-near-miss
```

AI、Role、Task、Agent、ToolまたはProviderが無許可でArtifactを作成・変更した場合、それが自分の誤生成物、不要物、Temporary Artifactまたは完全に特定済みであっても、削除、上書き、Move、Rollback、CleanupまたはEvidence整合化を自己判断で行わない。即時停止し、Exact Path、Action、Before／After、現在状態、復元可能性および必要な次Actionをユーザーへ報告し、明示指示を待つ。

### CONST-SRC-007 — Artifact Permission Hardening Reservation

```yaml
state: user_directed_research_reservation
classification:
  - mutation_control
  - human_gate
  - platform_portability
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2design-011--artifact-permission-hardeningは未決定の独立mutation
```

AI／Agent／Tool／Automationが作成したArtifactのPermission／ACLを、Artifactの種類とRiskに応じて強化する構想を未決定の将来候補とする。作成主体がAI側であることはPermission変更Authorityを生成しない。Permission変更はExact Target、Before／After、継承、Platform差、Lockout Risk、Rollbackおよび人間の明示承認を必要とする独立Mutationである。

### CONST-SRC-008 — Automation LevelとControl Stateの分離

```yaml
state: user_directed_design_input
classification:
  - automation_control
  - state_machine
  - human_gate
```

Automationの許可粒度を示すLevelと、現在実行可能かを示す`OFF／ARMED／ON／PAUSED／EMERGENCY_STOP`を分離する。`ARMED → ON`はREADY EvidenceとTwo-key Activationを必要とし、`EMERGENCY_STOP`からの再開は人間の明示的な再承認を必要とする。

### CONST-SRC-009 — Mechanical Enforcement Research Reservation

```yaml
state: user_directed_research_reservation
classification:
  - machine_enforcement
  - mutation_control
  - provider_adapter
```

Path Allowlist、外部DirectoryのRead-only化、隔離Workspace／Worktree、実行前後Mutation Inventory、Authorized Root外Diff検知およびTool WrapperによるPath検証を、将来の機械的強制候補とする。現時点では未実装・未承認であり、導入Mutationは人間の明示承認を必要とする。

### CONST-SRC-010 — Backup存在とRestore Evidenceの分離

```yaml
state: user_directed_design_input
classification:
  - backup
  - recovery
  - evidence
```

Backupが存在することと、復元可能性が確認されていることを分離する。ユーザーが必要と判断する場合は、暗号化、Backup完了時刻、対象／対象外、Restore Procedureおよび一部Restore実績をEvidence候補とする。PC広域Backupはユーザー担当であり、AI側のRoot外Accessを許可しない。

## 5. Intake Rule

Pilot、通常運用、Incident、Near Miss、Provider併用またはAgent／Tool設計から憲法へ直接使える知見を得た場合、次を記録する。

```text
Source／Evidence ID
Timestamp／Phase／Work Unit
Original Path／Revision
Observation／Failure／Near Miss
Candidate Rule／Chapter
Existing Rule Conflict
Detection／Violation Response／Recovery Candidate
Human Intervention
Portability Impact
Normative State
Open Decision
```

事実を変に要約、再解釈または一般化しない。抽象化はSource Traceを保持し、Project／Provider固有事実とPortable Rule候補を区別した上で行う。

## 6. Current Open Items

- Phase 2 Automation Pilotの実運用Evidence。
- Multi-provider OrchestrationのAuthority／Evidence／Conflict。
- Context／Resource Limit時のLossless Handoff境界。
- 人間が最上位規則の追加・変更を明示指示した場合だけ適用する、Human-only Amendment／反映Protocol。AI側の候補登録は含めない。
- Agent／Tool適用前のConstitution Research Preview開始条件。
- Lossless Source CompilationのSource Freeze／Post-freeze Artifact設計。
- Permission HardeningのArtifact Classification、Platform Contract、DefaultとRollback。
- Mechanical EnforcementのFalse Positive、Lockout、Provider差およびRecovery。
- Lightweight CheckpointとCommit／Push／Backupの責務分離。

## 7. Related Documents

- [Constitution Research Index](constitution_research_index_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)
