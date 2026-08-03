# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721111659.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Machine-safe Slug                     : nazuna-research
Naming Exception Authority            : 設計者役Task Only
Approved Naming Exceptions            : None
Deprecated Name Match in docs/        : 0／Pass
Public Repository Owner               : margpa-labs
Public Repository                     : margpa-labs/margpa-runtime-llm
Commit Link to Personal Account       : Allowed
Phase 1-G Minimal Web Surface          : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Waiting Phase 1-G Review
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721111659.md](documentation_index_20260721111659.md)から継承する。

本Snapshotでは、`docs/`内の廃止済み第一者名義をPrivacy Exceptionにより直接洗浄し、表示名を`Nazuna Research`へ統一した。

## 3. Replaced／Superseded Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical_scrubbed | [documentation_index_20260721111659.md](documentation_index_20260721111659.md) | 本文書 |
| superseded | [common_public_identity_and_naming_rule_20260721111659.md](handoffs/common_public_identity_and_naming_rule_20260721111659.md) | [common_public_identity_and_naming_rule_20260721112925.md](handoffs/common_public_identity_and_naming_rule_20260721112925.md) |

既存の[公開識別子・個人情報取扱方針](requirements/public_identity_and_personal_information_policy_20260721111659.md)は、Privacy Exceptionにより実値を除去した状態で継続する。名義例外なしの最新Decisionは本Snapshotの追加正本を優先する。

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_mandatory | [公開名義・名称の統一決定](requirements/public_identity_and_naming_decision_20260721112925.md) | `Nazuna Research`への例外なし統一 |
| current_common_rule | [共通公開名義・名称規則](handoffs/common_public_identity_and_naming_rule_20260721112925.md) | 全担当Task向け必須規則 |
| completed | [Docs公開名義洗浄Report](operations/public_identity_docs_scrub_report_20260721112925.md) | 直接洗浄範囲・変換・ゼロ件検証 |

## 5. Naming Rule

```text
Human-readable First-party Name : Nazuna Research
Project Internal Name           : Nazuna Research Governance LLM
Machine-safe Slug               : nazuna-research
```

別の第一者識別子をDocsへ記録する必要性は、設計者役Taskだけが判断できる。現時点の承認済み例外はない。

他の担当Taskは、実値を再挿入せず設計者役TaskへEscalateする。

## 6. Privacy Scrub Result

```text
Target Root        : docs/
Initial Occurrence : 67
Initial Files      : 32
Final Occurrence   : 0
Result             : PASS
```

Historical Docsを直接変更したため、対象Fileの過去Size／Digestは現在内容のEvidenceとして使用しない。Phase 1-exで公開候補ArtifactのManifestとDigestを再生成する。

## 7. Commit Attribution

Commit Author Nameは`Nazuna Research`とする。Commitから個人GitHub Accountへ辿れることは許容するが、Account Handleや個人EmailをDocsへ記録しない。

## 8. Immediate Next Gate

[Phase 1-G実装担当Status](handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)と関連RepositoryをReviewする。

Review後は新TimestampのDesigner ReviewとDocumentation Indexを一緒に作成する。

## 9. Authorization Boundary

今回許可された変更は`docs/`内の名義洗浄と正本更新までである。

次はまだ行わない。

- `src/`、`tests/`、`scripts/`、`config/`、Root Metadataの識別情報洗浄
- Git設定変更／Git初期化／Commit／Push
- README／LICENSE／NOTICE／CITATION生成
- Phase 1-ex開始
- Phase 1-H実装
- Lightning Full Upload
- Backup

## 10. Append-only／Privacy Exception

新しいDecision、Common Rule、Scrub Report、IndexはAppend-onlyで追加した。既存32文書の該当箇所は、公開識別情報洗浄を優先するPrivacy Exceptionとして直接変更した。
