# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727225735
state_at: 2026-07-27 22:57:35 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../current/project_continuity/project_continuity_master_ja.md
  - ../../../../public/roadmap_ja.md
  - ../operations/pre_initial_commit_documentation_refresh_plan_ja.md
supersedes: documentation_index_20260727224609.md
source: phase_1_ex_revised_execution_order
```

本Snapshotは[22:46:09版](documentation_index_20260727224609.md)までの全状態を継承する。

## Added Artifacts

- [Phase 1-ex 実行順変更／Git未使用掲載境界 Record](operations/phase_1_ex_revised_execution_order_and_pre_git_publication_boundary_20260727225735.md)
- [Phase Index Before Change](operations/phase_index_phase_1_ex_before_revised_execution_order_ja_20260727225735.md)
- [Phase Index After Change](operations/phase_index_phase_1_ex_after_revised_execution_order_ja_20260727225735.md)
- [Pre-initial Commit Documentation Refresh Plan Before Change](operations/pre_initial_commit_documentation_refresh_plan_phase_1_ex_before_revised_execution_order_ja_20260727225735.md)
- [Pre-initial Commit Documentation Refresh Plan After Change](operations/pre_initial_commit_documentation_refresh_plan_phase_1_ex_after_revised_execution_order_ja_20260727225735.md)
- [Current Index Before Change](../../../current/history/index/documentation_index_phase_1_ex_before_revised_execution_order_ja_20260727225735.md)
- [Current Index After Change](../../../current/history/index/documentation_index_phase_1_ex_after_revised_execution_order_ja_20260727225735.md)
- [Project Continuity Before Change](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_revised_execution_order_ja_20260727225735.md)
- [Project Continuity After Change](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_revised_execution_order_ja_20260727225735.md)
- [Public Roadmap Before Change](../../../../public/history/roadmap/roadmap_phase_1_ex_before_revised_execution_order_ja_20260727225735.md)
- [Public Roadmap After Change](../../../../public/history/roadmap/roadmap_phase_1_ex_after_revised_execution_order_ja_20260727225735.md)

## Recorded State

```text
Active Phase:
  PHASE 1-EX／IN PROGRESS

Execution Order:
  REVISED／10 NORMALIZED STAGES

Next Stage:
  PRE-GIT GITHUB PREPARATION／DETAILED USER INSTRUCTIONS PENDING

Local Git:
  NOT INITIALIZED

Git Operation:
  NOT PERFORMED

GitHub Publication:
  NOT PERFORMED

Public Demo:
  DESIGN ACCEPTED／NOT IMPLEMENTED／NOT ANONYMOUSLY PUBLIC

Mac Documentation RAG:
  RESERVED／NOT IMPLEMENTED

Initial Commit:
  NOT CREATED

Phase 1-ex Backup:
  NOT CREATED

Phase 2:
  NOT STARTED
```

## Revised Order

1. Git未使用のGitHub掲載準備／一時掲載
2. Public Demo基盤／最終確認／匿名公開有効化
3. Mac限定簡易Documentation RAG＋External Hook
4. Git運用設計
5. Git初期化／公開Sanitation／初回Commit直前準備
6. 必要Docs再整理／Final Lossless／Design Governance Recovery更新
7. 全体Review／Test／Privacy Scan
8. 初回Commit
9. Phase 1-ex Backup
10. Phase 2

ユーザー原文の重複番号`4`は、内容と前後関係を変えず、参照用に10段階へ正規化した。

## Important Decisions

- Stage 1ではGitを使用しない。
- Stage 1の具体的な掲載手順・対象・完了条件は、ユーザーの後続指示を待つ。
- Basic認証Previewと匿名Public Demoを分離する。
- Public Demoは認証なしを予定する一方、Rate Limit、Token上限、Cost／Resource保護を必須候補とする。
- Public DemoではTool、RAGおよび外部操作を無効にする。
- Mac限定簡易RAGは将来外部環境へ接続できるHookを維持する。
- Stage 5では初回Commitをまだ作成しない。
- Stage 1掲載物、Stage 5のGitHub公開との対応およびStage 8初回Commitの関係はStage 4で確定する。
- 不明な順序境界を設計統括者役が推測で変更しない。
- 本Docs更新はGit操作、GitHub掲載、匿名公開またはPhase完了を許可しない。

## Integrity

```text
Phase 1-ex Index:
627f6d1ab2e5cefe86ce32125ffe6e1a9712200bf318d83756d6368a48365529893620e9d065fc0948b937a125f3f9bf47a0e7840fad40af82a5d7c9f91a5a14

Current Documentation Index:
19dd118340a47d1917f90690232fed5e1f9548b2b6f350e09ce39aa7bf2fef15841be72f8272b64e90040776b63cfd3215960dd5b3e28b87a82d7078185ffff2

Project Continuity Master:
92837f39f5addee652ee9ac9027afba0e1e50e43fcffd275cc1039296fbf0d7bb8f901adeb859f13e412ab5169d52bdb0f9554c9e406d0fb0509e573af811dee

Public Roadmap:
0de08f125de2eaf9fffd7ad9c132ef477e8c009ce25728cd1ddcae491a195c79a62c3a151c15534e082a1ee012d5cf18f01fb546d573bd08d99966e912b8b2b4

Pre-initial Commit Documentation Refresh Plan:
b70bd9ca2acb3dc37f83d8a55ce50abaa903f127efc6792c84a1785d00cf17da023f8460122e8c6238c032d13abf4f0cf2739189788e4c34e47f39bd8a448607

Execution Order Record:
5797fd9bc319a53e777449ae7d4bf875bae325ae890e859d1355cee066f60cf054347eb4fa1b1ba9d5537e572c6bfd5042925e9a456e35a785cb40a622a140a2
```

## Snapshot Validation

```text
Phase Index Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Current Index Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Project Continuity Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Public Roadmap Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Pre-initial Commit Plan Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Stable／New Record Relative Links Checked:
  294

Missing Links:
  0

Private Absolute Path／Personal Identifier／Credential Variable Scan:
  0 MATCH
```

## Boundary

本Snapshotは、Phase 1-exの残工程順変更と、Git未使用一時掲載／後段Git運用の境界を記録した時点を示す。

GitHub掲載準備、GitHub掲載、Public Demo実装、匿名公開、Mac簡易RAG、Git設計、Git初期化、初回Commit、Phase 1-ex BackupまたはPhase 2を完了状態へ変更しない。
