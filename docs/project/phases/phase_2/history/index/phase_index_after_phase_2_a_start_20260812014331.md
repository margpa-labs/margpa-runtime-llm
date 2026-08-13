# MARGPA Runtime LLM Phase 2 Index

```yaml
document_id: phase_2_index
status: phase_2_a_active_p2_a_wu_001
phase: phase_2
active_subphase: phase_2_a
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-12 01:43:31 JST
owner: プロジェクト責任者兼設計統括者役
project_responsibility: combined_with_design_governance
independent_task_state: p2_0_tasks_closed_phase_2_a_controller_active
functional_implementation_started: false
```

## 1. Phase Entry Decision

ユーザーはPhase 1-ex完了を改めてAcceptedし、Phase 2開始と自動化Pilot設計の継続を明示した。Human-private Recovery AssetはAutomation側の認識、EvidenceまたはActivation Gateに含めない。

```text
Phase 1-ex          : COMPLETE／ACCEPTED
Phase 2             : STARTED
Current Subphase    : Phase 2-A／Phase Contract・Conversation Domain Foundation
Pilot Design        : COMPLETE／BOUNDED-UNIT VIABILITY ESTABLISHED
P2-0-WU-002         : ACCEPTED／CLOSED／BOUNDED READ RECOVERY PASS
P2-0-WU-003         : CONTENT・MUTATION SAFETY PASS／PROVIDER GRAMMAR FAIL／ADJUST REQUIRED
P2-0-WU-004         : ACCEPTED／CLOSED／CAPABILITY-SEMANTICS RETEST PASS
Independent Task    : P2-0-WU-004 IDLE／NO FURTHER ACTION AUTHORIZED
Pilot Execution     : ADJUSTED_GO／USER ACCEPTED／BOUNDED_UNIT CEILING
Phase 2-A Work Unit : P2-A-WU-001／DESIGN FREEZE IN PROGRESS
Functional Work     : PHASE 2-A DESIGN ACTIVE／SOURCE MUTATION NOT YET STARTED
Capability Contract : ACTIVATED AND VERIFIED IN P2-0-WU-004
Git Checkpoint      : CONTENT COMMIT f21829f PUSHED／LOCAL・ORIGIN・REMOTE ALIGNED／POSTFLIGHT RECORDED
Current Stop Point  : NONE／P2-A-WU-001 ACTIVE
```

ユーザーはPhase 2-A開始前BackupとGitHub反映を確認し、Phase 2-Aを完全自動化で完遂する到達線を明示承認した。指定Project Root内のPhase 2-A設計、Domain Contract、Port、対応TestおよびDocsを、`bounded_unit`連結方式で進める。Phase 2-B以降、Git／External／Secret／課金／Destructive ActionまたはAuthorized Root外は許可されない。

## 2. Phase Goal

Phase 2のMilestoneは`Persistent Chat and Explicit Runtime Composition`である。

- Conversation／Session／Turn／Message Identity
- Process／BrowserをまたぐConversation Persistence／Resume
- Chat List、History、New Chat、Regenerate、Branch候補
- Configuration Control Surface
- 一般利用者向け設定と研究・開発者向け設定の分離
- Runtime Composition Switchboardの基礎
- Phase 1-ex Documentation RAGのSourceを保持したFollow-up
- macOS／LightningでのCross-environment Acceptance

元来の機能作業へ入る前に、Phase 2-0でDocument-driven Orchestration Pilotの成立性を最小単位から検証する。

## 3. Subphase Plan

```text
Phase 2-0 : Document-driven Orchestration Pilot Design／Bootstrap
Phase 2-A : Phase Contract／Conversation Domain Foundation
Phase 2-B : Conversation Persistence／Lifecycle Services
Phase 2-C : Conversation Application UX
Phase 2-D : Configuration Control Surface／Research Developer Mode
Phase 2-E : Runtime Composition Switchboard／Documentation RAG Follow-up
Phase 2-F : Cross-environment Acceptance／Phase Closure
```

