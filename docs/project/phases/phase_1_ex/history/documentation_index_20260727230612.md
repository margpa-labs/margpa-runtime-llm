# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727230612
state_at: 2026-07-27 23:06:12 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../current/project_continuity/project_continuity_master_ja.md
  - ../../../shared/conventions/documentation_rules_ja.md
  - ../../../shared/operations/documentation_structure_and_task_operations_ja.md
  - ../../../../public/roadmap_ja.md
supersedes: documentation_index_20260727225735.md
source: optional_english_derivative_scope_and_deferral_reservation
```

本Snapshotは[22:57:35版](documentation_index_20260727225735.md)までの全状態を継承する。

## Added Artifacts

- [任意英語派生版 Scope／延期予約 Record](operations/optional_english_derivative_scope_and_deferral_reservation_20260727230612.md)
- [Documentation Rules Before](../../../shared/history/conventions/documentation_rules_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Documentation Rules After](../../../shared/history/conventions/documentation_rules_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)
- [Documentation Structure／Task Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Documentation Structure／Task Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)
- [Project Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Project Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)
- [Public Roadmap Before](../../../../public/history/roadmap/roadmap_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Public Roadmap After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_optional_english_scope_reservation_ja_20260727230612.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_optional_english_scope_reservation_ja_20260727230612.md)

## Recorded Rule

```text
English Derivative Status:
  OPTIONAL／RESERVED／NOT CREATED

Target Stable Roots:
  docs/project/current/
  docs/project/shared/
  docs/public/

Target Documents:
  ALL NON-HISTORY *_ja STABLE DOCUMENTS

Excluded:
  docs/project/current/history/**
  docs/project/shared/history/**
  docs/public/history/**

Canonical Language:
  JAPANESE

English Granularity:
  SAME AS JAPANESE CANONICAL

Preferred Timing:
  PHASE 1-EX STAGE 6 IF CAPACITY ALLOWS

Deferral:
  LATER DATE OR EARLY PHASE 2

Phase Gate:
  NOT MANDATORY
```

## Important Decisions

- Shared Stable文書も英語派生版の対象へ追加した。
- Current／Shared／Publicの各Root以下を対象とする。
- 各Root配下の`history/`は再帰的に全件除外する。
- History Snapshot、Append-only Index、Event、Before／After原文および旧版を翻訳・Renameしない。
- 英語版は概要、短縮版または抄訳ではなく、日本語正本と同じ粒度とする。
- Stage 6に余力があれば作成する。
- 余力がなければ後日またはPhase 2前半へ延期する。
- 未作成だけを理由にPhase 1-ex、初回Commit、BackupまたはPhase 2移行を自動的に拒否しない。

## Integrity

```text
Documentation Rules:
d064baecc89635c0482e65d3abf53f02a3c0d9b7bb25c10ff2be5af724726f3b4b8b7b9929cadbf52612ff81b392f7fd9f9bb0e83ecb98ede0eec65ec1fedd4c

Documentation Structure／Task Operations:
fb952082aa10ff2873d7d2666dc930a7ec0ae27f781cac481290cb000a262370aa7b705d4ef59bfd7a9a38217217fd98de4992dfe624ef1f3a991a4d333acf80

Project Continuity Master:
11ac9fcb43c59dbb13b1cfac3426849ad31429625d22a095efe4f00fa2316c184a675afe66923580d2d5d323e29119a8a75f03a0b82395f8e07182fd345bcfa9

Public Roadmap:
095e263a242ba02fa688a14ddfc3c917b029ac1a1c0c9259f8d75c34f6140914e10b69d07f1f289f0255aaff483f77b8ea0c1a839647aed3d7b12dbae4768dd3

Phase 1-ex Index:
6a5dd7e04df94603740ca7f5c664dd8ec9f069a0a0b5ce3678795664476687ca496b92f390ec9be3be8c558e57976107e83878adad17d33d6641a4bc2f54c418

Current Documentation Index:
6747a6f2e5e9d2f3da094f5b5fcc4392a3a575b6946b0788b22da774d9524de9161f4fef60a754a2a814e95a8794bdddae66298487954efd0d2d1b0d73dd33b7

Reservation Record:
96fb644e187ee76e4b2fdf7ac6af1cab76e51f7163920df821fa78893885102c240972c66c7b436c9b03bf1d9397e5cfcb2083f14f30a829f791a1da0b8b9698
```

## Snapshot Validation

```text
Documentation Rules Stable／After:
  BYTE-FOR-BYTE MATCH

Documentation Structure／Task Operations Stable／After:
  BYTE-FOR-BYTE MATCH

Project Continuity Stable／After:
  BYTE-FOR-BYTE MATCH

Public Roadmap Stable／After:
  BYTE-FOR-BYTE MATCH

Phase Index Stable／After:
  BYTE-FOR-BYTE MATCH

Current Index Stable／After:
  BYTE-FOR-BYTE MATCH

Stable／New Record Relative Links Checked:
  306

Missing Links:
  0

Private Absolute Path／Personal Identifier／Credential Variable Scan:
  0 MATCH
```

## Boundary

本Snapshotは英語派生版の対象範囲、History除外および延期先を予約した状態を示す。

英語派生版の作成、翻訳、JA／EN同等性検証、公開またはPhase 1-ex完了を示さない。
