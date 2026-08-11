# Development Governance Constitution Source Evidence Register

```yaml
document_id: development_governance_constitution_source_evidence_register
status: active_cumulative_register
normative: false
language: ja
created_at: 2026-08-09 18:41:34 JST
updated_at: 2026-08-11 13:09:30 JST
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

### CONST-SRC-011 — Provider-neutral Bounded Read Capability

```yaml
state: pilot_observation_pending_user_decision
normative_effect: none
classification:
  - provider_adapter
  - capability
  - least_privilege
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-004--read-capability不整合に対するfail-closed
```

Phase 2-0初回Pilotでは、Local Docs読取要件とShell全面禁止が衝突し、Provider-native File Reader不在によりRecoveryが成立しなかった。Portable Coreでは「何のCommandを使うか」ではなく、Read対象、Authorized Root、Exact Manifest、Digest、Mutation禁止、EvidenceおよびStopをCapability Contractとして表現し、Provider固有の読取手段をAdapterへ分離する必要性が観測された。

本項は新しい最上位規則、Shell許可またはAdapter採用決定ではない。具体的なRead手段、許可範囲、Command構文、再試験およびNormative化は、ユーザーの`ADJUST`判断と別Envelopeを必要とする。

### CONST-SRC-012 — Provider Task Metadata Registration Lifecycle

```yaml
state: pilot_observation_pending_user_decision
normative_effect: none
classification:
  - provider_adapter
  - task_lifecycle
  - evidence
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-002--新task登録とexact-title設定のeventual-consistency
```

Task作成APIがIDを返した時点と、Title／Status等の後続操作がTaskを解決可能になる時点が一致しないProvider挙動を観測した。Portable Coreは`task_created`と`task_registered／metadata_addressable`を分離し、Provider Adapterは登録観測、Exact Metadata設定、Read-back Verificationおよび部分失敗Evidenceを扱う必要がある可能性がある。

本項は自動再試行、固定待機時間、再試行回数またはTask再作成を許可しない。初回事例ではユーザー承認なしに再試行せず、既存Taskへの1回だけの再試行をHuman Gate後に実施した。

### CONST-SRC-013 — Capability不整合時のFail-closed Evidence

```yaml
state: observed_effectiveness_pending_compilation
normative_effect: none
classification:
  - stop
  - evidence
  - capability
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-003--authority-acknowledgementの成立
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-004--read-capability不整合に対するfail-closed
```

Child Taskは、Authority Acknowledgement時点で未検証事項を未検証のまま保持し、Recovery時に規則適合Read Capabilityがないと判定すると、文書内容を推測せず、未回復、Evidence 0および必要なHuman Gateを返して停止した。安全な停止が機能目的の達成と同義ではないこと、Safety PassとFunctional Failを同じ`PASS／FAIL`へ潰さず分離する必要性が確認された。

### CONST-SRC-014 — General Hard-code Prohibition／最高責任者役の運用判断

```yaml
state: human_directed_effective_in_current_operations
normative_effect: effective_via_current_normative_sources
classification:
  - supreme_rule
  - portability
  - hard_code_prohibition
  - human_only_amendment
source:
  - ../task_roles/task_role_write_authority_policy_ja.md#1002-general-hard-code-prohibition
  - ../automation/automation_governance_index_ja.md#8-general-hard-code-prohibitionportability
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-013--固定document-packageはhard-codeと過剰生成を生む
human_direction_at: 2026-08-11 11:34:01 JST
```

ユーザーの明示指示により、「可能な限りHard-codeを禁止し、技術的または論理的にどうしても必要な場合だけ管理された例外として許可候補とする」を最上位規則群へ追加した。通常運転、Automation、全設計、全Role、全Task、全Agent、全Toolおよび全Providerへ適用する。

不可避なHard-codeには、理由、代替案、代替不能性、Exact Scope、Owner、変更・Review方法、除去／Migration条件、TestおよびEvidenceを要求する。便宜、速度、現行Project／Providerへの最適化または「一時的」であることだけを理由にしない。Manifest、Envelope、Role View、ConfigまたはFreeze EventによるExact Runtime Bindingは、再利用されるCoreへの固定埋込みと区別する。

許可範囲内でHard-codeの不可避性、抽象化方法、EvidenceおよびTestを都度判断するAuthorityは、その時点の最高責任者役にある。人間へ戻すのは、最上位規則改変、Root／Scope／Authority拡張、ユーザー専用領域または明示Human Gateに該当する事項である。

本項はAI側の自発候補登録ではない。Human-only Supreme Rule Authorityに基づく、今回の明示指示の代行反映である。

### CONST-SRC-015 — 委譲Roleによる動的Documentation判断

```yaml
state: current_policy_design_under_phase_2_review
normative_effect: effective_in_current_role_and_docs_design
classification:
  - document_source_of_truth
  - resource_control
  - context_control
  - portability
