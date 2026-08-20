# Automation Governance Index

```yaml
document_id: automation_governance_index
status: current
normative: true
language: ja
created_at: 2026-08-09 18:11:00 JST
updated_at: 2026-08-21 03:10:52 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
```

## 1. Purpose

本Directoryは、Task Orchestration、自動化Control、Pilot Evidence、Provider差、Human Gate、停止、復旧および将来の統合憲法への入力を、一つの正本入口から追跡するための専用領域である。

自動化関連EvidenceをOperations、Phase、会話またはProvider固有設定へ分散させず、本IndexからStable、History、Phase実験および憲法計画を解決できる状態を維持する。

本DirectoryはAutomation固有のControl、連結実行差分およびEvidenceを保持する。通常運転と共通するRole権限、Docs権限、Task Artifact、From／To、HistoryおよびReview規則を複製せず、[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)を参照する。

## 2. Canonical Structure

```text
docs/project/shared/automation/
├─ automation_governance_index_ja.md
├─ automation_control_profile_ja.md
├─ automation_governance_evidence_log_ja.md
├─ pre_pilot_governance_baseline_ja.md
├─ documentation_capability_contract_ja.md
├─ provider_memory_and_repository_canonical_authority_ja.md
└─ provider_adapters/
   ├─ codex_desktop_bounded_read_adapter_ja.md
   └─ codex_desktop_documentation_io_adapter_ja.md

docs/project/shared/history/automation/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Stable文書を変更する前後に、同名系統の完全SnapshotをHistoryへ保存する。HistoryはAppend-onlyであり、既存Snapshotを要約、再解釈または上書きしない。

## 3. Stable Documents

- [Automation Control Profile](automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)
- [Pre-pilot Automation Governance Baseline](pre_pilot_governance_baseline_ja.md)
- [Documentation Capability Contract](documentation_capability_contract_ja.md)
- [Provider Memory／Repository Canonical Authority](provider_memory_and_repository_canonical_authority_ja.md)
- [Transition Blocker／Escalation／Closure Contract](../operations/transition_blocker_escalation_and_closure_contract_ja.md)
- [Codex Desktop Bounded Read Adapter](provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Codex Desktop Documentation I/O Adapter](provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)

## 4. Related Normative Sources

- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Experimental Document-driven Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Task Execution Routing／Cost Control](../operations/task_execution_routing_and_cost_control_ja.md)
- [Transition Blocker／Escalation／Closure Contract](../operations/transition_blocker_escalation_and_closure_contract_ja.md)
- [Git Workflow Policy](../operations/git_workflow_policy_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Constitution Research Index](../constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)

## 5. Supremacy Boundary

Automation Level、Role、Task数、Provider Capability、Phase ScopeまたはProject Scopeに関係なく、次を上書きできない。

```text
明示的に指定されたAuthorized Root／Allowed Path外へ、
ユーザーの個別許可なく触れてはならない。
```

「触れる」にはRead、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL、Temporary Artifact、Cache、Symlink追跡、External MountおよびToolの暗黙Accessを含む。

本規則はプロジェクト責任者兼設計統括者役、将来の上位Role、全Task、全Agent、全Tool、全Provider、Automation OFF／任意の自動化段階へ適用する最上位規則群の一つである。Roleや自動化範囲から例外を生成しない。

最上位規則群は、ユーザーまたはユーザーが明示指定した人間が将来追加を指示できる意味で閉集合としない。AI、Role、Task、Agent、Tool、AutomationまたはProviderは、最上位規則の新規追加、文言変更、削除、並替え、例外化、候補登録またはそれらの指示を自発的に行ってはならない。できるのは事実、Incident、Conflictまたは不明点を報告して停止することだけである。当該最上位規則へのDocs反映も、人間が対象とActionを明示指示した範囲の代行に限る。

## 6. Role State

当面、Project全体を統括する現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。

- Project ResponsibilityとDesign GovernanceのStable／History／Recovery Folderは両方維持する。
- Recoveryは分離したまま相互参照する。
- 兼務はAuthorityの合算、最上位規則からの免除またはUser Gateの代理を意味しない。
- Pilot開始Transitionが成立した時点で、Provider Capabilityが許せば現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。
- Task名変更が失敗または不可能な場合は、Role Identity不一致としてPilot開始を停止し、推測で続行しない。

## 7. Pilot Start Gate and Effective Authority

Automation Pilotは、共通Role／Docs AuthorityへAccepted Envelopeによる連結実行差分を重ねて起動する。通常運転用とAutomation用のRole権限表またはDocs権限表を別々に作らない。

1. Pilot Design／Role Authority Matrix／Envelope／Handoff／Stop／EvidenceのReview合格。
2. 対象Automation Profile、Role Binding、Authorized Root、Allowed Paths／Actions、Task上限、期限およびHuman GateのFreeze。
3. ユーザーによるExact EnvelopeのAcceptance。
4. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示。
5. その後のユーザーによる「ok。では開始する。」の明示。

片方の発言、過去の同意、類似表現、会話の流れ、設計完了またはTask作成Capabilityだけでは開始しない。Ready宣言後に状態が変化した場合はReadyを失効させ、再Preflightする。

Automation LevelとControl Stateを分離する。Control Stateは`OFF／ARMED／ON／PAUSED／EMERGENCY_STOP`を基本状態とする。`ON`後は[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)とAccepted Envelopeの交差にある`ROLE_ALLOWED` Actionを、承認済み到達線まで連結実行できる。

Docs Authorityは共通Role契約の独立Dimensionとし、Role Viewは`READ／CREATE_NEW／APPEND_NEW／EXISTING_WRITE_USER_EXPLICIT／REVIEW_ONLY／DENY`を明示する。既存Stable文書への直書きは、Modeを問わず、ユーザーがExact TargetとActionを明示した場合だけ成立する。必要Artifactは、当該Docs Authorityを委譲されたRole／TaskがMode共通のDocs／運用規則に沿って都度判断し、Cross-Role対象または競合だけを最高責任者役が調整する。

Automationは全判断をProject Controllerへ集中させない。各Role／Taskは委譲範囲内のRoutine判断を自律的に行い、直属上位Roleへ上げるのは例外、重大Finding、Scope外、Conflict、Cross-Phase影響、Resource／Provider異常または定義済みReview／Acceptance Gateとする。

未解決事項、Current Blocker、Role-owned Work、Deferred EvidenceおよびUser Gateは[Transition Blocker／Escalation／Closure Contract](../operations/transition_blocker_escalation_and_closure_contract_ja.md)により分離する。安全停止からUser Escalationを自動導出せず、最高責任者役と各委譲Roleは、自Authority内で解決できる作業を閉じてからHuman-only Gateだけを上げる。

最高責任者役は、Findingを`Transition Impact: HOLD／NONE`とResolution Routeへ分け、現在必須のRole-owned Workを完了までHoldし、次工程Work、Deferred EvidenceおよびHuman Gateを動的にルーティングする。分類候補をUserへ渡して判断させず、Current Impact、Owner、再開条件および推奨判定まで統合する。

## 8. General Hard-code Prohibition／Portability

General Hard-code ProhibitionのNormative本文は[Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)を正本とする。Automation側は、Portable Core、Project Manifest、Provider Adapter、Authorization EnvelopeおよびRuntime Bindingの分離だけを固有差分として保持し、共通規則を再掲して重複正本化しない。

Codex、Claude Codeその他Providerを併用する場合も、同一Core ContractをAdapter越しに適用し、Provider差を理由にAuthority、禁止、EvidenceまたはStopを弱めない。許可範囲内のHard-code不可避性と抽象化方法は、その時点の最高責任者役が都度判断する。

### 8.1 Role別委譲範囲内の動的Documentation判断

Automationは判断まで機械的に固定しない。必要Artifact、統合可否、担当内Exact PathおよびFrom／Toは、当該Authorityを委譲されたRole／Taskが、共通Role／Docs Authority、情報Loss、State、Risk、Review、Recovery、Cost、ContextおよびProvider Capabilityから都度判断する。Cross-Role対象、競合および上位Gateは最高責任者役が調整する。

Project Bindingと上位Roleからの委譲は許可Document Root／Classを与え、当該Docs Authorityを持つRoleが必要な対象を固定する。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。固定Packageまたは別のResolver Subsystemを設けず、この判断によって既存Stableへの直書き、既存History Mutation、許可外Document ClassまたはAuthorized Root外へのAuthorityを生成しない。

## 9. Evidence Accumulation

Pilot、通常運用、Incident、Near MissまたはProvider併用から、Automation／Constitutionへ直接使える知見を得た場合は[Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)へ累積追加する。

記録対象：

- 成功だけでなく、偶然成功、停止遅延、Human Interventionおよび未検知領域
- Automation Levelの過剰／不足
- Provider間HandoffとCapability差
- Scope、Folder Boundary、Authority、Cost、ContextおよびRecovery
- 新規Project／既存Projectへの移植性
- Agent／Tool／Agent-driven Developmentへの適用可能性

Evidenceの追加だけでRuleを自動変更しない。最上位Ruleの追加・変更・削除・例外化は、人間の明示指示なしに検討対象、候補またはDocs変更として扱わない。

憲法へのSource採用、Chapter候補、ConflictおよびNormative昇格状態は、Automation Evidence Logと分離して[Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)へ登録する。Automation側は事実Evidence、Constitution側はSource Trace付き制度候補を担当する。

## 10. Current State

```text
Combined Role          : active／project responsibility + design governance
Automation Profile     : bounded_unit pilot
Control State          : OFF／PHASE 2 COMPLETE／PHASE 3 READY・NOT STARTED
P2-0-WU-002            : accepted／closed
P2-0-WU-003            : content and mutation safety pass／provider grammar fail／adjust required
P2-0-WU-003 Artifact   : retained／content verified／no cleanup
Capability Contract    : activated／verified in P2-0-WU-004
Provider Mapping       : semantic mapping verified／mechanical grammar enforcement unavailable and not required
P2-0-WU-004            : accepted／closed／6 of 6 conformance pass
Batch Capability       : unavailable／deny
Multi-provider Use     : Phase 2-E bounded experiment executed／no general promotion
Cross-provider Result  : technical・handoff chain success／supreme-rule compliance failure
Provider Memory        : noncanonical／future create-update-reliance prohibited
Permission Hardening   : future candidate／undecided
Mechanical Enforcement : research reservation only／not claimed
Git／External Mutation : none
```

## 11. Latest Phase Evidence

- [Phase 2 Pre-pilot Governance Full Consolidation](../../phases/phase_2/history/operations/phase_2_pre_pilot_governance_full_consolidation_20260809195620.md)
- [Phase 2 Documentation Index Snapshot](../../phases/phase_2/history/index/documentation_index_20260809195620.md)
- [Mode-invariant Role／Document Authority Correction](../../phases/phase_2/history/operations/phase_2_0_mode_invariant_role_and_document_authority_correction_20260811104642.md)
- [Phase 2 Documentation Index Snapshot 20260811104642](../../phases/phase_2/history/index/documentation_index_20260811104642.md)
- [Responsible-role Dynamic Judgment Correction](../../phases/phase_2/history/operations/phase_2_0_responsible_role_dynamic_judgment_correction_20260811122047.md)
- [Phase 2 Documentation Index Snapshot 20260811122047](../../phases/phase_2/history/index/documentation_index_20260811122047.md)
- [Delegated Role Dynamic Judgment Hierarchy](../../phases/phase_2/history/operations/phase_2_0_delegated_role_dynamic_judgment_hierarchy_20260811124635.md)
- [Phase 2 Documentation Index Snapshot 20260811124635](../../phases/phase_2/history/index/documentation_index_20260811124635.md)
- [P2-0-WU-003 Controller Review](../../phases/phase_2/history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [Write Success／Command Grammar Failure Evidence](../history/automation/automation_governance_evidence_phase_2_write_success_command_grammar_failure_ja_20260811225656.md)
- [Capability Contract Redesign after P2-0-WU-003](../../phases/phase_2/history/operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md)
- [P2-0-WU-004 Result](../../phases/phase_2/history/operations/phase_2_0_documentation_capability_conformance_result_p2_0_wu_004_20260811233209.md)
- [P2-0-WU-004 Controller Review](../../phases/phase_2/history/operations/phase_2_0_documentation_capability_controller_review_p2_0_wu_004_20260812001515.md)
- [P2-0-WU-004 User Acceptance](../../phases/phase_2/history/operations/phase_2_0_documentation_capability_user_acceptance_p2_0_wu_004_20260812001837.md)
- [P2-0 Cumulative Controller Review](../../phases/phase_2/history/operations/phase_2_0_automation_pilot_cumulative_controller_review_20260812002752.md)
- [P2-0 Blocker Correction／Closure-ready Evidence](../../phases/phase_2/history/operations/phase_2_0_blocker_correction_and_closure_ready_20260812004603.md)
- [Blocker／Responsibility／Human Decision Budget Evidence](../history/automation/automation_governance_evidence_phase_2_blocker_responsibility_and_human_decision_budget_ja_20260812005818.md)
- [Transition Routing表現訂正Evidence](../history/automation/automation_governance_evidence_phase_2_transition_routing_expression_correction_ja_20260812011543.md)
- [P2-0 Final Closure Acceptance／Phase 2-A Ready](../../phases/phase_2/history/operations/phase_2_0_final_closure_acceptance_and_phase_2_a_ready_20260812012339.md)
- [Phase 2-E Claude Cross-provider／Agent Automation PoC](../history/automation/automation_governance_evidence_phase_2_e_claude_cross_provider_and_agent_automation_poc_ja_20260815005913.md)
- [Phase 2-E Claude Completion Evidence](../history/automation/automation_governance_evidence_phase_2_e_claude_completion_ja_20260815075428.md)
- [Phase 2-E Claude Rework Cycle](../history/automation/automation_governance_evidence_phase_2_e_claude_rework_cycle_ja_20260815085208.md)
- [Phase 2-E Claude Final Rework Cycle](../history/automation/automation_governance_evidence_phase_2_e_claude_final_rework_cycle_ja_20260815092832.md)
- [Phase 2-E Cross-provider Final Assessment](../history/automation/automation_governance_evidence_phase_2_e_cross_provider_final_assessment_ja_20260815095155.md)

現在のControl Stateは`OFF／PHASE 2 COMPLETE／PHASE 3 READY・NOT STARTED`である。P2-0-WU-003のArtifactは保持し、成果物成功とContract遵守を分離したまま、P2-0-WU-004のExact Package、実行、Controller Review、User Final AcceptanceおよびP2-0 Final Acceptanceが完了した。Phase 2-A～2-DではCodex内のRole Chain、Phase 2-EではClaude内Role ChainとCodex独立Reviewを接続したCross-provider Chainを検証した。

Phase 2-EのTechnical／Handoff Chain、Mac Manual AcceptanceおよびCodex Final Reviewは成功したが、Claude Provider MemoryへのAuthorized Root外書込みにより最上位規則適合は失敗した。Provider Memoryは非正本・依存禁止とし、Cross-provider Recovery／Authority／EvidenceをRepository内Docsへ限定する。この結果から正式Automation Mode、上位Automation Levelまたは全Provider一般化を自動承認しない。Phase 2はClosed、Phase 3は`READY／NOT STARTED`であり、開始時の別Human Gateを維持する。
