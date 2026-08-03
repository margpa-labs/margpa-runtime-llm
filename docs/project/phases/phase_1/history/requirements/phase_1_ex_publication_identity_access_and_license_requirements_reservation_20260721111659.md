# Phase 1-ex 公開名義・Access・License要件予約

- 文書ID: `phase_1_ex_publication_identity_access_and_license_requirements_reservation`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 親要件: [phase_1_ex_operations_reorganization_requirements_20260720231036.md](phase_1_ex_operations_reorganization_requirements_20260720231036.md)
- 公開識別情報正本: [public_identity_and_personal_information_policy_20260721111659.md](public_identity_and_personal_information_policy_20260721111659.md)
- supersedes: なし（Phase 1-ex公開移行詳細の追加予約）

## 1. Position

本書はPhase 1-exで実施する公開Repository移行、公開名義整理、License Staging、Citation／Notice作成、公開前検証の追加要件を予約する。

現在は予約段階であり、調査Command、Repository変更、Git操作、公開Artifact生成、Pushをまだ開始しない。

## 2. Public Identity

```text
Organization／Repository Owner : margpa-labs
Public Author／Research Name    : Nazuna Research
Public Repository              : https://github.com/margpa-labs/margpa-runtime-llm
Commit Author Name             : Nazuna Research
Commit Account Traceability    : 個人GitHub Accountへ辿れることを許容
```

Commit Emailは個人の実Emailを公開しない候補を優先する。GitHub提供noreply Email等により個人GitHub Accountへ帰属・リンクされることは許容する。

## 3. Two Public Access Boundaries

GitHub RepositoryとLightning AI Studio上の公開UIは、別の公開境界として扱う。

### 3.1 GitHub Repository

GitHub上のProject Source／Docsは、初期公開段階では次の方針とする。

```text
閲覧                : 許可
評価                : 許可範囲をLicenseで定義
GitHub機能上のFork  : GitHub利用規約上の権利を妨げない
その他の利用        : 明示許諾がない限り禁止
OSS                 : まだ該当しない
```

初期公開はOpen Sourceではなく、Evaluation-onlyのSource-available公開である。

「評価」の具体的範囲はPhase 1-exでLicense文面として確定する。最低限、次を明示する。

- Source閲覧
- Clone／Download／GitHub Forkの扱い
- Local実行評価の可否
- 評価に必要な一時的変更の可否
- Benchmarkと結果公開の可否
- Commercial／Production／Service利用禁止
- 再配布／再公開／Sublicense禁止
- 派生物作成／配布禁止
- AI Training／Dataset化の扱い
- Evaluation終了後の保管／削除
- Warranty／Liability Disclaimer
- 違反時の権利終了

GitHub Public RepositoryのPlatform上、利用者には閲覧とForkに関するGitHub利用規約上の権利が生じる。Project独自Licenseは、GitHub利用規約を上書きするものではなく、それ以外の追加利用権を定義・制限する。

### 3.2 Lightning Public UI

Lightning公開UIは、利用者が画面に公開された機能を自由に操作・評価できるInteractive Demoとする。

許可範囲：

- 公開UIへのAccess
- Prompt入力
- 新規Chat
- 公開された設定値の変更
- 生成／停止／再試行
- 画面へ返された結果の閲覧
- 通常利用範囲での機能評価

Lightning UIの自由利用は、次の権利を自動的に付与しない。

- GitHub Sourceの再利用／再配布
- Model Weightの取得
- 管理画面／CredentialへのAccess
- 未公開API／InfrastructureへのAccess
- Service妨害、過剰負荷、不正Access
- Projectの商用再提供

公開UIの利用条件、生成結果の扱い、Rate／Resource制約、Model由来の制約は、公開前にREADME／UI Notice／利用条件へ整理する。

## 4. License Staging

### 4.1 Initial Stage

ある程度以上完成するまで、Project Codeは独自のEvaluation-only License候補とする。

```text
Classification : Source-available／Proprietary Evaluation-only
Open Source     : No
Primary File    : LICENSE
Language        : English authoritative text候補
```

独自License文面は法的効果を持つため、公開前に専門家確認を推奨する旨を記録する。

### 4.2 Future OSS Stage

一定の完成条件を満たした後、ユーザー判断によりOSS Licenseへ変更可能とする。

OSS移行時は次を記録する。

- OSS化対象Version／Tag／Commit
- 採用License
- 過去Evaluation-only Releaseの扱い
- Contributor権利とRelicense可否
- Third-party Licenseとの整合
- License変更日
- README／NOTICE／CITATION／Package Metadata更新

OSS化を将来予定していることは、現在のEvaluation-only版へOSS権利を先行付与するものではない。

## 5. Root Public Files

Phase 1-exでは、既存予約に加えて次を公開候補として作成する。

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

### 5.1 `CITATION.cff`

```text
Language        : English
CFF Version     : 1.2.0
Author Entity   : Nazuna Research
Repository Code : https://github.com/margpa-labs/margpa-runtime-llm
License         : Custom Licenseのため架空SPDX IDを使用しない
License URL     : Public Repository内のLICENSE URL候補
```

Version／Release Date／DOIは、実在値が確定した場合だけ記載する。架空値や予定値をCitation Metadataへ入れない。

### 5.2 `NOTICE.md`

```text
Language : Japanese and English
```

最低限、次を含める。

