# 文書作成・命名・更新共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書
- 正本言語: 日本語
- supersedes: `documentation_rules_20260718174637.md`

## 1. 目的

この文書は、`docs/`以下に作成する文書のファイル名、時刻、言語、更新、正本、引き継ぎ方法を統一する共通ルールである。

設計者、実装者、対外向けDocs作成者、その他の担当タスクは、文書を新規作成する前にこのルールを参照する。

## 1.1 プロジェクトルートと相対Pathの解決

このProjectにおけるProject Rootの論理表記は、次とする。

```text
margpa-runtime-llm/
```

現在のLocal環境における実体Path：

```text
/path/to/margpa-runtime-llm/
```

ユーザーが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合は、明示的に別の基準Pathが指定されていない限り、Project Rootを基準として解釈する。

例：

```text
User指定 : docs/
解釈      : margpa-runtime-llm/docs/

User指定 : docs/architecture/
解釈      : margpa-runtime-llm/docs/architecture/
```

相対PathをHome Directory、現在のTask固有Directory、外部Model Root等へ勝手に読み替えない。

## 1.2 タスク間の情報伝達

設計者、実装者、対外向けDocs作成者、その他の担当タスク間における情報伝達、決定事項、進捗通達、未決事項、引き継ぎは、原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

担当タスクは、会話内だけで重要な決定や進捗を閉じず、ユーザーから記録を許可・依頼された場合は、適切なRequirements、Architecture、Governance、ADR、Handoffへ反映する。

ただし、Docsへの記録は明示的な作成・更新権限がある場合に限る。単にDocsを読むよう依頼されたことを、編集許可として扱わない。

## 1.3 Docs参照時の読み取り専用原則

`margpa-runtime-llm/docs/`を読み込む、確認する、参照する、引き継ぐよう指示された場合、原則として必ず読み取り専用で扱う。

次の操作は、ユーザーから明示的な変更指示または作成・更新許可がない限り行わない。

- File作成
- File編集
- File削除
- File名変更
- Directory作成・削除
- Status変更
- 正本の差し替え
- 内容の自動修正

矛盾、誤記、古い情報、Link切れ等を発見した場合も、読み取り依頼だけで勝手に修正しない。発見内容を報告し、変更権限を確認する。

「Docsを参照する権限」と「Docsを変更する権限」は別の権限として扱う。

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

## 5.1 プロジェクト通称の共通表記

Projectの通称は、次を正本とする。

```text
Nazuna Research Governance LLM
```

Project名と表示名を併記する場合は、次の表記を使用する。

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

新規Docs、Handoff、README、Architecture説明では、通称を勝手に短縮・翻訳・変更せず、`Nazuna Research Governance LLM`へ統一する。

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

`docs/`以下の文書は、厳格なAppend-Only方式で管理する。

### 7.1 作成済み文書の不変性

作成済みDocsは原則として変更しない。

変更しない対象：

- 本文
- Metadata
- Status
- Link
- File名
- Timestamp
- 誤字
- 表現

誤字、Link切れ、意味を変えない修正であっても、既存Fileを直接編集せず、新しいTimestampを持つ後継Fileを作成する。

### 7.2 変更時は新規Fileを作成する

要件追加、設計変更、進捗更新、Status更新、誤記修正を行う場合は、新しい作成時刻を持つ新規Fileを作成する。

例：

```text
project_requirements_20260718174637.md
project_requirements_20260718193435.md
```

同じFile名への上書きは禁止する。

### 7.3 `supersedes`の記録

後継文書には、置換する旧文書をMetadataとして明記する。

```text
supersedes: project_requirements_20260718174637.md
```

必要に応じて複数の旧文書を参照できる。

旧文書へ`superseded`、`後継文書`等を追記しない。それ自体が旧Snapshotの改変になるためである。

旧文書の状態と後継関係は、新しい`documentation_index`側で管理する。

### 7.4 Documentation IndexもAppend-Onlyとする

`documentation_index`も上書きしない。

文書構成、最新文書、Status、後継関係が変わるたびに、新TimestampのIndexを作成する。

```text
documentation_index_20260718174637.md
documentation_index_20260718193435.md
```

古いIndexを残すことで、その時点で何が正本だったかを再現可能にする。

### 7.5 HandoffとStatusもAppend-Onlyとする

Handoff、進捗通達、担当別Statusも毎回新規Fileとして作成する。

例：

```text
common_project_handoff_YYYYMMDDHHMMSS.md
designer_status_<topic>_YYYYMMDDHHMMSS.md
implementer_status_<topic>_YYYYMMDDHHMMSS.md
external_docs_status_<topic>_YYYYMMDDHHMMSS.md
```

過去のHandoffやStatusを上書きしない。

### 7.6 新しいものを最新とする

同じ文書ID、同じ主題、同じFile Prefixに属する文書では、File名末尾のTimestampが最も新しいFileを最新とする。

```text
project_requirements_20260718174637.md
project_requirements_20260718193435.md  ← 最新
```

`documentation_index`についても、Timestampが最も新しいものを最新Indexとする。

新しい文書が古い内容へ戻すRollbackであっても、新Timestampの文書を作成する。そのため、常に「新しいものが最新」という判定を維持する。

### 7.7 古い文書を削除しない

古い文書はDevelopment ProcessとDecision Historyの一部として保持する。

原則として次を行わない。

- Delete
- Rename
- Move
- Content Rewrite
- Metadata Rewrite

例外的なHistory修復が必要な場合は、ユーザーから明示的な許可を得て、修復内容と理由を新しいIndexまたは専用History文書へ記録する。

## 8. 正本と最新の決定

最新の`documentation_index_*.md`を最初に確認する。

最新Indexは、次を管理する。

- 現在の最新文書
- 過去文書
- supersedes関係
- Current Document Set
- Historical Document Set

同じ文書系列では、Timestampが最も新しい文書を最新とする。

新規Taskは、古いIndexや古いHandoffだけを根拠に作業を開始しない。

## 8.1 Append-Onlyの必須7原則

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes`として旧Fileを明記する
4. `documentation_index`も上書きせず、新Timestampで作る
5. 古いIndexを残し、各時点の正本文書構成を再現可能にする
6. HandoffやStatusも毎回新規作成する
7. 古い文書へ`superseded`表記を追記せず、新Index側で状態を示す

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
- 既存Fileを上書きしない
- 古い文書を削除・改名・移動しない
- 古い文書へStatusや後継情報を追記しない
- 最新Indexを確認せずに作業を開始しない
- 日本語正本と英語文書の内容を無管理で分岐させない
- 古い引き継ぎ文書だけを根拠に実装しない
- 確定、暫定、未決、将来、対象外を混同しない
- ユーザー固有のSecretやCredentialをDocsへ記載しない

## 12. このSnapshotについて

この文書は、`documentation_rules_20260718174637.md`を置換し、Append-Only方式を正式な共通ルールとして追加した後継文書である。
