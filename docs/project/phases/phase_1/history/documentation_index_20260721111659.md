# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721093952.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research
Public Repository Owner               : margpa-labs
Public Repository                     : margpa-labs/margpa-runtime-llm
Commit Link to Personal GitHub Account : Allowed
GitHub Initial License Stage           : Evaluation-only Source-available／Reserved
Lightning Public UI Access             : Exposed Functions Freely Usable／Reserved
Phase 1-A～1-E                         : Accepted
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Phase 1-F Lightning Native Gate        : Not Run／Not Complete
Phase 1-G Minimal Web Surface          : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Accepted Reservation／Waiting Phase 1-G Review
Lightning Full Upload                  : Deferred until Phase 1-H Mac Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721093952.md](documentation_index_20260721093952.md)から継承する。

本Snapshotでは、旧第一者名義規則を`Nazuna Research`中心の新規則へ置き換え、Phase 1-exのGitHub／Lightning Access境界、License Staging、CITATION／NOTICE、Commit帰属許容を追加した。

Phase 1-Gについては[実装担当Status](handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)の存在を確認したが、本Snapshotでは内容Reviewを行っていない。したがってAcceptedではなく`Review Pending`である。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721093952.md](documentation_index_20260721093952.md) | 本文書 |
| superseded | [public_identity_and_personal_information_policy_20260720220216.md](requirements/public_identity_and_personal_information_policy_20260720220216.md) | [public_identity_and_personal_information_policy_20260721111659.md](requirements/public_identity_and_personal_information_policy_20260721111659.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [公開識別子・個人情報取扱方針](requirements/public_identity_and_personal_information_policy_20260721111659.md) | `Nazuna Research`中心の公開名義正本 |
| accepted_reservation | [Phase 1-ex 公開名義・Access・License要件予約](requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md) | GitHub／Lightning境界、License、CITATION、NOTICE、公開移行 |
| current_common_rule | [共通公開名義・名称規則](handoffs/common_public_identity_and_naming_rule_20260721111659.md) | 全担当Taskが使用する短い共通規則 |

## 5. Current Identity Rule

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Repository Owner             : margpa-labs
Repository URL               : https://github.com/margpa-labs/margpa-runtime-llm
```

第一者の公開名義は例外なく`Nazuna Research`とする。GitHub Account Handleやnoreply Commit Email等の技術識別子を文書化する必要性は、設計者役Taskだけが判断する。

Commitから個人GitHub Accountへ辿れることは許容する。個人情報をSource／Docsへ追加掲載する許可ではない。

## 6. Public Access Boundary

### GitHub

初期公開は閲覧・評価限定のSource-available公開とし、OSSとは表示しない。GitHub利用規約上の閲覧／Forkを妨げず、それ以外の権利を独自Evaluation-only Licenseで定義する。

### Lightning

Lightning公開UIは、画面へ公開した通常機能を利用者が自由に操作・評価できるDemoとする。これはGitHub Sourceの再利用権、Model Weight取得権、管理権限を付与するものではない。

## 7. Phase 1-ex Public File Reservation

```text
README.md
LICENSE
CITATION.cff                  # English
NOTICE.md                     # Japanese／English
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

`CITATION.cff`はAuthor Entityを`Nazuna Research`とし、Custom Licenseを架空SPDX IDとして記載しない。必要時は`license-url`で`LICENSE`を参照する。

## 8. Immediate Next Gate

Phase 1-G実装担当Statusと関連RepositoryをReviewする。

Review後は、既存運用規則どおり新Timestampで次を一緒に作成する。

```text
docs/handoffs/designer_review_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
docs/documentation_index_YYYYMMDDHHMMSS.md
```

Phase 1-G Accepted前にPhase 1-Hへ着手しない。

## 9. Phase 1-ex Deferred Work

- 公開対象のRead-only Inventory
- 識別情報分類Manifest
- 洗浄済みPublic Export設計
- Evaluation-only License具体文面
- `CITATION.cff`／`NOTICE.md`作成
- Commit Author／Email設定
- PII／Secret／Path／Symlink／Binary検証
- 実装担当向けRead-only Preflight Handoff
- Public Repositoryへの初回Commit／Push

## 10. Authorization Boundary

本Snapshotで即時適用するのは、今後新規作成する内容における`Nazuna Research`の名義規則だけである。

次はまだ許可しない。

- Phase 1-ex開始
- 既存Repository全体の識別情報走査
- 既存Fileの一括置換／削除／Rename
- README／LICENSE／NOTICE／CITATION生成
- Git設定変更／Git初期化／Commit／Tag
- Git History書換え
- GitHub Push
- Lightning設定変更
- Phase 1-H実装
- Backup

## 11. Append-Only

既存Docsを編集せず、新TimestampのPolicy、Phase 1-ex Reservation、Common Rule、Indexとして追加した。新しいPolicyが旧第一者名義Policyを明示的にSupersedeする。
