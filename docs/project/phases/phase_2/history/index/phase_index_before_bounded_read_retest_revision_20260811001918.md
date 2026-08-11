# MARGPA Runtime LLM Phase 2 Index

```yaml
document_id: phase_2_index
status: in_progress
phase: phase_2
active_subphase: phase_2_0_initial_pilot_review_pending
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 00:04:35 JST
owner: プロジェクト責任者兼設計統括者役
project_responsibility: combined_with_design_governance
independent_task_created: true
functional_implementation_started: false
```

## 1. Phase Entry Decision

ユーザーはGitHub、最新DocsおよびBackupを確認し、Phase 1-ex完了を改めてAcceptedし、Phase 2開始と自動化Pilot設計の継続を明示した。

```text
Phase 1-ex          : COMPLETE／ACCEPTED
Phase 2             : STARTED
Current Subphase    : Phase 2-0 Initial Pilot Review Pending
Pilot Design        : INITIAL BOUNDED UNIT EXECUTED
Authorization       : draft-2 ACCEPTED FOR P2-0-WU-001／UNIT CONSUMED
Independent Task    : ONE CREATED／IDLE／REVIEW WAITING
Pilot Execution     : SAFETY PASS／RECOVERY FAIL／ADJUST PROPOSED
Functional Work     : NOT STARTED
Capability Preflight: TASK MANAGEMENT PASS／LOCAL FILE READER GAP
Git Checkpoint      : LOCAL／ORIGIN ALIGNED AT ea320a13
Current Stop Point  : USER GO／ADJUST／STOP DECISION
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
- [Automation Pilot Execution Plan](operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Phase Designer Bootstrap Handoff Draft](handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)

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

## 5. Authorization Boundary

初回Taskの作成とPilot開始には、次を全て必要とする。

1. Phase 2-0 Design PackageのReview合格。
2. Read-only Provider Capability Preflight合格。
3. Exact Manifest／Envelope Revision／Handoff Revision・DigestのFreeze。
4. 対象差分Reviewと、ユーザーによる当該Commit／Pushの明示承認後にGit Checkpointを作成し、Local／Remote一致を確認。
5. ユーザーによる大規模Backup取得完了の明示報告。
6. ユーザーによる[Authorization Envelope Draft](governance/phase_2_0_authorization_envelope_draft_ja.md)Exact Revisionと1件のChild Task作成範囲の明示承認。
7. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示と`ARMED`化。
8. その後のユーザーによる「ok。では開始する。」の明示と`ON`化。

Envelope外のTask、権限拡張、File／Git／GitHub／External／Secret／課金／Destructive Action、Phase移行またはUser Gate省略は、改めてユーザー明示承認を必要とする。

最上位規則の追加・変更・削除・例外化およびそれらの指示はHuman-only Authorityである。Pilot中の全Taskは最上位Rule候補を自発登録しない。違反または疑いの発生後は、誤生成Artifactを含むCleanupも行わず、ユーザーへ報告して指示を待つ。

## 6. Project Responsibility／Design Governance

- [Project Responsibility Handoff](../../shared/project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Project Responsibility Recovery Manifest](../../shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md)
- [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Design Governance Recovery Manifest](../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804061104.md)

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。プロジェクト責任者役Recoveryは設計統括者役Recoveryを置換せず、両Folder／Stable／History／Recoveryを分離して相互参照する。Pilot Start Event成立直後だけTask名変更を試行し、それ以前は変更しない。

両Roleは絶対禁止、Docs、Authority、Mutation、Backup、Git／公開およびUser Gateから免除されない。

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

- 初回`P2-0-WU-001`に対するユーザーの`GO／ADJUST／STOP`確定
- `ADJUST`の場合、Provider-neutral Read CapabilityとProvider Adapter境界の再設計
- 新Envelope Revision、再試験Task数、旧Task保持および新しいHuman Gateの確定
- 再試験する場合のGit Checkpoint／Backup粒度のユーザー判断
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

## 11. Formal Deferrals

- Current／Shared／Public非History Stableの英語派生版は、日本語正本と同粒度で作成する後続作業へ延期する。Phase 2開始のBlockerではない。
- Constitution本体のCompilationはAgent／Tool本格実装前の別Gateであり、Phase 2-0ではEvidence収集だけを行う。
- Phase 1-ex Documentation RAG回答品質の追加調整は、Guard／Judge／Governance、高性能Modelまたは後続RAG Phaseと合わせて再開する。
- Claude Code等とのMulti-provider Orchestrationは未決定の将来検証候補であり、Phase 2-0初回Work Unitには含めない。

## 12. Current Stop

初回有界PilotはSafety Pass／Recovery Failで終了し、`REVIEW_PENDING／PAUSED`で停止している。現在の提案は`ADJUST`だが、ユーザーFinal Decisionではない。既存Taskへ追加Follow-upを送らず、新Task、Envelope Revision、Docs再設計、Source実装、Git／External MutationまたはPhase 2-Aへ進まない。

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
Control State           : PAUSED／REVIEW_PENDING
Automation Level        : bounded_unit
READY Evidence          : completed for draft-2
Dual Consent            : completed for P2-0-WU-001
Independent Task        : one created／idle／review waiting
Pilot                    : safety pass／recovery fail／adjust proposed
Task Rename              : exact title confirmed after one user-authorized retry
Capability Preflight     : task management pass／local file reader gap observed
Permission Hardening     : undecided／not authorized
Mechanical Enforcement  : research candidates only／not implemented
Commit／Push             : no new authorization for post-pilot Docs
```

最上位規則の追加・変更・削除・並替え・例外化・候補登録は、ユーザーまたはユーザーが明示指定した人間だけが指示できる。Pilot、Provider、Role、Automation Levelまたは将来の上位権限は例外を生成しない。
