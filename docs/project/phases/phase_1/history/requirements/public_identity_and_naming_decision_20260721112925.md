# 公開名義・名称の統一決定

- 文書ID: `public_identity_and_naming_decision`
- 状態: `current_mandatory`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 関連方針: [public_identity_and_personal_information_policy_20260721111659.md](public_identity_and_personal_information_policy_20260721111659.md)
- supersedes: なし（公開名義の例外なし統一を確定する追加正本）

## 1. Mandatory Decision

今後使用する第一者の名義、名称、作者名、研究名義、Maintainer表示名、研究主体名は、すべて次へ統一する。

```text
Nazuna Research
```

現在、別の第一者名義をDocsへ残す承認済み例外はない。

## 2. Decision Authority

`Nazuna Research`以外の第一者識別子を使用する技術的必要性は、本Projectの設計者役Taskだけが判断できる。

他の担当Taskは、次を行わない。

- 独自判断による旧名義の復元
- 外部Account HandleのDocsへの追加
- 作者名の短縮、翻訳、別名化
- 歴史説明を理由とした廃止済み名義の再掲
- Source／Docs／Metadataへの例外追加

必要性が疑われる場合は、実値を書かずに設計者役TaskへEscalateする。

## 3. Fixed Public Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
Repository Organization      : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

## 4. Machine-safe Slug

Spaceを使用できないPackage ID、Namespace、Directory例等では、次のMachine-safe Slugを使用できる。

```text
nazuna-research
```

これは別名義ではなく、`Nazuna Research`を機械識別子へ正規化した表現である。

例：

```text
nazuna-research.margpa
nazuna-research_domain_extensions
```

## 5. Commit Traceability

Commit Author Nameは`Nazuna Research`とする。

Commit Metadataから個人GitHub Accountへ辿れることは許容する。ただし、Account Handleや個人EmailをDocsへ記載する必要性は別問題であり、現時点では記載しない。

## 6. Documentation Requirement

- 新規Docsでは`Nazuna Research`を使用する。
- Historical Docsを公開候補へ含める場合も、第一者名義を`Nazuna Research`へ統一する。
- 廃止済み名義を移行説明や検索結果としてDocsへ再掲しない。
- Scrub Reportは削除対象の実値を記録しない。
- 全担当向けCommon RuleとDocumentation Indexは本Decisionを参照する。

## 7. Current Verification State

2026-07-21 11:29:25 JST時点で、`docs/`全体の廃止済み第一者名義に対するCase-insensitive Search結果は0件である。

Machine-safe Slugは、必要なGovernance Package／Namespace例にだけ存在する。

## 8. Authorization Boundary

本書は名義規則を即時適用する。

本書だけではSource、Config、Git Metadata、Remote Repository、GitHub Account設定の変更を許可しない。`docs/`以外の公開識別情報洗浄は、Phase 1-exのPreflight、Review、専用Handoff後に実施する。

