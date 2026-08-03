# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](task_role_write_authority_policy_20260719142558.md)
- Backup Policy: [phase_completion_backup_policy_20260719142558.md](../operations/phase_completion_backup_policy_20260719142558.md)
- supersedes: `documentation_rules_20260718193435.md`

## 1. 目的

本書は、`docs/`のFile名、時刻、言語、Append-Only更新、正本、担当TaskのWrite Authority、Review／Index、Phase完了Backupの共通ルールを定義する。

新しいTaskは、最新Documentation Indexと本書を最初に参照する。

## 2. Project Root

Logical Root：

```text
margpa-runtime-llm/
```

Current Local Root：

```text
/path/to/margpa-runtime-llm/
```

Userが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合は、明示的な別基準がない限りProject Root基準とする。

## 3. Project表記

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

新規Docsでは通称を`Nazuna Research Governance LLM`へ統一する。

## 4. Task間Communication

要件、Decision、Progress、Finding、Review、Handoff、未解決事項、Phase Statusは原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

会話内だけで重要Decisionを閉じない。ただしDocsへの記録はUserの指示とTask Role Authorityの範囲内で行う。

## 5. Docs Read-only Principle

Docsを読み込む、参照する、引き継ぐ、確認する依頼は、原則としてRead-onlyである。

次は明示的なWrite指示またはRole Authorityがない限り行わない。

- File作成／編集／削除
- Rename／Move
- Status変更
- 正本差し替え
- Link修正
- 誤字修正

問題を発見しても読み取り依頼だけで勝手に修正せず、Findingを報告する。

## 6. Filename

Markdown文書は次の形式とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

概念正規表現：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

規則：

- 説明部分は英小文字／数字
- `_`区切り
- 空白／Hyphen／日本語をFile名に使用しない
- 末尾に14桁Timestamp
- ADRは`adr_0001_...`形式
- Model ID／Class名／原表記は本文で保持

## 7. Timestamp

```text
YYYYMMDDHHMMSS
```

Timezone：

```text
Asia/Tokyo／JST
```

同一設計Snapshotで複数文書を作る場合は、作成開始時刻を共有できる。全Fileに同じSnapshot／作成日時を記載する。

## 8. Language

本文は可能な限り日本語とする。

原表記を保持する主なもの：

- Model／Repository ID
- Class／Function／Config Key
- Protocol／Licenseの正式名
- ARGD／DAGD等のDefinition上の識別子
- Code上の識別子

## 9. Required Metadata

各文書の先頭に可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
Snapshot
担当／対象
正本言語
上位／関連文書
supersedes
```

## 10. Append-Only

`docs/`はStrict Append-Onlyとする。

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes: old_file_YYYYMMDDHHMMSS.md`を記載する
4. Documentation Indexも上書きせず新Timestampで作る
5. 古いIndexを残し、各時点のCurrent Setを再現可能にする
6. Handoff／Status／Reviewも毎回新規作成する
7. 古い文書へSuperseded表記を追記せず、新Index側で状態を示す

誤字、Link切れ、意味を変えない修正でも既存Fileを直接編集しない。

## 11. Latest／Current

- 同一系列でTimestampが最も新しいFileを最新とする
- 最新`documentation_index_*`をCurrent Set判定の入口とする
- Rollback内容でも新Timestampを使う
- 古いDocs／Indexを削除／Rename／Moveしない
- 古いHandoffだけを根拠に作業を開始しない

## 12. Directory

```text
docs/
├─ requirements/  要件、制約、共通Rule、Role Authority
├─ architecture/  System構成、Model、Storage、Roadmap
├─ governance/    ARGD／DAGD、Audit、Evaluation、Security
├─ adr/           Decision、理由、代替案
├─ operations/    Phase Backup、Snapshot、Restore、Release Operations
├─ user_manual/   内部User Manual
├─ public/        将来の対外Public Docs
└─ handoffs/      Common／Designer／Implementer／External Handoff／Status／Review
```

`docs/public/`は必要になった時点で作成する。

## 13. Role Authority

詳細正本：

- [task_role_write_authority_policy_20260719142558.md](task_role_write_authority_policy_20260719142558.md)

要約：

```text
設計者:
  Requirements／Architecture／Governance／ADR／Operations
  User Manual／Index／Common／Designer Handoff／Review
  各担当の開始用Handoff

実装者:
  src／tests／scripts
  implementer_status_*
  config／Root FileはAccepted Handoff + User許可で条件付き

対外Docs作成者:
  README／docs/public/
  external_docs_status_*
  Canonical DocsはRead-only
```

## 14. Review／Index Pairing

実装者Statusを設計者がReviewした場合、原則として次を同一Snapshotで作成する。

```text
designer_review_<topic>_YYYYMMDDHHMMSS.md
documentation_index_YYYYMMDDHHMMSS.md
```

ReviewとIndexは設計者役のOwnershipとする。

Findingがある場合でも、Review依頼だけでSource Fixを行わない。

## 15. Handoff／Status

- `common_project_handoff_*`: 設計者
- `designer_handoff_*`: 設計者
- `designer_review_*`: 設計者
- `implementer_handoff_*`: 設計者が開始指示として作成
- `implementer_status_*`: 実装者
- `public_documentation_handoff_*`: 設計者が開始指示として作成
- `external_docs_status_*`: 対外Docs作成者

すべてAppend-Onlyとする。

## 16. Operational Status

設計者役と実装者役の分業は、Phase 1-A／1-B／1-C／1-DおよびPhase 1-EのDesign／Handoff／Implementation Cycleで実運用され、現時点で有効に機能している。

対外Docs作成者役はTask作成済みだが、本格的な実作業検証は未完了である。

## 17. Phase Completion Backup

詳細正本：

- [phase_completion_backup_policy_20260719142558.md](../operations/phase_completion_backup_policy_20260719142558.md)

Backup Trigger：

```text
設計者がIndependent Review／Final Docs／Indexを完了し、
「Phase Nは完了。次はPhase N+1です」
と明示した直後。
```

Backupは完了宣言後、次Phaseの実質的変更前に行う。Implementer StatusだけではTriggerとしない。

## 18. New Task Reading Order

1. 最新`documentation_index_*`
2. 最新`common_project_handoff_*`
3. 本Documentation Rules
4. Task Role Authority Policy
5. 担当領域のRequirements／Architecture／Governance
6. 関連ADR
7. 最新Designer Handoff／Status／Review

## 19. Prohibited

- TimestampなしMarkdownの新規作成
- Existing Docsの上書き／削除／Rename／Move
- 古いDocsへ後継Status追記
- Latest Index未確認での作業開始
- Role Scope外Write
- Read依頼からのWrite Authority推定
- Review依頼からのFix Authority推定
- Secret／Credential／Personal DataのDocs記載
- 確定／暂定／未決／Future／Scope外の混同

## 20. Policy Update

本書を変更する場合は既存Fileを編集せず、新Timestampの後継文書とDocumentation Indexを作成する。
