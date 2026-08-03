# Project Responsibility Recovery Manifest — Phase 1-ex Final

```yaml
document_type: project_responsibility_recovery_manifest
status: final_complete_accepted
phase_closed: phase_1_ex
next_phase_gate: phase_2_ready_to_start
created_at: 2026-08-04 06:11:04 JST
role: プロジェクト責任者役
git_baseline_before_closure: 844394106f0330b9b8bd3652813642f34132a647
git_commit: commit_containing_this_manifest
```

## 1. Recovery Result

本ManifestとCanonical Docsだけから、プロジェクト責任者役と設計統括者役の両方を復元し、必要に応じてPhase設計担当者役、実装者役および対外Docs役を再構成できるため`pass`とする。

## 2. Required Reading Order

1. [Current Documentation Index](../../../current/documentation_index_ja.md)
2. [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
3. [Project Responsibility Handoff](../../project_responsibility_handoff/project_responsibility_handoff_ja.md)
4. 本Manifest
5. [Design Governance Handoff](../../design_governance_handoff/design_governance_handoff_ja.md)
6. [Final Design Governance Recovery Manifest](../design_governance_handoff/design_governance_recovery_manifest_20260804061104.md)
7. [Task Role／Write Authority Policy](../../task_roles/task_role_write_authority_policy_ja.md)
8. [Documentation Structure／Task Operations](../../operations/documentation_structure_and_task_operations_ja.md)
9. [Phase Completion Review／Backup Gate](../../operations/phase_completion_review_and_backup_gate_ja.md)
10. [Phase 1-ex Index](../../../phases/phase_1_ex/phase_index_ja.md)
11. [Phase 2 Preplan](../../operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
12. [Roadmap](../../../../public/roadmap_ja.md)

## 3. Project State

```text
Canonical Project Root       : margpa-runtime-llm
Git Branch                   : main
Pre-closure Remote Baseline  : 844394106f0330b9b8bd3652813642f34132a647
Phase 1                      : complete／accepted／backup verified
Phase 1-ex                   : complete／accepted
Phase 2                      : ready_to_start／not started
Tag／Release                 : none by user decision
Open Blocker                 : none
Accepted Deferral            : optional English derivatives only
```

## 4. Authority Reconstruction

- Userは最終Decision、Backup、Git／GitHub、External Service、Secret、課金、Destructive ActionおよびPhase移行のAuthorityを保持する。
- プロジェクト責任者役はProject全体、Phase Gate、Role編成、Cross-Phase不変条件、RecoveryとFinal Reviewを調整する。
- 設計統括者役はRequirements、Architecture、Canonical Docs、Phase DesignおよびTechnical Reviewを担う。
- プロジェクト責任者役を含む全Roleは絶対禁止、Docs運用、Authority、Mutation、Evidence、Backup、Git／公開およびUser Gateに従属する。
- 「良かれ」、推測、会話の流れ、緊急性またはRole名を許可の代替にしない。

## 5. Phase 2 First Gate

Phase 2の最初は`Phase 2-0`のDocument-driven Orchestration Pilot設計である。

```text
Pilot Requirements／Capability／Authority／Cost／Stop／Recovery
  → User-approved Authorization Envelope
  → 必要Task作成／命名／Authority設定
  → Handoff／Status／Follow-up／Review
  → single bounded work unit
  → GO／ADJUST／STOP
  → original Phase 2-A～2-F
```

本ManifestはPhase 2の開始可能性を証明するが、Task作成、Task名変更、Pilot開始または機能実装のAuthorizationを生成しない。

## 6. Integrity Anchors

| Document | SHA-512 |
|---|---|
| `docs/project/current/documentation_index_ja.md` | `315b1ae6a4f20ad47b5e92e8aeeef7ce7385fea07d31a48f52692be553fca76d366cde7135b68e7089104237c7917943bb28b3e404be57d25bdebcb6182efc53` |
| `docs/project/current/project_continuity/project_continuity_master_ja.md` | `2501fc0460474db02fd271e9839cc45a5765f4ffbedaa5bf01136b9c992d32c6476f3b7a46556027f3239e275bb4f3952642018ceeb559c5be032902d80b0d9c` |
| `docs/public/roadmap_ja.md` | `87a5277e483357e5d9ac921fdcef097cbc0e3c5797637d391f81402862b2ba8992cabf1d9e2e96b97db77ca41bf306be21f1304b70d76e5b7bce5efb6620cf92` |
| `docs/project/phases/phase_1_ex/phase_index_ja.md` | `eabd3715072dbc4a01538644540ab5d183418bb786a4d4b0bec5858aea03a28458b250b11eb20341ed080ba3f42639f1881ea2091e5f49adfac517971888847e` |
| `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md` | `57032ef561bd85d30b282e82730facdd82421615a0aca09e1bfd07c692094fe953f6d5af945a6d247f6e3cf31bede9dce9550fa97d6f11d50bc2b8dc0c12d203` |
| `docs/project/shared/project_responsibility_handoff/project_responsibility_handoff_ja.md` | `1c9bcc38f0c5915ff8044cb05be24a5d681b18df094890b6232fbe18aa31de24a3b65edeb230409d18c9f5d1aee74932493836e55f9ad6ae0add0c9f80281af7` |
| `docs/project/phases/phase_1_ex/lossless/phase_1_ex_lossless_manifest.json` | `17c8cd037baf8d195bf0b41e8a5e15315007704464c5ba1057413b421e5ceb3706b042059aec85d84c758c731890505645914a9d5e604ea0802559fb5aae38c4` |

## 7. Reconstruction Test

```text
Project state explained without old task conversation       : pass
User／Role／Git／Backup／External authority separated       : pass
Design governance role reconstructable                       : pass
Phase designer／implementer／external docs roles reconstructable: pass
Phase 2 first gate and stop boundary recoverable              : pass
Open blocker and accepted deferral recoverable                : pass
```