P2-0は`ADJUSTED_GO／bounded_unit ceiling`としてAccepted／Closedとなった。2-A～2-Fの局所設計、Task構成およびAcceptanceは、各Subphaseで最高責任者役と委譲Roleが動的に確定し、最上位規則、Role AuthorityおよびHuman Gateを維持する。

## 4. Phase 2-0 Design Package

- [Automation Pilot Requirements](requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Automation Pilot Architecture](architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest Draft](governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Phase Designer Role View Draft](governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Automation Pilot Execution Plan](operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Phase Designer Bootstrap Handoff Draft](handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Documentation Capability Contract](../../shared/automation/documentation_capability_contract_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)

`*_draft_ja.md`はP2-0設計経緯と初期ContractのStable参照であり、現在有効なTask Authorityまたは未完了Gateを表さない。実行時Authorityは各Work UnitのFrozen History PackageとUser Acceptanceで確定し、P2-0 Closure後に旧Draftを次Subphaseへ流用しない。

Work Unit State：

```text
P2-0-WU-001 : consumed／safety pass／recovery fail
P2-0-WU-002 : accepted／closed／18 of 18 bounded read recovery
P2-0-WU-003 : result verified／literal provider grammar fail／adjust required
P2-0-WU-004 : accepted／closed／6 of 6 capability-semantics conformance pass
```

P2-0-WU-003 Result：

```text
Artifact Content    : PASS
Exact Path／Digest  : PASS
Existing Mutation  : ZERO
Additional Artifact: ZERO
Provider Grammar   : FAIL by Child self-report
Stop Behavior      : PASS／no cleanup
Overall            : ADJUST_REQUIRED／not accepted
```

再設計後の検証結果：

```text
ID                  : P2-0-WU-004
Name                : Capability-semantics Bounded Documentation Create Retest
Task                : Phase 2設計担当者役 P2-0-WU-004
Manifest Coverage   : 6／6／1,324 lines
Read Scope          : exact_single_target_read
Write Result        : one exact create／existing mutation 0
Provider Policy     : semantic_mapping
Batch Capability    : unavailable／deny
Controller Review   : PASS／ACCEPTED
User Final Acceptance: ACCEPTED／CLOSED
```

P2-0-WU-003成果物はEvidenceとして保持し、削除・上書き・再生成しない。P2-0-WU-004では、Raw Command名ではなくAuthority、Exact Scope、Capability Semantics、Provider Mapping、Invocation EvidenceおよびResult／Mutation Reviewを分離する。過去のAcceptanceまたはStart Eventを継承しない。

## 5. Authorization Boundary／Completed Gate

P2-0-WU-004では次のGateが順序どおり成立した。

1. Documentation Capability ContractとProvider MappingのReview合格。
2. Small Exact Manifest、Envelope、Role View、Handoff、Adapter RevisionおよびDetached Freeze Receiptの確定。
3. `exact_single_target_read`、一件の新規Create、Batch DenyおよびMutation BoundaryのPreflight合格。
4. ユーザーによるExact Packageと新Task 1件の明示承認。
5. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示と`ARMED`化。
6. その後のユーザーによる「ok。では開始する。」の明示と`ON`化。

P2-0-WU-004の完了は、Envelope外のTask、旧TaskへのAction、権限拡張、File／Git／GitHub／External／Secret／課金／Destructive ActionまたはPhase 2-Aの実行Authorityを生成しない。P2-0 ClosureはユーザーのFinal Acceptanceにより完了した。Phase 2-A開始前のHuman Gateは区切りBackupと明示的な開始指示に限定する。

Automation Pilotでは、通常運転と共通のRole／Docs Authority、運用規則およびRoleごとの判断責任を使い、Exact Accepted Envelopeが承認済み到達線内の連結実行だけを有効化する。同じ規則をMode別に複製せず、判断を機械的Resolverへ置換しない。全Role／Taskは委譲された役割、実行権限、Docs Authority、Accepted DesignおよびWork Unit内を都度判断し、Routine Actionごとに最高責任者役へ確認しない。既存Stable文書への直書きは、Modeを問わずユーザーがExact TargetとActionを明示した場合だけ成立する。

