# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260801154412
state_at: 2026-08-01 15:44:12 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260801113340.md
  - architecture/lightning_documentation_rag_deployment_snapshot_follow_up_architecture_20260801154412.md
  - operations/documentation_rag_manual_test_3_and_lightning_recovery_findings_20260801154412.md
  - handoffs/designer_review_phase_1_ex_documentation_rag_cross_environment_manual_acceptance_20260801154412.md
  - ../../../shared/operations/runtime_deployment_snapshot_policy_ja.md
  - ../../../shared/history/operations/runtime_deployment_snapshot_policy_phase_1_ex_ja_20260801154412.md
  - operations/roadmap_documentation_rag_cross_environment_acceptance_update_20260801154412.md
  - ../../../../public/roadmap_ja.md
  - ../../../../public/history/roadmap/roadmap_phase_1_ex_before_documentation_rag_cross_environment_acceptance_ja_20260801154412.md
  - ../../../../public/history/roadmap/roadmap_phase_1_ex_after_documentation_rag_cross_environment_acceptance_ja_20260801154412.md
supersedes: documentation_index_20260801113340.md
source: documentation_rag_cross_environment_manual_acceptance_and_runtime_deployment_snapshot_recovery
```

本Snapshotは[2026-08-01 11:33:40版](documentation_index_20260801113340.md)までの全状態を継承し、Documentation RAG第3回手動Test、Lightning Runtime復旧、Cross-environment Manual Acceptance、Runtime Deployment Snapshot運用方針およびRoadmap更新をAppend-onlyで追加する。

旧Requirements、Architecture、ADR、Handoff、Status、Review、Evidence、Roadmap SnapshotおよびIndexは各時点の判断を示すHistoryとして保持し、編集または削除しない。Phase Index Stableは変更していない。

## 1. Final Functional Decision for Phase 1-ex Documentation RAG

- [Cross-environment Manual Acceptance Review](handoffs/designer_review_phase_1_ex_documentation_rag_cross_environment_manual_acceptance_20260801154412.md)
- [第3回Manual Test／Lightning Recovery Findings](operations/documentation_rag_manual_test_3_and_lightning_recovery_findings_20260801154412.md)

```text
Mac Local Documentation RAG:
  ACCEPTED

Lightning Basic Preview Public-doc RAG:
  ACCEPTED

Lightning Public Demo Public-doc RAG:
  ACCEPTED

Public 8-doc Corpus Boundary:
  ACCEPTED

Cross-environment Adapter Hook:
  COMPLETE

Answer Quality:
  KNOWN LIMITATIONS／FUTURE TUNING

Phase 7 Full RAG:
  NOT IMPLEMENTED／NOT CLAIMED
```

RAG Adapter、ON／OFF、Corpus境界、Retrieval、CitationおよびCross-environment動作は完了とする。軽量ModelとLexical Retrievalの回答品質は別課題であり、今回の完了宣言へ正確性保証を含めない。

## 2. Lightning Recovery Evidence

最初の配置では、最新実装差分が前提とするMac Documentation RAG基盤Sourceと、Lightning側Baselineが一致していなかった。

```text
Observed:
  missing adapter module
  old web contract
  mixed config contract
  uploaded shell permission loss

Recovery:
  coherent src／config／scripts／tests snapshot
  project metadata synchronization
  bounded shell permission restoration
  import smoke
  focused tests
```

復旧後Evidence：

```text
SCRIPT_PERMISSION_EXIT:
  0

COHERENT_RUNTIME_IMPORT_OK:
  PASS

WEB_IMPORT_OK:
  PASS

RAG_INTEGRATION_IMPORT_OK:
  PASS

RAG_TEST_PLACEMENT_EXIT:
  0

Focused RAG／Web／Runtime:
  185 passed
  1 skipped
  29.49s

Web Integration:
  28 passed
  0.75s

Lightning Public／Basic auto-start and RAG:
  PASS
```

Node.js不在によるStatic Web Security Contract 1 Skipは明示されており、Python Runtime AcceptanceをBlockしない。

## 3. Runtime Deployment Snapshot Policy

- [Stable Runtime Deployment Snapshot運用方針](../../../shared/operations/runtime_deployment_snapshot_policy_ja.md)
- [Initial History Snapshot](../../../shared/history/operations/runtime_deployment_snapshot_policy_phase_1_ex_ja_20260801154412.md)
- [Lightning Follow-up Architecture](architecture/lightning_documentation_rag_deployment_snapshot_follow_up_architecture_20260801154412.md)

```text
Verified same baseline:
  bounded delta may be used