- Project名と公開名義
- Repository Owner
- 現在のLicense Stage
- `LICENSE`が権利許諾の正本であること
- ARGD／DAGD等の個別LicenseとAttribution
- Third-party Library／Model／Artifactの権利分離
- Model WeightをRepositoryへ含めないこと
- Trademark／No Endorsement候補
- 日本語と英語の対応関係

`NOTICE.md`へLicense本文を重複させず、権利許諾の正本を`LICENSE`へ一本化する。

## 6. Component License Separation

Top-level Project Licenseを全Artifactへ一括適用しない。

最低限、次を分離する。

```text
Project-owned Source Code
Project-owned Documentation
ARGD／DAGD Definition
Third-party Governance Definition
Model Weight／Tokenizer／Config
Python Dependency
Web／UI Asset
Sample／Generated Output
```

ARGD／DAGDのCC-BY-SA-4.0、Model License、第三者Dependency License、個別AttributionをTop-level Evaluation-only Licenseで上書きしない。

## 7. Identifier Classification Rule

公開対象内の廃止済み第一者名義等を、文脈を無視して単純一括置換しない。次のClassへ分類する。

```text
repository_identity
  → margpa-labs／新Repository URL

public_author_identity
  → Nazuna Research

personal_information
  → 削除または中立化

local_environment_identifier
  → 匿名化または公開対象外

technical_account_identifier
  → 必要時のみ保持

immutable_provenance
  → 変更禁止／理由記録

third_party_identity
  → 正式表記を維持

manual_review
  → 自動変更禁止／ユーザー判断待ち
```

## 8. Phase 1-ex Required Work

Phase 1-exでは、実変更前に次を行う。

1. 公開面へ現れ得るFile／Metadata／HistoryのRead-only Inventory
2. 識別情報分類Manifest作成
3. 変更対象、変更方法、非変更理由の一覧化
4. Public AllowlistとPrivate Exclusionの確定
5. 洗浄済みPublic Exportの設計
6. License／CITATION／NOTICEのDraft設計
7. Commit Author／Email／Account帰属確認
8. PII／Secret／Path／Symlink／Binary／Model検査設計
9. Verification／Completion Gate定義
10. 実装担当向けRead-only Preflight Handoff

Read-only Preflight ReviewがAcceptedになるまで、置換、File削除、History変更、Public Export、Pushを行わない。

## 9. Migration Strategy

既存開発Treeや履歴を直接洗浄しない。原則として次の構成を優先する。

```text
Development Source／Internal Evidence
  ↓ Read-only Inventory
Classification Manifest
  ↓ Allowlist Export
Sanitized Public Staging Tree
  ↓ Validation
User／Designer Approval
  ↓ Clean Public Commit
margpa-labs/margpa-runtime-llm
```

履歴を移行する必要がある場合も、原本ではなく専用Clone／Copyを対象とする。

## 10. Verification／Completion Conditions

公開前に最低限、次をすべて満たす。

- Repository URL／Badge／Clone URLが新Repositoryを指す。
- Public Author／Maintainer名が`Nazuna Research`である。
- 廃止済み第一者名義の残存箇所が全件分類済みである。
- 本名、LinkedIn、職務経歴、個人連絡先、個人Pathがない。
- Secret／Credential／Tokenがない。
- `.venv`、Model Weight、Symlink、Cache、Local Logがない。
- LICENSE、README、NOTICE、CITATIONの表示が矛盾しない。
- `CITATION.cff`がCFF 1.2.0 Schema Validationへ合格する。
- Third-party Attribution／Licenseを保持している。
- Public Exportから環境を再構築できる。
- Test、Link Check、Archive Manifest、Hash検証が合格する。
- Commit Author Nameが`Nazuna Research`である。
- Commitから個人GitHub Accountへ辿れる可能性が許容済みDecisionと一致する。
- GitHub権利境界とLightning UI利用境界が明記されている。
- Push対象Commit／Treeをユーザーが最終確認している。

## 11. Documentation Ownership

- 設計者役／将来の設計統括者役が本要件、分類規則、Architecture、ADR、Preflight Handoffを管理する。
- 実装担当はRead-only Preflight結果とPublic Export実装Statusを新規Handoffとして記録する。
- 対外Docs役がREADME、NOTICE、CITATION、公開Docsを作成する。
- LICENSEの最終権利条件はユーザー決定を必須とする。
- Pushは専用Authorizationとユーザー最終承認を必須とする。

## 12. Authorization Boundary

本書はPhase 1-exのAccepted Reservationである。

現時点では次を行わない。

- Phase 1-ex開始
- Repository全体の識別情報走査
- 既存Fileの置換／削除／Rename
- README／LICENSE／NOTICE／CITATION生成
- Git初期化／Commit／Tag／Remote設定
- Git History書換え
- 公開RepositoryへのPush
- Lightning設定変更

これらはPhase 1-G Review、Phase 1-H、Lightning検証、Phase 1完了Gateとの順序を確認したうえで、Phase 1-ex開始指示後に実施する。

## 13. References

- GitHub Docs: [Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- GitHub Docs: [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
- GitHub Docs: [About CITATION files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- Citation File Format: [CFF 1.2.0 Schema Guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md)
- GitHub Docs: [Setting your commit email address](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- Open Source Initiative: [The Open Source Definition](https://opensource.org/osd)