source:
  - ../task_roles/role_authority_matrix_ja.md#7-role別委譲範囲内の動的documentation判断
  - ../operations/documentation_structure_and_task_operations_ja.md#13-task間情報伝達
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-013--固定document-packageはhard-codeと過剰生成を生む
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-014--automationは判断を機械化せず最高責任者役の判断を連結する
```

Work Unitへ固定のIndex／Handoff／Status／Review Packageを一律生成しない。各Role／Taskは、委譲されたRole Authority、Docs Authority、Work UnitおよびAccepted Designの交差内で、最上位規則群と共通Docs／運用規則に沿って必要Artifactを都度判断する。最高責任者役はProject／Cross-Role／Cross-Phase対象、競合、委譲境界およびReview Gateを調整するが、全RoleのRoutine判断を逐次承認する中央Resolverにはならない。

一つのArtifactが複数責務をLosslessに満たせる場合は統合し、必要性を示せないArtifactは作らない。Project Bindingと上位Roleからの委譲が許可Document Root／Classを与え、当該Docs Authorityを持つRoleが必要な対象をExact Class／Pathへ固定する。独立した機械的Resolverを前提にせず、この判断はAuthorityを生成せず、既存Stableへの直書き、既存History Mutation、許可外Document ClassまたはAuthorized Root外を許可しない。

### CONST-SRC-016 — Delegated Role-local Judgment／Layered Completion

```yaml
state: current_policy_design_under_phase_2_review
normative_effect: effective_in_current_role_and_automation_design
classification:
  - authority_roles_and_delegation
  - task_lifecycle
  - review
  - escalation
  - automation_control
source:
  - ../task_roles/task_role_write_authority_policy_ja.md#1011-全roletaskの委譲範囲内動的判断
  - ../task_roles/role_authority_matrix_ja.md#81-layered-judgmentno-routine-micro-escalation
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-015--全roletaskの委譲範囲内動的判断と段階的完了連鎖
```

最高責任者役だけでなく、全Role／Taskが、自身へ委譲された役割、実行権限、Docs Authority、Accepted DesignおよびWork Unitの範囲内で都度判断する。Role分離は全判断の中央集権化を意味せず、責務、判断範囲、ReviewおよびEscalation先を階層化する。

実装担当役はAccepted Designと担当Source／Test Scope内を自律実行し、Phase別設計担当者役はAssigned Phase内の設計判断、実装担当への伝達、局所Reviewおよび再作業指示を自律実行する。例外、重大問題、Scope外、規則Conflict、Cross-Phase影響、Security／Privacy／Recovery Risk、Resource／Provider異常または定義済みGateだけを直属上位へEscalateする。問題なく進行するRoutine Actionごとに最高責任者役へ確認しない。

初期の標準完了連鎖は、`Implementer完了報告 → Phase Designer Review／局所Accepted → 最高責任者役Review／Task完了判定案 → User Acceptance → 次Work Unit`とする。十分なEvidence、安全性、安定性、有効性、RecoveryおよびCost評価後に、同じ階層契約をTask／有界Work UnitからSubphase、Phase、Project単位へ段階的に拡張する。

### CONST-SRC-017 — Tiered Escalation／Communication Authority Separation

```yaml
state: current_policy_design_under_phase_2_review
normative_effect: effective_in_current_role_and_pilot_design
classification:
  - authority_roles_and_delegation
  - task_lifecycle
  - handoff
  - escalation
  - human_gate
