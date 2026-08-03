# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260804045158
state_at: 2026-08-04 04:51:58 JST
status: current_snapshot
supersedes: documentation_index_20260804043434.md
source: user_directed_project_responsibility_phase_3_pilot_and_executable_constitution_design
phase_complete: false
```

本Snapshotは[2026-08-04 04:34:34版](documentation_index_20260804043434.md)までの全状態を継承し、Project責任者の規範従属、Phase 2成立性／Phase 3再現性・移植性Pilot、章別統合憲法、Rule ID、規範優先順位、Constitution View、Operational Evidence分類、Near Miss、Governance TestおよびResearch Preview開始条件をAppend-onlyで追加する。

## 1. Accepted Design Reservations

```text
Project Responsible Rule Exemption: none
Phase 2 Pilot Role               : feasibility validation
Phase 3 Pilot Role               : reproducibility／portability validation
Pilot Expansion                  : evidence-based／user-gated
Constitution Form                : integrated system／chapter-separated files
Rule Identity                    : stable Rule ID required
Role Delivery                    : derived Constitution View
Future Compiler                  : candidate／not implemented
Evidence                         : success＋incident＋near miss＋human intervention
Research Preview                 : v0.x start criteria reserved
Constitution Folder              : not created
Phase 2／3 Pilot                 : not started
```

## 2. Project Responsibility Boundary

Project責任者はProject全体を統括するが、絶対禁止事項、Docs規則、Authority規則、Mutation、Git／External Boundary、Backup、Evidenceおよび停止条件から免除されない。Project Responsibility、Role名、Tool Capability、長期の成功または承認待ち状態は、自己Authority拡張または規則上書きを生成しない。

承認、確認、Manual TestまたはUser Decisionを待つための安全な停止は、Rule違反ではない。

## 3. Phase 2・3 Pilot

```text
Phase 2:
  bounded work unitから開始
  orchestration成立性を検証

Phase 3:
  Phase 2 Acceptance後に別Gateで開始
  異なる要件／Task／Context／Evidence Domainで再現性・移植性を検証

Expansion:
  connected units → subphase → phase completion → project completion
  各段階でEvidenceとUser Gateが必要
```

Phase 2成功はPhase 3の自動実行Authorityを生成しない。Phase 3開始時にも対象、粒度、Authority、Cost、Stop、RecoveryおよびAcceptanceを明示する。

## 4. Constitution Architecture

憲法は一つの統合体系だが、単一巨大Markdownにはしない。

```text
Constitution Index
  ├─ Scope／Supremacy／Definitions
  ├─ Absolute Prohibitions
  ├─ Authority／Roles／Delegation
  ├─ Documentation Source of Truth
  ├─ Task Lifecycle／Handoff
  ├─ Mutation／Change Control
  ├─ Resource／Budget／Context
  ├─ Stop／Recovery／Backup
  ├─ Evidence／Audit／Review
  ├─ Agent／Tool Governance
  ├─ Exception／Emergency
  └─ Amendment／Version／Migration
```

Index、Revision、Digest、Rule ID、ManifestおよびSource Traceabilityで一つの正本体系として束ねる。Codex DesktopとClaude Codeの差はProvider Adapterへ分離する。

## 5. Rule／View／Priority

各Ruleは、Rule ID、分類、対象、規則、検知、違反時動作、復旧、EvidenceおよびSource Traceを持つ。

```text
Absolute Rule
  > Formal Exception／Emergency Approval
  > Phase Authorization Envelope
  > Role Authority
  > Phase Contract
  > Task Handoff
  > Ordinary Conversation
  > Inference／Convention／Good Intent
