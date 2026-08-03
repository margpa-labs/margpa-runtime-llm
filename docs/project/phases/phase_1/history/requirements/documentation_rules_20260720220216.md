# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](task_role_write_authority_policy_20260719142558.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](public_identity_and_personal_information_policy_20260720220216.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../operations/phase_completion_backup_policy_20260719171836.md)
- Known Issues／Observations: [known_issues_and_observations_20260719171836.md](../operations/known_issues_and_observations_20260719171836.md)
- supersedes: `documentation_rules_20260719171836.md`

## 1. 目的

本書は、Docsの基準Path、公開識別子、File名、時刻、言語、Append-Only、正本、担当TaskのWrite Authority、Review／Index、Phase完了Backupを定義する。

新しいTaskは、最新Documentation Index、本書、Privacy Policyを最初に参照する。

## 2. Project Root

Logical Rootは`margpa-runtime-llm/`である。ユーザーが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合、明示的な別基準がない限りProject Root基準とする。

文書やSampleへ個人固有のCurrent Local Rootを記録せず、必要な場合は`/path/to/margpa-runtime-llm`等の抽象Pathを使う。

## 3. Project表記と公開識別子

```text
Project Name   : margpa-runtime-llm
Display Name   : MARGPA Runtime LLM
Internal Name  : Nazuna Research Governance LLM
Public Identity: Nazuna Research
```

第一者の作者、設計者、開発者、Maintainer等の固有名表記は`Nazuna Research`へ統一する。役割名である「ユーザー」「設計者役担当Task」「実装担当Task」等は固有名ではないため使用できる。

## 4. Task間Communication

要件、Decision、Progress、Finding、Review、Handoff、未解決事項、Phase Statusは原則`margpa-runtime-llm/docs/`を共通基盤とする。

会話内だけで重要Decisionを閉じない。ただしDocsへの記録はユーザー指示とTask Role Authorityの範囲内で行う。

## 5. Docs Read-only Principle

Docsを読み込む、参照する、引き継ぐ、確認する依頼は原則Read-onlyである。明示的なWrite指示またはRole Authorityがない限り、作成、編集、削除、Rename、Move、Status変更、正本差し替え、Link修正を行わない。

## 6. Filename／Timestamp／Language

Markdown文書は次の形式とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

- 説明部分は英小文字／数字と`_`
- 末尾はAsia/Tokyoの作成時刻`YYYYMMDDHHMMSS`
- ADRは`adr_0001_...`形式
- 同一設計Snapshotの複数文書は同じTimestampを共有できる
- 本文は可能な限り日本語とする
- Model ID、Class名、Protocol、License、Definition識別子は正式表記を保持する

## 7. Required Metadata

各文書の先頭に可能な限り、文書ID、状態、作成日時、更新日時、Snapshot、担当、正本言語、関連文書、`supersedes`を記載する。

## 8. Append-Only

`docs/`は原則Strict Append-Onlyとする。

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes`を記載する
4. Documentation Indexも上書きせず新Timestampで作る
5. 古いIndexを残し、各時点のCurrent Setを再現可能にする
6. Handoff／Status／Reviewも毎回新規作成する
7. 古い文書へSuperseded表記を追記しない
8. 同一系列ではTimestampが最も新しいFileを最新とする
9. 最新`documentation_index_*`をCurrent Setの入口とする

## 9. Privacy／Security Exception

個人情報、Credential、Secret、公開不適切なLocal PathはAppend-Onlyより優先する。発見時は既存Fileを直接削除または匿名化できる。

例外適用時は、実値を再掲しない新規Scrub ReportとIndexを作り、歴史SnapshotがBitwise同一でなくなった事実を記録する。削除情報を復元・再掲しない。

詳細は[公開識別子・個人情報取扱方針](public_identity_and_personal_information_policy_20260720220216.md)を正本とする。

## 10. Directory

```text
docs/
├─ requirements/  要件、制約、共通Rule、Role Authority
├─ architecture/  System構成、Model、Storage、Roadmap
├─ governance/    Governance、Audit、Evaluation、Security
├─ adr/           Decision、理由、代替案
├─ operations/    Backup、Snapshot、Restore、Release、Known Issues、Scrub Report
├─ user_manual/   内部User Manual／User Acceptance Test
├─ public/        将来の対外Public Docs
└─ handoffs/      Common／Designer／Implementer／External Handoff／Status／Review
```

## 11. Role Authority

```text
設計者:
  Requirements／Architecture／Governance／ADR／Operations
  User Manual／Index／Common／Designer Handoff／Review
  各担当の開始用Handoff

実装者:
  src／tests／scripts
  implementer_status_*
  config／Root FileはAccepted Handoff + ユーザー許可で条件付き

対外Docs作成者:
  README／docs/public/
  external_docs_status_*
  Canonical DocsはRead-only
```

設計者役と実装者役の分業はPhase 1の実運用で有効に機能した。対外Docs作成者役は本格的な実作業検証前である。

## 12. Review／Index Pairing

実装者Statusを設計者がReviewした場合、原則として同一Snapshotの`designer_review_<topic>_*`と`documentation_index_*`を作る。FindingがあってもReview依頼だけでSourceを修正しない。

非BlockerのFindingは最新`known_issues_and_observations_*`へStable ID、State、Severity、再現、影響、Disposition、再評価条件を記録する。

## 13. Handoff／Status Ownership

- `common_project_handoff_*`: 設計者
- `designer_handoff_*`: 設計者
- `designer_review_*`: 設計者
- `implementer_handoff_*`: 設計者が開始指示として作成
- `implementer_status_*`: 実装者
- `public_documentation_handoff_*`: 設計者が開始指示として作成
- `external_docs_status_*`: 対外Docs作成者

## 14. Phase Completion Backup

Backup Triggerは次の二重条件である。

```text
Gate A: 設計者役がPhase完了と次Phase移行可能を明示
Gate B: ユーザーが対象User Manual／Snapshotの受入テスト全項目合格を明示
```

両Gateが同一Project状態について成立した後、次Phaseの実質的変更前にBackupする。Material Changeが入った場合は影響範囲に応じReviewまたはUser Testを再実行する。

## 15. 公開前確認

Public Docs作成、Source Archive、Git／GitHub公開の直前にPrivacy Policyの公開前Gateを実行する。Git Author／Committer、外部Account、Repository設定は、ユーザーの別途許可なく変更しない。
