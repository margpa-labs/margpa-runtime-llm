# 担当Task別Write／Read Authority Policy

- 文書ID: `task_role_write_authority_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 設計者役、実装者役、対外Docs作成者役、将来担当Task
- 正本言語: 日本語
- Documentation Rules: [documentation_rules_20260719142558.md](documentation_rules_20260719142558.md)
- Backup Policy: [phase_completion_backup_policy_20260719142558.md](../operations/phase_completion_backup_policy_20260719142558.md)
- supersedes: なし（新規Authority Policy系列）

## 1. 目的

本Policyは、担当TaskごとのStanding Write Scope、Read-only Scope、Phase固有のConditional ScopeおよびHandoffのOwnershipを定義する。

目的：

- 設計と実装の分離
- 正本Docsの保護
- 実装担当の明確な作業範囲
- Review時の独立性
- 対外Docsと内部正本の分離
- 不要な権限拡大の防止
- Task間Handoffの再現性

## 2. Authorityの性質

本PolicyはProject運用上のWrite Authorityであり、OS／Filesystem上の技術的Permissionと同一ではない。

- Userが最終Authorityを持つ
- Userの明示的な個別指示は本PolicyのStanding Scopeを限定的に拡張・縮小できる
- 引き継ぎやRead依頼はWrite Authorityを意味しない
- 技術的にWrite可能でも、Policy上のAuthorityがなければ書き込まない
- Userの個別許可は対象、期間、Phase、File Scopeを越えて一般化しない

## 3. Scopeの3分類

### Standing Write Scope

役割に通常付与されるWrite範囲。

### Conditional Write Scope

Accepted HandoffとUserの実装／作業許可で、Phaseごとに一時的に追加されるWrite範囲。

### Read-only Scope

参照／Review／Testはできるが、既存Contentの修正・上書き・削除はできない範囲。

## 4. 設計者役担当Task

### 4.1 Standing Write Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/                     # 内部User Manualの現行Owner
docs/documentation_index_*
docs/handoffs/common_*
docs/handoffs/designer_*
```

次のHandoffはFile Prefixが異なっても、開始指示として設計者役が作成できる。

```text
docs/handoffs/implementer_handoff_*
docs/handoffs/public_documentation_handoff_*
将来の担当開始用Handoff
```

### 4.2 Owned Document Types

- Requirements
- Architecture
- Governance正本
- ADR
- Roadmap
- Documentation Rules
- Role Authority Policy
- Operations Policy
- Phase Completion／Snapshot Record
- Documentation Index
- Designer Review／Final Review
- Common Handoff
- Designer Handoff
- 各担当の開始用Handoff
- 内部User Manual

### 4.3 Review Authority

設計者役は、実装者役のStatusとSource／Config／TestをRead-onlyでIndependent Reviewする。

可能な操作：

- Source／Config／Test参照
- Static Test／Unit Test／Integration Test実行
- Native Runtime検証
- Hash／Manifest／Link検証
- Finding／Acceptance判定
- `designer_review_*`作成
- Reviewと同時の新Documentation Index作成

Review依頼はSource／Config／TestのFix実装を意味しない。Findingがある場合はReviewへ記録し、実装担当へFollow-upを返す。

### 4.4 Read-only Scope

```text
src/
tests/
scripts/
config/
pyproject.toml
uv.lock
README等の対外Docs担当Owner領域
docs/handoffs/implementer_status_*
docs/handoffs/external_docs_status_*
```

設計者役が実装を兼務する場合は、UserがそのTaskに対して実装範囲を明示的に許可する。

## 5. 実装者役担当Task

### 5.1 Standing Write Scope

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

### 5.2 Conditional Write Scope

次はStanding Scopeではない。Accepted Designer Handoffが対象Pathを明記し、Userが当該Phaseの実装開始を許可した場合だけWriteできる。

```text
config/
pyproject.toml
uv.lock
ルートのBuild／Runtime設定
Migration File
Phase固有Asset
新規Directory
```

Handoffに書かれていないFileへのWriteが必要になった場合は、独断でScopeを広げず設計者／Userへ返す。

### 5.3 Status Ownership

実装者役は、実装またはFollow-upごとに新TimestampのStatusを作成する。

```text
docs/handoffs/implementer_status_<topic>_YYYYMMDDHHMMSS.md
```

Statusには次を含める。

- Authorization／Scope
- Changed／Added File
- Implementation Summary
- Test Command／Result
- Native Verification
- Hash／Dependency／Schema変更
- Known Limitation
- Acceptance Criteria対応
- Review依頼

