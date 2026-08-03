# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](task_role_write_authority_policy_20260719142558.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](public_identity_and_personal_information_policy_20260720220216.md)
- Backup／Publication Policy: [phase_completion_backup_policy_20260720222402.md](../operations/phase_completion_backup_policy_20260720222402.md)
- Known Issues／Observations: [known_issues_and_observations_20260719171836.md](../operations/known_issues_and_observations_20260719171836.md)
- supersedes: `documentation_rules_20260720220216.md`

## 1. Project／Identity

```text
Project Root   : margpa-runtime-llm/
Project Name   : margpa-runtime-llm
Display Name   : MARGPA Runtime LLM
Internal Name  : Nazuna Research Governance LLM
Public Identity: Nazuna Research
```

相対PathはProject Root基準とする。第一者の作者、設計者、開発者、Maintainer等の固有名は`Nazuna Research`へ統一する。個人固有絶対PathをDocsやSourceへ記録しない。

## 2. Task間Communication／Read-only

要件、Decision、Progress、Review、Handoff、未解決事項、Phase Statusは原則`docs/`を共通基盤とする。

Docsの読込、参照、確認依頼は原則Read-onlyであり、明示的Write指示またはRole Authorityなしに編集、削除、Rename、Move、正本差し替えを行わない。

## 3. Filename／Timestamp／Language

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

- TimestampはAsia/Tokyoの`YYYYMMDDHHMMSS`
- 同一Snapshotの複数文書は同じTimestampを共有できる
- 本文は可能な限り日本語
- 正式なModel ID、Class、Protocol、License、Definition識別子は原表記を保持
- 先頭Metadataに文書ID、状態、時刻、Snapshot、担当、関連文書、`supersedes`を記載

## 4. Append-Only

1. 作成済みDocsは原則変更しない
2. 変更時は新Timestampの後継Fileを作る
3. 後継Fileに`supersedes`を記載する
4. Index、Handoff、Status、Reviewも毎回新規作成する
5. 古い文書へSuperseded表記を追記しない
6. 最新Timestampを最新とする
7. 最新`documentation_index_*`をCurrent Setの入口とする

個人情報、Credential、Secret、公開不適切Pathの削除はPrivacy／Security例外として既存Fileへ直接適用できる。実値を再掲しないScrub ReportとIndexを残す。

## 5. Directory／Ownership

```text
requirements : 設計者
architecture : 設計者
governance   : 設計者
adr          : 設計者
operations   : 設計者
user_manual  : 設計者
handoffs     : File系列ごとの担当
public       : 対外Docs作成者
```

- 設計者はRequirements、Architecture、Governance、ADR、Operations、Manual、Index、Handoff、Reviewを担当する
- 実装者は`src/`、`tests/`、`scripts/`、`implementer_status_*`を担当する
- `config/`とRoot FileはAccepted Handoffとユーザー許可で実装者が変更できる
- 対外Docs作成者はREADME、`docs/public/`、`external_docs_status_*`を担当し、Canonical DocsはRead-onlyとする
- Implementer Statusを設計者がReviewした場合、ReviewとIndexを同一Snapshotで作る

## 6. Phase Backup／GitHub公開

Phase Backupは次の両Gate後に行う。

```text
Gate A: 設計者のPhase完了／次Phase着手可能宣言
Gate B: ユーザーの受入テスト合格宣言
```

原則、各PhaseのBackup確定後に同一SnapshotをGitHubへ反映する。初回だけはPhase 1-ex「運用再整備」完了後までGitHub公開を延期する。

毎回、Backup Candidate内の`margpa-runtime-llm/`から`.DS_Store`、`.venv`、Model、Symlink、Cache、Bytecode、Coverage、Secret、Local Data等の不要物を除去し、Inventory、Privacy、SHA-512、Restoreを検証してからBackupを確定する。

詳細は[Phase完了Backup／GitHub公開運用Policy](../operations/phase_completion_backup_policy_20260720222402.md)を正本とする。

## 7. Phase 1-ex

Phase 1と初回GitHub公開の間にPhase 1-ex「運用再整備」を追加する。詳細は未定義であり、[要件プレースホルダー](phase_1_ex_operations_reorganization_requirements_20260720222402.md)から後続定義する。

## 8. Authorization Boundary

Docsへの要件記録だけではSource変更、Backup生成、Git操作、GitHub操作、外部環境操作、公開を許可しない。
