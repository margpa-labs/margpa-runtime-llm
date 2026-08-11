# MARGPA Runtime LLM Phase 2 Index

```yaml
document_id: phase_2_index
status: in_progress
phase: phase_2
active_subphase: phase_2_0_pre_restart_commit_checkpoint
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 13:27:41 JST
owner: プロジェクト責任者兼設計統括者役
project_responsibility: combined_with_design_governance
independent_task_state: old_task_idle_new_task_not_created
functional_implementation_started: false
```

## 1. Phase Entry Decision

ユーザーはPhase 1-ex完了を改めてAcceptedし、Phase 2開始と自動化Pilot設計の継続を明示した。Human-private Recovery AssetはAutomation側の認識、EvidenceまたはActivation Gateに含めない。

```text
Phase 1-ex          : COMPLETE／ACCEPTED
Phase 2             : STARTED
Current Subphase    : Phase 2-0 draft-4 Final Alignment Gate
Pilot Design        : ROLE-LOCAL JUDGMENT／TIERED ESCALATION／ENVELOPE／HANDOFF AUTHORITY ALIGNED／REVIEW PASSED
Authorization       : draft-2 CONSUMED／draft-3／3a INVALIDATED／draft-4 NOT ACCEPTED
Independent Task    : OLD TASK IDLE／NEW TASK NOT CREATED
Pilot Execution     : SAFETY PASS／RECOVERY FAIL／ADJUST DIRECTION ACCEPTED FOR DESIGN
Functional Work     : NOT STARTED
Capability Preflight: TASK MANAGEMENT PASS／LOCAL FILE READER GAP
Git Checkpoint      : CONTENT COMMIT f21829f PUSHED／LOCAL・ORIGIN・REMOTE ALIGNED／POSTFLIGHT RECORDED
Current Stop Point  : DRAFT-4 PACKAGE FINAL ALIGNMENT BEFORE FREEZE
```

Phase 2開始は、独立Task作成、Pilot実行、Phase 2-A以降の設計／実装またはGit／External Mutationを包括許可しない。

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

2-A～2-Fの開始条件、局所再設計権限およびAcceptanceは、Phase 2-0の`GO／ADJUST／STOP`とユーザー判断後に確定する。

## 4. Phase 2-0 Design Package

- [Automation Pilot Requirements](requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Automation Pilot Architecture](architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest Draft](governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Phase Designer Role View Draft](governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Automation Pilot Execution Plan](operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Phase Designer Bootstrap Handoff Draft](handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)

初回候補Work Unit：

```text
ID              : P2-0-WU-001
Name            : Docs-only Recovery and Authority Acknowledgement
Candidate Task  : Phase 2設計担当者役／maximum one
Write Authority : none
Git Authority   : none
External／Secret: none
Sub-agent       : none
Output          : conversation-only structured recovery assessment
```

初回実行結果：

```text
Task Creation       : PASS／exactly one
Exact Task Title    : PASS after one user-authorized retry
Authority ACK       : PASS
Docs Recovery       : FAIL／0 of 18 read
Stop Behavior       : PASS／fail-closed
Mutation            : ZERO
Current Review      : ADJUST proposed／user decision pending
```

Recovery未達の直接原因は、Local Docs読取要件とShell全面禁止を同時に課した一方、実行ProviderにLocal Text Fileを直接読むProvider-native Readerがなかったことである。TaskはShell等へ迂回せず停止したため、安全性の成立と機能目的の未達を分離して評価する。

再試験Draft：

```text
ID              : P2-0-WU-002
Name            : Bounded Read Cold Recovery Retest
Candidate Task  : Phase 2設計担当者役 P2-0-WU-002／one new Task
Read Scope      : Frozen Exact Manifest 18 entries
Read Adapter    : Provider-specific bounded read grammar
Write Authority : none
Old Task Action : none
Current State   : design draft／not authorized
```

Path一覧は一つのRead Manifestへ集約し、Core CapabilityとCodex固有Adapterを分離する。再試験は旧Conversationを持たない新Taskを使用し、過去のAcceptanceまたはStart Eventを継承しない。

## 5. Authorization Boundary

再試験Taskの作成とPilot再開には、次を全て必要とする。

