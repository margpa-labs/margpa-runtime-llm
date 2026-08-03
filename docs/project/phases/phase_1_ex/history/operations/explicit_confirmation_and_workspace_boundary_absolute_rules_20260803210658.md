# Explicit Confirmation／Workspace Boundary Absolute Rules

```yaml
document_id: explicit_confirmation_and_workspace_boundary_absolute_rules
phase: phase_1_ex
status: accepted_permanent_rule
language: ja
created_at: 2026-08-03 21:06:58 JST
owner: 設計統括者役
applies_to: all_roles_all_tasks_all_agents_all_tools
failure_policy: ask_then_fail_closed
```

## 1. User Directive

ユーザーは、Command-only Request誤実行Incidentを受け、次の原則を全Role共通の絶対禁止事項として追加した。

1. 「良かれ」「推測」「話の流れ」で、明示されていない許可を勝手に成立させない。
2. 意図、対象、Action、Root、Mutation有無、外部Accessまたは副作用に1%でも不明点がある場合、必ずユーザーへ確認する。
3. 本Project作業では`MARGPA-RUNTIME-LLM/`を外周境界とし、当該ターンの明示許可なしに外部へ触れない。
4. 外周境界内も、許可された正確なRoot／Pathだけを対象とし、同じ親Directoryに存在することを許可とみなさない。
5. `other/`はユーザー専用領域として通常Authorityから除外し、根本的に触れない。
6. 未許可DirectoryへCopy Folder、Temporary Artifact、Stage、Cache、Backupまたは生成物を作らない。
7. Phase 2以降の半自動／ほぼ自動Orchestration実験は完全な別件として切り分け、本原則の例外や包括許可として扱わない。

## 2. Absolute Interpretation Rule

```text
良かれと思うこと          ≠ 許可
ユーザーの利益になる推測   ≠ 許可
話の流れ                  ≠ 許可
過去の許可                ≠ 今回の許可
将来必要になる見込み       ≠ 許可
Roleの責務                ≠ 個別Actionの許可
自動化実験の計画           ≠ 現在作業の許可
同じ親Directory内          ≠ Access許可
```

不明点を担当が合理的に補完して進めることは禁止する。1%でも不明なら、Textで確認し、回答が得られるまでTool Call、Command、Filesystem Access、外部操作、Task委譲または自動処理を開始・継続しない。

## 3. Filesystem Boundary

```text
Outer Boundary:
  MARGPA-RUNTIME-LLM/

Default Allowed Scope:
  当該ターンでユーザーが許可した正確なRoot／Pathだけ

Explicitly Excluded User-only Scope:
  other/

Outside／Unlisted Scope:
  deny
```

外周境界外では、Read、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL変更、Temporary Artifact作成およびToolの暗黙Accessを禁止する。

外周境界内でも、Git Staging、Backup、Phase Backup、Sibling Projectその他の未許可Directoryを自動的に対象へ含めない。`other/`は、ユーザーが本禁止を当該ターンで明示的に一時解除し、正確な対象PathとActionを特定した場合を除き、Readを含む全Accessを拒否する。

## 4. Prior Evidence／Recurrence Prevention

ユーザーは、過去にも担当が未許可の場所へCopy Folderを作成し、強い是正要求が生じた事実を再確認した。本件とCommand-only Request誤実行Incidentは、別々の偶発事象ではなく、担当が善意、推測または作業効率からAuthorityを補完すると発生する共通Failure Patternとして扱う。

再発防止は「より慎重に推測する」ことではない。推測によるAuthority生成を禁止し、不明時には必ず確認することがControlである。

## 5. Phase 2以降のOrchestrationとの分離

Phase 2以降に予定する、設計統括者役、Phase担当設計者役および実装者役を中心とした半自動／ほぼ自動Orchestration実験は、事前にユーザーが承認したOrchestration Envelope内でのみ動作できる。

Envelopeには、少なくとも対象Root、Allowed Paths、Allowed Actions、Forbidden Actions、Task／Role、停止条件、Review Gate、Backup GateおよびUser Gateを含める。Envelope外または1%でも不明な状態では自動化を停止し、確認する。

自動化実験は次を許可しない。

- 本原則の解除
- Project外Accessの包括許可
- `other/`へのAccess
- 未列挙PathのMutation
- HandoffにないTask作成または委譲
- 「じゃ、あとよろしく」を無制限Authorityへ変換すること
- User Gate、Review GateまたはBackup Gateの代行

## 6. Violation Handling

違反または違反疑いはCritical Governance Deviationとして扱う。

1. 即時停止する。
2. 修復、Rollback、追加確認CommandまたはEvidence収集を無許可で実行しない。
3. 実施済みAction、正確な対象、影響、復元可能範囲および復元不能範囲をTextで報告する。
4. ユーザーの明示指示を待つ。

## 7. Normative Sources

- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Command-only Request誤実行Incident](command_only_request_unauthorized_permission_execution_incident_20260803205250.md)