初期の責任連鎖は、`Implementer完了報告 → Phase Designer Review／局所Accepted → 最高責任者役Review／Task完了判定案 → User Acceptance → 次Work Unit`とする。例外、重大問題、Scope外、規則Conflict、Cross-Phase影響、Security／Privacy／Recovery Risk、Provider／Resource異常または定義済みGateだけを直属上位へEscalateする。初期はTask／有界Work Unit単位で検証し、Evidence後にSubphase、Phase、Project単位へ段階的に拡張する。

Human-private Backup／Recovery AssetはAI側の認識、Read、Evidence、ValidationまたはActivation Gateへ入れない。最上位規則群とExact Authorized Rootは例外なく維持する。

最上位規則の追加・変更・削除・例外化およびそれらの指示はHuman-only Authorityである。Pilot中の全Taskは最上位Rule候補を自発登録しない。違反または疑いの発生後は、誤生成Artifactを含むCleanupも行わず、ユーザーへ報告して指示を待つ。

## 6. Project Responsibility／Design Governance

- [Project Responsibility Handoff](../../shared/project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Project Responsibility Recovery Manifest](../../shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md)
- [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Design Governance Recovery Manifest](../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804061104.md)

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。プロジェクト責任者役Recoveryは設計統括者役Recoveryを置換せず、両Folder／Stable／History／Recoveryを分離して相互参照する。Pilot Start Event成立直後だけTask名変更を試行し、それ以前は変更しない。

両RoleはHuman-defined Supreme Rulesから一切免除されない。Automation `ON`時はAccepted EnvelopeとRole Authority Matrixの交差内を自律実行し、通常運用の下位GateをAI判断で再適用しない。

## 7. Empirical Evidence Input

- [Automation Governance Index](../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../shared/automation/automation_governance_evidence_log_ja.md)
- [Constitution Research Index](../../shared/constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../../shared/constitution/constitution_source_evidence_register_ja.md)
- [Experimental Document-driven Orchestration](../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Cross-project Development Governance Constitution Plan](../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)

Phase 1-ex Closureから、Exact Scope、Semantic Freshness、Test後Cache、Transactional Closure、Post-freeze Evidence、Stable／History Byte一致、Recovery分離およびScoped Authorizationの知見をPilot設計へ反映した。

## 8. Privacy／Secret／Unwanted Artifact Scan Timing

Repository全体のPrivacy、Secret、識別情報、不要物およびPublication Sanitation Scanは、CommitまたはPushを行う作業単位だけで実施する。通常のDocs編集、設計、Review、Test、HandoffまたはPhase途中Backupごとに広域Scanを繰り返さない。

具体的な疑い、Incidentまたはユーザーの明示依頼がある場合は、対象を限定したRead-only Checkを例外実施できる。本Gate Reconciliation単位はユーザーがCommit／Pushを明示承認済みであるため、公開Sanitation Policyに従うPreflight／Outgoing範囲Scanを実施する。

## 9. History／Index Rule

Phase 2から、Append-only Documentation Index Snapshotは次へ保存する。

```text
docs/project/phases/phase_2/history/index/documentation_index_YYYYMMDDHHMMSS.md
```

最新Stable入口は本`phase_index_ja.md`のまま維持する。Timestampを付けるのはHistory Snapshotだけとする。Phase 1／Phase 1-exの旧Indexを遡及移動しない。

## 10. Current Open Gates

- P2-A-WU-001 Phase Contract／Domain／Storage Boundary Design Freeze
- P2-A-WU-002 Domain Contracts／Ports／Unit Test Implementation
- P2-A-WU-003 Compatibility／Acceptance／Subphase Closure Review

P2-0累積Evidenceと`ADJUSTED_GO／bounded_unit ceiling`はユーザーによりAccepted／Closedとなった。Phase 2-A開始Gateも成立済みで、現在のTechnical Blockerはない。Provider Lifecycle、Resource、Multi-provider、機械的Path強制、`workflow／phase／project` AutomationおよびConstitution Compilationは後続研究・昇格条件である。

## 10.1 Latest Design Revision Evidence

