# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260802221749
state_at: 2026-08-02 22:17:49 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../current/project_continuity/project_continuity_master_ja.md
  - ../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md
  - ../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md
  - ../../../shared/operations/task_execution_routing_and_cost_control_ja.md
  - ../../../shared/task_roles/task_role_write_authority_policy_ja.md
  - ../../../../public/roadmap_ja.md
supersedes: documentation_index_20260802220659.md
source: user_requested_phase_2_subphases_near_automatic_role_orchestration_resource_and_authority_risk_controls
```

本Snapshotは[2026-08-02 22:06:59版](documentation_index_20260802220659.md)までの全状態を継承し、Phase 2の2-A～2-F分割、Phase専用設計／実装Task、準自動的なRole間Handoff、Resource Limit中断および全RoleのAuthority逸脱可能性をAppend-onlyで記録する。

## 1. Phase 2 Subphase Plan

```text
Phase 2-A : Phase Contract／Conversation Domain Foundation
Phase 2-B : Conversation Persistence／Lifecycle Services
Phase 2-C : Conversation Application UX
Phase 2-D : Configuration Control Surface／Research Developer Mode
Phase 2-E : Runtime Composition Switchboard／Documentation RAG Follow-up
Phase 2-F : Cross-environment Acceptance／Phase Closure
```

2-Aから2-Fまでを原則の依存順とする。Phase 3～Phase 9へ同じ分解法を適用するかはPhase 2-FでPilot成果を評価して都度決定する。Phase 10以降は特殊性が高いため、現時点の横展開対象から除外する。

## 2. Task Orchestration

```text
設計統括者役      : Project／Cross-Phase／Authority／Final Review
Phase 2設計担当者役 : Phase 2専用の独立Task
Phase 2実装者役     : Phase 2専用の独立Taskを基本案
```

各Subphaseは、設計統括者役のScope固定、Phase設計担当者役の局所設計、設計統括者役のAccepted Handoff、実装者役の実装／Status、Phase設計担当者役の局所Review、設計統括者役のFinal Subphase Reviewの順で進める。

Phase 2開始時にユーザーが`Phase Orchestration Authorization Envelope`を明示承認した場合、事前列挙されたTask、Routine Handoff、Status、ReviewおよびFollow-upをその範囲内で連結できる。Envelope外のTask、権限拡張、External／Git／Secret／Destructive ActionまたはUser Gate省略は追加承認を必要とする。

## 3. Implementer Task Renewal

Phase 2実装者Taskは、Current State、Accepted Handoff、Write Scope、Open Finding、TestおよびMutation Inventoryを安全に解決できる間はPhase内で継続利用できる。

次では更新を検討する。

- Context Limit／Task不安定化／Service Limit
- Accepted ScopeまたはArchitectureの大きな切替
- Authority逸脱または無許可Mutationの疑い
- Status／Evidence不足によるRecovery不能
- 同一原因のFollow-up失敗／Handoff誤読の繰返
- Phase変更時のContext分離便益

更新前に旧TaskのWriteを止め、最終Status、Files Changed、Test、Open Finding、Git／External StateおよびRecovery Pathを固定する。

## 4. Resource／Authority Risk

Codex利用可能量、Credit、QuotaまたはService Limitで作業が途中停止しうる。未完了状態をCompleteと表記せず、`PAUSED_RESOURCE_LIMIT`相当で最後の確認済み状態、Open Finding、次の最小ActionおよびRecovery Pathを固定する。別Model／Account／Service、追加課金または代替Task群へ自動切替しない。

設計統括者役を含む全Role／Task／Agent／Toolが権限外または運用ルール外Actionを取りうることを前提とする。Role名、上位責任、成功実績またはTool PermissionはComplianceの保証ではない。Mutation前Scope解決、変更後Inventory、Cross-role Review、Stop GateおよびRecovery Evidenceを必須とする。逸脱または疑い検出後は、自動修復／無許可Rollback／証跡削除を行わず停止する。

## 5. Stable Updates

- [Phase 2 Subphase／Task Orchestration Preplan](../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Experimental Document-driven Codex Task Orchestration](../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Task Execution Routing／Cost Control](../../../shared/operations/task_execution_routing_and_cost_control_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)
- [Public Roadmap](../../../../public/roadmap_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)

## 6. Stable History

### Before

- [Roadmap Before](../../../../public/history/roadmap/roadmap_phase_1_ex_before_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Project Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Experiment Before](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_before_phase_2_subphase_preplan_ja_20260802221749.md)
- [Task Routing Before](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_before_phase_2_subphase_preplan_ja_20260802221749.md)
- [Role Authority Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_phase_2_orchestration_risk_controls_ja_20260802221749.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)

### After

- [Roadmap After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Project Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)
- [Experiment After](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_after_phase_2_subphase_preplan_ja_20260802221749.md)
- [Task Routing After](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_after_phase_2_subphase_preplan_ja_20260802221749.md)
- [Phase 2 Preplan Initial Snapshot](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_ja_20260802221749.md)
- [Phase 2 Preplan Link-corrected Stable Snapshot](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_link_corrected_ja_20260802221749.md)
- [Role Authority After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_phase_2_orchestration_risk_controls_ja_20260802221749.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_phase_2_subphase_orchestration_preplan_ja_20260802221749.md)

## 7. SHA-512

```text
Previous Documentation Index:
  402bc129193fa5a3ed8c32a4e3b333ea5bc84f3dd80cc7c09bffb1ca402e0b0b551a66a64d9559f3e28ee05b9cac797ac30f9b8b5ac95bddedc4da07991918b4

