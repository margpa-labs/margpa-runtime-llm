# 文書作成・命名・更新共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書
- 正本言語: 日本語

## 1. 目的

この文書は、`docs/`以下に作成する文書のファイル名、時刻、言語、更新、正本、引き継ぎ方法を統一する共通ルールである。

設計者、実装者、対外向けDocs作成者、その他の担当タスクは、文書を新規作成する前にこのルールを参照する。

## 2. 必須ファイル名形式

Markdown文書のファイル名は、次の形式を必須とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

例：

```text
system_architecture_20260718174023.md
runtime_governance_20260718174023.md
common_project_handoff_20260718174023.md
adr_0001_initial_model_selection_20260718174023.md
```

正規表現の概念形：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

## 3. ファイル名の規則

- 説明部分は英語の小文字を使用する
- 単語の区切りには`_`を使用する
- 空白を使用しない
- ハイフンを使用しない
- 日本語をファイル名に使用しない
- 最後に14桁の作成時刻を必ず付ける
- 拡張子は原則`.md`とする
- ADRは`adr_0001_...`の形式で連番を持たせる
- Model ID、Class名、設定キー等の原表記は本文中に記載し、ファイル名へ無理に再現しない

## 4. 時刻の規則

14桁の時刻形式：

```text
YYYYMMDDHHMMSS
```

内訳：

```text
YYYY : 年
MM   : 月
DD   : 日
HH   : 時（24時間）
MM   : 分
SS   : 秒
```

Timezoneは`Asia/Tokyo / JST`を正本とする。

複数文書を一つの設計Snapshotとして一括作成する場合は、文書セットの作成開始時刻を全ファイルで共有してよい。この場合、全ファイルのFront Matter相当のメタデータに同じ作成日時を記載し、同一Snapshotであることを明示する。

## 5. 文書本文の言語

本文は可能な限り日本語で作成する。

英語を保持するもの：

- Model ID
- Repository ID
- Class名
- 関数名
- 設定キー
- Protocol名
- Licenseの正式名称
- 外部資料の正式名称
- コード上必要な識別子
- ARGD／DAGD等の定義上の正式語

英語資料を参照する場合は、日本語で内容を説明し、原文名称と参照先を併記する。

## 6. 文書の必須メタデータ

各文書の先頭には、可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
担当または対象
正本言語
上位文書
置換対象
```

状態候補：

```text
draft
current
experimental
deprecated
superseded
archived
```

## 7. 更新と版管理

### 7.1 軽微な修正

誤字、リンク修正、意味を変えない表現修正は既存ファイルを更新してよい。その場合は本文の`更新日時`を更新する。

### 7.2 実質的な改訂

要件、設計判断、Module Boundary、公開方針等を実質的に変更する場合は、新しい作成時刻を持つ新規ファイルを作成する。

新しい文書には次を記載する。

```text
置換対象: 旧ファイル名
```

旧文書には、可能な場合は次を追記する。

```text
状態: superseded
後継文書: 新ファイル名
```

## 8. 正本の決定

同じ主題の文書が複数ある場合、単純に時刻が新しいものを自動的な正本とはしない。

`docs/documentation_index_*.md`で`current`として指定された文書を現在の正本とする。

## 9. Directoryの役割

```text
docs/
├─ requirements/  要件、制約、MVP、未決事項
├─ architecture/  システム構成、Model、Storage、Roadmap
├─ governance/    ARGD、DAGD、監査、評価、安全性
├─ adr/           設計判断と理由
└─ handoffs/      共通・担当別の引き継ぎ
```

必要になった場合は、同じ命名規則に従って追加Directoryを設ける。

## 10. 引き継ぎ時の利用方法

新しい担当タスクは、原則として次の順に読む。

1. 最新の`documentation_index_*.md`
2. 最新の`common_project_handoff_*.md`
3. 担当領域のRequirements／Architecture／Governance
4. 関連ADR
5. 未決事項と次の作業

引き継ぎ文書は正本の内容を勝手に変更せず、正本への参照と現在地点を示す。

## 11. 禁止事項

- Timestampを持たないMarkdown文書を新規作成しない
- 同名ファイルを上書きして重大な設計変更を隠さない
- 日本語正本と英語文書の内容を無管理で分岐させない
- 古い引き継ぎ文書だけを根拠に実装しない
- 確定、暫定、未決、将来、対象外を混同しない
- ユーザー固有のSecretやCredentialをDocsへ記載しない

## 12. このSnapshotについて

この文書を含む初期文書セットは、`20260718174637`を共通Snapshot時刻として作成した。