source:
  - ../task_roles/task_role_write_authority_policy_ja.md#104-善意推測話の流れによるauthority生成禁止
  - ../task_roles/role_authority_matrix_ja.md#5-role-capability-matrix
  - ../operations/research_asset_mutation_control_ja.md#32-善意推測会話contextによる許可補完の絶対禁止
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-016--delegated-escalationenvelopehandoff-authority整合
```

不明なActionはFail-closedで停止するが、全ての不明点をUserへ直接送らない。担当Role内の技術、設計、実装、Test、Docs解釈または下位Role調整は直属上位Roleへ、Cross-Role、Cross-Phase、委譲境界または重大Riskは段階的に最高責任者役へ、ユーザー意図、最上位規則、Authorized Root／Authority拡張、Human-only Gateまたは最高責任者役でも解決不能な事項はUserへ送る。

Task作成／命名AuthorityとRole間Communication Authorityを分離する。Phase Designerは新Taskを作成・命名せず、既にAssignedされたImplementerへHandoff／Follow-up／再作業指示を行える。Implementerは新Taskを作成せず、直属上位Phase DesignerへStatus／完了報告／Escalationを返せる。上位Roleは自身のAuthority外を解釈で補完せず、Human-only事項を代理決定しない。

### CONST-SRC-018 — Authority Subject／Lifecycle State／Activationの分離

```yaml
state: current_policy_design_under_phase_2_review
normative_effect: candidate_for_constitution_compilation
classification:
  - authority_roles_and_delegation
  - rule_priority
  - task_lifecycle
  - human_gate
  - automation_control
source:
  - ../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-017--controllerchild-authority-subjectとreviewacceptance-stateの明示
  - ../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md#3-allowed-controller-actions
  - ../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md#6-child-absolute-prohibitionscontroller-boundary
```

Rule、PermissionおよびProhibitionは、対象Subject、Role、Lifecycle State、Activation ConditionおよびDelegation Directionを明示する。同一文書にControllerとChildが存在する場合、Childへの禁止をControllerの正当なPreparationへ誤適用せず、Controller AuthorityをChildへ暗黙移転しない。

`design reviewed`、`user accepted`、`digest frozen`、`READY／ARMED`および`ON`は別状態である。前段の成立は後段のAuthorityを生成しない。状態遷移はEvidenceとHuman Gateを伴い、類似表現または会話の流れで補完しない。

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

- Phase 2 Automation Pilot初回実運用Evidenceの`ADJUST／GO／STOP`ユーザー判断。
- Bounded Read CapabilityのPortable Core／Provider Adapter境界と再試験Envelope。
- Task Metadata登録のEventual Consistencyを固定待機へHard-codeせず扱う方法。
- Multi-provider OrchestrationのAuthority／Evidence／Conflict。
- Context／Resource Limit時のLossless Handoff境界。
- 人間が最上位規則の追加・変更を明示指示した場合だけ適用する、Human-only Amendment／反映Protocol。AI側の候補登録は含めない。
- Agent／Tool適用前のConstitution Research Preview開始条件。
- Lossless Source CompilationのSource Freeze／Post-freeze Artifact設計。
- Permission HardeningのArtifact Classification、Platform Contract、DefaultとRollback。
- Mechanical EnforcementのFalse Positive、Lockout、Provider差およびRecovery。
- Lightweight CheckpointとCommit／Push／Backupの責務分離。
- 委譲Roleによる動的Documentation判断の説明可能性、過少／過剰生成Review、Escalation閾値およびProvider差。
- Tiered EscalationがProvider間Messaging、Task不在時または複数上位Role環境でも同じ意味を維持できるか。
- 不可避なHard-codeを審査するEvidence Schemaと除去／Migration Trigger。
- Authority Subjectが複数存在する文書で、禁止・許可・委譲先を機械検証するSchema。

## 7. Related Documents

- [Constitution Research Index](constitution_research_index_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)
