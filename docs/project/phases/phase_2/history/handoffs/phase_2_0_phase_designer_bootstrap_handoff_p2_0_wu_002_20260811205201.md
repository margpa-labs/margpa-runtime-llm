# Phase 2-0 Phase Designer Bootstrap Handoff — P2-0-WU-002

```yaml
document_id: phase_2_0_phase_designer_bootstrap_handoff_p2_0_wu_002_20260811205201
status: frozen_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 20:52:01 JST
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
control_state_at_freeze: PAUSED
task_created: false
```

## 1. Authority Boundary

本Handoffは`P2-0-WU-002`用のFrozen Candidateであり、User Acceptance、Task作成、Prompt送信、Automation StartまたはLocal Readを単独で許可しない。

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
Manifest SHA-512                : 743200c694953ec290c767913800bad3b759df2b86e52ec3aa35140b5f989a116d1a25570dee4111bae7aa85276595aea93b1ea456014f2079a20dbb67e96136
Ordered Path-set SHA-512        : 6951f39466881d9dc89cd6ba618d8c7c756dd6c23ed30557a737bf92624434e08e5f947409be6132dd017706d1f06607eb1388b25f32e578d28fcfd8dae2c836
Package Set SHA-512             : c31638f727117a22427135b241f4f9a301c47546394fda8fbad83aad1753d768251370a8377373ba6310d4d73a95924573653daa2fba41dd370acdc081d9a007
Source Handoff Draft SHA-512    : 75b5d14116249f70a79fe8390051598dd5d25d2507ba6bbea0a887885640be3aae01531c2782d43a91d885933636e89aef359f3ed31e2021cc8ad8503838cc12
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
  docs/project/phases/phase_2/history/handoffs/phase_2_0_phase_designer_status_p2_0_wu_002_20260811205201.md
Review／Evidence:
  docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811205201.md
Index:
  docs/project/phases/phase_2/history/index/documentation_index_after_p2_0_wu_002_20260811205201.md
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

- [Detached Freeze Receipt](../operations/phase_2_0_bounded_read_retest_freeze_receipt_20260811205201.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View draft-2](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Provider Adapter](../../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