```

Role／Phase／Task／Provider別`Constitution View`はCanonical RevisionとDigestから生成する。ViewはAuthorityを追加できず、Stale Revision、Digest不一致またはConflict時はFail-closedとする。

## 6. Evidence Classification

```text
RULE_EFFECTIVE
RULE_AMBIGUOUS
RULE_MISSING
RULE_OVERRESTRICTIVE
RULE_UNENFORCEABLE
HUMAN_GATE_REQUIRED
AUTOMATION_CANDIDATE
```

成功だけでなく、人間が介入しなければ危険だった地点、曖昧Ruleでも偶然成功した地点および停止すべきなのに進行しかけた地点をNear Missとして保存する。

## 7. Updated Stable Documents

### Current

- [Requirements Specification](../../../current/requirements/requirements_specification_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)

### Shared

- [Cross-project Development Governance Constitution Plan](../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Experimental Document-driven Codex Task Orchestration](../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Design Governance Handoff](../../../shared/design_governance_handoff/design_governance_handoff_ja.md)

### Phase／Public

- [Phase 1-ex Index](../phase_index_ja.md)
- [Decision Record](operations/executable_governance_constitution_and_phase_2_3_pilot_evidence_design_20260804045158.md)
- [Public Roadmap](../../../../public/roadmap_ja.md)

## 8. Before／After Snapshot Set

- [Requirements Before](../../../current/history/requirements/requirements_specification_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Requirements After](../../../current/history/requirements/requirements_specification_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Constitution Plan Before](../../../shared/history/operations/cross_project_development_governance_constitution_plan_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Constitution Plan After](../../../shared/history/operations/cross_project_development_governance_constitution_plan_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Orchestration Before](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Orchestration After](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Phase 2 Preplan Before](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Phase 2 Preplan After](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Docs Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Docs Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Role Policy Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Role Policy After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Design Handoff Before](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Design Handoff After](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Roadmap Before](../../../../public/history/roadmap/roadmap_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Roadmap After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045158.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_executable_constitution_and_phase_3_pilot_reservation_ja_20260804045159.md)

## 9. Stable SHA-512

```text
Requirements:
41401ed8788930026c711adbb4afef30e782245e8492d4422c5d371597afaa0891d333525773c2d4fb9757825cca13547c1a911142c58b7d21d1dfaa613877dd

Project Continuity:
d19e525d4136086701a9aab86e7531571f0e58318a43bcf8b3928ccff8caee6694d388848b80f1557e7b7773db3bd138709e63c15c9d1252283cba3789bcd43f

Current Index:
2136ce68fffc753175195260a2d8d238de4edc0f307d1d253e7616a1ae0b1b337542a6aed7cc291358c4731dd4d42599c27b0146f16806898ea534831f5edd37

Constitution Plan:
918a5d18be19e82f6dbfe642a817c5a15a3ba04335e173357a5a0a0c9b91974955d3457b2626d96a1c2099535622add7c22f87ac1f3e350d43af72f0a1e3d233

Orchestration Pilot:
06161000194de5c72d08f17ed94cd98869e6c600fe286b7f6b850f03b78aef1cc38d746fd586fff1cdaab05f249dc4438150e9268fc26a0d939fd7680884685c

Phase 2 Preplan:
b5d2141a8a5bba196fdff8047eddc962f09612fe3cb965bce52cebb2fc3c0802f52a6a2e82be4e174c2df6361d8ae005589d4b69d7a3502edabf799a6421d89f

Docs Operations:
a4eb3a756f5c54718a5533e29a21d5356a66cdabc60dcd7eb57d56dc7052feb273c1872ca457f7a97d6e4e4991b23db1511700f3e437146ad1be7ce3d0d9bca3

Role Policy:
6cdda8a1b4243f80c903bd522c11c152162f14e00483dc3566a359eb651bc8f48df55e5e9bf4657e2afbfd7710c7017d60e6235b51dea664c17cf18152bc62c1

Design Handoff:
cb45b71a0d2125bcb4fa2d25ae8e2225d232662a0494fa87833e1ad2c6b729881456cb784f47972fef9ebf9d0788bcfb38e215042eaf41710d06db05c83b37ba

Public Roadmap:
e5bf03c99c63e7fe0cf2864f7562ef9f1ca7c5eb86328f7055c8a2e4406271a2ac23a24f319ebfbeae65060255e80090037aacc9bc6a274b413ee8910daaff3c

Phase Index:
8c9fe4c40383fc633e06052b3d29331a21936d91bea6aa628c0540cd82376c8bd19e1ef8198f102030eed0d43e7abd0f9c39601853d1104a53553b1a343ee69a

Decision Record:
313db0a519ca22cab740e8ebf3b161f80b63eff7882fe0a44f8047b69373810bbec30bec0a36aa8274c8e13f7b16a2345fee3b99711f5e3bdd2d89bb3aa43ed4
```

## 10. Mutation Boundary

```text
Authorized Project Docs     : updated／added
Runtime／Config／Tests      : unchanged
Git Commit／Push／Tag      : none
Remote／Visibility         : unchanged
Task／Sub-agent Creation   : none
Constitution Folder        : not created
Constitution Compiler      : not implemented
Phase 2／3 Pilot           : not started
Desktop Source             : not created
```

## 11. Remaining Gate

Phase 1-ex Final Lossless、Final Recovery、Phase Final Review／Test／Privacy Scan、User Acceptance、Backup、最終Git反映およびPhase 2 Start Gateは未完了である。本設計予約だけを根拠にPhase 2 Taskを作成またはPilotを開始しない。