実装者役は`designer_review_*`または`documentation_index_*`を作成しない。

### 5.4 Read-only Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/
docs/documentation_index_*
docs/handoffs/common_*
docs/handoffs/designer_*
その他のCanonical Docs
```

要件・Architecture・Governance／ADR正本に問題を発見しても直接修正しない。Statusへ記録し、設計者役へ返す。

## 6. 対外Docs作成者役担当Task

### 6.1 Standing Write Scope

```text
README*
docs/public/                         # 将来のPublic Docs候補
docs/handoffs/external_docs_status_*
```

License、Security Policy、Contribution Policyまたは法的表記の変更は、Userの明示的な個別許可を必要とする。

### 6.2 Read-only Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/
docs/documentation_index_*
src/
tests/
config/
```

対外DocsはCanonical Docsを参照して作成する。Canonicalな要件・Architecture・Governanceの内容を直接変更しない。

### 6.3 Status Ownership

```text
docs/handoffs/external_docs_status_<topic>_YYYYMMDDHHMMSS.md
```

対外Docs作成者役は、正本とPublic Docsの矛盾をStatusへ記録し、設計者／Userへ返す。

## 7. `docs/operations/` Ownership

Standing Owner：

```text
設計者役担当Task
```

対象：

- Phase Completion Backup Policy
- Snapshot Record
- Restore Policy／Restore Result
- Release／Milestone Operations
- Backup Naming／Retention
- Operationsの人間向け記録

External Archive、Manifest／Receiptの実ファイル生成は`docs/operations/`のWrite Authorityに自動的に含まれない。Project外WriteまたはBackup Operatorの許可を別途必要とする。

## 8. Documentation Index Ownership

`documentation_index_*`のStanding Ownerは設計者役とする。

新Indexを作成する主なTiming：

- Requirements／Architecture／Governance／ADR更新
- Designer Handoff更新
- Designer Review完了
- Phase／Milestone Status更新
- Common Rule／Operations Policy更新
- Current／Historical Setの変更

実装者Statusの作成時は、実装者がIndexを作らず、設計者Review時にReviewとIndexをセットで作成する。

## 9. Handoff／Review Naming Ownership

| Prefix／Type | Standing Owner |
|---|---|
| `common_project_handoff_*` | 設計者 |
| `designer_handoff_*` | 設計者 |
| `designer_review_*` | 設計者 |
| `implementer_handoff_*` | 設計者（開始指示） |
| `implementer_status_*` | 実装者 |
| `public_documentation_handoff_*` | 設計者（開始指示） |
| `external_docs_status_*` | 対外Docs作成者 |

Follow-upでも過去Fileを上書きせず、新Timestampを使用する。

## 10. Operational Validation Status

### 設計者役／実装者役

現在の設計者役と実装者役の分業は、Phase 1-A／1-B／1-C／1-Dの実装、Status、Review、Follow-up、Final Acceptanceで実運用された。

また、Phase 1-EでRequirements／Architecture／ADR／Formal Handoffを設計者が作成し、実装者が実装を担当する流れが継続している。

現時点の評価：

```text
設計者役／実装者役の分業は、実運用上有効に機能している。
```

今後も当面の間、本Authority構造をCurrent Policyとする。

### 対外Docs作成者役

対外Docs作成者役はTask作成済みだが、現時点で実作業による十分な運用検証は完了していない。

そのため、対外Docs役のAuthorityは暂定的に正式化するが、実運用後に必要に応じて後継Policyで調整できる。

## 11. Conflict／Escalation

次の場合は作業を独断で続けず、User／Ownerへ返す。

- 複数役割が同じFileを同時変更する
- Standing Scope外のWriteが必要
- Canonical Docsと実装が矛盾
- HandoffとUser Instructionが矛盾
- Current Indexが不明
- 既存File上書きが必要に見える
- Secret／Personal Data／External Credentialが関係
- 破壊的操作が必要

## 12. Prohibited Actions

- 担当外のCanonical Fileを勝手に変更しない
- Read依頼をWrite許可と解釈しない
- Review依頼をFix許可と解釈しない
- 古いDocs／Handoff／Status／Reviewを上書きしない
- Userの一回限りの許可をStanding Authorityに変換しない
- 実装者が設計Decisionを黙って変更しない
- 設計者がIndependent Review中に黙ってSource Fixしない
- 対外Docs役がCanonical要件をPublic向けに黙って改変しない

## 13. Policy Change

本Policyを変更する場合は既存Fileを編集せず、新Timestampの後継Policyと最新Documentation Indexを作成する。

