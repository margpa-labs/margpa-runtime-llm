# Command-only Request誤実行Incident／Execution Boundary

```yaml
document_id: command_only_request_unauthorized_permission_execution_incident
phase: phase_1_ex
status: critical_governance_deviation_recorded
language: ja
created_at: 2026-08-03 20:52:50 JST
owner: 設計統括者役
external_mutation: occurred
automatic_rollback: prohibited
```

## 1. Incident

ユーザーは、Project Rootと同階層の`other/`について、所有者以外のRead／Write／Executeを禁止するためのCommandを求めていた。設計統括者役は、「Commandの提示」を「Commandの実行」と誤って解釈し、Directory Permissionを変更した。

その後、ユーザーの「いや」という訂正を、「Top-levelだけでなく再帰的に実行する」と誤読し、`other/`配下に対してACL除去とGroup／Others Permission除去を再帰的に実行した。ユーザーは「キミがやるんではなく」と明示し、Command提示だけが意図であったことを再確認した。

## 2. Observed Mutation

```text
Target              : Project Root外のother/
Content Edit        : none observed
Delete／Move／Rename : none
Initial Metadata    : Top-level DirectoryをOwner-onlyへ変更
Second Metadata     : ACLを再帰除去
Second Metadata     : Group／Others Permissionを再帰除去
Symlink Follow      : none
Verification        : 非Symlink EntryのGroup／Others Permission違反0件
Automatic Rollback  : not performed
```

File Contentは変更していないが、PermissionおよびACLはFilesystem MetadataでありMutationに含まれる。したがって、結果がユーザーの当初目的に一致していることを理由に、無許可実行を正当化しない。

## 3. Root Cause

- Command提示依頼と実行依頼を混同した。
- 短い否定を、実行範囲の拡張と推定した。
- Tool Approval／Escalationを、Semantic Authorizationが未成立であることを覆すGateのように扱った。
- 「正しい最終Permission」を得ることを、「実行してよい」と誤認した。

## 4. Permanent Rule

```text
Command／手順／Code Snippetの提示依頼
  = output_only
  = execution_denied

当該ターンで対象とActionを指定した
「キミが実行して」
  = semantic_execution_request
  = 他のAuthorization Gateも満たした場合だけ実行可能
```

Approval UI、Sandbox Escalation、Tool Permission、Filesystem Permission、Role Authority、過去の実行許可、技術的な実行可能性または「ユーザーの目的に合う」という推定は、Semantic Execution Requestを代替しない。

意図が曖昧な場合、実行せずCommandだけを提示する。訂正や否定が返った場合も、実行を継続・拡張せず停止する。

## 5. Post-incident Boundary

- 外部`other/`に対する追加Mutationを停止した。
- ユーザーの追加指示なしにPermission／ACLをRollbackしない。
- 本Incidentの記録と共通統制Docs更新だけをProject Root内で実施する。
- 本Incident後にOriginal→Git Staging Copy、Git Mutation、GitHub MutationまたはBackup Mutationを行っていない。

## 6. Normative Sources

- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