Public Roadmap Before:
  b9d72a6c9c55953d6792f262ecf1fa8cd74ac80aa5f24fe80463d5a8bdeb4017e34c21c4ddb25829aa9debf4e38d6fd09c9ecf081ec78d743c452a0980c2163f
Public Roadmap After:
  53d2b32f90fe91b5dc835de7ac259a89c247d85a080d38e27ccfe546f7b9298b2a256ddaf206708031b8c6541b721bb842ec2ffbbfae62749383fa736a5bba82

Project Continuity Before:
  08f1d348e8554308e3be3324ab755cf547d130a67688d96412ed3df12be4c91fd754e91442020f35b2979bbb3a2eae1ab4f1be138df9917b136f5c8e4c8ad221
Project Continuity After:
  fdd9a0f2033fa9364bb9c0b3fc29ef25aa9530dd145f2b3868ec6cee48baa2cc87783753c399290e850f1a224eff55f68eb232d31854af4bff3977c051690f7a

Current Documentation Index Before:
  a7fe2875d2fbfc9f48c32c22bceae69f3214bd5a69d19ac78b71914b958991f8e53f53cb809cacb82e747d74423229256a4d4386a31063be5e270faab7b3d958
Current Documentation Index After:
  e893108dad4e89c1bf39fa6181589c57c12375ca724478c0bf3708e665f7a4a255fb23a482966f0dbceca8ba62d2b4bf41b7085b7e5f725f4c99eea1f6bfc8eb

Experiment Before:
  60e44584a0b555d16cf9efd16b7f4097bba6610625ee171c1ccb05acd676230868a266b7a00f53e74adcfa635bf1863e8d6cf61da60713c41a07c0e8e278494f
Experiment After:
  c1397b3b4f539d799a5ca6720a14ae3f1bd0c6dbcd4abf6e767974594d2808369fbfb1fdb687943566e4b1e0057738c749aae9b70fa89c0a9a8332aaa2f52d1d

Task Routing Before:
  01e7c23d17d8d8bfd35f5a3d1834835c6cf24d1ff3c24af4d87d563fd76a004d340f8254641723e7cec476fb9a34e6d6ac6c97acdf9bdf1621ae213238d2e4a2
Task Routing After:
  679c23fcf24d1897d102f614181724f1b041b7e3360c2c5a22e87a0cec52ae00b7f362cee17bc96d85a6adb7df13d2eac77a6fe52f21daf44766a89ba154f8f6

Phase 2 Preplan Initial Snapshot:
  71af90a2395b322a3677a73fcb63afa4ee46028ecc3caab20d7be169242af81f920621bb95ac4859207c1569893c3464faa6226b5589a031264f7661137fafca
Phase 2 Preplan Link-corrected Stable:
  43fc5eb4172b31e1da46921ba492046de5a16a5711d915a5142f93fa6421beae93134c299efc3ad6b5b02a74a7b853eab90aa8932fe9fa5b329b217526e96955

Role Authority Before:
  9cda793d74c7ef194afe74e5e92603130a0a329581173bf15cee5e1e3e52e43f609402cb831333811065aa643edb6be827d7d2d2147c896c0648962ae4bd22f3
Role Authority After:
  47b261a5fe410c7e84bc3f30642de43ac1b8da466a4a7f795475f81e6f362fcf949b3692265a2860bf4d4dcc6c2f240c9f446fb518c212e9b4d36fd694af39a5

Phase 1-ex Index Before:
  b04e4018d3efa1e89700d74a7624dab08a3832e059f1f3183f48d16dd25e6b2737a5607bd2948e02eaa6fce770aaece8734fd37b2d6949f0aba5ab6678406ed2
Phase 1-ex Index After:
  80b2a810af7fae3a0c20520345ad26873d9f9a0bd5fdc6b4e9a3637f1081191b4a6a0efa2ebe7528090d3abd3d8c6d0143b66b90a8b9df934b911bee088d8571
```

## 8. Mutation Boundary

```text
Project Source／Config／Tests : unchanged
Root Public Artifacts         : unchanged
Git Operation                 : none
GitHub Operation              : none
External Filesystem Operation : none
Independent Task Creation     : none
Sub-agent Dispatch            : none
```

## 9. Next Gate

Phase 1-exの残作業、Final Review、User AcceptanceおよびBackupを先に完了する。Phase 2開始時には本Preplanをそのまま実行せず、Current State、User Requirement、Git／Worktree、利用可能量および利用可能なTask Toolを再確認し、Phase 2設計担当者役の開始HandoffとOrchestration Authorization EnvelopeをAccepted化する。
