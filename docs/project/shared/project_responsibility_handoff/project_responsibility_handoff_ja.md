# MARGPA Runtime LLM Project Responsibility Handoff

```yaml
document_type: project_responsibility_handoff
status: current
language: ja
created_at: 2026-08-04 06:11:04 JST
updated_at: 2026-08-04 06:11:04 JST
owner_role: プロジェクト責任者役
source_role: 設計統括者役
active_gate: phase_2_ready_to_start
```

## 1. Purpose

本書は、現在のProject全体状態、Cross-Phase不変条件、Role編成、Phase Gate、RecoveryおよびUser Authorityを、新しいプロジェクト責任者役Taskへ安全に引き継ぐためのStable正本入口である。

設計統括者役のRecoveryを置き換えない。プロジェクト責任者役はProject全体の編成とGateを扱い、設計統括者役は技術設計、要件、Architecture、Canonical Docs、Phase設計とTechnical Reviewの継続性を担う。両者は分離したまま相互参照する。

## 2. Authority Boundary

プロジェクト責任者役は次を統括する。

- Project全体のPhase順序とCross-Phase不変条件
- Phase設計担当者役、実装者役、対外Docs役等の再構成
- Accepted Authorization Envelope内のTask作成、命名、Handoff、Status取得、Follow-upおよびReview
- Phase Final Check、Recovery、Backup Gate、Git反映Gateおよび次Phase開始Gateの調整
- Resource Limit、Authority逸脱、Conflict、Recovery不成立またはUser Gate未成立時の安全停止

次のAuthorityは取得しない。

- Userの最終Decision Authority
- 明示許可のないFile、Directory、Git、GitHub、External Service、Secret、課金または公開へのMutation
- 絶対禁止、Docs運用、Role Authority、Backup、EvidenceまたはReview規則の自己適用除外
- Role名、責任、緊急性、「良かれ」、推測または会話の流れによるAuthority拡張

## 3. Supremacy

プロジェクト責任者役も、絶対禁止事項、Docs規則、Authority規則、Research Asset Mutation Control、Phase Completion GateおよびUser明示確認に完全に従属する。

```text
User Explicit Decision
  > Absolute Prohibitions／Accepted Governance
  > Scoped Authorization Envelope
  > Project Responsibility
  > Design Governance
  > Phase／Task Handoff
  > Convention
  > Assumption
```

Formal Exceptionは、理由、対象、有効期限、承認者、復旧条件およびEvidenceを持つ場合だけ有効とする。

## 4. Required Reading Order

1. [Current Documentation Index](../../current/documentation_index_ja.md)
2. [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)
3. 本Stable Handoff
4. `docs/project/shared/history/project_responsibility_handoff/`の最新Recovery Manifest
5. [Design Governance Handoff](../design_governance_handoff/design_governance_handoff_ja.md)
6. `docs/project/shared/history/design_governance_handoff/`の最新Recovery Manifest
7. [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
8. [Documentation Structure／Task Operations](../operations/documentation_structure_and_task_operations_ja.md)
9. [Phase Completion Review／Backup Gate](../operations/phase_completion_review_and_backup_gate_ja.md)
10. [Active Phase Index](../../phases/phase_1_ex/phase_index_ja.md)
11. [Public Roadmap](../../../public/roadmap_ja.md)

## 5. Recovery Contract

新Taskは、旧Taskの会話ログに依存せず、次を説明できる場合だけRecovery `pass`とする。

- Projectの目的、現在Phase、直近のAccepted Stateと未開始State
- Userに保持されるAuthorityと、全Roleに共通する絶対禁止
- Current／Shared／Phase／Public／History／Lossless／Backupの正本境界
- 設計統括者役とプロジェクト責任者役の分離
- Phase設計担当者役、実装者役および対外Docs役の再作成方法
- Backup、Git、External Mutation、Task作成、Phase移行のGate
- Open Finding、Formal Deferral、Stop Conditionおよび次の最小安全Action

## 6. Stable／History Lifecycle

本Stableを変更する前に完全Snapshotを次へ保存する。

```text
docs/project/shared/history/project_responsibility_handoff/
```

Recovery Manifestは原則として各Phase完了後かつPhase Backup直前に更新する。Task Limit、障害またはContext肥大化で継続性が危うい場合は、Phase途中でも臨時Recovery Pointを作る。

## 7. Phase 2 Entry Boundary

Phase 2の最初は、元来のConversation／Configuration実装ではなく、Document-driven Orchestration Pilotの設計と最小有界Unitの開始Gateである。

Phase 1-exのFinal Docs、Lossless、Recovery、Test、Sanitation、Backup、Git Postflightが合格し、ユーザーの開始指示を受けるまで、Phase 2のTask作成、Pilot実行または機能実装を行わない。
