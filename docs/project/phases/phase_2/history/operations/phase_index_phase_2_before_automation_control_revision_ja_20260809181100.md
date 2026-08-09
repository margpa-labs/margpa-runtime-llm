# MARGPA Runtime LLM Phase 2 Index

```yaml
document_id: phase_2_index
status: in_progress
phase: phase_2
active_subphase: phase_2_0_automation_pilot_design
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-04 11:17:44 JST
owner: 設計統括者役
project_responsibility: current_design_governance_role
independent_task_created: false
functional_implementation_started: false
```

## 1. Phase Entry Decision

ユーザーはGitHub、最新DocsおよびBackupを確認し、Phase 1-ex完了を改めてAcceptedし、Phase 2開始と自動化Pilot設計の継続を明示した。

```text
Phase 1-ex          : COMPLETE／ACCEPTED
Phase 2             : STARTED
Current Subphase    : Phase 2-0 Automation Pilot Design
Pilot Design        : DRAFT COMPLETE／REVIEW PENDING
Authorization       : DRAFT／NOT ACCEPTED
Independent Task    : NOT CREATED
Pilot Execution     : NOT STARTED
Functional Work     : NOT STARTED
Current Stop Point  : USER DESIGN REVIEW
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

## 5. Authorization Boundary

初回Taskの作成には、次を両方必要とする。

1. ユーザーによる[Authorization Envelope Draft](governance/phase_2_0_authorization_envelope_draft_ja.md)の明示承認。
2. Accepted Envelopeに基づく独立Task作成の明示依頼。

Envelope外のTask、権限拡張、File／Git／GitHub／External／Secret／課金／Destructive Action、Phase移行またはUser Gate省略は、改めてユーザー明示承認を必要とする。

## 6. Project Responsibility／Design Governance

- [Project Responsibility Handoff](../../shared/project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Project Responsibility Recovery Manifest](../../shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md)
- [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Design Governance Recovery Manifest](../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804061104.md)

プロジェクト責任者役Recoveryは、設計統括者役Recoveryを置換しない。Project全体とCross-Phase Gateを扱うRoleと、技術設計とCanonical Meaningを扱うRoleを分離し、相互参照してLosslessに復元する。

両Roleは絶対禁止、Docs、Authority、Mutation、Backup、Git／公開およびUser Gateから免除されない。

## 7. Empirical Evidence Input

- [Automation／Governance Evidence Log](../../shared/operations/automation_governance_evidence_log_ja.md)
- [Experimental Document-driven Orchestration](../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Cross-project Development Governance Constitution Plan](../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)

Phase 1-ex Closureから、Exact Scope、Semantic Freshness、Test後Cache、Transactional Closure、Post-freeze Evidence、Stable／History Byte一致、Recovery分離およびScoped Authorizationの知見をPilot設計へ反映した。

## 8. Privacy／Secret／Unwanted Artifact Scan Timing

Repository全体のPrivacy、Secret、識別情報、不要物およびPublication Sanitation Scanは、CommitまたはPushを行う作業単位だけで実施する。通常のDocs編集、設計、Review、Test、HandoffまたはPhase途中Backupごとに広域Scanを繰り返さない。

具体的な疑い、Incidentまたはユーザーの明示依頼がある場合は、対象を限定したRead-only Checkを例外実施できる。本Phase 2-0設計単位ではCommit／Pushを行わないため、広域Scanは実施しない。

## 9. History／Index Rule

Phase 2から、Append-only Documentation Index Snapshotは次へ保存する。

```text
docs/project/phases/phase_2/history/index/documentation_index_YYYYMMDDHHMMSS.md
```

最新Stable入口は本`phase_index_ja.md`のまま維持する。Timestampを付けるのはHistory Snapshotだけとする。Phase 1／Phase 1-exの旧Indexを遡及移動しない。

## 10. Current Open Gates

- ユーザーによるPhase 2-0 Design Package Review
- Authorization Envelopeの`GO／ADJUST／STOP`
- 独立Taskを作成する場合の明示依頼
- Task Capabilityの実行直前Read-only Preflight
- `P2-0-WU-001`の実行／Review
- Pilot全体の`GO／ADJUST／STOP`
- 元来のPhase 2-A開始判断

## 11. Formal Deferrals

- Current／Shared／Public非History Stableの英語派生版は、日本語正本と同粒度で作成する後続作業へ延期する。Phase 2開始のBlockerではない。
- Constitution本体のCompilationはAgent／Tool本格実装前の別Gateであり、Phase 2-0ではEvidence収集だけを行う。
- Phase 1-ex Documentation RAG回答品質の追加調整は、Guard／Judge／Governance、高性能Modelまたは後続RAG Phaseと合わせて再開する。

## 12. Current Stop

設計Packageを作成した時点で停止する。Task作成、Task命名、Prompt送信、Pilot実行、Source実装、CommitまたはPushへ進まない。次のActionはユーザーの設計Review結果に従う。

## 13. Related Current／Public Entry

- [Current Documentation Index](../../current/documentation_index_ja.md)
- [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)
- [Public Roadmap](../../../public/roadmap_ja.md)
- [README](../../../../README.md)

