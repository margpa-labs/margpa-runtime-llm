# MARGPA Runtime LLM Phase 2 Index

```yaml
document_id: phase_2_index
status: complete_accepted
phase: phase_2
active_subphase: phase_2_f_complete
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-21 03:10:52 JST
owner: プロジェクト責任者兼設計統括者役
project_responsibility: combined_with_design_governance
independent_task_state: phase_2_tasks_closed_or_historical
functional_implementation_started: true
```

## 1. Phase Entry Decision

ユーザーはPhase 1-ex完了を改めてAcceptedし、Phase 2開始と自動化Pilot設計の継続を明示した。Human-private Recovery AssetはAutomation側の認識、EvidenceまたはActivation Gateに含めない。

```text
Phase 1-ex          : COMPLETE／ACCEPTED
Phase 2             : COMPLETE／ACCEPTED
Current Subphase    : Phase 2-F COMPLETE／PHASE CLOSED
Pilot Design        : COMPLETE／BOUNDED-UNIT VIABILITY ESTABLISHED
P2-0-WU-002         : ACCEPTED／CLOSED／BOUNDED READ RECOVERY PASS
P2-0-WU-003         : CONTENT・MUTATION SAFETY PASS／PROVIDER GRAMMAR FAIL／ADJUST REQUIRED
P2-0-WU-004         : ACCEPTED／CLOSED／CAPABILITY-SEMANTICS RETEST PASS
Independent Task    : P2-0-WU-004 IDLE／NO FURTHER ACTION AUTHORIZED
Pilot Execution     : ADJUSTED_GO／USER ACCEPTED／BOUNDED_UNIT CEILING
Phase 2-A Work Unit : P2-A-WU-003／COMPLETE／USER ACCEPTED
Functional Work     : PHASE 2-A～2-D COMPLETE／USER ACCEPTED
Automation Evidence : PHASE 2-B～2-D ROLE CHAIN PASS／PHASE 2-E CROSS-PROVIDER CHAIN PASS WITH GOVERNANCE VIOLATION
Multi-provider Gate : CLAUDE COMPLETE_CANDIDATE／CODEX REVIEW／MAC MANUAL ACCEPTANCE COMPLETE
Capability Contract : ACTIVATED AND VERIFIED IN P2-0-WU-004
Git Checkpoint      : CONTENT COMMIT f21829f PUSHED／LOCAL・ORIGIN・REMOTE ALIGNED／POSTFLIGHT RECORDED
Current Stop Point  : PHASE 2 COMPLETE／PHASE 3 READY・NOT STARTED／AUTOMATION OFF
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

## 4.1 Phase 2-A Design／Execution Package

- [Conversation Domain Requirements](requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Conversation Domain Architecture](architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [Conversation Domain ADR](adr/phase_2_a_conversation_domain_adr_ja.md)
- [Implementation Authorization Envelope](governance/phase_2_a_implementation_authorization_envelope_ja.md)
- [Execution Plan](operations/phase_2_a_execution_plan_ja.md)
- [Implementation Handoff](handoffs/phase_2_a_implementation_handoff_ja.md)
- [P2-A-WU-001 Design Freeze Receipt](history/operations/phase_2_a_wu_001_design_freeze_receipt_20260812015152.md)
- [P2-A-WU-002 Implementer Status](history/handoffs/implementer_status_phase_2_a_wu_002_20260812020515.md)
- [P2-A-WU-002 Controller Review](history/operations/phase_2_a_wu_002_controller_review_20260812020515.md)
- [P2-A-WU-003 Closure Review](history/operations/phase_2_a_wu_003_closure_review_20260812021052.md)
- [P2-A-WU-003 Final Closure Review](history/operations/phase_2_a_wu_003_final_closure_review_20260812021546.md)
- [P2-A-WU-001 Freeze Correction Receipt](history/operations/phase_2_a_wu_001_design_freeze_correction_receipt_20260812021546.md)
- [Phase 2-A Bounded Automation Evidence](history/operations/phase_2_a_bounded_automation_execution_evidence_20260812021546.md)
- [Phase 2-A Role Delegation Evidence Correction](history/operations/phase_2_a_role_delegation_evidence_correction_20260814002301.md)
- [Phase 2-B Entry Handoff](handoffs/phase_2_b_entry_handoff_ja.md)

P2-A-WU-001では、Conversation／Scope／Session／Turn／Message／Storage Operation／Generation Requestを分離し、`1 Turn = 1 User + 0/1 Assistant`、Branch Projection、Store-owned CAS Revision、Explicit Migration、Public／Shared Preview Zero-writeおよびPhase 1 v1無変更をFreezeした。Component Registry／SwitchboardはPhase 2-Eであり、Phase 2-Aへ戻さない。

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

## 4.2 Phase 2-B Design／Implementation Package

- [Conversation Persistence Requirements](requirements/phase_2_b_conversation_persistence_requirements_ja.md)
- [Conversation Persistence Architecture](architecture/phase_2_b_conversation_persistence_architecture_ja.md)
- [Conversation Persistence ADR](adr/phase_2_b_conversation_persistence_adr_ja.md)
- [Implementation Handoff](handoffs/phase_2_b_implementation_handoff_ja.md)
- [Acceptance Matrix](operations/phase_2_b_acceptance_matrix_ja.md)
- [Design Freeze Receipt](history/operations/phase_2_b_design_freeze_receipt_20260814013652.md)
- [Implementer Status](history/handoffs/implementer_status_phase_2_b_20260814015827.md)
- [Initial Design Conformance Review](history/operations/phase_2_b_design_conformance_review_20260814020244.md)
- [Implementer Rework Status](history/handoffs/implementer_rework_status_phase_2_b_20260814021434.md)
- [Final Design Conformance Review](history/operations/phase_2_b_design_conformance_final_review_20260814021951.md)
- [Controller Closure](history/operations/phase_2_b_controller_closure_20260814022130.md)

Phase 2-Bでは、Phase 2-AのDomain／Portを変更せず、交換可能なLocal SQLite Adapter、Atomic CAS／Operation Idempotency、Explicit Schema／Migration／Checkpoint、Lifecycle Service、Generation Context MapperおよびCrash Recoveryを実装した。初回ReviewのRequired Finding 4件を実装者へ返し、同一Role Chain内の再作業と再Reviewで全件を解消した。

```text
Phase 2-B Target       : 49 passed
Conversation／Web      : 154 passed
Full Suite             : 528 passed／3 deselected
Ruff／Mypy             : PASS
Project runtime_data/  : absent
Existing v1 mutation   : 0
Public／Basic binding  : 0
Sensitive persistence  : 0
Closure                : PASS／GO
```

Phase 2-Bは、独立Taskによる`Designer → Implementer → Designer Review → Implementer Rework → Designer Final Review → Controller Closure`を成立させた。これは役割分業型Automationの最初の合格Evidenceであるが、Phase／Project単位の無条件自動化昇格を意味しない。次はPhase 2-Cの別Versioned Persistent API／UX設計から開始する。

## 4.3 Phase 2-C Design／Implementation Package

- [Persistent API／UX Requirements](requirements/phase_2_c_persistent_conversation_api_ux_requirements_ja.md)
- [Persistent API／UX Architecture](architecture/phase_2_c_persistent_conversation_api_ux_architecture_ja.md)
- [Persistent API／UX ADR](adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md)
- [Implementation Handoff](handoffs/phase_2_c_implementation_handoff_ja.md)
- [Acceptance Matrix](operations/phase_2_c_acceptance_matrix_ja.md)
- [Design Freeze Receipt](history/operations/phase_2_c_design_freeze_receipt_20260814023310.md)
- [Implementer Status](history/handoffs/implementer_status_phase_2_c_20260814030637.md)
- [Initial Design Review](history/operations/phase_2_c_design_conformance_review_20260814031257.md)
- [Implementer Rework Status](history/handoffs/implementer_rework_status_phase_2_c_20260814032250.md)
- [Final Design Review](history/operations/phase_2_c_design_conformance_final_review_20260814032523.md)
- [Controller Closure](history/operations/phase_2_c_controller_closure_20260814032700.md)

Phase 2-Cでは、Local／Loopback／Explicit opt-in専用の`/api/v2/conversations/**`、Server RepositoryをCanonical SourceとするChat List／History／Resume／Retry／Regenerate／Branch／Stop、CAS ConflictおよびBrowser Source-of-truth Cutoverを実装した。Capability確定前のv1 Fallback、非Durable Terminal SSEおよびZero-persistence Evidence不足は、実装者再作業と設計再Reviewで解消した。

```text
Phase 2-C Target       : 52 passed
Conversation／Web      : 226 passed
Full Suite             : 567 passed／3 deselected
Ruff／Mypy／Node        : PASS
Project runtime_data/  : absent
Existing v1 mutation   : 0
Public／Basic build/read/write: 0
Client full-history payload  : 0
Closure                : TECHNICAL PASS／GO
```

Real BrowserでのLocal Private Persistent UX手動Matrixは、Phase 2-B～2-D統合後にユーザーが実施した。Startup Recovery、Conversation復元、RAG Citation再描画およびManual Checklist 1～7は合格し、Phase 2-Cは`COMPLETE／USER ACCEPTED`である。Checklist 8は後続検討であり、Completion Blockerではない。

## 4.4 Phase 2-D Design／Implementation Package

- [Configuration Control Requirements](requirements/phase_2_d_configuration_control_requirements_ja.md)
- [Configuration Control Architecture](architecture/phase_2_d_configuration_control_architecture_ja.md)
- [Configuration Control ADR](adr/phase_2_d_configuration_control_adr_ja.md)
- [Implementation Handoff](handoffs/phase_2_d_implementation_handoff_ja.md)
- [Acceptance Matrix](operations/phase_2_d_acceptance_matrix_ja.md)
- [Design Freeze Receipt](history/operations/phase_2_d_design_freeze_receipt_20260814033900.md)
- [Test Module Identity Correction](history/operations/phase_2_d_test_module_identity_correction_20260814035021.md)
- [Implementer Status](history/handoffs/implementer_status_phase_2_d_20260814035807.md)
- [Initial Design Review](history/operations/phase_2_d_design_conformance_review_20260814040416.md)
- [Implementer Rework Status](history/handoffs/implementer_rework_status_phase_2_d_20260814040833.md)
- [Final Design Review](history/operations/phase_2_d_design_conformance_final_review_20260814041029.md)
- [Controller Closure](history/operations/phase_2_d_controller_closure_20260814041200.md)

Phase 2-Dでは、Local／Loopback／Auth-disabled／Explicit opt-in専用のProcess-local Configuration Controlを実装した。Effective ConfigはTyped Allowlist、Per-field Source、Canonical SHA-512 DigestおよびRevision CASを持ち、Live Applyを`research_developer_mode`だけへ限定する。RAG HookはAvailabilityとEnabled状態を分離し、Recording Hookは通常`off`かつRecorder Call 0である。Public／Basic、既存v1、Persistent Conversation、Tracked TOML、Environment、CLI、Secret、Agent／Tool／Switchboardへ設定WriteまたはAuthority拡張を行わない。

```text
Phase 2-D Target       : 105 passed
Config／Conversation／Web: 392 passed
Full Suite             : 613 passed／3 deselected
Ruff／Mypy／Node        : PASS
Project runtime_data/  : absent
Public／Basic control  : build/read/write/apply/route-call 0
Config／Secret write   : 0
Recorder／Agent／Tool  : 0
Closure                : TECHNICAL PASS／GO
```

初回ReviewでFeature DisabledとAdapter Unavailableの混同を検出し、4-state Projection、矛盾DescriptorのFail-closedおよびUnavailable変更時のMutation 0へ修正した。Test Module Identity衝突は、実装者が無断Scope拡張せず設計担当者へ戻し、Exact Correctionとして空Package Marker一件だけを追加して解消した。

## 4.5 Phase 2-E Claude Code Provider Bootstrap

- [Claude Design Governance Index](handoffs/claude_code/phase_2_e_claude_design_governance_index_ja.md)
- [Claude Design Governance Handoff](handoffs/claude_code/phase_2_e_claude_design_governance_handoff_ja.md)
- [Persistent RAG Citation Evidence Reservation](history/operations/phase_2_e_persistent_rag_citation_evidence_reservation_20260814215110.md)
- [Multi-provider Claude Code Delegation Decision](../../shared/history/automation/multi_provider_claude_code_phase_2_e_delegation_decision_20260814224356.md)
- [Claude Phase 2-E Completion Handoff](history/handoffs/claude_phase_2_e_completion_handoff_20260815075322.md)
- [Codex Required Rework Handoff](history/handoffs/codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md)
- [Claude Rework Completion Handoff](history/handoffs/claude_phase_2_e_rework_completion_handoff_20260815084816.md)
- [Codex Final Rework Handoff](history/handoffs/codex_to_claude_phase_2_e_final_rework_handoff_20260815090218.md)
- [Claude Final Rework Completion Handoff](history/handoffs/claude_phase_2_e_final_rework_completion_handoff_20260815092725.md)
- [Codex to Claude Mac Manual Acceptance Handoff](history/handoffs/codex_to_claude_phase_2_e_mac_manual_acceptance_handoff_20260815095155.md)
- [Cross-provider Final Assessment](../../shared/history/automation/automation_governance_evidence_phase_2_e_cross_provider_final_assessment_ja_20260815095155.md)
- [Provider Memory／Repository Canonical Authority](../../shared/automation/provider_memory_and_repository_canonical_authority_ja.md)
- [Phase 2-E Technical／Cross-provider Checkpoint](history/operations/phase_2_e_technical_and_cross_provider_checkpoint_20260815101850.md)

Codex側の利用可能量をPhase 2-E完了後の最終Reviewへ残すため、Phase 2-EはClaude Code側へ有界委譲した。Codexプロジェクト責任者兼設計統括者役を最高責任者として維持し、Claude設計統括者役、Claude Phase 2-E設計担当者役およびClaude Phase 2-E実装者役が、Recovery、Design、Freeze、Implementation、Test、ReworkおよびFinal Reviewを`COMPLETE_CANDIDATE`まで連結した。

Claude側は既存Stable文書を変更せず、設計・Handoff・Status・Review・CorrectionおよびCompletion EvidenceをTimestamp付きHistoryへAppend-onlyで新規作成した。Source／Testの変更はFrozen DesignとCodex Correctionの範囲内で行い、Routineな設計・実装・再作業をClaude側Role Chainで解決した。Codex独立Reviewは、実Mac DB Migration、Component Digest、Citation Schema VersionおよびSafe Decode境界のFindingを検出し、Claude側が局所Reworkで全件Closeした。最終自動検証は674件合格、3件deselected、Ruff／Mypy／Node検証合格である。

Phase 2-Eの実装対象であるRuntime Composition Switchboard Foundation、Documentation RAG Multi-turn Follow-upおよびPersistent Citation EvidenceはTechnical `COMPLETE_CANDIDATE`である。Reload、Server Restart、Chat再Open、Resume、Retry／RegenerateおよびBranch Selectを越えるCitation復元を自動Testで確認し、既存DB Migrationは明示Opt-in／Checkpoint／Digest／Rollback／Fail-closed契約へ修正した。現在は実Mac DBを用いるMigrationとBrowser Manual Acceptance、そのResult Handoffに対するCodex最終Reviewを残す。Phase 2-EをAcceptedまたはClosedとはまだ表記しない。

Agent自動化／Cross-provider実験もPhase 2-E成果の一部である。Provider間Handoff、Role Chain、Independent ReviewおよびCorrection Loopは成功した。一方、Claude Provider MemoryへのAuthorized Root外書込みは最上位規則違反であり、Governance適合は失敗である。Technical Success、Automation Chain Success、Cross-provider Review SuccessおよびSupreme-rule Compliance Failureを混同せず分離記録する。既存のProvider Memoryは非正本として無視し、今後の作成、更新または依存を禁止する。Cross-provider正本はRepository内Index／Handoff／Evidenceだけとする。

Phase 2-FはPhase 2-E Manual AcceptanceとCodex Closure後に別途開始する。LightningへのPhase 2反映は行わず、Phase 3またはPhase 4完了後の別Gateへ延期する。

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

## 10. Final Gate State

- P2-A-WU-001 Phase Contract／Domain／Storage Boundary Design Freeze：COMPLETE
- P2-A-WU-002 Domain Contracts／Ports／Unit Test Implementation：COMPLETE
- P2-A-WU-003 Compatibility／Acceptance／Subphase Closure Review：COMPLETE／GO
- Phase 2-B Conversation Persistence／Lifecycle：COMPLETE／USER ACCEPTED
- Phase 2-C Persistent API／Conversation UX：COMPLETE／USER ACCEPTED
- Phase 2-D Configuration Control Surface：COMPLETE／USER ACCEPTED
- Phase 2-E Runtime Composition／Documentation RAG：COMPLETE／USER ACCEPTED
- Phase 2-E Cross-provider Experiment：TECHNICAL／HANDOFF CHAIN SUCCESS、GOVERNANCE VIOLATION RECORDED
- Phase 2-E Mac Manual Acceptance：COMPLETE／PASS
- Phase 2-F Mac Final Acceptance／Phase Final Inspection：COMPLETE／PASS
- Phase 2 Lightning Cross-acceptance：FORMALLY DEFERRED TO PHASE 3／NON-BLOCKING

現在のTechnical Blockerはない。Phase 2-B～2-Dでは、独立Taskによる`Phase Designer → Implementer → Phase Designer Review → Implementer Rework → Phase Designer Final Review → Project Controller Closure`を3 Subphase連続で成立させた。Phase 2-EではClaude側Role ChainとCodex独立Reviewを接続し、Cross-provider Correction Loopまで成立させた。ただしAuthorized Root外Provider Memory書込みの最上位規則違反があるため、Governance適合や正式Automation Modeへ昇格させない。Phase／Project単位の無条件Automation、全Providerへの一般化、Resource／Credit自動制御または機械的Authorized Root Enforcementも未成立である。

Phase 2-A～2-DのReal Browser Manual MatrixとPhase 2-E Mac Manual Acceptanceはユーザー受入済みである。Phase 2-FではMac側の最終検査、Docs／Lossless／Recovery整合、Publication SanitationおよびPhase Closureを完了した。Lightning横断Acceptanceはユーザー指示によりPhase 3へ正式延期し、Phase 2完了のBlockerにしない。

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
- [P2-A-WU-001 Design Freeze Receipt](history/operations/phase_2_a_wu_001_design_freeze_receipt_20260812015152.md)
- [P2-A-WU-002 Controller Review](history/operations/phase_2_a_wu_002_controller_review_20260812020515.md)
- [P2-A-WU-003 Closure Review](history/operations/phase_2_a_wu_003_closure_review_20260812021052.md)
- [P2-A-WU-003 Final Closure Review](history/operations/phase_2_a_wu_003_final_closure_review_20260812021546.md)
- [P2-A Role Delegation Evidence Correction](history/operations/phase_2_a_role_delegation_evidence_correction_20260814002301.md)
- [Phase 2-B Controller Closure](history/operations/phase_2_b_controller_closure_20260814022130.md)
- [Phase 2-C Controller Closure](history/operations/phase_2_c_controller_closure_20260814032700.md)
- [Phase 2-D Controller Closure](history/operations/phase_2_d_controller_closure_20260814041200.md)
- [Phase 2-B～2-D Campaign Controller Closure](history/operations/phase_2_b_to_d_campaign_controller_closure_20260814042000.md)
- [Phase 2-B～2-D Manual Acceptance Rework](history/operations/phase_2_b_to_d_manual_acceptance_rework_20260814205814.md)
- [Phase 2-A～2-D User Manual Acceptance](history/operations/phase_2_a_to_d_user_manual_acceptance_20260814210500.md)
- [Documentation Index Snapshot 20260814210500](history/index/documentation_index_20260814210500.md)
- [Phase 2-E Persistent RAG Citation Evidence Reservation](history/operations/phase_2_e_persistent_rag_citation_evidence_reservation_20260814215110.md)
- [Documentation Index Snapshot 20260814215110](history/index/documentation_index_20260814215110.md)
- [Claude Design Governance Index](handoffs/claude_code/phase_2_e_claude_design_governance_index_ja.md)
- [Claude Design Governance Handoff](handoffs/claude_code/phase_2_e_claude_design_governance_handoff_ja.md)
- [Multi-provider Claude Code Delegation Decision](../../shared/history/automation/multi_provider_claude_code_phase_2_e_delegation_decision_20260814224356.md)

## 11. Formal Deferrals

- Current／Shared／Public非History Stableの英語派生版は、日本語正本と同粒度で作成する後続作業へ延期する。Phase 2開始のBlockerではない。
- Constitution本体のCompilationはAgent／Tool本格実装前の別Gateであり、Phase 2-0ではEvidence収集だけを行う。
- Phase 1-ex Documentation RAG回答品質の追加調整は、Guard／Judge／Governance、高性能Modelまたは後続RAG Phaseと合わせて再開する。
- Browser Reload、Server Restartおよび保存済みChat再表示を越えるPersistent Citation Evidenceは、Phase 2-E Documentation RAG Follow-upのExact Designへ引き継ぐ。Current Page-memory Citation境界はPhase 2-A～2-DのAccepted Stateとして保持する。
- Phase 2-0では未決定だったMulti-provider Orchestrationは、Phase 2-EでClaude Codeを用いる最初の有界検証へ移行した。Claude以外のProviderへの拡張、正式Mode化およびPhase／Project単位への昇格は、Phase 2-EのEvidenceとCodex最終Review後まで延期する。

## 12. Current Closure State

P2-0-WU-002はBounded Read Recoveryに合格した。P2-0-WU-003はExact Resultを一件作成し、Content、Path、DigestおよびMutation Safetyに合格したが、子TaskがAccepted HandoffのProvider Grammar違反を自己申告したため、`ADJUST_REQUIRED`として安全停止した。成果物はIncident Evidenceとして保持し、Cleanupまたは遡及修正を行わない。

P2-0-WU-004はCapability Semantics、Provider Mapping、Invocation EvidenceおよびDimension-separated Reviewを用いて合格し、User Final Acceptanceにより`ACCEPTED／CLOSED`となった。P2-0の有界Automation成立性は確認済みであり、Controller提案は`ADJUSTED_GO／bounded_unit ceiling`である。

P2-0累積Evidence、Stable整合およびController提案はユーザーによりFinal Acceptedとなり、P2-0は`COMPLETE／ACCEPTED／CLOSED`である。Phase 2-AもDomain／Port Contract、Compatibility ReviewおよびFull Validationを完了し、ユーザーのPhase 2-B開始指示によってFinal Acceptedとなった。

Phase 2-BはLocal SQLite Persistence／Lifecycle、Phase 2-CはLocal Persistent API／Conversation UX、Phase 2-DはLocal Configuration Controlを実装し、各Subphaseで初回Review Findingを局所再作業によって解消した。統合検証はTarget 272件、Full Suite 613件合格、3件deselected、Ruff／Mypy／Node合格である。Project Rootへの`runtime_data/`生成、Public／BasicへのPersistent／Configuration Binding、Sensitive Data通常保存およびAgent／Tool／Switchboardの先行実装は0である。

Phase 2-B～2-DのTechnical Scopeは`COMPLETE／PASS／GO`である。その後のManual AcceptanceでRecovery ID OverflowとCitation Rerender Lossを検出したが、Bounded Rework、252件のConversation／Web Regression、615件のFull Suiteおよびユーザーの再起動／復元／RAG引用確認で解消した。Phase 2-A～2-Dは`COMPLETE／USER ACCEPTED`である。

Phase 2-EはClaude Code用Recovery Index、Frozen Design、Source／Test実装、Claude内Review、Codex独立Review、Exact Rework、Mac Manual AcceptanceおよびCodex Final Reviewまで完了し、`COMPLETE／USER ACCEPTED`である。Cross-provider実験はTechnical／Handoff Chain Successと、Provider Memory書込みによるGovernance Violationを分離して記録済みである。Phase 2-Fも完了し、Phase 2は`COMPLETE／ACCEPTED`となった。Phase 3は`READY／NOT STARTED／AUTOMATION OFF`であり、別の開始Gateを必要とする。

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
Control State           : OFF／PHASE 2 COMPLETE／PHASE 3 READY・NOT STARTED
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
Commit／Push             : Phase 2 final closure and Phase 3 READY snapshot authorized／pending
```

最上位規則の追加・変更・削除・並替え・例外化・候補登録は、ユーザーまたはユーザーが明示指定した人間だけが指示できる。Pilot、Provider、Role、Automation Levelまたは将来の上位権限は例外を生成しない。

General Hard-code ProhibitionのNormative本文と許可範囲内の判断Authorityは[Task Role／Write Authority Policy](../../shared/task_roles/task_role_write_authority_policy_ja.md)を正本とする。Phase Indexでは重複条文を増やさず、Phase 2-0固有の状態と投影だけを記録する。

## 15. Phase 2-F Final Closure

```text
Phase 2-A～2-D          : COMPLETE／USER ACCEPTED
Phase 2-E               : COMPLETE／USER ACCEPTED
Mac Final Acceptance    : PASS
Lightning Acceptance    : DEFERRED TO PHASE 3／NON-BLOCKING
Backend Full Suite      : 697 PASSED／3 DESELECTED
Frontend Test           : 101 PASSED
Static／Type／Build      : RUFF／MYPY／LINT／BUILD PASS
Config／Definition      : TOML／JSON／SHELL CONTRACT PASS
Cross-provider Result   : TECHNICAL SUCCESS／GOVERNANCE VIOLATION RETAINED
Open Technical Blocker  : NONE
User Backup             : USER REPORTED COMPLETE／PRIVATE ASSET NOT READ BY AI
User Final Acceptance   : PRE-AUTHORIZED FOR SUCCESSFUL PHASE 2-F
Phase 2 Decision        : COMPLETE／ACCEPTED
Next Phase              : PHASE 3 READY／NOT STARTED／AUTOMATION OFF
Tag／Release             : NOT CREATED／NOT AUTHORIZED
```

Codex実行環境ではmacOS Metal Command Queueを生成できないため、同環境内からのNative Model起動だけは成立しなかった。これはGGUF読取り、Application Contract、Browser Buildまたはユーザー実機のAccepted Evidenceを否定するものではない。Phase 2-A～2-EのNative／Browser AcceptanceはユーザーおよびClaude側の実機Evidenceを正本とし、Codex側ではBuild済みUIの表示、Settings、Language、Theme、Sidebar、Static Contractおよび自動Testを再検証した。
