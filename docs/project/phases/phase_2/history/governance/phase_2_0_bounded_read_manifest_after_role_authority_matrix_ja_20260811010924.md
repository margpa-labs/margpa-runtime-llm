# Phase 2-0 Bounded Read Manifest Draft

```yaml
document_id: phase_2_0_bounded_read_manifest_draft
manifest_id: p2-0-read-manifest-001
revision: draft-2
status: draft_not_frozen
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
language: ja
created_at: 2026-08-11 00:19:18 JST
updated_at: 2026-08-11 01:09:24 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
authorized_root: runtime_resolved_project_manifest
entry_count: 18
```

## 1. Purpose

本Manifestは、`P2-0-WU-002`でCold Recovery対象とするLocal Documentationを、曖昧なDirectory探索ではなくExact Path Setとして固定するDraftである。

本書の存在は、File読取、Shell実行、Task作成、Git操作またはPilot再開を許可しない。Accepted Envelope、Frozen Digest、Provider Adapter Preflight、READY／ARMEDおよびUser Start Eventを別途必要とする。

## 2. Boundary

```text
Allowed Read Target = Authorized Root + Exact Relative Path Entry
Directory Read       = prohibited
Discovery            = prohibited
Implicit Expansion   = prohibited
Symlink Traversal    = prohibited
Mutation             = prohibited
```

Manifest Entryに含まれないPathを必要と判断した場合、Taskは追加探索せず、Missing Informationとして停止する。存在しないEntry、Unreadable Entry、Digest不一致またはManifest Revision不一致もFail-closed対象とする。

## 3. Exact Reading Order

| Order | Relative Path | Purpose |
|---:|---|---|
| 1 | `docs/project/current/documentation_index_ja.md` | Current Stable入口 |
| 2 | `docs/project/current/project_continuity/project_continuity_master_ja.md` | Project Continuity |
| 3 | `docs/project/shared/project_responsibility_handoff/project_responsibility_handoff_ja.md` | Project Responsibility |
| 4 | `docs/project/shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md` | Project Responsibility Recovery |
| 5 | `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md` | Design Governance |
| 6 | `docs/project/shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804061104.md` | Design Governance Recovery |
| 7 | `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md` | Role／Write Authority |
| 8 | `docs/project/shared/task_roles/role_authority_matrix_ja.md` | Effective Role Authority |
| 9 | `docs/project/shared/operations/research_asset_mutation_control_ja.md` | Mutation Control |
| 10 | `docs/project/shared/operations/experimental_document_driven_codex_task_orchestration_ja.md` | Orchestration Operating Context |
| 11 | `docs/project/shared/automation/automation_governance_index_ja.md` | Automation Stable入口 |
| 12 | `docs/project/shared/automation/automation_control_profile_ja.md` | Automation Level／State |
| 13 | `docs/project/phases/phase_2/phase_index_ja.md` | Active Phase State |
| 14 | `docs/project/phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md` | Pilot Requirements |
| 15 | `docs/project/phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md` | Pilot Architecture |
| 16 | `docs/project/phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md` | Exact Envelope Revision |
| 17 | `docs/project/phases/phase_2/governance/phase_2_0_phase_designer_role_view_draft_ja.md` | Exact Role View |
| 18 | `docs/project/phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md` | Execution／Review Gate |

## 4. Freeze Contract

Design Package確定後、ControllerはAuthorized Root内でRead-onlyに次を検証し、Detached Freeze Receiptへ記録する。

```text
Manifest ID／Revision
Exact Entry Count
Each Relative Path
Each File SHA-512
Ordered Path-set SHA-512
Manifest File SHA-512
Envelope Revision
Handoff Revision／SHA-512
Role Authority Matrix／Role View Revision／SHA-512
Freeze Timestamp
```

本Manifest内へ自己Digestまたは相互参照文書の循環Digestを埋め込まない。Digest FreezeはAppend-only Operations Evidenceへ保存し、Acceptance時にそのReceiptをExact指定する。

## 5. Prohibited Interpretation

- `docs/`全体のRead許可ではない。
- Parent DirectoryのList、Search、GlobまたはRecursive Traversal許可ではない。
- Path名が似ている別Fileへの代替許可ではない。
- Missing EntryをHistory、Git、Networkまたは別Taskから補う許可ではない。
- ManifestをTask自身が編集、再生成または拡張する許可ではない。

## 6. Current State

```text
Manifest              : draft-2／not frozen
Envelope              : draft-4／not accepted
Provider Adapter      : design candidate／not activated
Detached Freeze Receipt: previous receipts invalidated by role authority redesign
Task                  : not created for P2-0-WU-002
Control State         : PAUSED／ROLE_AUTHORITY_DESIGN
```

## 7. Related Documents

- [Authorization Envelope Draft](phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View](phase_2_0_phase_designer_role_view_draft_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
