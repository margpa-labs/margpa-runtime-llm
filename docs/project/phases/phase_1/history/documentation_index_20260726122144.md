# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_phase_1_backup_complete`
- 作成日時: `2026-07-26 12:21:44 JST`
- 更新日時: `2026-07-26 12:21:44 JST`
- Snapshot: `20260726122144`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726121346.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Lightning Pure CPU Runtime                 : Accepted
Mac／Lightning Full Repository Suite       : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Backup                             : Complete／Verified
Git／GitHub                                : Not Started
Phase 1-ex                                 : Ready／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726121346.md](documentation_index_20260726121346.md)を継承する。

Phase 1確定Backup SetをProject Root外へ保存し、Archive、Manifest、ReceiptのSHA-512、Temporary Restore、Inventory、全File Hash、PrivacyおよびSecret Scanを検証した。

## 3. Phase 1 Backup Record

[phase_1_backup_completion_record_20260726122144.md](operations/phase_1_backup_completion_record_20260726122144.md)

```text
Backup Snapshot : 20260726121941
File Count      : 422
Archive Size    : 1,377,193 bytes
Archive SHA-512 : 9eaabdee62a36e072df5d990d68e9986ca34b2894f8d6212ac3db4c26c85b2947be6052e0b4bbace2575f774a28eb1694a8e6a846330d6b1c307b75d6931b483
Restore         : PASS
```

## 4. Backup Input Index

[documentation_index_20260726121346.md](documentation_index_20260726121346.md)

Backup Archiveには入力Indexまでが含まれる。本Backup完了記録と本IndexはDetached Post-backup Evidenceであり、次回BackupまたはGit Historyへ引き継ぐ。

## 5. Phase 1 Finalization

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

## 6. Phase 1-ex Current Requirements

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

Current Sequence：

```text
1. Lightning Auto-start Read-only Preflight
2. Git運用設計
3. Git公開準備
4. docs/構造再設計
5. 全担当Taskへ通知
6. Lossless Docs再整理
7. Canonical／公開Docs
8. Mac限定簡易RAG
9. Review／Test／Privacy Scan
10. Initial Commit／Tag／Phase 1-ex Backup
11. GitHub公開
```

## 7. Current Public Demo Decision

```text
Current Preview            : Basic認証を維持
Personal Contact in Repo   : 掲載しない
README                     : 「将来、Public Demo方式も検討しています。」
Public Demo Guard          : Future
Traffic-aware Auto-start   : Phase 1-ex早期Preflight
```

## 8. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

## 9. Authorization Boundary

Phase 1確定Backupは完了した。

次はまだ開始していない。

- Phase 1-ex変更
- Lightning Auto-start Preflight／設定変更
- Git初期化、Commit、Tag、Remote、Push
- Docs Directory Migration
- Canonical Docs生成
- Simple RAG実装
- GitHub公開

## 10. Append-Only

旧Index、Backup入力IndexおよびDetached Backup Evidenceを保持する。本IndexをPhase 1 Backup完了後の最新入口とする。
