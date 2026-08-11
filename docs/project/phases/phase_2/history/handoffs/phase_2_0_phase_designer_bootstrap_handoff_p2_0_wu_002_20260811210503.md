# Phase 2-0 Phase Designer Bootstrap Handoff — P2-0-WU-002

```yaml
document_id: phase_2_0_phase_designer_bootstrap_handoff_p2_0_wu_002_20260811210503
status: frozen_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 21:05:03 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
task_title: Phase 2設計担当者役 P2-0-WU-002
envelope_id: p2-0-envelope-001
envelope_revision: draft-4
manifest_id: p2-0-read-manifest-001
manifest_revision: draft-2
manifest_entry_count: 18
role_view_id: p2-0-role-view-phase-designer-001
role_view_revision: draft-2
provider_adapter: codex_desktop_bounded_read_adapter
freeze_receipt_id: p2-0-freeze-receipt-004
control_state_at_freeze: PAUSED
task_created: false
supersedes_candidate: phase_2_0_phase_designer_bootstrap_handoff_p2_0_wu_002_20260811205659
```

## 1. Authority Boundary

本Handoffは`P2-0-WU-002`用のCurrent Frozen Candidateであり、User Acceptance、Task作成、Prompt送信、Automation StartまたはLocal Readを単独で許可しない。20260811205659 CandidateはUser Acceptance前の意味整合Reviewで、Frozen Stable文書内に旧状態表示が残ることを検出したため、Append-only Evidenceとして保持し、本Candidateで置換する。

開始には次を順序どおり必要とする。

1. Exact Detached Freeze Receiptと本HandoffのユーザーAcceptance。
2. 新しい独立Task 1件のユーザーAcceptance。
3. ControllerのREADY／`ARMED`宣言。
4. 後続ユーザーのStart宣言と`ON`遷移。

## 2. Objective

旧Conversationを渡さない新規Taskが、Frozen Manifest 18件だけをAccepted Provider Adapterで全文読取し、Project、Phase、Role、Authority、禁止事項、Open GateおよびFirst Safe Actionを復元できるか再試験する。

Child TaskのWrite／Git／External／Secret／Destructive／Task作成Authorityは全て`NONE`である。Recovery AssessmentはConversation Outputとして返し、Fileへ書かない。

## 3. Frozen Identity

```text
Authorized Root Identity SHA-512 : 7be2dad926cb5b7f4c03b5d544a2ef6f9efc109819ed1fc49379c30834b4b5489c17681d562a89165299af8e97baed23b694a20c49e437c634aa329a99c73b5e
Manifest SHA-512                : 81a38ca3ad20cd8592555389c0aec77f8b3c446c80da6c8e3ca4f22624046707c53b832120651e3cf51810c1fc0d8d6ffbac5269890dc4e60eefd53c4e2a1aa0
Ordered Path-set SHA-512        : 6951f39466881d9dc89cd6ba618d8c7c756dd6c23ed30557a737bf92624434e08e5f947409be6132dd017706d1f06607eb1388b25f32e578d28fcfd8dae2c836
Package Set SHA-512             : ea45d89b1d9557ba3b20a3962138859d3508addfd44a49e1ac7be53a0593a21836e40501d1cbff97e3a046994f06f681904148c1ebb2fcb2ee395fef805bf09b
Source Handoff Draft SHA-512    : 9e3b1e689b476ea177d64dbc4934d4701696409bd7ab10fda3a26fb8d6ef76488e0cb55f160922b1a116f82e33f363d2d6ac5850f579ef8e71995203867c71f2
Provider Adapter SHA-512        : ca42704fd8cddd155866f1c9a002971294585b43c72fabb9e0ec6b4cbfa76f4ec11c44b390f67a2c9137bf65d94dd03251982724dd4e1bcc2cc8ee2688be3c4d
```

Authorized Rootの平文Absolute Pathは公開可能文書へ保存しない。ControllerがTask実行時のProvider `workdir`へExact設定し、本DigestでIdentityを照合する。Childは`pwd`、探索または推測でRootを導出しない。

## 4. First-turn ACK Contract

最初のTurnではLocal Readを開始せず、次だけを返す。

```text
ACK_STATUS
Role
Task Title
Work Unit
Envelope ID／Revision
Manifest ID／Revision／Entry Count
Role View ID／Revision
Provider Adapter
Write Scope = NONE
Git／External／Secret／Destructive／Task Creation = NONE
Human Gates
Stop Conditions
Frozen Handoff SHA-512
Open Questions
```

ACK不一致時はFollow-up、Retry、別Task作成またはAuthority拡張を行わず停止する。

## 5. Recovery Contract

ACK合格後の一回だけのFollow-upで、[Bounded Read Manifest](../../governance/phase_2_0_bounded_read_manifest_draft_ja.md)の順序に従う。

各EntryについてLine Count、Observed SHA-512、1～250行単位の連続Page、Gap／OverlapおよびComplete状態を会話上で記録する。18件全てのDigest一致と全文Coverageを満たした場合だけ、Recovery内容を評価する。

Outputは[Bootstrap Handoff Draft](../../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)の`RECOVERY_ASSESSMENT`／`MUTATION_REPORT`契約に従う。

## 6. Exact Controller Artifact Scope

ControllerがTask実行後に必要性を判断して新規作成できるExact Pathは次だけである。Childは作成しない。

```text
Status:
  docs/project/phases/phase_2/history/handoffs/phase_2_0_phase_designer_status_p2_0_wu_002_20260811210503.md
Review／Evidence:
  docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md
Index:
  docs/project/phases/phase_2/history/index/documentation_index_after_p2_0_wu_002_20260811210503.md
```

StatusはPhase DesignerからControllerへの論理的報告、Review／EvidenceはControllerからUserへの判定案、Indexは当該Work UnitのNavigation／Recovery入口とする。実行結果により不要と判断したArtifactは作らないが、別Pathへ代替しない。

## 7. Stop Conditions

- Envelope、Manifest、Role View、Handoff、Adapter、Freeze Receipt、TitleまたはControl State不一致。
- Manifest Entryの不存在、Unreadable、Digest不一致またはPage Coverage不完全。
- Adapter Grammar外Command、Root／Manifest外ReadまたはMutationが必要。
- Context、Quota、Provider、Tool OutputまたはEvidenceが不安定。
- Authority、Current StateまたはSource of Truthを優先順位で解決不能。

停止時は確認済み／未確認Entry、Exact Stop Reason、Mutation Reportおよび必要なHuman Gateだけを返す。Cleanup、Rollback、Retry、Scope拡張または推測補完を行わない。

## 8. Related Documents

- [Detached Freeze Receipt](../operations/phase_2_0_bounded_read_retest_freeze_receipt_20260811210503.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View draft-2](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Provider Adapter](../../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
