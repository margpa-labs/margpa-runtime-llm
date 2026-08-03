# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260803210658
state_at: 2026-08-03 21:06:58 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - operations/explicit_confirmation_and_workspace_boundary_absolute_rules_20260803210658.md
  - ../../../shared/operations/research_asset_mutation_control_ja.md
  - ../../../shared/operations/documentation_structure_and_task_operations_ja.md
  - ../../../shared/task_roles/task_role_write_authority_policy_ja.md
supersedes: documentation_index_20260803205250.md
source: user_directed_absolute_confirmation_workspace_boundary_and_automation_separation_rules
```

本Snapshotは[2026-08-03 20:52:50版](documentation_index_20260803205250.md)までの全状態を継承し、善意・推測・会話ContextによるAuthority生成禁止、1%不明時の必須確認、`MARGPA-RUNTIME-LLM/`外周境界、`other/`接触禁止およびPhase 2以降のOrchestration実験との完全分離をAppend-onlyで記録する。

## 1. Accepted Permanent Rules

- 「良かれ」「推測」「話の流れ」「過去の許可」「効率」「安全化」「Roleの責務」を、明示されていない許可へ変換しない。
- 意図、対象、Action、Root、Mutation有無、外部Access、委譲範囲または副作用に1%でも不明点があれば、必ずユーザーへ確認し、回答まで停止する。
- 本Project作業の外周境界は`MARGPA-RUNTIME-LLM/`とし、その外部へ当該ターンの明示許可なく触れない。
- 外周境界内も、当該ターンで許可された正確なRoot／Pathだけを対象とする。
- `other/`はユーザー専用領域として通常Authorityから除外し、明示的な一時解除がない限りReadを含む全Accessを拒否する。
- 未許可DirectoryへCopy Folder、Temporary Artifact、Stage、Cache、Backupまたは生成物を作成しない。
- Phase 2以降の半自動／ほぼ自動Orchestration実験は事前承認済みEnvelope内だけの別運用であり、本原則の例外、包括的権限委任または現在作業へのStanding Authorizationではない。
- 違反または違反疑いでは即時停止し、ユーザーの明示指示なしに修復、Rollbackまたは追加Evidence収集を行わない。

## 2. Evidence／Normative Sources

- [Explicit Confirmation／Workspace Boundary Absolute Rules](operations/explicit_confirmation_and_workspace_boundary_absolute_rules_20260803210658.md)
- [Research Asset Mutation Control](../../../shared/operations/research_asset_mutation_control_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)

## 3. Before／After Snapshot

- [Research Asset Mutation Control Before](../../../shared/history/operations/research_asset_mutation_control_phase_1_ex_before_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Research Asset Mutation Control After](../../../shared/history/operations/research_asset_mutation_control_phase_1_ex_after_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Documentation Structure／Task Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Documentation Structure／Task Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Task Role／Write Authority Policy Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Task Role／Write Authority Policy After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_explicit_confirmation_and_workspace_boundary_ja_20260803210658.md)

## 4. SHA-512

```text
Previous Documentation Index:
d866a5e1c934d65b1f3bcf6a02e8734eb033bf3563631e0947bde45003cd790b3e1dd37525596cc9ea8531a4ead04bebfdab2e19702759198cb018f87f7ed086

Research Asset Mutation Control Before:
8937cc7b81c6e406a0ee54f1aae8a168d6885523b68427a912aed3d4423c8243ca3197a685b9d738fa17047c50ed43b5b733b0f44e6c86a7696dd45ebda1dc11

Research Asset Mutation Control After／Stable:
570c00bb7836713da5b10ce985133225fac9f524ec2db3302a18526deb0fa6cad00adbc4d22d9b612f2dcf8193b814b9222983614d5d7628ac98bb9cd0a9fd8b

Documentation Structure／Task Operations Before:
ed63018757a9834afd7f4777787113a938a8b2dea5f89ee026903745d39387226d313d7a4bdbd64e19da8c1bf161a11aefedbcb53ca215b44269db4d0421af93

Documentation Structure／Task Operations After／Stable:
4b2007fab4a655a2644454df72f9ecf9caa20131b576157948bd5cac95ce978278d4610eda6b0546af0339cba311a9fb8fee45c972bbe962aa130d9a6f4267a2

Task Role／Write Authority Policy Before:
c4845e20ed59b276c851efac67555863cf8a46b5d831793f65dc03a60ba943f9506a37bbfffaa5f5170de436159fd83f1159ee0be75db7a154e224f6850245f0

Task Role／Write Authority Policy After／Stable:
6629590fd70e73e0d1a61195ceac9b15842fc6784c485cdcfca3644bad73f666abdc9a3b97ae8c1994c3b261ac39c0a24753ed45edf62770a7b299d1177247e3

Absolute Rule Record:
43001d5b336188d3f02468271da38b58242976480bc5aef3c95389c6326ed79606b24f2ada27212650737f2517d380edbfc749e844aa3b8521e0641e6968a8dd

Phase Index Before:
ea1b6aeb61a608662cc15e8a66b23b3c4e69963e2f63f2fb5e99c55ffd2341e5905825e2888411286224f8de964ecf884b0278bcc36fa678389a5c0d1de63538

Phase Index After／Stable:
4a78c3f3f5f6e8b58ab00d4e7ac0f2e68725ac4fd91554eabb1ea0f2f5ab5178af854ef7501fc0951d67bec9fd9f459ae42c0f351a508a3ac15611ea8435d06c
```

## 5. Mutation Boundary

```text
Original Project:
  Docs規則／Role規則／Phase Index／History／Documentation Indexだけを追加・更新

MARGPA-RUNTIME-LLM外       : not accessed
other/                     : not accessed
Sibling Directory          : not accessed
Project Source／Config／Tests: unchanged
Git Staging Clone          : unchanged
Backup ZIP                 : unchanged
Git Operation              : none
GitHub Operation           : none
Delete                     : none
Task／Sub-agent Creation    : none
```

## 6. Post-inventory Delta

本Timestampの規則、Absolute Rule Record、Before／After Snapshotおよび本Documentation Indexは、Git Read-only Delta Inventory後に追加された正当なDocs-only Deltaである。実Copy前の最終Delta RefreshでSource→Target Integration Manifestへ追加する。

## 7. Next Gate

以後、対象、Action、Rootまたは意図に1%でも不明点がある場合は、推測せずユーザーへ確認する。Phase 2以降の自動化実験を含め、事前承認済みEnvelope外へ進まない。

Git統合では、本Docs-only Delta、Source→Target Integration Manifest、Copy Dry-runおよびユーザー承認が揃うまで、実Copy、Delete、`git add`、Commit、Tag、Push、MergeまたはHistory Rewriteへ進まない。