Unknown baseline／multiple phases behind／cross-layer feature:
  coherent runtime deployment snapshot has high priority
```

標準Runtime Deployment単位は`src／config／scripts／tests／pyproject.toml／uv.lock／.python-version`とする。`.venv`、Model、Cache、Secret、Private Bootstrap、Allowlist外Docsおよび利用者Dataは無条件に含めない。

本方針は「常に全Artifactを上書きする」規則ではなく、Baseline不一致と調査Costが大きい場合に高優先度で選択する運用判断である。

## 4. Roadmap Update

- [Roadmap Stable](../../../../public/roadmap_ja.md)
- [Roadmap Before Snapshot](../../../../public/history/roadmap/roadmap_phase_1_ex_before_documentation_rag_cross_environment_acceptance_ja_20260801154412.md)
- [Roadmap After Snapshot](../../../../public/history/roadmap/roadmap_phase_1_ex_after_documentation_rag_cross_environment_acceptance_ja_20260801154412.md)
- [Roadmap Update Record](operations/roadmap_documentation_rag_cross_environment_acceptance_update_20260801154412.md)

Roadmapへ次を反映した。

- Gitを使用しないGitHub直接掲載完了
- 認証なしPublic Demo Surface完了
- Basic／Public Traffic-aware Auto-start成立
- Mac／Lightning Documentation RAG完了
- 公開8文書Corpus境界
- RAG回答品質は後続Tuning
- Phase 1-exの次工程はGit運用設計

Overview、Concept、README、Current、Project Continuityおよび英語派生版の全面更新はPhase 1-ex終盤まで保留している。

## 5. Integrity

```text
Previous Documentation Index:
  3b3614dba755bb4d6ca795f583e58ac641692b985ad958ce058a380c1fcd57c0b81673cc30e8530132e6c755467fb13ddcc8e3c4a93402f9cdc0c31fee240a4f

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Manual Findings:
  d4f91b7daa2062e04cd82f9f60941d08c015668c03588def63c4794067660e4faa3dfcfa17fd3d782700d806b072b5686ec94aafb2a2fd4abaf96a6a59453d4f

Designer Review:
  85285b4b8c6370238259ea33ef407965b820d121220565d9f9d8d01c807456d4db43e7b1e5daf22ac17815e41dd45077918d24b3b63b513e9ba0ed8a035df04e

Deployment Architecture:
  bd0efaaeb4958de8ef0a19eb9e389fd81837e8ba511a3289292c2cffc233fcabab6c50c3e4bd7fbca7ca76e8629d52811415d1b0e14fbece8a59fbdd6a47f479

Deployment Policy Stable／History:
  3db350d7cbff6caba1b952049ea6c54edb30a3f22b9fff2a0144d45ab15c9b506649f3dfe7b88f307c957ebce7ecb83fcb86a2a71071fc661ad529ad888b2669

Roadmap Before:
  7ef57196d6c0a4c02ecdb26bc22484c4e0fe345e72795a9f546b0fbba34bc6aba9d29682c4c9b58859e3127519b8ed19bd16e61a96504f44d792ca18de864884

Roadmap Stable／After:
  f8e0c05ef74e5bcea8db28984c0dd25938ea8634716d94be5b03c8ad656c320607d919d814e32297ab47add2a1039c376cb3d69ebd57e7bc739a5772c307cec4
```

## 6. Mutation Boundary

```text
Source／Config／Script／Test Mutation in Local Project:
  NONE

Model／Lightning／API Builder／Git／GitHub Operation by Designer:
  NONE

Phase Index Mutation:
  NONE

Existing History Mutation:
  NONE

Stable Updated:
  docs/public/roadmap_ja.md

Stable Added:
  runtime_deployment_snapshot_policy_ja.md

Append-only Added:
  Manual Findings
  Follow-up Architecture
  Designer Review
  Roadmap Before／After Snapshot
  Shared Policy History Snapshot
  Roadmap Update Record
  Documentation Index Snapshot
```

## 7. Next Gate

Phase 1-exの次工程はGit運用設計である。

```text
Next:
  Branch／Tag／Commit rules
  Author／Email
  Remote／Public Repository
  Backup／Phase relationship

Not yet authorized:
  git init
  first commit
  history rewrite
  remote push
```

Git運用設計のAccepted後、Git初期化／公開Sanitationを初回Commit直前まで進める。
