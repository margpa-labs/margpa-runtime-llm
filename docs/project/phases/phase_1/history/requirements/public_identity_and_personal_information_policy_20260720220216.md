# 公開識別子・個人情報取扱方針

- 文書ID: `public_identity_and_personal_information_policy`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. 決定

本Projectにおける第一者の公開識別子は、次の表記だけに統一する。

```text
Nazuna Research
```

Projectの作者、設計者、開発者、Maintainer、連絡主体、Copyright主体等を公開文書やMetadataへ記載する場合も、この表記を使用する。

## 2. 禁止する第一者情報

公開候補Artifactへ次を記録しない。

- 法的氏名、実名、旧名、別表記、音訳表記
- Local OSのAccount名
- Home Directoryを含む個人固有の絶対Path
- Local Hostname、端末名、Machine固有識別子
- 個人Email、電話番号、住所、生年月日
- Credential、API Key、Secret、Private Key、Cookie、Token
- Private Repository、非公開資料、Local Attachmentへの到達Path
- 実会話Log、RAG投入資料その他の個人Data

## 3. 適用対象

本方針は次へ適用する。

- `src/`、`tests/`、`scripts/`、`config/`
- Root Metadata、License、README、Release Artifact
- `docs/`以下の内部文書と公開文書
- Sample、Log、Evidence、Screenshot、Terminal出力
- Archive、Manifest、Git Commit Metadata、GitHub表示情報

公開前には、本文だけでなくFile名、Symlink、Archive内Path、画像Metadata、生成物も検査する。

## 4. 第三者情報

Model、Library、Protocol、Paper、Repository、License等に必要な第三者の正式な名称と帰属は削除しない。

`Nazuna Research`への統一は第一者の公開Identityに対する規則であり、第三者をProject作者として誤表示する規則ではない。

## 5. 架空値と禁止例

Privacy FilterやPath RedactionのTestに必要な架空値、または設計文書内の抽象化された禁止例は、実在人物・実環境へ結び付かない場合に限り保持できる。

架空値は`example`、`<MODEL_ROOT>`、`/path/to/...`等、架空であることが明確な表現を使う。

## 6. Local-only Artifact

次は公開Artifactへ含めない。

- `.venv/`
- `models` SymlinkとModel本体
- `*.gguf`
- Cache、Coverage Data、Bytecode
- `.DS_Store`
- `var/`以下のLocal Runtime Data

これらはLocal実行に必要でも、公開Source ArchiveやGit管理対象ではない。公開Archive作成時はIgnore設定だけに依存せず、収録Manifestを検査する。

## 7. Append-Onlyの例外

個人情報、Credential、Secret、公開不適切なLocal Pathを既存Docsで発見した場合、Privacy／Securityを優先し、既存Fileを直接削除または匿名化できる。

この処理はStrict Append-Onlyの例外である。次を残す。

- 実値を再掲しないScrub Report
- 対象範囲と検査方法
- 検査結果
- 歴史SnapshotがBitwise同一ではなくなった事実

削除した個人情報を履歴復元目的で新Docsへ再記録してはならない。

## 8. 公開前Gate

公開前に最低限、次を確認する。

1. 第一者表記が`Nazuna Research`へ統一されている
2. 個人固有Path、Hostname、連絡先、Credentialがない
3. `.venv`、Model、Cache、Local LogがArchiveへ入っていない
4. Sample LogとScreenshotが匿名化されている
5. Git Author／CommitterとGitHub Profileの公開範囲をユーザーが確認している
6. 第三者LicenseとAttributionが保持されている

Gitを将来開始する際は、公開前にGitのAuthor名とEmailを別途確認する。現在の本方針だけで外部Service設定を変更しない。