1. Phase 2-0 Design PackageのReview合格。
2. Bounded Read Provider Adapter Preflight合格。
3. [Role Authority Matrix](../../shared/task_roles/role_authority_matrix_ja.md)、Document Authorityを明示した[Phase Designer Role View draft-2](governance/phase_2_0_phase_designer_role_view_draft_ja.md)、Exact Manifest／Envelope draft-4／Handoff／AdapterとDetached Freeze Receiptの確定。
4. ユーザーによる[Authorization Envelope Draft](governance/phase_2_0_authorization_envelope_draft_ja.md)Exact draft-4、Role View、Freeze Receiptと新Task 1件の明示承認。
5. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示と`ARMED`化。
6. その後のユーザーによる「ok。では開始する。」の明示と`ON`化。

Envelope外のTask、旧TaskへのAction、権限拡張、File／Git／GitHub／External／Secret／課金／Destructive Action、Phase移行またはUser Gate省略は、改めてユーザー明示承認を必要とする。

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

- 本Roadmap／Current Documentation Index／Phase 2 Indexを含むDocs CheckpointのCommit／PushとLocal／Remote一致確認
- Role View draft-2／Authorization Envelope draft-4／Manifest／Handoff／Provider Adapterの最終整合確認
- Bounded Read Provider Adapter再照合
- Exact Manifest／Detached Freeze Receiptの再作成
- Exact draft-4／Role View／Freeze Receipt／新Task 1件のユーザーAcceptance
- Controller READY／ARMEDと後続User Start
- Pilot全体の`GO／ADJUST／STOP`
- 元来のPhase 2-A開始判断

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

## 11. Formal Deferrals

- Current／Shared／Public非History Stableの英語派生版は、日本語正本と同粒度で作成する後続作業へ延期する。Phase 2開始のBlockerではない。
- Constitution本体のCompilationはAgent／Tool本格実装前の別Gateであり、Phase 2-0ではEvidence収集だけを行う。
- Phase 1-ex Documentation RAG回答品質の追加調整は、Guard／Judge／Governance、高性能Modelまたは後続RAG Phaseと合わせて再開する。
- Claude Code等とのMulti-provider Orchestrationは未決定の将来検証候補であり、Phase 2-0初回Work Unitには含めない。

## 12. Current Stop

初回有界PilotはSafety Pass／Recovery Failで終了した。その後の再設計で、Role／Docs Authorityを通常運転用とAutomation用へ不要に二重化しかけたため、共通Role契約＋Automation Overlayへ修正した。固定Document PackageがHard-codeと過剰生成を生むことをReviewで検出した後、さらに独立したDynamic Resolverを前提にする過剰設計と、全判断を最高責任者役へ集中させる危険を検出した。現行設計は、通常運転と同様に、全Role／Taskが最上位規則群と共通Docs／運用規則を守りつつ委譲範囲内を都度判断し、最高責任者役はProject／Cross-Role／Gateを調整し、Automationは承認済み到達線内の連結だけを追加する構造へ修正した。

現在は`PAUSED／ROLE_AUTHORITY_DESIGN`である。委譲Role-local Judgment、Tiered Escalation、Authorization Envelope投影およびCommunication Authority分離のCorrection Reviewは合格し、本状態のDocs CheckpointをCommit `f21829f`として`origin/main`へPushした。次はdraft-4 Package最終整合、FreezeおよびTwo-key Activationであり、それ以前に新Taskを作成しない。

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
Control State           : PAUSED／ROLE_AUTHORITY_DESIGN
Automation Level        : bounded_unit
READY Evidence          : draft-2 consumed／draft-3／3a invalidated／draft-4 pending
Document Authority      : common mode-invariant matrix corrected／tiered escalation and communication authority aligned／review passed
Dual Consent            : draft-2 consumed／draft-4 not performed
Independent Task        : old one idle／new none
Pilot                    : safety pass／recovery fail／adjust proposed
Task Rename              : exact title confirmed after one user-authorized retry
Capability Preflight     : task management pass／bounded read grammar sample pass／full recheck pending
Permission Hardening     : undecided／not authorized
Mechanical Enforcement  : research candidates only／not implemented
Commit／Push             : content commit f21829f pushed／local・origin・remote aligned
```

最上位規則の追加・変更・削除・並替え・例外化・候補登録は、ユーザーまたはユーザーが明示指定した人間だけが指示できる。Pilot、Provider、Role、Automation Levelまたは将来の上位権限は例外を生成しない。

General Hard-code ProhibitionのNormative本文と許可範囲内の判断Authorityは[Task Role／Write Authority Policy](../../shared/task_roles/task_role_write_authority_policy_ja.md)を正本とする。Phase Indexでは重複条文を増やさず、Phase 2-0固有の状態と投影だけを記録する。