- [Automation Control／Combined Role Revision](history/operations/phase_2_automation_control_and_combined_role_revision_20260809181100.md)
- [Documentation Index Snapshot 20260809181100](history/index/documentation_index_20260809181100.md)
- [Constitution Workspace／Pre-pilot Checkpoint Reservation](history/operations/phase_2_constitution_workspace_and_pre_pilot_checkpoint_reservation_20260809184134.md)
- [Documentation Index Snapshot 20260809184134](history/index/documentation_index_20260809184134.md)
- [Pre-pilot Governance Full Consolidation](history/operations/phase_2_pre_pilot_governance_full_consolidation_20260809195620.md)
- [Documentation Index Snapshot 20260809195620](history/index/documentation_index_20260809195620.md)
- [Pre-pilot Gate Reconciliation](history/operations/phase_2_pre_pilot_gate_reconciliation_20260809210503.md)
- [Documentation Index Snapshot 20260809210503](history/index/documentation_index_20260809210503.md)
- [Initial Automation Pilot Execution Evidence](history/operations/phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
- [Documentation Index Snapshot 20260811000435](history/index/documentation_index_20260811000435.md)
- [Bounded Read Retest Redesign Evidence](history/operations/phase_2_0_bounded_read_retest_redesign_20260811001918.md)
- [Role Authority Matrix Redesign Evidence](history/operations/phase_2_0_role_authority_matrix_redesign_20260811010924.md)
- [Draft-3からDocument Authorityまでの新規知見](history/operations/phase_2_0_draft3_to_document_authority_findings_20260811013723.md)
- [Mode-invariant Role／Document Authority Correction](history/operations/phase_2_0_mode_invariant_role_and_document_authority_correction_20260811104642.md)
- [Documentation Index Snapshot 20260811104642](history/index/documentation_index_20260811104642.md)
- [Dynamic Documentation Resolution／General Hard-code Rule Evidence](history/operations/phase_2_0_dynamic_documentation_resolution_and_general_hardcode_rule_20260811113401.md)
- [Documentation Index Snapshot 20260811113401](history/index/documentation_index_20260811113401.md)
- [Responsible-role Dynamic Judgment Correction](history/operations/phase_2_0_responsible_role_dynamic_judgment_correction_20260811122047.md)
- [Documentation Index Snapshot 20260811122047](history/index/documentation_index_20260811122047.md)
- [Delegated Role-local Judgment／Layered Completion Evidence](history/operations/phase_2_0_delegated_role_dynamic_judgment_hierarchy_20260811124635.md)
- [Documentation Index Snapshot 20260811124635](history/index/documentation_index_20260811124635.md)
- [Delegated Escalation／Envelope／Handoff Authority Correction](history/operations/phase_2_0_delegated_escalation_and_handoff_correction_20260811130930.md)
- [Documentation Index Snapshot 20260811130930](history/index/documentation_index_20260811130930.md)
- [Roadmap／Current State Checkpoint Refresh](history/operations/phase_2_0_roadmap_and_checkpoint_state_refresh_20260811132741.md)
- [Documentation Index Snapshot 20260811132741](history/index/documentation_index_20260811132741.md)
- [P2-0-WU-003 Controller Review](history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [P2-0-WU-003 Capability Contract Redesign](history/operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md)
- [P2-0-WU-004 Result](history/operations/phase_2_0_documentation_capability_conformance_result_p2_0_wu_004_20260811233209.md)
- [P2-0-WU-004 Controller Review](history/operations/phase_2_0_documentation_capability_controller_review_p2_0_wu_004_20260812001515.md)
- [P2-0-WU-004 User Acceptance](history/operations/phase_2_0_documentation_capability_user_acceptance_p2_0_wu_004_20260812001837.md)
- [P2-0 Cumulative Controller Review](history/operations/phase_2_0_automation_pilot_cumulative_controller_review_20260812002752.md)
- [P2-0 Blocker Correction／Closure-ready](history/operations/phase_2_0_blocker_correction_and_closure_ready_20260812004603.md)
- [P2-0 Final Closure Acceptance／Phase 2-A Ready](history/operations/phase_2_0_final_closure_acceptance_and_phase_2_a_ready_20260812012339.md)
- [Phase 2-A Start／Automation Activation Receipt](history/operations/phase_2_a_start_and_automation_activation_receipt_20260812014331.md)

## 11. Formal Deferrals

- Current／Shared／Public非History Stableの英語派生版は、日本語正本と同粒度で作成する後続作業へ延期する。Phase 2開始のBlockerではない。
- Constitution本体のCompilationはAgent／Tool本格実装前の別Gateであり、Phase 2-0ではEvidence収集だけを行う。
- Phase 1-ex Documentation RAG回答品質の追加調整は、Guard／Judge／Governance、高性能Modelまたは後続RAG Phaseと合わせて再開する。
- Claude Code等とのMulti-provider Orchestrationは未決定の将来検証候補であり、Phase 2-0初回Work Unitには含めない。

## 12. Current Closure State

P2-0-WU-002はBounded Read Recoveryに合格した。P2-0-WU-003はExact Resultを一件作成し、Content、Path、DigestおよびMutation Safetyに合格したが、子TaskがAccepted HandoffのProvider Grammar違反を自己申告したため、`ADJUST_REQUIRED`として安全停止した。成果物はIncident Evidenceとして保持し、Cleanupまたは遡及修正を行わない。

P2-0-WU-004はCapability Semantics、Provider Mapping、Invocation EvidenceおよびDimension-separated Reviewを用いて合格し、User Final Acceptanceにより`ACCEPTED／CLOSED`となった。P2-0の有界Automation成立性は確認済みであり、Controller提案は`ADJUSTED_GO／bounded_unit ceiling`である。

P2-0累積Evidence、Stable整合およびController提案はユーザーによりFinal Acceptedとなり、P2-0は`COMPLETE／ACCEPTED／CLOSED`である。Phase 2-A開始前Backupと開始指示も成立し、現在はP2-A-WU-001の設計Freezeを実行中である。利用可能量等で中断する場合は、本IndexとAppend-only Statusを最後の確認済み地点へ更新する。

## 13. Related Current／Public Entry

- [Current Documentation Index](../../current/documentation_index_ja.md)
- [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)
- [Public Roadmap](../../../public/roadmap_ja.md)
- [README](../../../../README.md)

## 14. Pre-pilot Governance Baseline

- [Pre-pilot Automation Governance Baseline](../../shared/automation/pre_pilot_governance_baseline_ja.md)
- [Research Asset Mutation Control](../../shared/operations/research_asset_mutation_control_ja.md)
- [Git Workflow Policy](../../shared/operations/git_workflow_policy_ja.md)
- [Phase Completion Review／Backup Gate](../../shared/operations/phase_completion_review_and_backup_gate_ja.md)

```text
Control State           : ON／PHASE 2-A／P2-A-WU-001 ACTIVE
Automation Level        : bounded_unit
P2-0-WU-002             : accepted／closed
P2-0-WU-003             : content pass／provider grammar fail／adjust required
P2-0-WU-003 Artifact    : retained／content verified／no cleanup
P2-0-WU-004             : accepted／closed／capability-semantics pass
Capability Contract     : activated／verified in WU-004
Provider Mapping        : semantic_mapping／mechanical enforcement unavailable
Batch Capability        : unavailable／deny
Permission Hardening     : undecided／not authorized
Mechanical Enforcement  : research candidates only／not implemented
Commit／Push             : content commit f21829f pushed／local・origin・remote aligned
```

最上位規則の追加・変更・削除・並替え・例外化・候補登録は、ユーザーまたはユーザーが明示指定した人間だけが指示できる。Pilot、Provider、Role、Automation Levelまたは将来の上位権限は例外を生成しない。

General Hard-code ProhibitionのNormative本文と許可範囲内の判断Authorityは[Task Role／Write Authority Policy](../../shared/task_roles/task_role_write_authority_policy_ja.md)を正本とする。Phase Indexでは重複条文を増やさず、Phase 2-0固有の状態と投影だけを記録する。
