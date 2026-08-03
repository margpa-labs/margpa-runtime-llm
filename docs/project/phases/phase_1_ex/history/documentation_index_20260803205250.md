# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260803205250
state_at: 2026-08-03 20:52:50 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - operations/command_only_request_unauthorized_permission_execution_incident_20260803205250.md
  - ../../../shared/operations/research_asset_mutation_control_ja.md
  - ../../../shared/operations/documentation_structure_and_task_operations_ja.md
  - ../../../shared/task_roles/task_role_write_authority_policy_ja.md
supersedes: documentation_index_20260803201448.md
source: user_directed_absolute_prohibition_for_executing_command_only_requests
```

本Snapshotは[2026-08-03 20:14:48版](documentation_index_20260803201448.md)までの全状態を継承し、Command／手順／Code Snippetの提示依頼と実行許可を完全分離する絶対禁止事項、および外部`other/`に対する誤実行IncidentをAppend-onlyで記録する。

## 1. Accepted State

- 「コマンドをくれ」「ここに出して」「手順を教えて」「僕がやる」「キミがやるんではなく」等は`output_only`であり、Command、Tool、Filesystem MutationまたはExternal Actionの実行を絶対禁止する。
- 実行は、当該ターンでユーザーが対象とActionを特定し、「キミが実行して」等と明示した場合だけ可能とする。
- 「いや」等の短い否定、訂正、目的、過去の依頼、作業の流れまたは善意を、新しい実行許可へ変換しない。
- Approval UI、Sandbox Escalation、Tool Permission、Filesystem PermissionおよびRole AuthorityはSemantic Authorizationではない。
- 意図が曖昧な場合は、Commandまたは手順をTextで提示して停止する。
- 違反または違反疑いはCritical Governance Deviationとして即時停止し、ユーザーの明示指示なしにRollback、修復または追加Mutationを行わない。
- 本規則は設計統括者役を含む全Role、全Task、全Agentおよび全Toolへ適用する。

## 2. Incident Evidence

- [Command-only Request誤実行Incident／Execution Boundary](operations/command_only_request_unauthorized_permission_execution_incident_20260803205250.md)
- [Research Asset Mutation Control](../../../shared/operations/research_asset_mutation_control_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)

ユーザーはProject Root外の`other/`に適用するCommandの提示を求めていた。設計統括者役はこれを実行依頼と誤認し、Top-level Permissionを変更した後、短い訂正を再帰実行要求と誤認してACL除去およびGroup／Others Permission除去を実行した。

本Incident後、外部対象への追加Mutationおよび無許可Rollbackは停止した。内容Fileの編集・削除は観測されていないが、Permission Metadataを無許可で変更した事実をCritical Governance Deviationとして保持する。

## 3. Before／After Snapshot

- [Research Asset Mutation Control Before](../../../shared/history/operations/research_asset_mutation_control_phase_1_ex_before_command_only_execution_prohibition_ja_20260803205250.md)
- [Research Asset Mutation Control After](../../../shared/history/operations/research_asset_mutation_control_phase_1_ex_after_command_only_execution_prohibition_ja_20260803205250.md)
- [Documentation Structure／Task Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_command_only_execution_prohibition_ja_20260803205250.md)
- [Documentation Structure／Task Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_command_only_execution_prohibition_ja_20260803205250.md)
- [Task Role／Write Authority Policy Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_command_only_execution_prohibition_ja_20260803205250.md)
- [Task Role／Write Authority Policy After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_command_only_execution_prohibition_ja_20260803205250.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_command_only_execution_prohibition_ja_20260803205250.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_command_only_execution_prohibition_ja_20260803205250.md)

## 4. SHA-512

```text
Previous Documentation Index:
43e133a44f6cc60cd33dd149fe8281f99da0e4628caca12cdbf1788c63169a58a77abe313a120e4dfd9d6f1e1491e617babab598566b20f8b294ef18b9cc5154

Research Asset Mutation Control Before:
eafebff8f2aa6c62e1626792d7bc6dfc5cb71e3295adce3098565717aa47a377271ff7fc067587b6ca2ee1c8d418fd5a56793cda1500be3713a16a1920eb1dd4

Research Asset Mutation Control After／Stable:
8937cc7b81c6e406a0ee54f1aae8a168d6885523b68427a912aed3d4423c8243ca3197a685b9d738fa17047c50ed43b5b733b0f44e6c86a7696dd45ebda1dc11

Documentation Structure／Task Operations Before:
5cfb452dfd71e737800ecfa00056b1fa5a0327bb4b7da537d8f452071254b64205d2978868b023db7bd3f5fcac9e029edf345295c1f0e8a3ffc349c61ae8db95

Documentation Structure／Task Operations After／Stable:
ed63018757a9834afd7f4777787113a938a8b2dea5f89ee026903745d39387226d313d7a4bdbd64e19da8c1bf161a11aefedbcb53ca215b44269db4d0421af93

Task Role／Write Authority Policy Before:
697e05b5c4b827e10c535b0cccbe40d9f33b6c0518f354e95dff841458cae0d8e4582f358a74bfa09cb8ede231e8cfcb123f6065f2b010465f391e07bc260c0d

Task Role／Write Authority Policy After／Stable:
c4845e20ed59b276c851efac67555863cf8a46b5d831793f65dc03a60ba943f9506a37bbfffaa5f5170de436159fd83f1159ee0be75db7a154e224f6850245f0

Incident Record:
c77cf2f57c6e01262af0209502b27eb88580663d704ab93695d5fe38e256ce09c5ada24a824023862c95147b045ecbcfe631b84deaac66ffd0c338fa5d1dba83

Phase Index Before:
9419f6815fa32966d98906987f731ee508032a6850d580e10db9e7b397234f11f4a55fa08513645e0c7acaad962cdc8ad89ddd0fb88c531346412b37dc959329

Phase Index After／Stable:
ea1b6aeb61a608662cc15e8a66b23b3c4e69963e2f63f2fb5e99c55ffd2341e5905825e2888411286224f8de964ecf884b0278bcc36fa678389a5c0d1de63538
```

## 5. Mutation Boundary

```text
Original Project:
  Docs運用規則／権限規則／Incident Evidence／Phase Index／History／Documentation Indexだけを追加・更新

Project外のother/             : 本Docs Operationでは追加変更なし
Project Source／Config／Tests : unchanged
Git Staging Clone             : unchanged
Backup ZIP                    : unchanged
Git Operation                 : none
GitHub Operation              : none
Delete                        : none
Independent Task Creation     : none
Sub-agent Dispatch            : none
```

## 6. Post-inventory Delta

本Timestampの規則、Incident Record、Before／After Snapshotおよび本Documentation Indexは、先行するGit Read-only Delta Inventory後に追加された正当なDocs-only Deltaである。

実Copy前の最終Delta Refreshで、本Timestampの新規／更新DocsをSource→Target Integration Manifestへ追加する。

## 7. Next Gate

今後、Commandまたは手順の提示を求められた場合はText出力だけを行う。実行へ進むには、当該ターンで対象とActionを特定した明示的な実行依頼を必須とする。

Git統合については、Source→Target Integration Manifest、Copy Dry-run、Post-inventory Docs-only Deltaおよびユーザー承認が揃うまで、実Copy、Delete、`git add`、Commit、Tag、Push、MergeまたはHistory Rewriteへ進まない。
