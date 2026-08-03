# README Required Elements／Document Responsibility Rules

```yaml
document_id: readme_required_elements_and_document_responsibility_rules
status: completed
phase: phase_1_ex
created_at: 2026-07-27 13:14:45 JST
owner: 設計統括者役
targets:
  - README.md
  - docs/project/shared/conventions/documentation_rules_ja.md
trigger: user_required_restoration_and_rule_formalization
```

## Purpose

READMEの責務是正時に削りすぎた必須要素を戻し、上位文書と下位文書の責務をShared Documentation Rulesへ正式に固定した。

## README Restoration

READMEへ次を簡潔に戻した。

- Projectの中核的特徴
- Research Preview／Open Source状態
- Model Weight非同梱
- 第三者Artifactごとの独立した利用条件
- LLM出力の誤り・欠落・予期しない挙動
- 動作、互換性、正確性、安全性、完全性、可用性および特定目的適合性を保証しないこと
- 各文書の内容が変更される可能性
- RoadmapとLegal Artifactの優先関係

次は戻していない。

- 個別実行環境
- Hardware／Memory／Architecture／Acceleration／Version
- Model Artifact／Directory Tree
- Setup／CLI／Server操作
- External Service操作
- 未搭載機能と将来Componentの詳細列挙

READMEへ次の文を明記した。

> 各文書は修正する必要性があるため、都度内容が変更される可能性があります。

## Documentation Responsibility Rules

Shared Documentation Rulesへ、文書作成前に対象読者、役割、正本範囲、必須要素、禁止する詳細および参照先を確定する規則を追加した。

責務を明文化した文書：

- README
- Public Overview
- Public Concept
- Public Roadmap
- Requirements Specification
- System Architecture
- Technology Selection
- Basic Design
- Runtime Governance Specification
- Project Continuity Master
- Phase Index
- Phase Requirements／Architecture／ADR
- Operations／Evidence
- User Manual
- Handoff／Status／Review

必要な重複と不要な重複を分離した。

```text
必要:
  READMEの短い免責＋Legal正本への導線
  README／Overviewの現在Phase＋Roadmap導線
  Overviewの中核原則＋Concept／Architecture導線
  正本が単独で成立するための前提と結論

不要:
  READMEの環境Matrix／Command
  Overviewの個別Acceptance Log
  ConceptのPhase別Checklist
  Roadmapの操作手順全文
  複数正本への同一Schema全文コピー
```

## Stable／History

### README

```text
Before:
  docs/project/phases/phase_1_ex/history/operations/
  readme_before_required_elements_restoration_20260727131258.md

After:
  docs/project/phases/phase_1_ex/history/operations/
  readme_after_required_elements_restoration_20260727131419.md
```

```text
Before Lines : 59
After Lines  : 74

Before SHA-512:
d859f29c406a97be4216d991aa6ec765f36b9e2a65dbd222bb24464fdbf05382cd9fcdb77898ce148d2d1c13786493c85c31f321026b74f99ab784218636efa0

After SHA-512:
862f252417ed1154d7262ee5694cf918bcf41789b7df13681085512384d0f603b486f1db9886c231f7bf80d57dc4350b7c1919aa475eca6b3d7d128337ed2571
```

### Documentation Rules

```text
Before:
  docs/project/shared/history/conventions/
  documentation_rules_phase_1_ex_before_document_responsibility_rules_ja_20260727131258.md

After:
  docs/project/shared/history/conventions/
  documentation_rules_phase_1_ex_after_document_responsibility_rules_ja_20260727131419.md
```

```text
Before SHA-512:
fe536ec8975d60d9142b79b7bbf220297ba49f8bb7ecd7b24a7e2dad063b6027f61c1f634affffc9f2e1cc90cf98906ae1930400dc4524b88c9d201924a8e122

After SHA-512:
a5237b48480768c7a1b018e47c5cc85bb5e78dd9d6cf82ed10bd593b3099c748bb2dbf226a62585f845b2a80e4ef1f8b589e217bfacf121bdc8c0743b8d3d0ff
```

Filename Timestamp訂正前に作成した`20260727131008`版は、同一内容・同一HashのImmutable Duplicateとして残している。正規導線は実際のSnapshot作成時刻に対応する`20260727131258`版を使用する。

### Current Documentation Index

```text
Before:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_before_readme_required_elements_and_responsibility_rules_ja_20260727131434.md

After:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_after_readme_required_elements_and_responsibility_rules_ja_20260727131715.md
```

```text
Before SHA-512:
3da96b9d153af34979b4b793846fd80d47a8c4a4478dbe40f3272abbcd3ce9ecff5fefe4dd4b52de1b66cf7543c709123a87d1a4854fb28c84f2b86a3d5c21cf

After SHA-512:
5f24a297f834b792e773303ea242efb18c33756a55ca576853dcd93962940a161c01d72b7aff8055e196745e073f7ecc580e7437b69df28beeb25265538d8242
```

### Phase 1-ex Index

```text
Before:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_before_readme_required_elements_and_responsibility_rules_20260727131434.md

After:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_after_readme_required_elements_and_responsibility_rules_20260727131715.md
```

```text
Before SHA-512:
3e914a3738d9d8cf01d7d688d79770f0ebec97d0e5c1eb2fd27de546738342db3a68b4c363b40f25d2b315adffee0313d78855b296a9ab77ac5316a219236cb8

After SHA-512:
be73918927f765bd9eece8e9e7246f5dd1b3a06243de49242cc7181307267dab834f2ca055418fe6468414e545516edc11ac681898e98f8b5a94a444359cbec0
```

## Rule

文書責務を理由に必要情報を削りすぎず、自己完結を理由に詳細を複製しすぎない。上位文書は読者が判断を誤らないための要点と正本導線を保持し、詳細は責務を持つ下位文書へ委ねる。

## Validation

```text
README Required Elements                : pass
Requested Documentation Change Notice   : pass
README Detailed Environment／Commands   : absent
Documentation Responsibility Rules      : pass
Stable／After Snapshot Match             : pass
Relative Links Checked                  : 274
Missing Links                           : 0
Old Identity／Private Path               : 0
.DS_Store                               : 0
```

## Boundary

本作業はREADMEの必須要素とDocs作成Ruleの修正である。個別環境、操作手順または未搭載機能詳細をREADMEへ戻していない。Overview、Concept、Roadmap、Current Canonical、実装、Phase状態、Git、Public Demo、RAGまたはBackupの状態を変更しない。
