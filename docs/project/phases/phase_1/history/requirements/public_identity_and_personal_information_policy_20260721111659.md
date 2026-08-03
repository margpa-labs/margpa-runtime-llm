# 公開識別子・個人情報取扱方針

- 文書ID: `public_identity_and_personal_information_policy`
- 状態: `current`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- supersedes: `public_identity_and_personal_information_policy_20260720220216.md`

## 1. 決定

本Projectにおける第一者の公開上の作者名、研究名義、Maintainer表示名、研究主体名、Copyright表示名には、原則として次を使用する。

```text
Nazuna Research
```

今後新規作成するSource、Docs、Metadata、公開Artifact、UI表示、Release情報では、特段の技術的・歴史的理由により別名義を使う必要がある場合を除き、`Nazuna Research`へ統一する。

廃止済み第一者名義は、一般的な作者表示名として使用しない。

## 2. Public Repository Identity

```text
Organization／Repository Owner : margpa-labs
Public Author／Research Name    : Nazuna Research
Public Repository              : margpa-labs/margpa-runtime-llm
Repository URL                 : https://github.com/margpa-labs/margpa-runtime-llm
```

GitHub Owner、Repository URL、Clone URL、Badge、Workflow参照、Package Metadata等では、役割に応じて`margpa-labs`または上記Repository URLを使用する。

`margpa-labs`はRepository Namespaceであり、作者表示名`Nazuna Research`とは役割を分ける。

## 3. 名義例外の判断権限

第一者名義はすべて`Nazuna Research`へ統一する。別の第一者名義または識別子をDocsへ記録する必要性は、設計者役Taskだけが判断できる。現時点で承認済み例外はない。

- 実在するGitHub Account Handleを正確に示す必要がある。
- GitHub提供のnoreply Commit Email等、Account Handleを含む技術識別子を使用する。
- Commit、Tag、Release、Audit Evidenceの出所を正確に示す必要がある。
- 既存ArtifactのAuthor Metadata、Hash対象、過去VersionのProvenanceを改変できない。
- 第三者Service上の既存識別子として変更不能である。
- 移行規則内で旧名義を検索・分類するため、文字列そのものを例示する必要がある。

例外を使用する場合は、単なる慣習や置換漏れではなく、保持理由を説明可能にする。

意味上必要か不明な箇所は自動置換せず、`manual_review`として判断待ちにする。

## 4. 表示名と技術識別子の分離

次を同一視しない。

```text
Display Author Name : Nazuna Research
Repository Owner    : margpa-labs
GitHub Account      : 必要時のみ実在Account Handle
Commit Name         : Nazuna Research
Commit Email        : 別途選択する技術識別子
```

Commitから個人GitHub Accountへ辿れることは、ユーザー判断により許容する。

ただし、Commit Nameは`Nazuna Research`を使用し、個人の実Emailを公開する必要はない。GitHub noreply Email等を使用する場合、そのAccount Handleが技術識別子として表示されることを許容する。

GitHubはCommit Emailを用いてCommitをAccountへ関連付けるため、表示名変更だけではAccount帰属は変わらない。この挙動は本Projectでは既知かつ許容されたものとして扱う。

## 5. Naming Application Matrix

| 対象 | 使用する値 | 備考 |
|---|---|---|
| 作者／研究主体／Maintainer表示 | `Nazuna Research` | 原則固定 |
| Copyright主体表示 | `Nazuna Research` | 法的確認が必要な場合は別途Review |
| Citation Author | `Nazuna Research` | CFF Entity Nameとして記録 |
| Git Commit Author Name | `Nazuna Research` | Emailとは分離 |
| GitHub Organization／Owner | `margpa-labs` | Repository Namespace |
| Repository URL | `https://github.com/margpa-labs/margpa-runtime-llm` | 公開正本 |
| GitHub Account Handle | 実在値 | 技術上必要な場合だけ |
| Project通称 | `Nazuna Research Governance LLM` | 固定 |
| 第三者Author／Organization | 第三者の正式名 | 変更禁止 |

## 6. 禁止する第一者情報

公開候補Artifactへ次を記録しない。

