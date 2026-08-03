# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727131830
state_at: 2026-07-27 13:18:30 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../../../README.md
  - ../../../shared/conventions/documentation_rules_ja.md
supersedes: documentation_index_20260727125834.md
source: readme_required_elements_and_document_responsibility_rules
```

本Snapshotは[12:58:34版](documentation_index_20260727125834.md)までの全状態を継承する。

## Added／Changed Artifacts

- [README Stable](../../../../../README.md)
- [Documentation Rules Stable](../../../shared/conventions/documentation_rules_ja.md)
- [README Before Restoration](operations/readme_before_required_elements_restoration_20260727131258.md)
- [README After Restoration](operations/readme_after_required_elements_restoration_20260727131419.md)
- [Documentation Rules Before](../../../shared/history/conventions/documentation_rules_phase_1_ex_before_document_responsibility_rules_ja_20260727131258.md)
- [Documentation Rules After](../../../shared/history/conventions/documentation_rules_phase_1_ex_after_document_responsibility_rules_ja_20260727131419.md)
- [Change Record](operations/readme_required_elements_and_document_responsibility_rules_20260727131445.md)
- [Current Index Before Change](../../../current/history/index/documentation_index_phase_1_ex_before_readme_required_elements_and_responsibility_rules_ja_20260727131434.md)
- [Current Index After Change](../../../current/history/index/documentation_index_phase_1_ex_after_readme_required_elements_and_responsibility_rules_ja_20260727131715.md)
- [Phase Index Before Change](operations/phase_index_before_readme_required_elements_and_responsibility_rules_20260727131434.md)
- [Phase Index After Change](operations/phase_index_after_readme_required_elements_and_responsibility_rules_20260727131715.md)

## README Required Elements

READMEへ、入口文書として必要な次の要素を簡潔に戻した。

- Projectの中核的特徴
- Research Preview／Open Source状態
- Model Weight非同梱
- 第三者Artifactの独立した利用条件
- LLM出力上の注意
- 一切の保証を行わないこと
- 文書内容が変更される可能性
- RoadmapおよびLegal正本への導線

READMEへ次の文を明記した。

> 各文書は修正する必要性があるため、都度内容が変更される可能性があります。

個別実行環境、Hardware、Model配置、Setup、CLI、Server操作、External Service操作および未搭載機能の詳細はREADMEへ戻していない。

## Document Responsibility Separation

Shared Documentation Rulesへ、各文書の対象読者、役割、正本範囲、必須要素、記載しない詳細および参照先を作成前に確定する規則を追加した。

次の責務を個別に明文化した。

- README
- Public Overview
- Public Concept
- Public Roadmap
- Current Canonical
- Phase Index／Phase Requirements／Architecture／ADR
- Operations／Evidence
- User Manual
- Handoff／Status／Review

また、必要な短い重複と、責務を越えた詳細複製を区別するReview Checklistを追加した。

## Integrity

```text
README:
862f252417ed1154d7262ee5694cf918bcf41789b7df13681085512384d0f603b486f1db9886c231f7bf80d57dc4350b7c1919aa475eca6b3d7d128337ed2571

Documentation Rules:
a5237b48480768c7a1b018e47c5cc85bb5e78dd9d6cf82ed10bd593b3099c748bb2dbf226a62585f845b2a80e4ef1f8b589e217bfacf121bdc8c0743b8d3d0ff

Current Documentation Index:
5f24a297f834b792e773303ea242efb18c33756a55ca576853dcd93962940a161c01d72b7aff8055e196745e073f7ecc580e7437b69df28beeb25265538d8242

Phase 1-ex Index:
be73918927f765bd9eece8e9e7246f5dd1b3a06243de49242cc7181307267dab834f2ca055418fe6468414e545516edc11ac681898e98f8b5a94a444359cbec0

Change Record:
aeafb3e57f1026fb88195588fbeceb92ecaaaca7613b0b19fd0fbdaa88b3f2a63cfdbed9e498b416f22db19aac0b4045478f2a8a574f671de8e717e009f45c8e
```

## Validation

```text
README Required Elements                : pass
Requested Documentation Change Notice   : pass
README Detailed Environment／Commands   : absent
Documentation Responsibility Rules      : pass
Relative Links Checked                  : 274
Missing Links                           : 0
Old Identity／Private Path               : 0
Stable／After Snapshot Match             : pass
.DS_Store                               : 0
```

## Boundary

本更新はREADMEの必須要素復元とDocs作成Ruleの明文化である。Public Overview、Concept、Roadmap、Current Canonical、実装、Phase状態、Git、Public Demo、RAG、Final Lossless、Final ReviewまたはBackupの状態を変更しない。
