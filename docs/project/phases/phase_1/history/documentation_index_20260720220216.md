# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719202333.md`

## 1. Current Position

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
User Acceptance                : Waiting
Backup                         : Not Triggered
Publication                    : Planned／Not Authorized
Privacy Scrub                  : Complete for managed files
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260719202333.md](documentation_index_20260719202333.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_rules_20260719171836.md](requirements/documentation_rules_20260719171836.md) | [documentation_rules_20260720220216.md](requirements/documentation_rules_20260720220216.md) |
| historical | [common_project_handoff_20260719202333.md](handoffs/common_project_handoff_20260719202333.md) | [common_project_handoff_20260720220216.md](handoffs/common_project_handoff_20260720220216.md) |
| historical | [documentation_index_20260719202333.md](documentation_index_20260719202333.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [public_identity_and_personal_information_policy_20260720220216.md](requirements/public_identity_and_personal_information_policy_20260720220216.md) | 第一者公開Identityと個人情報の正本方針 |
| complete | [publication_privacy_scrub_report_20260720220216.md](operations/publication_privacy_scrub_report_20260720220216.md) | 管理対象FileのPrivacy Scrub記録 |
| reported | [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md) | Phase 1-F Repository実装報告／未Review |

## 5. Privacy Exception Record

ユーザーの明示指示に基づき、Privacy／Securityを優先して既存管理対象Docs内の第一者旧Identityと個人固有Pathを匿名化した。

このため一部のHistorical Snapshotは作成時のBit列と一致しない。削除情報は復元せず、設計内容とDecision履歴を保持する。

## 6. Public Identity

```text
Nazuna Research
```

第一者の作者、設計者、開発者、Maintainer等の公開固有名は上記へ統一する。第三者のModel、Library、Repository、License等の正式名称は保持する。

## 7. Next Gate

```text
Phase 1-F Independent Review
  → Lightning Upload Scope確定
  → CUDA Native Verification
  → CPU Verification／Disposition
  → Current User Manual
  → User Acceptance + Designer Completion Declaration
  → Backup
  → Publication Preparation
```

## 8. Authorization Boundary

本IndexはSource／Config変更、Lightning操作、Git／GitHub操作、Backup、公開、Phase 1-F Acceptance、Phase 1-G実装を許可しない。

## 9. Append-Only

新規方針文書は新Timestampで作成した。既存Docsの匿名化だけはPrivacy／Security例外として直接適用した。