- 法的氏名、実名、旧名、別表記、音訳表記
- Local OSのAccount名
- Home Directoryを含む個人固有の絶対Path
- Local Hostname、端末名、Machine固有識別子
- 個人Email、電話番号、住所、生年月日
- LinkedIn、職務経歴書、個人用Profile、個人連絡先への不要な参照
- Credential、API Key、Secret、Private Key、Cookie、Token
- Private Repository、非公開資料、Local Attachmentへの到達Path
- 実会話Log、RAG投入資料その他の個人Data

CommitからGitHub Accountへ辿れることを許容する決定は、上記の個人情報をSourceやDocsへ積極的に掲載する許可ではない。

## 7. 適用対象

本方針は次へ適用する。

- `src/`、`tests/`、`scripts/`、`config/`
- Root Metadata、License、README、Release Artifact
- `docs/`以下の内部文書と公開文書
- Sample、Log、Evidence、Screenshot、Terminal出力
- Archive、Manifest、Git Commit／Tag Metadata、GitHub表示情報
- `CITATION.cff`、`NOTICE.md`、`CODEOWNERS`
- Workflow、Badge、Package Metadata、生成物

公開前には本文だけでなく、File名、Symlink、Archive内Path、画像Metadata、Binary、生成物も検査する。

## 8. 第三者情報と不変Evidence

Model、Library、Protocol、Paper、Repository、License等に必要な第三者の正式な名称と帰属は削除または変更しない。

次へ一括置換を行わない。

- 第三者Author／Maintainer
- Upstream Repository ID
- Model ID／Revision
- License本文
- Citation
- Hash／Digest
- 署名対象
- 過去Logの真正性を示すEvidence

洗浄によりArtifact内容が変化した場合は、旧Digest内の文字列を置換せず、公開用Artifactから新しいDigestを再計算する。

## 9. Historical Docs／Artifact

本書以前のDocsに旧名義が含まれることは、直ちに当該Docsを破壊的に書き換える許可にならない。

Phase 1-exで次を分類する。

```text
Current Public-facing Source : Nazuna Researchへ変更
Historical Internal Record   : 原本保持または非公開
Public Historical Evidence   : 匿名化版／再生成版を別Artifact化
Immutable Provenance         : 変更せず理由を記録
Manual Review                : 判断待ち
```

公開用Repositoryは洗浄済みExportを優先し、内部の原本や既存開発履歴を直接破壊しない。

## 10. Local-only Artifact

次は公開Artifactへ含めない。

- `.venv/`
- `models` SymlinkとModel本体
- `*.gguf`
- Cache、Coverage Data、Bytecode
- `.DS_Store`
- `var/`以下のLocal Runtime Data

公開ArchiveやGit TreeはIgnore設定だけに依存せず、収録Manifestと実体を検査する。

## 11. Append-Onlyの例外

個人情報、Credential、Secret、公開不適切なLocal Pathを既存Docsで発見した場合、Privacy／Securityを優先し、既存Fileを直接削除または匿名化できる。

この処理はStrict Append-Onlyの例外である。次を残す。

- 実値を再掲しないScrub Report
- 対象範囲と検査方法
- 検査結果
- 歴史SnapshotがBitwise同一ではなくなった事実

削除した個人情報を履歴復元目的で新Docsへ再記録してはならない。

## 12. 公開前Gate

公開前に最低限、次を確認する。

1. 第一者の表示名が`Nazuna Research`へ統一されている。
2. Repository NamespaceとURLが`margpa-labs/margpa-runtime-llm`を指す。
3. 廃止済み第一者名義が公開候補Artifactに残っていない。
4. 個人固有Path、Hostname、連絡先、Credentialがない。
5. `.venv`、Model、Cache、Local Logが公開Treeへ入っていない。
6. Sample LogとScreenshotが匿名化されている。
7. Git Author Nameが`Nazuna Research`である。
8. Commit Account帰属をユーザーが許容した現在決定と整合する。
9. 第三者LicenseとAttributionが保持されている。
10. 洗浄後ArtifactのDigestが再計算されている。

## 13. Authorization Boundary

本書は今後使用する名義と公開識別情報の正本規則である。

本書だけでは既存Fileの一括置換、既存Docsの削除、Git設定変更、Git初期化、履歴書換え、公開RepositoryへのPushを許可しない。これらはPhase 1-exのPreflight、Review、個別Handoff、ユーザー承認後に実施する。
