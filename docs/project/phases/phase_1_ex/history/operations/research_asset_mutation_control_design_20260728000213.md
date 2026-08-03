# Research Asset Mutation Control Design

```yaml
document_id: research_asset_mutation_control_design
phase: phase_1_ex
status: effective
language: ja
created_at: 2026-07-28 00:02:13 JST
owner: 設計統括者役
supersedes: project_root_boundary_and_pre_mutation_gate_20260727235337.md
```

## 1. 目的

無許可Mutationを担当者の注意力だけに依存して防ぐのではなく、全Task、全Role、全Tool、Sub-agentおよび将来自動化へ適用するFail-closed統制として設計した。

## 2. 追加した統制

- Default Read-only／Default Deny
- Mutation Authorization Envelope
- Propose／Commit二段階Protocol
- 元Projectの原則Immutable化
- Project Root外操作の明示許可制
- Symbolic Link追跡の明示許可制
- ユーザーによる今回Backup完了宣言
- Proposed Diffの事前提示
- Pre-tool-call Self Check
- 単一作業単位で失効する承認
- Tool／Agent／Task委譲による迂回禁止
- 違反後の無許可Rollback／修復禁止
- Incident時の完全報告と停止

## 3. Cost Model

無許可Mutationの影響を、変更File数やCommand実行時間だけで評価しない。

次を連鎖損失として正式に扱う。

- 研究Folder全体のBackup増加
- PC保存容量の消費
- 全Project／関連Folder／Archiveの差分検証
- AI差分検証へ支払う有料利用量
- ユーザーの現金損失
- 再説明、監督、再確認および復旧判断の負担
- 精神的疲労
- 研究・設計・実装・公開時間の喪失
- Evidence、History、Metadataおよび原文の復元不能
- 研究・公開・業界上の機会損失

担当が損失規模を理解できない場合、軽微と推定せずFail Closedとする。

## 4. Stable Artifacts

- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Mutation Authorization Manifest Schema](../../../../shared/schemas/mutation_authorization_manifest_schema_v1.json)
- [Mutation Authorization Manifest Template](../../../../shared/templates/mutation_authorization_manifest_template_ja.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Design Governance Handoff](../../../../shared/design_governance_handoff/design_governance_handoff_ja.md)

## 5. History Snapshots

変更前：

- `docs/project/shared/history/conventions/documentation_rules_phase_1_ex_before_research_asset_mutation_control_ja_20260727235902.md`
- `docs/project/shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_research_asset_mutation_control_ja_20260727235902.md`
- `docs/project/shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_research_asset_mutation_control_ja_20260727235902.md`
- `docs/project/shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_before_research_asset_mutation_control_ja_20260727235902.md`

変更後：

- `docs/project/shared/history/conventions/documentation_rules_phase_1_ex_after_research_asset_mutation_control_ja_20260728000213.md`
- `docs/project/shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_research_asset_mutation_control_ja_20260728000213.md`
- `docs/project/shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_research_asset_mutation_control_ja_20260728000213.md`
- `docs/project/shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_after_research_asset_mutation_control_ja_20260728000213.md`

## 6. Integrity

```text
Documentation Rules:
d4a786e195a3640f391830225828d5c38f7846b44fd8ba4db6ab6b13ff8399bf35cbdce89d40554596e800f81fdb5a40d9e9962164a8ecca9775b71b27b3e095

Documentation Structure／Task Operations:
66f830b6836755d23373ff89ee9463e72124b52829b0aac974433ed8f8e0fbe74f26a1e0465b07b5a5edc8107784d3b1807d2476e96beff452787f5674282ac8

Task Role／Write Authority:
c71841aaac0896d560d1f5d8e509737c7d50427c2fbeb452053dd9801092a14a70788eb82200d1a4ba781237103366990f7b9ae18b20628dc7f180656bab2e0a

Design Governance Handoff:
e6ef806fd95f3d0620ee5f6f7854eee2cfc902c9143f9ec67c182ed4ac1a9cbe6ff92d423cef7b5e60074d2a13fb93b480b2ce06913de66455bcdec78d8d27b0

Research Asset Mutation Control:
eafebff8f2aa6c62e1626792d7bc6dfc5cb71e3295adce3098565717aa47a377271ff7fc067587b6ca2ee1c8d418fd5a56793cda1500be3713a16a1920eb1dd4

Manifest Schema:
e4b06327bb176fada46c0e7d39d46f9af88651479d30b8ff761377bb11817b212e210dbb5c372848bdbe9ad82f7e21b82ad4089e9fe53f59b83060b02643a27a

Manifest Template:
9b80bbb0a443755b51030dde99d9bd250d15084403998cb6967d06eee109a0799b494feb3a87547a73a380f03bf558cbf285204632858b34033a2bf1cb0c90d8
```

## 7. Boundary

本設計は無許可Mutationを新たに許可しない。

既発生変更の復旧、Project Root外Artifact操作、公開Sanitation、Git操作、GitHub操作、Backup作成または外部Service変更を許可しない。
