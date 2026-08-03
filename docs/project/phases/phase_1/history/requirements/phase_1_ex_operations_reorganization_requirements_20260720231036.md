# Phase 1-ex 運用再整備 要件

- 文書ID: `phase_1_ex_operations_reorganization_requirements`
- 状態: `accepted_reservation_requirements_incomplete`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- ADR: [ADR-0017](../adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md)
- supersedes: `phase_1_ex_operations_reorganization_requirements_20260720222402.md`

## 1. Phase Identity

```text
Phase ID : Phase 1-ex
Name     : 運用再整備
Position : Phase 1機能確定後／初回GitHub公開前
State    : Added／Accepted Reservation／Not Started
```

## 2. Current Non-execution Rule

Phase 1-ex開始指示までは、現在の設計者役、Docs Authority、Append-Only Rule、Directory Structure、Git未導入状態を維持する。

現時点で次を行わない。

- 設計統括者役への変更
- 新しいPhase設計者Taskの作成
- Git初期化／Commit／Remote／Push
- Docs Directory変更／File移動／Rename
- Write Authority変更
- 各担当Taskへの構造変更通知
- Lossless Compilation実行
- README／LICENSE／Public Docs生成

## 3. Role／Authority Reorganization

Phase 1-exで次の役割を再整理する。

- 設計統括者役
- 設計者役
- 実装者役
- 対外Docs役

対象：

- DirectoryごとのWrite Authority
- Read-only範囲
- Handoff／Status／Review／Index Ownership
- Phase開始／完了Gate
- Cross-Phase Escalation
- Public Docs／Lossless Compilation Ownership
- Git操作権限
- Backup／Release操作権限

現設計者役を設計統括者役へ変更するのはPhase 1-exの実行項目であり、現在はまだ設計者役とする。

## 4. Phase Design Delegation

Phase 1-ex完了後、必要に応じてPhaseごとに専用設計者役を配置する。

設計統括者役がPhase単位の上位設計、制約、受入境界、Handoffを渡す。Phase設計者役は、ユーザー要求またはEvidenceによる仕様変更を含め、上位設計から大きく外れない範囲で詳細を再設計できる。

Cross-Phase影響、共通Architecture、Accepted Policy変更はEscalation対象とする。

## 5. Git Transition

Phase 1-exからGit運用へ変更する。

要件定義対象：

- Repository初期化Point
- Initial Commit Scope
- Branch Strategy
- Commit Granularity／Message
- Phase Tag／Release
- Backup Snapshotとの対応
- Dirty State Gate
- Remote／Visibility
- Git Author／Committer Privacy
- Secret Scan／Ignore
- Rollback／Restore
- Docs HistoryとGit Historyの役割分担

初回GitHub公開はPhase 1-ex完了後とする。以後は原則、各Phaseのテスト、Docs、Final Gate、Backup確定後に同一SnapshotをGitHubへ反映する。

## 6. Docs Operating Model

Git運用次第で、これまで新Timestampで作成してきたDocsをPhase単位で1Fileへ再整理する。

必要条件：

- 公開して問題ない
- 新Taskが即引き継げる
- 原文の意味、Decision、Boundaryを変えない
- 運用／共通ルール／Handoff等はLossless
- Source InventoryとHashを持つ
- Current／Historical／Conflictingを外部Metadataで示す
- Public Derived DocsとCanonical Compilationを分離する

詳細は[Lossless Compilation要件](lossless_phase_document_compilation_requirements_20260720231036.md)を正本とする。

## 7. Docs Directory Migration

Phase 1-exで`docs/`の新Directory構造を設計し、Migration Plan、対象Inventory、Link更新、Validation、Rollbackを定義してから変更する。

変更完了後、各担当Taskへ新構造と権限を通知する。移行途中に新旧Pathを暗黙併用しない。

## 8. Public Docs

対外Docs役がPhase完了単位、テスト完了後、Backup前に作成または更新する。

```text
README.md
LICENSE
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

- Docsはすべて日本語
- README本文は敬語
- README末尾にEnglish Abstract
- READMEへ実在するLightning公開サイトURL
- LICENSEは英語公式原文を許容
- その他は研究文書風の日本語
- 将来`*_en.md`を追加可能だが現在は要求しない

## 9. Phase-end Sequence

```text
Implementation／Test完了
  → Phase Review
  → Lossless Phase Compilation
  → Public Derived Docs作成・更新
  → Privacy／License／Integrity Review
  → User Acceptance／Designer Final Gate
  → Backup Candidate／Sanitation／確定
  → Git Commit／Tag／GitHub反映
```

詳細なGate順序は既存Backup Policyと整合させ、Phase 1-exで最終確定する。

## 10. Remaining Definition Items

- Git Strategyの詳細
- Final Docs Directory Tree
- Current／Historical正本関係
- Lossless Compilation File Format／Script
- Public／Internal Source Set境界
- Project Code License
- README Template
- Phase Summary Template
- CI／Secret Scan／Link Check
- Migration Test／Rollback
- Phase 1-ex User Manual／Acceptance Criteria
- Phase 1-Gとの順序

## 11. Completion Gate

未定義項目がAcceptedになり、Role、Git、Docs、Migration、Compilation、Public Docs、Backup、Notification、Rollbackの検証が完了するまでPhase 1-ex完了を宣言しない。

## 12. Authorization Boundary

本書は要件予約を記録する。Phase 1-exの実行、Role変更、Task作成、Git操作、Directory変更、Docs統合、Public Docs生成、各担当通知、GitHub公開をまだ許可しない。

