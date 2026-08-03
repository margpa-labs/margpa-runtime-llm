# Design Governance Recovery Manifest — Phase 1-ex Final

```yaml
document_type: design_governance_recovery_manifest
status: final_complete_accepted
phase_closed: phase_1_ex
next_phase_gate: phase_2_ready_to_start
created_at: 2026-08-04 06:11:04 JST
role: 設計統括者役
git_baseline_before_closure: 844394106f0330b9b8bd3652813642f34132a647
git_commit: commit_containing_this_manifest
```

## 1. Recovery Result

旧Task会話に依存せず、本Manifestと列挙正本から次を復元できるため`pass`とする。

- Phase 1／Phase 1-exの実装、Review、User Acceptance、GitおよびBackup Gate
- Current／Shared／Phase／Public／History／Losslessの正本境界
- 設計統括者役のRequirements／Architecture／Canonical Docs／Phase Design Authority
- プロジェクト責任者役との分離
- Phase 2の最初がDocument-driven Orchestration Pilot設計であること
- 絶対禁止、User Gate、Resource Limit、Stop／Recovery、Backup、Git／公開のAuthority境界

## 2. Required Reading Order

1. [Current Documentation Index](../../../current/documentation_index_ja.md)
2. [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
3. [Design Governance Handoff](../../design_governance_handoff/design_governance_handoff_ja.md)
4. 本Manifest
5. [Project Responsibility Handoff](../../project_responsibility_handoff/project_responsibility_handoff_ja.md)
6. `docs/project/shared/history/project_responsibility_handoff/`のFinal Manifest
7. [Task Role／Write Authority Policy](../../task_roles/task_role_write_authority_policy_ja.md)
8. [Phase 1-ex Index](../../../phases/phase_1_ex/phase_index_ja.md)
9. [Phase 1-ex Final Lossless Manifest](../../../phases/phase_1_ex/lossless/phase_1_ex_lossless_manifest.json)
10. [Roadmap](../../../../public/roadmap_ja.md)

## 3. Final State

```text
Phase 1                         : complete／accepted
Phase 1-ex                      : complete／accepted
Phase 1-ex Final Lossless       : 373／373 reconstructed
Full Test                       : 430 passed／3 deselected
Static／Shell／TOML／JSON       : pass
Lightning Basic／Public         : accepted
Mac／Lightning Documentation RAG: accepted
Git Working Root               : margpa-runtime-llm
Git Workflow                   : operational
Optional English Derivatives   : formally deferred／non-blocking
Tag／Release                    : none by user decision
Phase 2                        : ready_to_start／not started
```

## 4. Integrity Anchors

| Document | SHA-512 |
|---|---|
| `docs/project/current/documentation_index_ja.md` | `315b1ae6a4f20ad47b5e92e8aeeef7ce7385fea07d31a48f52692be553fca76d366cde7135b68e7089104237c7917943bb28b3e404be57d25bdebcb6182efc53` |
| `docs/project/current/project_continuity/project_continuity_master_ja.md` | `2501fc0460474db02fd271e9839cc45a5765f4ffbedaa5bf01136b9c992d32c6476f3b7a46556027f3239e275bb4f3952642018ceeb559c5be032902d80b0d9c` |
| `docs/project/phases/phase_1_ex/phase_index_ja.md` | `eabd3715072dbc4a01538644540ab5d183418bb786a4d4b0bec5858aea03a28458b250b11eb20341ed080ba3f42639f1881ea2091e5f49adfac517971888847e` |
| `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md` | `57032ef561bd85d30b282e82730facdd82421615a0aca09e1bfd07c692094fe953f6d5af945a6d247f6e3cf31bede9dce9550fa97d6f11d50bc2b8dc0c12d203` |
| `docs/project/shared/project_responsibility_handoff/project_responsibility_handoff_ja.md` | `1c9bcc38f0c5915ff8044cb05be24a5d681b18df094890b6232fbe18aa31de24a3b65edeb230409d18c9f5d1aee74932493836e55f9ad6ae0add0c9f80281af7` |
| `docs/project/phases/phase_1_ex/lossless/phase_1_ex_lossless_manifest.json` | `17c8cd037baf8d195bf0b41e8a5e15315007704464c5ba1057413b421e5ceb3706b042059aec85d84c758c731890505645914a9d5e604ea0802559fb5aae38c4` |
| `docs/project/phases/phase_1_ex/lossless/phase_1_ex_lossless_ja.md` | `cdff05989ebcb0d6d3dc713c073f7042db8b5fb964c0e0d38e64954288ecfe248ed4227660d690171d67ab7dfa3daf453adfe3ba4e07ef50ece39474cd7228a2` |

## 5. Open Item

唯一のFormal DeferralはOptional English Derivativeである。Ownerはプロジェクト責任者役、Targetは後日またはPhase 2前半、Re-entryはユーザーの余力／必要性確認時である。日本語正本と同粒度、Source Trace、Link、Terminology、Privacyを検証する。

## 6. Stop Boundary

Phase 2は開始可能であるが、本ClosureでPhase 2 Task、Pilotまたは機能実装は作成・開始しない。次の作業はユーザーの新しい開始指示を必要とする。
